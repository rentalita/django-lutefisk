# -*- coding: utf-8 -*-

from django.conf import settings

_ = lambda x: x

LUTEFISK_SIGNIN_REDIRECT_URL = '/accounts/'
LUTEFISK_ACTIVATION_REQUIRED = True
LUTEFISK_ACTIVATION_DAYS = 7
LUTEFISK_ACTIVATION_NOTIFY = True
LUTEFISK_ACTIVATION_NOTIFY_DAYS = 5
LUTEFISK_ACTIVATED = 'ALREADY_ACTIVATED'
LUTEFISK_REMEMBER_ME_DAYS = (_('a month'), 30)
LUTEFISK_FORBIDDEN_USERNAMES = ('signup', 'signin', 'signout')
LUTEFISK_USE_HTTPS = True
LUTEFISK_DEFAULT_PRIVACY = 'registered'
LUTEFISK_USE_MESSAGES = False
LUTEFISK_LANGUAGE_FIELD = 'language'
LUTEFISK_WITHOUT_USERNAMES = True

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
