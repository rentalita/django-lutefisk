# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

import lutefisk.urls

urlpatterns = patterns('',
                       url(r'^accounts/', include(lutefisk.urls)),
                       )

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
