# -*- coding: utf-8 -*-

import datetime
import random
import urllib

from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable, User
from django.contrib.auth.tokens import default_token_generator
from django.db.models import get_model
from django.utils.hashcompat import md5_constructor
from django.utils.hashcompat import sha_constructor
from django.utils.http import base36_to_int


def signin_redirect(redirect=None, user=None):
    """
    Redirect user after successful sign in.

    First looks for a ``requested_redirect``. If not supplied will fall-back to
    the user specific account page. If all fails, will fall-back to the standard
    Django ``LOGIN_REDIRECT_URL`` setting. Returns a string defining the URI to
    go next.

    :param redirect:
    A value normally supplied by ``next`` form field. Gets preference
    before the default view which requires the user.

    :param user:
    A ``User`` object specifying the user who has just signed in.

    :return: String containing the URI to redirect to.

    """
    if redirect:
        return redirect
    elif user is not None:
        return settings.LUTEFISK_SIGNIN_REDIRECT_URL
    else:
        return settings.LOGIN_REDIRECT_URL


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
    The string that needs to be encrypted.

    :param salt:
    Optionally define your own salt. If none is supplied, will use a random
    string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not salt:
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
    return (salt, sha_constructor(salt+str(string)).hexdigest())


def get_profile_model():
    """
    Return the model class for the currently-active user profile
    model, as defined by the ``AUTH_PROFILE_MODULE`` setting.

    :return: The model that is used as profile.

    """
    if (not hasattr(settings, 'AUTH_PROFILE_MODULE')) or (not settings.AUTH_PROFILE_MODULE):
        raise SiteProfileNotAvailable

    profile_mod = get_model(*settings.AUTH_PROFILE_MODULE.split('.'))
    if profile_mod is None:
        raise SiteProfileNotAvailable
    return profile_mod


def get_protocol():
    """
    Returns a string with the current protocol.

    This can be either 'http' or 'https' depending on ``LUTEFISK_USE_HTTPS``
    setting.

    """
    protocol = 'http'
    if settings.LUTEFISK_USE_HTTPS:
        protocol = 'https'
    return protocol


def get_site_url():
    """
    Determine the site index. When all else fails return '/'.

    :return: A URL that points to the site index.

    """
    if hasattr(settings, 'SITE_URL'):
        return settings.SITE_URL
    return '/'


def get_datetime_now():
    """
    Returns datetime object with current point in time.

    In Django 1.4+ it uses Django's django.utils.timezone.now() which returns
    an aware or naive datetime that represents the current point in time
    when ``USE_TZ`` in project's settings is True or False respectively.
    In older versions of Django it uses datetime.datetime.now().

    """
    try:
        from django.utils import timezone
        return timezone.now()
    except ImportError:
        return datetime.datetime.now()


def confirm_password_reset(uidb36, token, token_generator=default_token_generator):
    try:
        user = User.objects.get(id=base36_to_int(uidb36))
    except (ValueError, User.DoesNotExist):
        user = None

    return user, token_generator.check_token(user, token) if user else False

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
