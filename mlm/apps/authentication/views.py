from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model, login

from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_text

from django.conf import settings

from braces.views import FormValidMessageMixin, FormInvalidMessageMixin

from mlm.apps.main import settings as mlm_settings

from .models import Profile
from .forms import UserCreationForm
from .tokens import account_activation_token

User = get_user_model()


class ProfileCreateView(
    LoginRequiredMixin, FormValidMessageMixin, FormInvalidMessageMixin, CreateView
):
    template_name = "auth/profile_form.html"
    model = Profile
    fields = ["first_name", "middle_name", "last_name", "avatar", "about_me"]
    form_valid_message = "Profile created successfully."
    form_invalid_message = "Profile not created."

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        obj = form.save(commit=False)

        if not self.request.user.mlm_clients.exists():
            parent_client_id = self.request.POST.get("mlmparent", None)

            if parent_client_id is None:
                messages.error(self.request, "L'ID du parent absent.")
                return super(ProfileCreateView, self).form_invalid(form)
            else:
                from mlm.apps.main.models import MLMClient  # isort:skip
                from mlm.apps.main.utils.base import create_client

                try:
                    parent_client = MLMClient.objects.get(client_id=parent_client_id)
                except MLMClient.DoesNotExist:
                    messages.error(self.request, "L'ID du parrain invalide.")
                    return super(ProfileCreateView, self).form_invalid(form)

                if (
                    parent_client.get_children().count()
                    >= mlm_settings.MAX_AFFILIATION_NUMBER
                ):
                    messages.error(
                        self.request,
                        "L'upline a atteint le nombre maximal de parrainages.",
                    )
                    return super(ProfileCreateView, self).form_invalid(form)

                create_client(self.request.user, parent=parent_client)

        obj.user = self.request.user
        self.object = obj.save()

        return super(ProfileCreateView, self).form_valid(form)

    def form_invalid(self, form):
        # print(form.errors)
        return super(ProfileCreateView, self).form_invalid(form)


class ProfileUpdateView(
    LoginRequiredMixin, FormValidMessageMixin, FormInvalidMessageMixin, UpdateView
):
    template_name = "auth/profile_form.html"
    model = Profile
    fields = ["first_name", "middle_name", "last_name", "avatar", "about_me"]
    form_valid_message = "Profile updated successfully."
    form_invalid_message = "Profile not updated."


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = "auth/profile_detail.html"
    model = Profile


class RegistrationView(FormView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("main:dashboard")

    def form_valid(self, form):
        user = form.save(commit=False)

        # Force Mail COnfirm ?
        if getattr(settings, "FORCE_MAIL_CONFIRM", True):
            user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        subject = "Activation de votre compte"
        message = render_to_string(
            "email/account_activation_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        user.email_user(subject, message)
        return redirect("auth:account_activation_sent")
        # return super().form_valid(form)


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.email_confirmed = True
            user.save()
            login(self.request, user)
            return redirect(getattr(settings, "LOGIN_REDIRECT_URL", "/"))
        else:
            return render(request, "registration/account_activation_invalid.html")


class AccountActivationSent(View):
    def get(self, request):
        return render(request, "registration/account_activation_sent.html")
