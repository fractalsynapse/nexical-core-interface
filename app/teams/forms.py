from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password

from app.users.forms import SignupForm
from app.users.models import User

from . import models


class BaseForm(forms.ModelForm):
    def set_user(self, user):
        self.user = user


class CreateForm(BaseForm):
    class Meta:
        model = models.Team
        fields = ["name"]

    def save(self, commit=True):
        self.instance.owner_id = self.user.id
        super().save(commit=commit)
        return self.instance


class UpdateForm(BaseForm):
    class Meta:
        model = models.Team
        fields = ["name"]  # "owner"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields["owner"].queryset = User.objects.filter(membership__team__id=self.instance.id)


class SignupForm(SignupForm):
    email = forms.EmailField(label="Email address", disabled=True)

    def __init__(self, *args, pk=None, **kwargs):
        self.invite = models.TeamInvite.objects.get(pk=pk)
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = self.invite.email
        self.fields.pop("invite_code")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            User.objects.get(email=email)
            raise forms.ValidationError(
                "A user with this email already exists in the system.",
                code="user_exists",
            )
        except User.DoesNotExist:
            pass
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and password != confirm_password:
            raise forms.ValidationError("Your passwords do not match.", code="password_mismatch")
        return confirm_password

    def signup(self, request):
        user = User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            settings={},
        )
        user.groups.add(Group.objects.get(name="team_member"))
        user.save()

        models.set_active_team(user, self.invite.team.id)
        emailaddress, created = EmailAddress.objects.get_or_create(
            user=user,
            email=self.cleaned_data["email"],
        )
        emailaddress.verified = True
        emailaddress.save()

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return user
