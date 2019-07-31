from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

from mlm.apps.main.models import MLMClient, MLMTransaction


class ClientDescendantTreeView(LoginRequiredMixin, View):
    template_name = "mlm/desc_tree.html"

    def get(self, request):
        page_title = _("Affiliations")
        return render(self.request, self.template_name, locals())


class TransactionsStatementListView(LoginRequiredMixin, ListView):
    template_name = "mlm/statement.html"
    model = MLMTransaction

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(client__user__pk=self.request.user.pk)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["page_title"] = _("Historique des Transactions")

        return context


class ClientBalanceView(LoginRequiredMixin, View):
    template_name = "mlm/balance.html"

    def get(self, request):
        page_title = _("Solde")
        return render(self.request, self.template_name, locals())
