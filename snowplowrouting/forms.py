from django import forms
from .models import InviteEmployee, Machinery, Schedule
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError((f"{value} is taken."), params={'value': value})

def validate_vin(value):
    if len(value) != 17:
        print(len(value))
        raise ValidationError((f"{value} must contain 17 digits."), params={'value': value})


class AddEmployeeForm(forms.ModelForm):
    email = forms.EmailField(max_length=300, required=True,
                             validators=[validate_email],
                             help_text='Enter email addresses',
                             widget=forms.TextInput(
                                 attrs={'class': 'form-widgets',
                                        'id': 'widget_mails',
                                        'placeholder': 'Add Email'
                                        }
                             )
                             )

    class Meta:
        model = InviteEmployee
        fields = ['email', 'token', 'county']


class AddMachineryForm(forms.ModelForm):

    model = forms.CharField(max_length=100, required=True,
                            help_text='Enter model',
                            widget=forms.TextInput(
                                attrs={'class': 'form-input',
                                       'id': 'widget_model',
                                       'placeholder': 'Brand/Model'
                                       }
                            )
                            )
    vin = forms.CharField(max_length=17, min_length=17, required=True,
                          validators=[validate_vin],
                          help_text='Enter VIN',
                          widget=forms.TextInput(
                              attrs={'class': 'form-input',
                                     'id': 'widget_vin',
                                     'placeholder': 'VIN'
                                     }
                          )
                          )
    tank_capacity = forms.FloatField(required=True,
                                     help_text='tank',
                                     widget=forms.NumberInput(
                                         attrs={'class': 'form-input',
                                                'id': 'widget_fst_name',
                                                'placeholder': 'Tank Capacity'
                                                }
                                     )
                                     )
    consumption = forms.FloatField(required=True,
                                   help_text='Consumption',
                                   widget=forms.NumberInput(
                                       attrs={'class': 'form-input',
                                              'id': 'widget_fst_name',
                                              'placeholder': 'Consumption'
                                              }
                                   )
                                   )

    ready = forms.BooleanField(required=False)

    county = forms.CharField(max_length=50, required=False,
                             widget=forms.HiddenInput(),
                             initial="temp"
                             )

    driver_id1 = forms.IntegerField(required=False,
                                   widget=forms.HiddenInput(),
                                   )
    driver_id2 = forms.IntegerField(required=False,
                                    widget=forms.HiddenInput(),
                                    )

    class Meta:
        model = Machinery
        fields = ['model', 'vin', 'tank_capacity', 'consumption', 'driver_id1', 'driver_id2', 'county', 'ready']


class AddSchedule(forms.ModelForm):
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    city = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Schedule
        fields = ['start_time', 'end_time', 'city']
