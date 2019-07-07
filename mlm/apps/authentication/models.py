from datetime import datetime, timedelta

# import jwt
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.urls import reverse_lazy

from mlm.apps.core.models import TimestampedModel


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from 'BaseUserManager', we get a lot of the same code used by
    Django to create a 'User'.

    All we have to do is override the 'create_user' function which we will use
    to create 'User' objects.
    """

    def create_user(self, username, email, password=None):
        """Create and return a 'User' with an email, username and password."""
        if username is None:
            raise TypeError("Users must have a username.")

        if email is None:
            raise TypeError("Users must have an email address.")

        if email:
            email = self.normalize_email(email)

        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a 'User' with superuser (admin) permissions.
        """
        if email is None:
            raise TypeError("Superusers must have an email.")

        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    # Each 'User' needs a human-readable unique identifier that we can use to
    # represent the 'User' in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a user no longer wishes to use our platform, they may try to delete
    # their account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. We
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The 'is_staff' flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users this flag will always be
    # false.
    is_staff = models.BooleanField(default=False)

    # Boolean True if Email has been confirmed
    email_confirmed = models.BooleanField(default=False)

    # More fields required by Django when specifying a custom user model.

    # The 'USERNAME_FIELD' property tells us which field we will use to log in.
    # In this case we want it to be the email field.
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]  # To Add Later

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this 'User'.

        This string is used when a 'User' is printed in the console.
        """
        return getattr(self, self.USERNAME_FIELD)

    # @property
    # def token(self):
    #     """
    #     Allows us to get a user's token by calling 'user.token' instead of
    #     'user.generate_jwt_token().

    #     The '@property' decorator above makes this possible. 'token' is called
    #     a "dynamic property".
    #     """
    #     return self._generate_jwt_token()

    @property
    def full_name(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name.
        """
        name = self.username
        if hasattr(self, "profile"):
            name = self.profile.get_full_name()

        return name

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        if hasattr(self, "profile"):
            return self.profile.get_short_name()
        else:
            return self.username

    def get_profile_url(self):
        if hasattr(self, "profile"):
            return reverse_lazy("auth:profile-detail", kwargs={"pk": self.profile.pk})
        else:
            return reverse_lazy("auth:profile-create")

    # def _generate_jwt_token(self):
    #     """
    #     Generates a JSON Web Token that stores this user's ID and has an expiry
    #     date set to 60 days into the future.
    #     """
    #     dt = datetime.now() + timedelta(days=60)

    #     token = jwt.encode(
    #         {"id": self.pk, "exp": int(dt.strftime("%s"))},
    #         settings.SECRET_KEY,
    #         algorithm="HS256",
    #     )

    #     return token.decode("utf-8")

    def email_user(self, subject, message):
        from django.core import mail  # isort:skip
        from django.utils.html import strip_tags  # isort:skip

        html_message = message
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL

        mail.send_mail(
            subject, plain_message, from_email, [self.email], html_message=html_message
        )


class Profile(TimestampedModel):
    user = models.OneToOneField("User", on_delete=models.CASCADE)

    # Let add the first and last name to know the customer
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150)

    avatar = models.ImageField(
        upload_to="user/avatar/", verbose_name="Photo", null=True, blank=True
    )
    about_me = models.TextField(null=True, blank=True, verbose_name="A propos de moi")

    def get_full_name(self):
        name = self.first_name
        if self.middle_name:
            name = (
                name + " " + self.middle_name
                if self.first_name
                else name + self.middle_name
            )
        name + self.last_name

        return name

    def get_short_name(self):
        return self.first_name

    def get_absolute_url(self):
        return reverse_lazy("auth:profile-detail", kwargs={"pk": self.pk})
