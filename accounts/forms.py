from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordChangeForm
from django.contrib.auth.models import User
from website.models import BirdUser


class SignUpForm(UserCreationForm):
    #username = forms.CharField(max_length=30)
    email = forms.CharField(max_length=200)
    exclude = ['username']

    class Meta:
        model = BirdUser
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder':'Email Address','autofocus': False})
        self.fields['password1'].widget.attrs.update({'placeholder':'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder':'Confirm Password'})
        # for field_name in ('username', 'email', 'password1', 'password2'):
        #     self.fields[field_name].help_text = ''
        # self.fields['username'].widget.attrs.update({'placeholder':'Username'})
        # error_messages={'required': 'Password must contain at least 8 characters!'}
        # self.fields['username'].error_messages.update({
        #     'required': 'Password must contain at least 8 characters!',
        # })

class UserLoginForm(AuthenticationForm):

    class Meta:
        model = BirdUser
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder':'Email Address','autofocus': False}),
        self.fields['password'].widget.attrs.update({'placeholder':'Password'})

# https://docs.djangoproject.com/en/1.8/_modules/django/contrib/auth/forms/#PasswordChangeForm
# https://github.com/django/django/blob/main/django/contrib/auth/forms.py#L363
class UserPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'placeholder': 'Old Password', 'autofocus': False}),
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'New Password'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Confirm new Password'})


