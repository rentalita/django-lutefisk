# -*- coding: utf-8 -*-

from django.contrib import admin

from lutefisk import utils

admin.site.register(utils.get_profile_model())

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
