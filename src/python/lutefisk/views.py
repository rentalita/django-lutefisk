# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.generic import list_detail
from django.views.generic.simple import direct_to_template

from lutefisk import forms
from lutefisk import models
from lutefisk import signals
from lutefisk import utils


def signup(request, template_name='lutefisk/signup_form.html',
           message_template_name='lutefisk/signup_message.html',
           success_url=None, extra_context=None):
    """ TODO:

    """

    if not extra_context:
        extra_context = dict()

    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    form = forms.SignupForm(data=data)

    if data is not None:
        if form.is_valid():
            user = form.save()

            signals.signup_complete.send(sender=None, user=user)

            if success_url:
                redirect_to = success_url
            else:
                redirect_to = utils.get_site_url()

            extra_context['EMAIL'] = form.cleaned_data['email']

            messages.add_message(request, messages.SUCCESS,
                                 render_to_string(message_template_name, extra_context),
                                 fail_silently=True)

            if request.user.is_authenticated():
                logout(request)

            return redirect(redirect_to)

    extra_context['form'] = form

    return direct_to_template(request, template_name, extra_context=extra_context)


def activate(request, username, activation_key,
             template_name='lutefisk/activate_fail.html',
             success_url=None, extra_context=None):
    """ TODO:

    """

    if not extra_context:
        extra_context = dict()

    user = models.LutefiskSignup.objects.activate_user(username, activation_key)

    if not user:
        return direct_to_template(request, template_name, extra_context=extra_context)

    user = authenticate(identification=user.email, check_password=False)
    login(request, user)

    if success_url:
        redirect_to = success_url
    else:
        redirect_to = reverse('lutefisk_profile_detail')

    return redirect(redirect_to)


@login_required
def signout(request, message_template_name='lutefisk/signout_message.html',
            extra_context=None):
    """ TODO:

    """

    logout(request)

    messages.add_message(request, messages.SUCCESS,
                         render_to_string(message_template_name, extra_context),
                         fail_silently=True)

    return redirect(utils.get_site_url())


@login_required
def email_change_confirm(request, confirmation_key,
                         message_template_name='lutefisk/email_change_confirm_message.html',
                         success_url=None, extra_context=None):
    """ TODO:

    """

    user = models.LutefiskSignup.objects.confirm_email(request.user.username, confirmation_key)

    if not user:
        raise Http404()

    if not extra_context:
        extra_context = dict()

    extra_context['EMAIL'] = user.email

    messages.add_message(request, messages.SUCCESS,
                         render_to_string(message_template_name, extra_context),
                         fail_silently=True)

    if success_url:
        redirect_to = success_url
    else:
        redirect_to = reverse('lutefisk_profile_detail')

    return redirect(redirect_to)


def password_reset(request, template_name='lutefisk/password_reset_form.html',
                   message_template_name='lutefisk/password_reset_message.html',
                   email_template_name='lutefisk/emails/password_reset_message.txt',
                   success_url=None, extra_context=None):
    """ TODO:

    """

    if not extra_context:
        extra_context = dict()

    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    form = forms.PasswordResetForm(data=data)

    if data is not None:
        if form.is_valid():
            form.save(email_template_name=email_template_name)

            extra_context['EMAIL'] = form.cleaned_data['email']

            messages.add_message(request, messages.SUCCESS,
                                 render_to_string(message_template_name, extra_context),
                                 fail_silently=True)

            if success_url:
                redirect_to = success_url
            else:
                redirect_to = utils.get_site_url()

            return redirect(redirect_to)

    extra_context['form'] = form

    return direct_to_template(request, template_name, extra_context=extra_context)


def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='lutefisk/password_reset_confirm_form.html',
                           message_template_name='lutefisk/password_reset_confirm_message.html',
                           success_url=None, extra_context=None):
    """ TODO:

    """

    user, validlink = utils.confirm_password_reset(uidb36, token)

    if user is None or not validlink:
        raise Http404()

    if not extra_context:
        extra_context = dict()

    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    form = forms.SetPasswordForm(user, data=data)

    if data is not None:
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.SUCCESS,
                                 render_to_string(message_template_name, extra_context),
                                 fail_silently=True)

            if success_url:
                redirect_to = success_url
            else:
                redirect_to = reverse('lutefisk_signin')

            return redirect(redirect_to)

    extra_context['form'] = form

    return direct_to_template(request, template_name, extra_context=extra_context)


def signin(request, template_name='lutefisk/signin_form.html',
           message_template_name='lutefisk/signin_fail_message.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_signin_function=utils.signin_redirect,
           extra_context=None):
    """ TODO:

    """

    if not extra_context:
        extra_context = dict()

    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    form = forms.AuthenticationForm(data=data)

    if data is not None:
        if form.is_valid():
            identification = form.cleaned_data['identification']
            password = form.cleaned_data['password']

            user = authenticate(identification=identification, password=password)

            if user.is_active:
                login(request, user)

                remember_me = form.cleaned_data['remember_me']

                if remember_me:
                    request.session.set_expiry(settings.LUTEFISK_REMEMBER_ME_DAYS[1] * 86400)
                else:
                    request.session.set_expiry(0)

                redirect_to = redirect_signin_function(request.REQUEST.get(redirect_field_name), user)
                return redirect(redirect_to)
            else:
                extra_context['EMAIL'] = user.email

                messages.add_message(request, messages.ERROR,
                                     render_to_string(message_template_name, extra_context),
                                     fail_silently=True)

                return redirect(utils.get_site_url())

    extra_context['form'] = form
    extra_context['next'] = request.REQUEST.get(redirect_field_name)

    return direct_to_template(request, template_name, extra_context=extra_context)


@login_required
def email_change(request, template_name='lutefisk/email_change_form.html',
                 message_template_name='lutefisk/email_change_message.html',
                 success_url=None, extra_context=None):
    """ TODO:

    """

    user = request.user
    profile = user.get_profile()

    if not extra_context:
        extra_context = dict()

    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    form = forms.ChangeEmailForm(user, data=data)

    if data is not None:
        if form.is_valid():
            form.save()

            extra_context['EMAIL'] = form.cleaned_data['email']

            messages.add_message(request, messages.SUCCESS,
                                 render_to_string(message_template_name, extra_context),
                                 fail_silently=True)

            if success_url:
                redirect_to = success_url
            else:
                redirect_to = reverse('lutefisk_profile_detail')

            return redirect(redirect_to)

    extra_context['form'] = form
    extra_context['profile'] = profile

    return direct_to_template(request, template_name, extra_context=extra_context)


@login_required
def password_change(request, template_name='lutefisk/password_change_form.html',
                    message_template_name='lutefisk/password_change_message.html',
                    success_url=None, extra_context=None):
    """ TODO:

    """

    user = request.user
    profile = user.get_profile()

    if not extra_context:
        extra_context = dict()

    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    form = forms.PasswordChangeForm(user, data=data)

    if data is not None:
        if form.is_valid():
            form.save()

            signals.password_complete.send(sender=None, user=user)

            messages.add_message(request, messages.SUCCESS,
                                 render_to_string(message_template_name, extra_context),
                                 fail_silently=True)

            if success_url:
                redirect_to = success_url
            else:
                redirect_to = reverse('lutefisk_profile_detail')

            return redirect(redirect_to)

    extra_context['form'] = form
    extra_context['profile'] = profile

    return direct_to_template(request, template_name, extra_context=extra_context)


@login_required
def profile_edit(request, template_name='lutefisk/profile_form.html',
                 success_url=None, extra_context=None, form=None, **kwargs):
    """ TODO:

    """

    user = request.user
    profile = user.get_profile()

    if not extra_context:
        extra_context = dict()

    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    if form is None:
        _form = EditProfileForm
    else:
        _form = form

    form = _form(data=data, instance=profile)

    if data is not None:
        if form.is_valid():
            profile = form.save()

            if success_url:
                redirect_to = success_url
            else:
                redirect_to = reverse('lutefisk_profile_detail')

            return redirect(redirect_to)

    extra_context['form'] = form
    extra_context['profile'] = profile

    return direct_to_template(request, template_name, extra_context=extra_context, **kwargs)


@login_required
def profile_detail(request, template_name='lutefisk/profile_detail.html',
                   extra_context=None, **kwargs):
    """ TODO:

    """

    user = request.user
    profile = user.get_profile()

    if not extra_context:
        extra_context = dict()

    extra_context['profile'] = profile

    return direct_to_template(request, template_name, extra_context=extra_context, **kwargs)

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
