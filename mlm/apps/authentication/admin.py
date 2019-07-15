from mlm.apps.authentication.models import User
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm  # , UserCreationForm
from django.utils.translation import gettext_lazy as _

# from import_export.admin import ImportExportModelAdmin

from .forms import *


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        # exclude = ('password',)

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields["email"] = forms.EmailField(label="E-mail", max_length=75)


UserAdmin.add_form = UserCreationForm

UserAdmin.add_fieldsets = (
    (
        "User Registration",
        {
            "classes": ("wide",),
            "fields": (("username", "email"), ("password1", "password2")),
        },
    ),
    # (
    #     "User Information",
    #     {"classes": ("wide",), "fields": (("first_name", "last_name"),)},
    # ),
)


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = UserCreationForm
    # add_form = UserAddForm

    list_display = (
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "created_at",
    )

    fieldsets = (
        UserAdmin.fieldsets[0],
        # UserAdmin.fieldsets[1],
        ("Address and Permissions", {"fields": ("groups",)}),
        ("Other Information", {"fields": ["is_active", "is_staff"]}),
    )


@admin.register(User)
class UserAdmin(CustomUserAdmin):
    # class UserAdmin(ImportExportModelAdmin, CustomUserAdmin):
    pass
