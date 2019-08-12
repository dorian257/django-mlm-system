from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, FormView, DetailView, UpdateView
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.conf import settings

from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_text

# from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

from braces.views import FormValidMessageMixin, FormInvalidMessageMixin

from mlm.apps.authentication.forms import AdminProfileCreationForm
from mlm.apps.authentication.tokens import account_activation_token
from mlm.apps.main.models import MLMClient, MLMTransaction, get_or_create_mlm_config
from mlm.apps.main.exceptions import MLMException
from mlm.apps.main.utils.base import deactivate_client, create_client
from mlm.apps.main import settings as mlm_settings
from mlm.apps.main.forms import MLMConfigForm

from .mixins import MLMAdminRequiredMixin

# User Model
User = get_user_model()


class AdminRegistrationView(MLMAdminRequiredMixin, FormInvalidMessageMixin, FormView):
    form_class = AdminProfileCreationForm
    template_name = "mlm/admin/user_registration.html"
    success_url = reverse_lazy("main:admin-clients-list")
    form_invalid_message = "Une erreur est survenue."

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        username = form.cleaned_data["username"]
        password = User.objects.make_random_password()
        parent_client = form.cleaned_data["parent"]

        # print(form.cleaned_data)

        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
        except:  # TODO: Except specific exceptions
            messages.error(
                self.request,
                _(
                    "Nous ne pouvions pas créer un utilisateur avec les informations données. Vérifiez-les puis rééssayez."
                ),
            )
            return super().form_invalid(form)

        profile = form.save(commit=False)

        # Force Mail COnfirm ?
        if getattr(settings, "FORCE_MAIL_CONFIRM", True):
            user.is_active = False
        user.save()

        messages.success(self.request, _("L'utilisateur a été créé avec succès."))

        # We save the profile
        profile.user = user
        profile.save()

        try:
            client = create_client(
                user, created_by=self.request.user, parent=parent_client
            )
        except MLMException as err:
            messages.error(self.request, err)
            return super().form_invalid(form)
        # We send the mail
        current_site = get_current_site(self.request)
        subject = "Validation de votre compte"
        message = render_to_string(
            "email/admin_account_activation_email.html",
            {
                "user": user,
                "user_client": client,
                "user_password": password,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        user.email_user(subject, message)
        messages.success(self.request, _("Le Client a été créé avec succès."))
        return HttpResponseRedirect(self.success_url)
        # return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["page_title"] = _("Enregistrement du client")

        return context


# class AdminClientUpdateView(MLMAdminRequiredMixin, FormInvalidMessageMixin, FormView):
#     form_class = AdminProfileCreationForm
#     template_name = "mlm/admin/user_registration.html"
#     success_url = reverse_lazy("main:admin-clients-list")
#     form_invalid_message = "Une erreur est survenue."

#     def form_valid(self, form):
#         email = form.cleaned_data["email"]
#         username = form.cleaned_data["username"]
#         password = User.objects.make_random_password()
#         parent_client = form.cleaned_data["parent"]

#         print(form.cleaned_data)

#         user = User.objects.create_user(
#             username=username, email=email, password=password
#         )

#         profile = form.save(commit=False)

#         # Force Mail COnfirm ?
#         if getattr(settings, "FORCE_MAIL_CONFIRM", True):
#             user.is_active = False
#         user.save()

#         messages.success(self.request, _("L'utilisateur a été créé avec succès."))

#         # We save the profile
#         profile.user = user
#         profile.save()

#         try:
#             client = create_client(
#                 user, created_by=self.request.user, parent=parent_client
#             )
#         except MLMException as err:
#             messages.error(self.request, err)
#             return super().form_invalid(form)
#         # We send the mail
#         current_site = get_current_site(self.request)
#         subject = "Validation de votre compte"
#         message = render_to_string(
#             "email/admin_account_activation_email.html",
#             {
#                 "user": user,
#                 "user_client": client,
#                 "user_password": password,
#                 "domain": current_site.domain,
#                 "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                 "token": account_activation_token.make_token(user),
#             },
#         )
#         user.email_user(subject, message)
#         messages.success(self.request, _("Le Client a été créé avec succès."))
#         return HttpResponseRedirect(self.success_url)
#         # return super().form_valid(form)

#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context["page_title"] = _("Enregistrement du client")

#         return context


class MLMConfigView(MLMAdminRequiredMixin, View):
    form_class = MLMConfigForm
    template_name = "mlm/admin/mlm_config.html"
    success_url = reverse_lazy("main:admin-clients-list")
    form_success_message = "Changement de configuration."
    page_title = "Configuration"

    def get(self, request):
        config = get_or_create_mlm_config()
        form = self.form_class(instance=config)
        page_title = self.page_title
        return render(self.request, self.template_name, locals())

    def post(self, request):
        form = self.form_class(self.request.POST)
        page_title = self.page_title
        if form.is_valid():
            form.save()
            messages.success(self.request, self.form_success_message)
            return HttpResponseRedirect(self.request.path)
        return render(self.request, self.template_name, locals())


# class MLMClientDetailView(MLMAdminRequiredMixin, DetailView):
#     template_name = "mlm/admin/mlm_client_detail.html"
#     model = MLMClient


class MLMClientDeactivateView(MLMAdminRequiredMixin, View):
    def get(self, request, type_, pk):
        client = get_object_or_404(MLMClient, pk=pk)
        if type_ == 1:
            client.is_active = True
            client.user.is_active = True
        elif type_ == 2:
            client.user.is_mlm_staff = True
        elif type_ == 3:
            client.user.is_mlm_staff = False
        else:
            client.is_active = False
            client.user.is_mlm_staff = False
            # client.user.is_active = True
        client.user.save()
        client.save()
        messages.success(
            self.request, _("Le statut du client a été changé avec succès.")
        )
        return HttpResponseRedirect(client.get_list_url())


class MLMClientListView(MLMAdminRequiredMixin, ListView):
    template_name = "mlm/admin/mlm_clients_list.html"
    # model = MLMClient
    queryset = MLMClient.objects.exclude(user__username=mlm_settings.SYSTEM_USERNAME)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["page_title"] = _("Liste de clients")

        return context


class MLMClientUpdateView(MLMAdminRequiredMixin, UpdateView):
    template_name = "mlm/admin/mlm_client_update.html"
    # model = MLMClient
    queryset = MLMClient.objects.exclude(user__username=mlm_settings.SYSTEM_USERNAME)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["page_title"] = _("Modification d'un client")

        return context
