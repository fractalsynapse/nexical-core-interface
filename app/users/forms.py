from allauth.account.utils import send_email_confirmation
from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from app.teams.models import Team, get_active_team, set_active_team

from .models import User, UserInvite


class SignupForm(forms.Form):
    first_name = forms.CharField(label="First name", max_length=150)
    last_name = forms.CharField(label="Last name", max_length=150)

    email = forms.EmailField(label="Email address")
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput)

    invite_code = forms.CharField(
        label="Invite code",
        max_length=6,
        help_text="If you do not have an invite code <a href='/contact'>please contact us</a>",
    )

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

    def clean_invite_code(self):
        invite_code = self.cleaned_data.get("invite_code")
        error_message = "You must specify a valid invite code to sign up for this site"
        error_code = "invalid_invite_code"
        try:
            self.invite = UserInvite.objects.get(code=self.cleaned_data.get("invite_code"))
            if self.invite.email != self.cleaned_data.get("email"):
                raise forms.ValidationError(error_message, code=error_code)
        except UserInvite.DoesNotExist:
            raise forms.ValidationError(error_message, code=error_code)
        return invite_code

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

        (team, created) = Team.objects.get_or_create(owner=user, name="Personal")
        if not get_active_team(user):
            set_active_team(user, team.id)

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        send_email_confirmation(request, user, True)

        self.invite.delete()
        return user


class AdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": forms.EmailField}


class AdminCreationForm(admin_forms.UserCreationForm):
    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": forms.EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }
