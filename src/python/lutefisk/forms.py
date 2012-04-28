# -*- coding: utf-8 -*-

import random

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, forms as auth_forms
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _

from lutefisk.models import LutefiskSignup
from lutefisk.utils import get_profile_model

required_attrs = {'class': 'required'}


class SignupForm(forms.Form):
    """ TODO:

    """

    legend = _('Sign Up')

    widget = forms.TextInput(attrs=dict(required_attrs, maxlength=75))
    email = forms.EmailField(widget=widget, label=_("Email"))

    widget = forms.PasswordInput(attrs=required_attrs, render_value=False)
    password1 = forms.CharField(widget=widget, label=_("Password"))

    widget = forms.PasswordInput(attrs=required_attrs, render_value=False)
    password2 = forms.CharField(widget=widget, label=_("Repeat password"))

    def clean_email(self):
        """ Validate that the e-mail address is unique. """
        cleaned_email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=cleaned_email):
            raise forms.ValidationError(_(u'This email address is already in use by someone else.'))
        return cleaned_email

    def clean(self):
        """
        Validates that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('The two passwords do not match.'))
        return self.cleaned_data

    def save(self):
        """ Creates a new user and account. Returns the newly created user. """
        while True:
            username = sha_constructor(str(random.random())).hexdigest()[:5]
            try:
                User.objects.get(username__iexact=username)
            except User.DoesNotExist: break

        cleaned_email = self.cleaned_data['email']
        password = self.cleaned_data['password1']

        new_user = LutefiskSignup.objects.create_user(username,
                                                      cleaned_email,
                                                      password,
                                                      not settings.LUTEFISK_ACTIVATION_REQUIRED,
                                                      settings.LUTEFISK_ACTIVATION_REQUIRED)
        return new_user

class SignupFormTos(SignupForm):
    """ Add a Terms of Service button to the ``SignupForm``. """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=required_attrs),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _('You must agree to the terms to register.')})

class AuthenticationForm(forms.Form):
    """
    A custom form where the identification can be a e-mail address or username.

    """

    legend = _('Sign In')

    widget = forms.TextInput(attrs=dict(required_attrs, maxlength=75))
    identification = forms.EmailField(widget=widget, label=_(u"Email"))

    widget = forms.PasswordInput(attrs=required_attrs, render_value=False)
    password = forms.CharField(widget=widget, label=_("Password"))

    remember_me = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['remember_me'].label = _(u'Remember me for %(days)s') % \
            {'days': _(settings.LUTEFISK_REMEMBER_ME_DAYS[0])}

    def clean(self):
        """
        Checks for the identification and password.

        If the combination can't be found will raise an invalid sign in error.

        """
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            user = authenticate(identification=identification, password=password)
            if user is None:
                raise forms.ValidationError(_(u"The password associated with this email address is incorrect."))
        return self.cleaned_data

class ChangeEmailForm(forms.Form):

    legend = _('Change Email')

    widget = forms.TextInput(attrs=dict(required_attrs, maxlength=75))
    email = forms.EmailField(widget=widget, label=_(u"New email"))

    def __init__(self, user, *args, **kwargs):
        """
        The current ``user`` is needed for initialisation of this form so
        that we can check if the email address is still free and not always
        returning ``True`` for this query because it's the users own e-mail
        address.

        """
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        if not isinstance(user, User):
            raise TypeError, "user must be an instance of User"
        else:
            self.user = user

    def clean_email(self):
        """ Validate that the email is not already registered with another user """
        cleaned_email = self.cleaned_data['email']
        if cleaned_email.lower() == self.user.email:
            raise forms.ValidationError(_(u'This is your current email address.'))
        if User.objects.filter(email__iexact=cleaned_email).exclude(email__iexact=self.user.email):
            raise forms.ValidationError(_(u'This email address is already in use by someone else.'))
        return cleaned_email

    def save(self):
        """
        Save method calls :func:`user.change_email()` method which sends out an
        email with an verification key to verify and with it enable this new
        email address.

        """
        return self.user.lutefisk_signup.change_email(self.cleaned_data['email'])

class SetPasswordForm(auth_forms.SetPasswordForm):

    legend = _('Set Password')

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = _('New password')
        self.fields['new_password2'].label = _('Repeat new password')

class PasswordChangeForm(auth_forms.PasswordChangeForm):

    legend = _('Change Password')

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = _('New password')
        self.fields['new_password2'].label = _('Repeat new password')
        self.fields['old_password'].label = _('Current password')

class PasswordResetForm(auth_forms.PasswordResetForm):

    legend = _('Reset Password')

    def save(self, *args, **kwargs):
        kwargs['use_https'] = True
        super(PasswordResetForm, self).save(*args, **kwargs)

class EditProfileForm(forms.ModelForm):

    legend = _('Edit Profile')

    class Meta:
        model = get_profile_model()
        exclude = ['user']

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
