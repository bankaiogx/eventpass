from datetime import date

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile, SupportRequest


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        required=True,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")

        return email

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data["date_of_birth"]

        if date_of_birth > date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")

        return date_of_birth

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "date_of_birth", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            Profile.objects.update_or_create(
                user=user,
                defaults={"date_of_birth": self.cleaned_data["date_of_birth"]},
            )

        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        required=True,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile")
        super().__init__(*args, **kwargs)
        self.fields["date_of_birth"].initial = self.profile.date_of_birth

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")

        return email

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data["date_of_birth"]

        if date_of_birth > date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")

        return date_of_birth

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            self.profile.date_of_birth = self.cleaned_data["date_of_birth"]
            self.profile.save()

        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class SupportRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = SupportRequest
        fields = ["subject", "message"]
