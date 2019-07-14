from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from mlm.apps.main.models import MLMClient


class ClientDescendantTreeView(LoginRequiredMixin, View):
    template_name = "mlm/desc_tree.html"

    def get(self, request):
        return render(self.request, self.template_name, locals())
