from django.urls import path, include

from .views import index, mlm_views, admin_views

app_name = "main"

admin_patterns = [
    path(
        "clients/list/",
        admin_views.MLMClientListView.as_view(),
        name="admin-clients-list",
    ),
    path(
        "client/create/",
        admin_views.AdminRegistrationView.as_view(),
        name="admin-client-create",
    ),
    path(
        "client/activation/<int:type_>/<int:pk>/",
        admin_views.MLMClientDeactivateView.as_view(),
        name="admin-client-activation",
    ),
    path(
        "client/add/",
        admin_views.AdminRegistrationView.as_view(),
        name="admin-client-add",
    ),
]


urlpatterns = [
    path("dashboard/", index.DashboardView.as_view(), name="dashboard"),
    path("no-client/", index.NoClientView.as_view(), name="no-client-redirect"),
    path("tree/", mlm_views.ClientDescendantTreeView.as_view(), name="tree"),
    path(
        "transactions/",
        mlm_views.TransactionsStatementListView.as_view(),
        name="statement",
    ),
    # ADMIN VIEWS
    path("mlmadmin/", include(admin_patterns)),
]
