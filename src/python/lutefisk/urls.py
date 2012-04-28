# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from lutefisk import views as lutefisk_views

urlpatterns = patterns('',
                       # Signup, signin and signout
                       url(r'^signup/$',
                           lutefisk_views.signup,
                           name='lutefisk_signup'),
                       url(r'^signin/$',
                           lutefisk_views.signin,
                           name='lutefisk_signin'),
                       url(r'^signout/$',
                           lutefisk_views.signout,
                           name='lutefisk_signout'),

                       # Reset password
                       url(r'^reset-password/$',
                           lutefisk_views.password_reset,
                           name='lutefisk_password_reset'),
                       url(r'^reset-password/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           lutefisk_views.password_reset_confirm,
                           name='lutefisk_password_reset_confirm'),

                       # Activate
                       url(r'^activate/(?P<username>[\.\w]+)/(?P<activation_key>\w+)/$',
                           lutefisk_views.activate,
                           name='lutefisk_activate'),

                       # Change email and confirm it
                       url(r'^change-email/$',
                           lutefisk_views.email_change,
                           name='lutefisk_email_change'),
                       url(r'^change-email/(?P<confirmation_key>\w+)/$',
                           lutefisk_views.email_change_confirm,
                           name='lutefisk_email_change_confirm'),

                       # Change password
                       url(r'^change-password/$',
                           lutefisk_views.password_change,
                           name='lutefisk_password_change'),

                       # Edit profile
                       url(r'^edit/$',
                           lutefisk_views.profile_edit,
                           name='lutefisk_profile_edit'),

                       # View profiles
                       url(r'^$',
                           lutefisk_views.profile_detail,
                           name='lutefisk_profile_detail'),
                       )

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
