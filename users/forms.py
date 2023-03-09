from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from snowplowrouting.models import InviteEmployee

email_used = False

def validate_email(value):
    global email_used
    if User.objects.filter(email=value).exists():
        email_used = True
        raise ValidationError((f"{value} is taken."), params={'value': value})

def validate_username(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError((f"{value} is taken."), params={'value': value})

class RegisterForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields.pop('password2')

    email = forms.EmailField(max_length=100, required=True,
                             validators=[validate_email],
                             help_text='Enter email addres',
                             widget=forms.TextInput(
                                 attrs={'class': 'form-widgets',
                                        'id': 'widget_mail',
                                        'placeholder': 'Email'
                                        }
                             )
                             )

    first_name = forms.CharField(max_length=50, required=True,
                                 help_text='Enter first name',
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-widgets-md6',
                                            'id': 'widget_fst_name',
                                            'placeholder': 'First Name'
                                            }
                                 )
                                 )

    last_name = forms.CharField(max_length=50, required=True,
                                help_text='Enter last name',
                                widget=forms.TextInput(
                                    attrs={'class': 'form-widgets-md6',
                                           'id': 'widget_lst_name',
                                           'placeholder': 'Last Name'
                                           }
                                )
                                )

    username = forms.CharField(max_length=50, required=True,
                               validators=[validate_username],
                               help_text='Enter username',
                               widget=forms.TextInput(
                                   attrs={'class': 'form-widgets',
                                          'id': 'widget_username',
                                          'placeholder': 'Username'
                                          }
                               )
                               )

    password1 = forms.CharField(max_length=50, required=True,
                                help_text='Enter password',
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-widgets',
                                           'id': 'widget_passw',
                                           'placeholder': 'Password'
                                           }
                                )
                                )

    validator_token = forms.CharField(max_length=50, required=True,
                                      help_text='Enter token',
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-widgets',
                                                 'id': 'widget_token',
                                                 'placeholder': 'Token'
                                                 }
                                      )
                                      )
    county = forms.CharField(max_length=50, required=False,
                             help_text='Select County',
                             widget=forms.TextInput(
                                 attrs={'class': 'form-widgets',
                                        'id': 'widget_county',
                                        'placeholder': 'Select on map'
                                        }
                             )
                             )

    status = forms.DecimalField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password1', 'username',
            'validator_token', 'county', 'status',
        ]

class RegisterEmployeeForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields.pop('password2')

    email = forms.EmailField(max_length=100, required=True,
                             validators=[validate_email],
                             help_text='Enter email addres',
                             widget=forms.TextInput(
                                 attrs={'class': 'form-widgets',
                                        'id': 'widget_mail',
                                        'placeholder': 'Email'
                                        }
                             )
                             )

    first_name = forms.CharField(max_length=50, required=True,
                                 help_text='Enter first name',
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-widgets-md6',
                                            'id': 'widget_fst_name',
                                            'placeholder': 'First Name'
                                            }
                                 )
                                 )

    last_name = forms.CharField(max_length=50, required=True,
                                help_text='Enter last name',
                                widget=forms.TextInput(
                                    attrs={'class': 'form-widgets-md6',
                                           'id': 'widget_lst_name',
                                           'placeholder': 'Last Name'
                                           }
                                )
                                )

    username = forms.CharField(max_length=50, required=True,
                               validators=[validate_username],
                               help_text='Enter username',
                               widget=forms.TextInput(
                                   attrs={'class': 'form-widgets',
                                          'id': 'widget_username',
                                          'placeholder': 'Username'
                                          }
                               )
                               )

    password1 = forms.CharField(max_length=50, required=True,
                                help_text='Enter password',
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-widgets',
                                           'id': 'widget_passw',
                                           'placeholder': 'Password'
                                           }
                                )
                                )

    validator_token = forms.CharField(max_length=50, required=True,
                                      help_text='Enter token',
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-widgets',
                                                 'id': 'widget_token',
                                                 'placeholder': 'Token'
                                                 }
                                      )
                                      )
    county = forms.CharField(max_length=50, required=False,
                             widget=forms.HiddenInput(),
                             initial="temp"
                             )

    status = forms.DecimalField(required=False)

    def clean(self):
        global email_used
        form_data = self.cleaned_data
        if not email_used:
            employee = InviteEmployee.objects.filter(email = form_data['email']).values()
            print(form_data)
            if employee.exists():
                if employee[0]['token'] != form_data['validator_token']:
                    self._errors['validator_token'] = ['That is not your token!']
                    del form_data['validator_token']
            else:
                self._errors['email'] = ['We can not find you!']
                del form_data['email']
        email_used = False
        return form_data

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password1', 'username',
            'validator_token', 'county', 'status',
        ]


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True,
                               help_text='Enter username',
                               widget=forms.TextInput(
                                   attrs={'class': 'form-widgets',
                                          'id': 'widget_username',
                                          'placeholder': 'Username'
                                          }
                               )
                               )
    password = forms.CharField(max_length=50, required=True,
                               help_text='Enter password',
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-widgets',
                                          'id': 'widget_passw',
                                          'placeholder': 'Password'
                                          }
                               )
                               )
