from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured

from lutefisk.utils import generate_sha1, get_protocol, get_datetime_now
from lutefisk.managers import LutefiskManager, LutefiskBaseProfileManager

import datetime, random


class LutefiskSignup(models.Model):
    """
    Lutefisk model which stores all the necessary information to have a full
    functional user implementation on your Django website.

    """
    user = models.OneToOneField(User,
                                verbose_name=_('user'),
                                related_name='lutefisk_signup')

    last_active = models.DateTimeField(_('last active'),
                                       blank=True,
                                       null=True,
                                       help_text=_('The last date that the user was active.'))

    activation_key = models.CharField(_('activation key'),
                                      max_length=40,
                                      blank=True)

    activation_notification_send = models.BooleanField(_('notification send'),
                                                       default=False,
                                                       help_text=_('Designates whether this user has already got a notification about activating their account.'))

    email_unconfirmed = models.EmailField(_('unconfirmed email address'),
                                          blank=True,
                                          help_text=_('Temporary email address when the user requests an email change.'))

    email_confirmation_key = models.CharField(_('unconfirmed email verification key'),
                                              max_length=40,
                                              blank=True)

    email_confirmation_key_created = models.DateTimeField(_('creation date of email confirmation key'),
                                                          blank=True,
                                                          null=True)


    objects = LutefiskManager()

    class Meta:
        verbose_name = _('lutefisk registration')
        verbose_name_plural = _('lutefisk registrations')

    def __unicode__(self):
        return '%s' % self.user.username

    def change_email(self, email):
        """
        Changes the email address for a user.

        A user needs to verify this new email address before it becomes
        active. By storing the new email address in a temporary field --
        ``temporary_email`` -- we are able to set this email address after the
        user has verified it by clicking on the verification URI in the email.
        This email gets send out by ``send_verification_email``.

        :param email:
        The new email address that the user wants to use.

        """
        self.email_unconfirmed = email

        salt, hash = generate_sha1(self.user.username)
        self.email_confirmation_key = hash
        self.email_confirmation_key_created = get_datetime_now()
        self.save()

        # Send email for activation
        self.send_confirmation_email()

    def send_confirmation_email(self):
        """
        Sends an email to confirm the new email address.

        This method sends out two emails. One to the new email address that
        contains the ``email_confirmation_key`` which is used to verify this
        this email address with :func:`LutefiskUser.objects.confirm_email`.

        The other email is to the old email address to let the user know that
        a request is made to change this email address.

        """
        context= {'user': self.user,
                  'without_usernames': settings.LUTEFISK_WITHOUT_USERNAMES,
                  'new_email': self.email_unconfirmed,
                  'protocol': get_protocol(),
                  'confirmation_key': self.email_confirmation_key,
                  'site': Site.objects.get_current()}


        # Email to the old address
        subject_old = render_to_string('lutefisk/emails/confirmation_email_subject_old.txt',
                                       context)
        subject_old = ''.join(subject_old.splitlines())

        message_old = render_to_string('lutefisk/emails/confirmation_email_message_old.txt',
                                       context)

        send_mail(subject_old,
                  message_old,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email])

        # Email to the new address
        subject_new = render_to_string('lutefisk/emails/confirmation_email_subject_new.txt',
                                       context)
        subject_new = ''.join(subject_new.splitlines())

        message_new = render_to_string('lutefisk/emails/confirmation_email_message_new.txt',
                                       context)

        send_mail(subject_new,
                  message_new,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.email_unconfirmed,])

    def activation_key_expired(self):
        """
        Checks if activation key is expired.

        Returns ``True`` when the ``activation_key`` of the user is expired and
        ``False`` if the key is still valid.

        The key is expired when it's set to the value defined in
        ``LUTEFISK_ACTIVATED`` or ``activation_key_created`` is beyond the
        amount of days defined in ``LUTEFISK_ACTIVATION_DAYS``.

        """
        expiration_days = datetime.timedelta(days=settings.LUTEFISK_ACTIVATION_DAYS)
        expiration_date = self.user.date_joined + expiration_days
        if self.activation_key == settings.LUTEFISK_ACTIVATED:
            return True
        if get_datetime_now() >= expiration_date:
            return True
        return False

    def send_activation_email(self):
        """
        Sends a activation email to the user.

        This email is send when the user wants to activate their newly created
        user.

        """
        context= {'user': self.user,
                  'without_usernames': settings.LUTEFISK_WITHOUT_USERNAMES,
                  'protocol': get_protocol(),
                  'activation_days': settings.LUTEFISK_ACTIVATION_DAYS,
                  'activation_key': self.activation_key,
                  'site': Site.objects.get_current()}

        subject = render_to_string('lutefisk/emails/activation_email_subject.txt',
                                   context)
        subject = ''.join(subject.splitlines())

        message = render_to_string('lutefisk/emails/activation_email_message.txt',
                                   context)
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email,])

class LutefiskBaseProfile(models.Model):
    """ Base model needed for extra profile functionality """
    PRIVACY_CHOICES = (
        ('open', _('Open')),
        ('registered', _('Registered')),
        ('closed', _('Closed')),
        )

    privacy = models.CharField(_('privacy'),
                               max_length=15,
                               choices=PRIVACY_CHOICES,
                               default=settings.LUTEFISK_DEFAULT_PRIVACY,
                               help_text = _('Designates who can view your profile.'))

    objects = LutefiskBaseProfileManager()


    class Meta:
        """
        Meta options making the model abstract and defining permissions.

        The model is ``abstract`` because it only supplies basic functionality
        to a more custom defined model that extends it. This way there is not
        another join needed.

        We also define custom permissions because we don't know how the model
        that extends this one is going to be called. So we don't know what
        permissions to check. For ex. if the user defines a profile model that
        is called ``MyProfile``, than the permissions would be
        ``add_myprofile`` etc. We want to be able to always check
        ``add_profile``, ``change_profile`` etc.

        """
        abstract = True

    def __unicode__(self):
        return 'Profile of %(username)s' % {'username': self.user.username}

    def get_full_name_or_username(self):
        """
        Returns the full name of the user, or if none is supplied will return
        the username.

        Also looks at ``LUTEFISK_WITHOUT_USERNAMES`` settings to define if it
        should return the username or email address when the full name is not
        supplied.

        :return:
        ``String`` containing the full name of the user. If no name is
        supplied it will return the username or email address depending on
        the ``LUTEFISK_WITHOUT_USERNAMES`` setting.

        """
        user = self.user
        if user.first_name or user.last_name:
            # We will return this as translated string. Maybe there are some
            # countries that first display the last name.
            name = _("%(first_name)s %(last_name)s") % \
                {'first_name': user.first_name,
                 'last_name': user.last_name}
        else:
            # Fallback to the username if usernames are used
            if not settings.LUTEFISK_WITHOUT_USERNAMES:
                name = "%(username)s" % {'username': user.username}
            else:
                name = "%(email)s" % {'email': user.email}
        return name.strip()

class LutefiskLanguageBaseProfile(LutefiskBaseProfile):
    """
    Extends the :class:`LutefiskBaseProfile` with a language choice.

    Use this model in combination with ``LutefiskLocaleMiddleware`` automatically
    set the language of users when they are signed in.

    """
    language = models.CharField(_('language'),
                                max_length=5,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE[:2])

    class Meta:
        abstract = True
