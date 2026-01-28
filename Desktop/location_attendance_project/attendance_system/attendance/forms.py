from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Employee, Attendance


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name (optional)',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name (optional)',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
        
        # Update help text styling
        self.fields['username'].help_text = 'Letters, digits, and @/./+/-/_ only.'
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'phone', 'department', 'position', 'office_latitude', 'office_longitude']
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee ID',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'type': 'tel',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department',
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter position',
            }),
            'office_latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Office latitude',
                'step': 'any',
            }),
            'office_longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Office longitude',
                'step': 'any',
            }),
        }


class AttendanceCheckInForm(forms.ModelForm):
    latitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Attendance
        fields = ['check_in_time', 'notes']
        widgets = {
            'check_in_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'check_in_time',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add any notes (optional)',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['check_in_time'].required = False


class AttendanceCheckOutForm(forms.ModelForm):
    latitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Attendance
        fields = ['check_out_time', 'notes']
        widgets = {
            'check_out_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'check_out_time',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add any notes (optional)',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['check_out_time'].required = False


class AttendanceFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Attendance.STATUS_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    employee = forms.ModelChoiceField(
        required=False,
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
