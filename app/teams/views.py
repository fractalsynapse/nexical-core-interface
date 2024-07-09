import django_tables2
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

# from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from app.projects.models import set_active_project
from app.users.models import check_verified_email
from app.utils.auth import TeamAccessMixin
from app.utils.views import ParamFormView

from . import forms, models


class TeamOwnershipMixin(TeamAccessMixin):
    def get_queryset(self):
        return self.model.objects.filter(team=self.team)

    def get_team_url(self, name, **kwargs):
        return reverse(name, kwargs={**kwargs, "team": self.team.id})

    def dispatch(self, request, *args, **kwargs):
        if "disable_check_team" not in kwargs:
            create_redirect = self._initialize_team(request)
            if create_redirect:
                return create_redirect
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team"] = self.team
        return context

    def _initialize_team(self, request):
        self.team = models.get_active_team(request.user)
        if not self.team:
            messages.error(
                request,
                "You do not currently have an active team selected.  "
                "Create a new team below or select a team in the header above.",
            )
            return redirect("teams:form_create")
        return None


class TeamTable(django_tables2.Table):
    name = django_tables2.Column(orderable=False)
    owner = django_tables2.Column(orderable=False)
    operations = django_tables2.Column(orderable=False, empty_values=(), verbose_name="")

    class Meta:
        model = models.Team
        fields = ["name", "owner", "operations"]

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    def render_operations(self, value, record):
        operations = ['<div class="text-right">']

        if self.user.id != record.owner.id and record.members.filter(user=self.user):
            members_url = reverse("teams:members", kwargs={"pk": record.id})
            operations.append(
                f'<a class="btn btn-primary px-4 py-2" title="Members" href="{members_url}">'
                + '<i class="bx bx-group"></i>'
                + "</a>"
            )
        if self.user.id == record.owner.id:
            update_url = reverse("teams:form_update", kwargs={"pk": record.id})
            operations.append(
                f'<a class="btn btn-primary px-4 py-2" title="Edit" href="{update_url}">'
                + '<i class="bx bx-edit"></i>'
                + "</a>"
            )
            remove_url = reverse("teams:remove", kwargs={"pk": record.id})
            operations.append(
                f'<a class="btn btn-primary ms-2 px-4 py-2" title="Remove" href="{remove_url}">'
                + '<i class="bx bx-trash-alt"></i>'
                + "</a>"
            )

        operations.append("</div>")
        return format_html("".join(operations))


class TeamMembershipTable(django_tables2.Table):
    user = django_tables2.Column(
        orderable=False,
        verbose_name="User",
        attrs={"th": {"class": "team-membership-user"}, "td": {"class": "team-membership-user"}},
    )
    created = django_tables2.Column(
        orderable=False,
        verbose_name="Joined",
        attrs={"th": {"class": "team-membership-join-date"}, "td": {"class": "team-membership-join-date"}},
    )
    remove = django_tables2.Column(
        orderable=False, empty_values=(), verbose_name="", attrs={"td": {"class": "team-membership-remove"}}
    )

    class Meta:
        model = models.TeamMembership
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = ["user", "created", "remove"]

    def __init__(self, user, team, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.team = team

    def render_remove(self, value, record):
        if record.team.owner.id != record.user.id:
            if self.user.id == self.team.owner.id:
                remove_url = reverse("teams:member_remove", kwargs={"pk": record.id})
                return format_html(
                    f'<a class="btn btn-outline-primary ms-2" title="Remove" href="{remove_url}">'
                    + '<i class="bx bx-trash-alt"></i>'
                    + "</a>"
                )
        elif self.user.id != self.team.owner.id:
            return format_html('<i class="bx bx-user-circle" title="Owner"></i>')
        return ""


class TeamInviteTable(django_tables2.Table):
    email = django_tables2.Column(
        orderable=False,
        verbose_name="Email",
        attrs={"th": {"class": "team-invite-email"}, "td": {"class": "team-invite-email"}},
    )
    created = django_tables2.Column(
        orderable=False,
        verbose_name="Sent",
        attrs={"th": {"class": "team-invite-date"}, "td": {"class": "team-invite-date"}},
    )
    resend = django_tables2.Column(
        orderable=False, empty_values=(), verbose_name="", attrs={"td": {"class": "team-invite-resend"}}
    )
    remove = django_tables2.Column(
        orderable=False, empty_values=(), verbose_name="", attrs={"td": {"class": "team-invite-remove"}}
    )

    class Meta:
        model = models.TeamInvite
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = ["email", "created", "resend", "remove"]

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    def render_resend(self, value, record):
        resend_url = reverse("teams:invite_send", kwargs={"team": record.team.id})
        resend_url = "{}?{}".format(resend_url, urlencode({"email": record.email}))
        return format_html(
            f'<a class="btn btn-outline-primary resend-link" title="Resend" href="{resend_url}">'
            + '<i class="bx bx-mail-send"></i>'
            + "</a>"
        )

    def render_remove(self, value, record):
        remove_url = reverse("teams:invite_remove", kwargs={"pk": record.id})
        return format_html(
            f'<a class="btn btn-outline-primary ms-2" title="Remove" href="{remove_url}">'
            + '<i class="bx bx-trash-alt"></i>'
            + "</a>"
        )


class ListView(TeamAccessMixin, TemplateView):
    template_name = "team_list.html"
    model = models.Team

    def get_queryset(self):
        return (
            self.model.objects.filter(Q(owner__id=self.request.user.id) | Q(members__user__id=self.request.user.id))
            .exclude(name="Personal")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context["team_count"] = kwargs["count"]
        context["teams"] = TeamTable(self.request.user, data=queryset)

        # context["help_title"] = "Team Help"
        # context["help_body"] = render_to_string("team_help.html")
        return context

    def dispatch(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        kwargs["count"] = queryset.count()

        if not kwargs["count"]:
            return redirect("teams:form_create")

        return super().dispatch(request, *args, **kwargs)


class FormMixin(TeamAccessMixin):
    template_name = "team_form.html"
    model = models.Team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset().filter(owner=self.request.user)
        context["team_count"] = queryset.count()

        # context["help_title"] = "Team Help"
        # context["help_body"] = render_to_string("team_help.html")
        return context


class CreateFormView(FormMixin, CreateView):
    form_class = forms.CreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "create"
        return context

    def form_valid(self, form):
        form.set_user(self.request.user)
        self.object = form.save()

        if not models.get_active_team(self.request.user, True):
            models.set_active_team(self.request.user, self.object.pk)

        self.object.create_event()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        return reverse("teams:form_update", kwargs={"pk": self.object.pk})


class UpdateFormView(FormMixin, UpdateView):
    form_class = forms.UpdateForm

    def dispatch(self, request, *args, **kwargs):
        team = get_object_or_404(models.Team, pk=self.kwargs["pk"])
        if team.owner.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "update"

        memberships = models.TeamMembership.objects.filter(team=self.object)
        context["membership_list"] = (
            TeamMembershipTable(self.request.user, self.object, data=memberships) if memberships.exists() else None
        )

        invites = models.TeamInvite.objects.filter(team=self.object)
        context["invite_list"] = TeamInviteTable(self.request.user, data=invites) if invites.exists() else None
        return context

    def form_valid(self, form):
        form.set_user(self.request.user)
        self.object.create_event()
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("teams:form_update", kwargs={"pk": self.object.pk})


class RemoveView(TeamAccessMixin, DeleteView):
    template_name = "team_confirm_delete.html"
    model = models.Team

    def dispatch(self, request, *args, **kwargs):
        team = get_object_or_404(models.Team, pk=self.kwargs["pk"])
        if team.owner.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, **kwargs):
        active_team_id = models.get_active_team(self.request.user, True)
        if active_team_id and active_team_id == str(self.object.pk):
            models.clear_active_team(self.request.user)

        return reverse("teams:list")


class MemberListView(TeamAccessMixin, TemplateView):
    template_name = "team_members.html"

    def dispatch(self, request, *args, **kwargs):
        self.team = get_object_or_404(models.Team, pk=self.kwargs["pk"])
        if not self.team.members.filter(user=request.user):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["team"] = self.team

        memberships = models.TeamMembership.objects.filter(team=self.team)
        context["membership_list"] = (
            TeamMembershipTable(self.request.user, self.team, data=memberships) if memberships.exists() else None
        )

        # context["help_title"] = "Team Help"
        # context["help_body"] = render_to_string("team_help.html")
        return context


class MemberRemoveView(TeamAccessMixin, DeleteView):
    template_name = "team_member_confirm_delete.html"
    model = models.TeamMembership

    def form_valid(self, form):
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        membership = get_object_or_404(models.TeamMembership, pk=self.kwargs["pk"])
        if membership.team.owner.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse("teams:form_update", kwargs={"pk": self.object.team.id})


class InviteRemoveView(TeamAccessMixin, DeleteView):
    template_name = "team_invite_confirm_delete.html"
    model = models.TeamInvite

    def dispatch(self, request, *args, **kwargs):
        invite = get_object_or_404(models.TeamInvite, pk=self.kwargs["pk"])
        if invite.team.owner.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse("teams:form_update", kwargs={"pk": self.object.team.id})


class InviteConfirmView(ParamFormView):
    template_name = "team_invite_signup.html"
    form_class = forms.SignupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["invite"] = self.invite
        return context

    def form_valid(self, form):
        team = self.invite.team
        project = team.projects.all().first()

        form.signup(self.request)

        self._add_membership(self.request.user)
        if project:
            set_active_project(self.request.user, project.id)

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("landing:start")

    def dispatch(self, request, *args, **kwargs):
        self.invite = get_object_or_404(models.TeamInvite, pk=self.kwargs["pk"])

        if request.user.is_authenticated:
            if self.invite.email not in request.user.verified_emails:
                raise PermissionDenied

            self._add_membership(self.request.user)
            return redirect("teams:list")

        user = check_verified_email(self.invite.email)
        if user:
            self._add_membership(user)
            return redirect("account_login")

        return super().dispatch(request, *args, **kwargs)

    def _add_membership(self, user):
        models.TeamMembership.objects.get_or_create(team=self.invite.team, user=user)
        self.invite.delete()
