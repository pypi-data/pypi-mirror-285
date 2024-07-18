# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""Authentication class mixins
---------------------------

This module defines various mixins that can be used within the Authentication
views to implement the different user creation strategies.
"""

import re
from itertools import chain
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from django_helmholtz_aai import app_settings
from django_helmholtz_aai import login as aai_login
from django_helmholtz_aai import models, signals

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

group_patt = re.compile(r".*:group:.*#.*")


class CreateUserMixin:
    """A mixin to create new users."""

    userinfo: Dict[str, Any]

    request: Any

    def create_user(self, **kwargs) -> models.HelmholtzUser:
        """Create a Django user for a Helmholtz AAI User.

        This method uses the
        :meth:`~django_helmholtz_aai.models.HelmholtzUserManager.create_aai_user`
        to create a new user.

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_user_created` signal
        """

        user = models.HelmholtzUser.objects.create_aai_user(  # type: ignore[attr-defined]
            self.userinfo, **kwargs
        )

        # emit the aai_user_created signal after the user has been created
        signals.aai_user_created.send(
            sender=user.__class__,
            user=user,
            request=self.request,
            userinfo=self.userinfo,
        )
        return user

    def get_or_create_user(self, **kwargs) -> models.HelmholtzUser:
        """Create a Django user for a Helmholtz AAI User.

        This method uses the
        :meth:`~django_helmholtz_aai.models.HelmholtzUserManager.create_aai_user`
        to create a new user.

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_user_created` signal
        """

        user, created = models.HelmholtzUser.objects.get_or_create_aai_user(  # type: ignore[attr-defined]
            self.userinfo, **kwargs
        )

        # emit the aai_user_created signal after the user has been created
        if created:
            signals.aai_user_created.send(
                sender=user.__class__,
                user=user,
                request=self.request,
                userinfo=self.userinfo,
            )
        return user


class UpdateUserMixin:
    """Mixin to perform an update on the user."""

    aai_user: models.HelmholtzUser

    userinfo: Dict[str, Any]

    request: Any

    @staticmethod
    def _username_exists(username: str):
        return bool(models.HelmholtzUser.objects.filter(username=username))

    def update_user(self, **to_update):
        """Update the user from the userinfo provided by the Helmholtz AAI.

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_user_updated` signal
        """
        userinfo = self.userinfo
        user = self.aai_user

        email = userinfo["email"]

        if app_settings.HELMHOLTZ_UPDATE_USERNAME:
            username = next(
                userinfo[key]
                for key in app_settings.HELMHOLTZ_USERNAME_FIELDS
                if userinfo.get(key)
            )
            if user.username != username and not self._username_exists(
                username
            ):
                to_update["username"] = username
        if user.first_name != userinfo["given_name"]:
            to_update["first_name"] = userinfo["given_name"]
        if user.last_name != userinfo["family_name"]:
            to_update["last_name"] = userinfo["family_name"]
        if app_settings.HELMHOLTZ_UPDATE_EMAIL:
            if user.email.lower() != email.lower():
                to_update["email"] = email
        self.apply_updates(to_update)

    def apply_updates(self, to_update: Dict):
        """Apply the update to the user and send the signal."""
        if to_update:
            user = self.aai_user
            for key, val in to_update.items():
                setattr(user, key, val)
            user.save()

            # emit the aai_user_updated signal as the user has been updated
            signals.aai_user_updated.send(
                sender=user.__class__,
                user=user,
                request=self.request,
                userinfo=self.userinfo,
                to_update=to_update,
            )

    def synchronize_vos(self):
        """Synchronize the memberships in the virtual organizations.

        This method checks the ``eduperson_entitlement`` of the AAI userinfo
        and

        1. creates the missing virtual organizations
        2. removes the user from virtual organizations that he or she does not
           belong to anymore
        3. adds the user to the virtual organizations that are new.

        Notes
        -----
        As we remove users from virtual organizations, this might end up in a
        lot of VOs without any users. One can remove these VOs via::

            python manage.py remove_empty_vos

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_vo_created`,
        :attr:`~django_helmholtz_aai.signals.aai_vo_entered` and
        :attr:`~django_helmholtz_aai.signals.aai_vo_left` signals.
        """
        user = self.aai_user
        if "eduperson_entitlement" in self.userinfo.keys():
            vos = self.userinfo["eduperson_entitlement"]
        else:
            vos = []

        # synchronize VOs
        current_vos = user.groups.filter(
            helmholtzvirtualorganization__isnull=False
        )
        if current_vos:
            vo_names = [
                t[0]
                for t in current_vos.values_list(
                    "helmholtzvirtualorganization__eduperson_entitlement"
                )
            ]
        else:
            vo_names = []
        actual_vos = list(filter(group_patt.match, vos))

        # remove VOs in the database
        for vo_name in set(vo_names) - set(actual_vos):
            vo = models.HelmholtzVirtualOrganization.objects.get(
                eduperson_entitlement=vo_name
            )
            self.leave_vo(vo)

        # add new VOs in the database
        for vo_name in set(actual_vos) - set(vo_names):
            try:
                vo = models.HelmholtzVirtualOrganization.objects.get(
                    eduperson_entitlement=vo_name
                )
            except (
                models.HelmholtzVirtualOrganization.DoesNotExist
            ):  # pylint: disable=no-member
                vo = self.create_vo(vo_name)
            self.join_vo(vo)

    def leave_vo(self, vo: models.HelmholtzVirtualOrganization):
        """Leave the given VO."""
        user = self.aai_user
        user.groups.remove(vo)
        signals.aai_vo_left.send(
            sender=vo.__class__,
            request=self.request,
            user=user,
            vo=vo,
            userinfo=self.userinfo,
        )

    def join_vo(self, vo: models.HelmholtzVirtualOrganization):
        """Join the given VO."""
        user = self.aai_user
        user.groups.add(vo)
        signals.aai_vo_entered.send(
            sender=vo.__class__,
            request=self.request,
            user=user,
            vo=vo,
            userinfo=self.userinfo,
        )

    def create_vo(self, vo_name: str) -> models.HelmholtzVirtualOrganization:
        """Create a new VO with the given name."""
        vo = models.HelmholtzVirtualOrganization.objects.create(
            name=vo_name, eduperson_entitlement=vo_name
        )
        signals.aai_vo_created.send(
            sender=vo.__class__,
            request=self.request,
            vo=vo,
            userinfo=self.userinfo,
        )
        return vo


class LoginUserMixin:
    """Mixin to login a user."""

    userinfo: Dict[str, Any]

    request: Any

    disable_user: Optional[bool] = None

    def login_user(self, user: models.HelmholtzUser):
        """Login the Helmholtz AAI user to the Django Application.

        Login is done via the top-level :func:`django_helmholtz_aai.login`
        function.

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_user_logged_in`
        signal
        """
        if not self.disable_user and user.is_active:
            user.backend = app_settings.HELMHOLTZ_USER_BACKEND  # type: ignore
            aai_login(self.request, user, self.userinfo)
            self.disable_user = False
        else:
            self.disable_user = True

    def get_success_url(self) -> str:
        """Return the URL to redirect to after processing a valid form."""
        return self.request.session.pop(
            "forward_after_aai_login", settings.LOGIN_REDIRECT_URL
        )


class PermissionDeniedReasonsClass(type):
    """
    Metaclass for classes that can have media definitions.
    """

    def __new__(mcs, name, bases, attrs):
        all_reasons = list(
            chain.from_iterable(
                base.PermissionDeniedReasons
                for base in bases
                if hasattr(base, "PermissionDeniedReasons")
            )
        )

        if "PermissionDeniedReasons" in attrs:
            all_reasons = [attrs["PermissionDeniedReasons"]] + all_reasons

        if all_reasons:
            attrs["PermissionDeniedReasons"] = TextChoices(
                "PermissionDeniedReasons",
                [(i.name, (i.value, i.label)) for i in all_reasons],
            )

        new_class = super().__new__(mcs, name, bases, attrs)

        return new_class


class PermissionRequiredReasoningMixin(PermissionRequiredMixin):
    userinfo: Dict[str, Any]

    request: Any

    class PermissionDeniedReasons(TextChoices):
        """Reasons why permissions are denied to login."""

        #: the virtual organization is not part of
        #: :setting:`HELMHOLTZ_ALLOWED_VOS_REGEXP`
        vo_not_allowed = (
            "vo_not_allowed",
            _(
                "Your virtual organizations are not allowed to log into "
                "this website."
            ),
        )

        #: the email has not yet been verified
        email_not_verified = (
            "email_not_verified",
            _("Your email has not been verified."),
        )

    #: The reason why the user cannot login.
    #:
    #: This attribute is set via the :meth:`has_permission` method
    permission_denied_reason: PermissionDeniedReasons

    def handle_no_permission(self):
        try:
            reason = self.PermissionDeniedReasons(
                self.permission_denied_reason
            )
        except ValueError:
            pass
        else:
            signals.login_denied.send(
                sender=models.HelmholtzUser,
                request=self.request,
                userinfo=self.userinfo,
                reason=str(reason),
                msg=reason.label % self.userinfo,
            )
        return super().handle_no_permission()

    def get_permission_denied_message(self) -> str:
        """Get the permission denied message for a specific reason.

        This method is called by the super-classes :meth:`handle_no_permission`
        method."""
        try:
            reason = self.PermissionDeniedReasons(
                self.permission_denied_reason
            )
        except ValueError:
            return super().get_permission_denied_message()  # type: ignore
        else:
            signals.login_denied.send(
                sender=models.HelmholtzUser,
                request=self.request,
                userinfo=self.userinfo,
                reason=str(reason),
                msg=reason.label % self.userinfo,
            )
            return reason.label % self.userinfo


class CheckEmailMixin:
    class PermissionDeniedReasons(TextChoices):
        #: the user is new and the email already exists
        email_exists = (
            "email_exists",
            _(
                "A user with the email "
                "<a href='mailto:%(email)s>%(email)s</a> already exists."
            ),
        )

        helmholtz_email_exists = (
            "helmholtz_email_exists",
            _(
                "A user with the email "
                "<a href='mailto:%(email)s'>%(email)s</a> "
                "is already connected to a "
                "different account in the Helmholtz AAI. Please logout at "
                "<a href='https://login.helmholtz.de'>"
                "https://login.helmholtz.de"
                "</a> and use the login provider you "
                "used last time. You can try your institution, or the social "
                "login providers GitHub, OrcID or Google."
            ),
        )

        #: account creation is disabled and no user could be found.
        no_user_exists = (
            "no_user_exists",
            _(
                "A user with the email %(email)s is not available on this "
                "website and the account creation is disabled. Please sign up or "
                "contact the website administrators."
            ),
        )

    def email_exists(
        self, email: str, UserModel: Type[User] = User, **kwargs
    ) -> bool:
        """Get a user from the email.

        ``**kwargs`` are used to filter the existing django users.
        """
        return bool(UserModel.objects.filter(email__iexact=email, **kwargs))


class NoUserExistsMixin:
    class PermissionDeniedReasons(TextChoices):
        """Reasons why permissions are denied to login."""

        #: account creation is disabled and no helmholtz user could be found.
        no_helmholtz_user_exists = (
            "no_helmholtz_user_exists",
            _(
                "A user with the eduperson_unique_id "
                "%(eduperson_unique_id)s does not exist in the system and "
                "account creation is disabled."
            ),
        )

    def user_exists(self, *args, **kwargs) -> bool:
        """Test if a user with the given id exists."""

        return models.HelmholtzUser.objects.filter(*args, **kwargs).exists()


class MapUserMixin:
    """A mixin to create new users."""

    userinfo: Dict[str, Any]

    def get_user_from_email(self, email: str, **kwargs) -> User:
        """Get a user from the email.

        ``**kwargs`` are used to filter the existing django users.
        """
        return User.objects.get(email__iexact=email, **kwargs)

    def map_user(self, **kwargs) -> models.HelmholtzUser:
        """Create an Helmholtz AAI User for an existing django user.

        This method creates a new helmholtz user for an already existing django
        user. ``**kwargs`` are used to filter the existing django users.
        """

        user_id = self.userinfo["eduperson_unique_id"]

        user = self.get_user_from_email(self.userinfo["email"], **kwargs)

        if hasattr(user, "helmholtzuser"):
            aai_user = user.helmholtzuser
            aai_user.eduperson_unique_id = user_id
            aai_user.userinfo = self.userinfo
        else:
            fields = {
                f.name: getattr(user, f.name)
                for f in User._meta.fields
                if not f.many_to_many
            }

            aai_user = models.HelmholtzUser(
                user_ptr=user,
                eduperson_unique_id=user_id,
                userinfo=self.userinfo,
                **fields,
            )
        aai_user.save()
        return aai_user
