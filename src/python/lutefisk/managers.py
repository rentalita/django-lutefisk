# -*- coding: utf-8 -*-

import datetime
import re

from django.conf import settings
from django.contrib.auth.models import User, UserManager, AnonymousUser
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _

from lutefisk import signals
from lutefisk import utils

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class LutefiskManager(UserManager):
    """ Extra functionality for the Lutefisk model. """

    def create_user(self, username, email, password, active=False,
                    send_email=True):
        """
        A simple wrapper that creates a new :class:`User`.

        :param username:
        String containing the username of the new user.

        :param email:
        String containing the email address of the new user.

        :param password:
        String containing the password for the new user.

        :param active:
        Boolean that defines if the user requires activation by clicking
        on a link in an e-mail. Defauts to ``True``.

        :param send_email:
        Boolean that defines if the user should be send an email. You could
        set this to ``False`` when you want to create a user in your own
        code, but don't want the user to activate through email.

        :return: :class:`User` instance representing the new user.

        """
        now = utils.get_datetime_now()

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = active
        new_user.save()

        lutefisk_profile = self.create_lutefisk_profile(new_user)

        # All users have an empty profile
        profile_model = utils.get_profile_model()
        try:
            new_profile = new_user.get_profile()
        except profile_model.DoesNotExist:
            new_profile = profile_model(user=new_user)
            new_profile.save(using=self._db)

        if send_email:
            lutefisk_profile.send_activation_email()
            
        return new_user

    def create_lutefisk_profile(self, user):
        """
        Creates an :class:`LutefiskSignup` instance for this user.

        :param user:
        Django :class:`User` instance.

        :return: The newly created :class:`LutefiskSignup` instance.

        """
        if isinstance(user.username, unicode):
            user.username = user.username.encode('utf-8')
        salt, activation_key = utils.generate_sha1(user.username)

        return self.create(user=user, activation_key=activation_key)

    def activate_user(self, username, activation_key):
        """
        Activate an :class:`User` by supplying a valid ``activation_key``.

        If the key is valid and an user is found, activates the user and
        return it. Also sends the ``activation_complete`` signal.

        :param username:
        String containing the username that wants to be activated.

        :param activation_key:
        String containing the secret SHA1 for a valid activation.

        :return:
        The newly activated :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(activation_key):
            try:
                lutefisk = self.get(user__username=username,
                                    activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not lutefisk.activation_key_expired():
                lutefisk.activation_key = settings.USERENA_ACTIVATED
                user = lutefisk.user
                user.is_active = True
                lutefisk.save(using=self._db)
                user.save(using=self._db)

                signals.activation_complete.send(sender=None, user=user)

                return user
        return False

    def confirm_email(self, username, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted e-mail
        address as the current e-mail address. Returns the user after
        success or ``False`` when the confirmation key is
        invalid. Also sends the ``confirmation_complete`` signal.

        :param username:
        String containing the username of the user that wants their email
        verified.

        :param confirmation_key:
        String containing the secret SHA1 that is used for verification.

        :return:
        The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                lutefisk = self.get(user__username=username,
                                    email_confirmation_key=confirmation_key,
                                    email_unconfirmed__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user = lutefisk.user
                old_email = user.email
                user.email = lutefisk.email_unconfirmed
                lutefisk.email_unconfirmed, lutefisk.email_confirmation_key = '',''
                lutefisk.save(using=self._db)
                user.save(using=self._db)

                signals.confirmation_complete.send(sender=None, user=user, old_email=old_email)

                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.

        """
        deleted_users = []
        for user in User.objects.filter(is_staff=False, is_active=False):
            if user.lutefisk_signup.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users


class LutefiskBaseProfileManager(models.Manager):
    """ Manager for :class:`LutefiskProfile` """
    def get_visible_profiles(self, user=None):
        """
        Returns all the visible profiles available to this user.

        For now keeps it simple by just applying the cases when a user is not
        active, a user has it's profile closed to everyone or a user only
        allows registered users to view their profile.

        :param user:
        A Django :class:`User` instance.

        :return:
        All profiles that are visible to this user.

        """
        profiles = self.all()

        filter_kwargs = {'user__is_active': True}

        profiles = profiles.filter(**filter_kwargs)
        if user and isinstance(user, AnonymousUser):
            profiles = profiles.exclude(Q(privacy='closed') | Q(privacy='registered'))
        else:
            profiles = profiles.exclude(Q(privacy='closed'))
        return profiles

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
