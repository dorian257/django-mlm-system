from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from .views import (
    ProfileCreateView,
    ProfileDetailView,
    ProfileUpdateView,
    ActivateAccountView,
    AccountActivationSent,
    RegistrationView,
)

app_name = "authentication"
urlpatterns = [
    # User
    path(
        "", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", RegistrationView.as_view(), name="register"),
    # Email Confirm
    path(
        "account_activation_sent/",
        AccountActivationSent.as_view(),
        name="account_activation_sent",
    ),
    re_path(
        r"^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        ActivateAccountView.as_view(),
        name="activate-account",
    ),
    # Password Reset
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    # Password Change
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    # Profile
    path("profile/create/", ProfileCreateView.as_view(), name="profile-create"),
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
    path(
        "profile/<int:pk>/update/", ProfileUpdateView.as_view(), name="profile-update"
    ),
]
