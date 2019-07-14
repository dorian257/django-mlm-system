from django.urls import path

from .views import index, mlm_views

app_name = "main"
urlpatterns = [
    path("dashboard/", index.DashboardView.as_view(), name="dashboard"),
    path("tree/", mlm_views.ClientDescendantTreeView.as_view(), name="tree"),
]
