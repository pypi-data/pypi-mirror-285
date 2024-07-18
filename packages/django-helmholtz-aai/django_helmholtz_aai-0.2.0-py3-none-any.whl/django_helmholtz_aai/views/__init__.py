# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2
# SPDX-License-Identifier: EUPL-1.2

"""Views
-----

Views of the django_helmholtz_aai app to be imported via the url config (see
:mod:`django_helmholtz_aai.urls`). We define two views here: The
:class:`HelmholtzLoginView` that redirects to the Helmholtz AAI, and the
:class:`HelmholtzAuthentificationView` that handles the user login after
successful login at the Helmholtz AAI.
"""

from __future__ import annotations

import re
import warnings
from enum import Enum
from itertools import product
from typing import TYPE_CHECKING, Any, Dict, Optional

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import classonlymethod
from django.utils.functional import cached_property
from django.views import generic

from django_helmholtz_aai import app_settings
from django_helmholtz_aai import login as aai_login
from django_helmholtz_aai import models, signals

from .auth import registry  # noqa: F401

oauth = OAuth()

SCOPES = [
    "profile",
    "email",
    "eduperson_unique_id",
]


oauth.register(name="helmholtz", **app_settings.HELMHOLTZ_CLIENT_KWS)


if TYPE_CHECKING:
    from django.contrib.auth.models import User


User = get_user_model()  # type: ignore  # noqa: F811

group_patt = re.compile(r".*:group:.*#.*")


class HelmholtzLoginView(LoginView):
    """A login view for the Helmholtz AAI that forwards to the OAuth login."""

    def get(self, request):
        """Get the redirect URL to the Helmholtz AAI."""
        if getattr(settings, "ROOT_URL", None):
            redirect_uri = settings.ROOT_URL + reverse(
                "django_helmholtz_aai:auth"
            )
        else:
            redirect_uri = request.build_absolute_uri(
                reverse("django_helmholtz_aai:auth")
            )
        request.session["forward_after_aai_login"] = self.get_success_url()
        return oauth.helmholtz.authorize_redirect(request, redirect_uri)

    def post(self, request):
        """Reimplemented post method to call :meth:`get`."""
        return self.get(request)


# -----------------------------------------------------------------------------
# -------------------------- Deprecated views ---------------------------------
# -----------------------------------------------------------------------------


class HelmholtzAuthentificationView(PermissionRequiredMixin, generic.View):
    """DEPRECATED VIEW."""

    aai_user: models.HelmholtzUser

    class PermissionDeniedReasons(str, Enum):
        """Reasons why permissions are denied to login."""

        #: the virtual organization is not part of
        #: :setting:`HELMHOLTZ_ALLOWED_VOS_REGEXP`
        vo_not_allowed = "vo_not_allowed"

        #: the email has not yet been verified
        email_not_verified = "email_not_verified"

        #: the email changed and is already taken on the website
        email_changed_and_taken = "email_changed_and_taken"

        #: the user is new and user creation is disabled by
        #: :setting:`HELMHOLTZ_CREATE_USERS`
        new_user = "new_user"

        #: the user is new and the email already exists
        email_exists = "email_exists"

        #: a user with the given email could not be found
        cannot_find_user = "cannot_find_user"

    #: The reason why the user cannot login.
    #:
    #: This attribute is set via the :meth:`has_permission` method
    permission_denied_reason: PermissionDeniedReasons

    #: Message templates that explain why a user is not allowed to login.
    #:
    #: via the Helmholtz AAI. Use in the :meth:`get_permission_denied_message`
    #: method.
    permission_denied_message_templates: dict[PermissionDeniedReasons, str] = {
        PermissionDeniedReasons.vo_not_allowed: (
            "Your virtual organizations are not allowed to log into "
            "this website."
        ),
        PermissionDeniedReasons.email_not_verified: (
            "Your email has not been verified."
        ),
        PermissionDeniedReasons.email_changed_and_taken: (
            "You email in the Helmholtz AAI changed to {email}. "
            "A user with this email already exists and on this "
            "website. Please contact the website administrators."
        ),
        PermissionDeniedReasons.new_user: (
            "Your email {email} does not yet have a user account on this "
            "website and the account creation is disabled. Please sign up or "
            "contact the website administrators."
        ),
        PermissionDeniedReasons.email_exists: (
            "A user with the email {email} already exists."
        ),
        PermissionDeniedReasons.cannot_find_user: (
            "A user with the email {email} is not available on this "
            "website and the account creation is disabled. Please sign up or "
            "contact the website administrators."
        ),
    }

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        warnings.warn(
            "The django_helmholtz_aai.views.HelmholtzAuthentificationView is "
            "deprecated. Please use one of the viewsets at "
            "django_helmholtz_aai.views.auth",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().as_view(*args, **kwargs)

    @cached_property
    def userinfo(self) -> Dict[str, Any]:
        """The userinfo as obtained from the Helmholtz AAI.

        The attributes of this dictionary are determined by the Django
        Helmholtz AAI [1]_

        References
        ----------
        .. [1] https://hifis.net/doc/helmholtz-aai/attributes/
        """
        token = oauth.helmholtz.authorize_access_token(self.request)
        return oauth.helmholtz.userinfo(request=self.request, token=token)

    def login_user(self, user: models.HelmholtzUser):
        """Login the Helmholtz AAI user to the Django Application.

        Login is done via the top-level :func:`django_helmholtz_aai.login`
        function.

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_user_logged_in`
        signal
        """
        user.backend = app_settings.HELMHOLTZ_USER_BACKEND  # type: ignore
        aai_login(self.request, user, self.userinfo)

    def get_success_url(self) -> str:
        """Return the URL to redirect to after processing a valid form."""
        return self.request.session.pop(
            "forward_after_aai_login", settings.LOGIN_REDIRECT_URL
        )

    def get(self, request):
        """Login the Helmholtz AAI user and update the data.

        This method logs in the aai user (or creates one if it does not exist
        already). Afterwards we update the user info from the information on
        the Helmholtz AAI using the :meth:`update_user` and
        :meth:`synchronize_vos` methods.
        """
        if self.is_new_user:
            self.aai_user = self.create_user(self.userinfo)
        else:
            self.update_user()

        self.synchronize_vos()

        self.login_user(self.aai_user)

        return redirect(self.get_success_url())

    def handle_no_permission(self):
        """Handle the response if the permission has been denied.

        This reimplemented method adds the :attr:`permission_denied_message`
        to the messages of the request using djangos messaging framework."""
        messages.add_message(
            self.request, messages.ERROR, self.get_permission_denied_message()
        )
        return super().handle_no_permission()

    def get_user_from_email(self, email: str) -> Optional[User]:
        """Get a user from the email"""
        try:
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None

    @cached_property
    def is_new_user(self) -> bool:
        """True if the Helmholtz AAI user has never logged in before."""
        user_id = self.userinfo["eduperson_unique_id"]
        try:
            self.aai_user = models.HelmholtzUser.objects.get(
                eduperson_unique_id=user_id
            )
        except models.HelmholtzUser.DoesNotExist:
            if app_settings.HELMHOLTZ_MAP_ACCOUNTS:
                user = self.get_user_from_email(self.userinfo["email"])
                if user is None:
                    return True
                fields = {
                    f.name: getattr(user, f.name)
                    for f in User._meta.fields
                    if not f.many_to_many
                }
                self.aai_user = models.HelmholtzUser(
                    user_ptr=user, eduperson_unique_id=user_id, **fields
                )
                self.aai_user.save()
                return False
            else:
                return True
        else:
            return False

    def has_permission(self) -> bool:
        """Check if the user has permission to login.

        This method checks, if the user belongs to the specified
        :attr:`~django_helmholtz_aai.app_settings.HELMHOLTZ_ALLOWED_VOS` and
        verifies that the email does not exist (if this is desired, see
        :attr:`~django_helmholtz_aai.app_settings.HELMHOLTZ_EMAIL_DUPLICATES_ALLOWED`
        setting).
        """
        userinfo = self.userinfo
        email = userinfo["email"]

        reasons = self.PermissionDeniedReasons

        # check if the user belongs to the allowed VOs
        if app_settings.HELMHOLTZ_ALLOWED_VOS_REGEXP and userinfo.get(
            "eduperson_entitlement"
        ):
            if not any(
                patt.match(vo)
                for patt, vo in product(
                    app_settings.HELMHOLTZ_ALLOWED_VOS_REGEXP,
                    userinfo["eduperson_entitlement"],
                )
            ):
                self.permission_denied_reason = reasons.vo_not_allowed
                return False
        elif app_settings.HELMHOLTZ_ALLOWED_VOS_REGEXP:
            return False

        # check for email verification
        if not userinfo["email_verified"]:
            self.permission_denied_reason = reasons.email_not_verified
            return False

        # check for email duplicates
        if not self.is_new_user:
            # check if we need to update the email and if yes, check if this
            # is possible
            if self.aai_user.email.lower() != email.lower():
                if self._email_exists(email):
                    self.permission_denied_reason = (
                        reasons.email_changed_and_taken
                    )
                    return False
        elif self.is_new_user and not app_settings.HELMHOLTZ_CREATE_USERS:
            if app_settings.HELMHOLTZ_MAP_ACCOUNTS:
                self.permission_denied_reason = reasons.cannot_find_user
            else:
                self.permission_denied_reason = reasons.new_user
            return False
        elif self._email_exists(email):
            self.permission_denied_reason = reasons.email_exists
            return False

        return True

    def get_permission_denied_message(self):
        """Get the permission denied message for a specific reason.

        This method is called by the super-classes :meth:`handle_no_permission`
        method."""
        templates = self.permission_denied_message_templates
        key = self.permission_denied_reason
        return templates[key].format(**self.userinfo)

    @staticmethod
    def _username_exists(username: str):
        return bool(models.HelmholtzUser.objects.filter(username=username))

    @staticmethod
    def _email_exists(email: str) -> bool:
        if app_settings.HELMHOLTZ_EMAIL_DUPLICATES_ALLOWED:
            return False
        return bool(models.HelmholtzUser.objects.filter(email__iexact=email))

    def create_user(self, userinfo: Dict[str, Any]) -> models.HelmholtzUser:
        """Create a Django user for a Helmholtz AAI User.

        This method uses the
        :meth:`~django_helmholtz_aai.models.HelmholtzUserManager.create_aai_user`
        to create a new user.

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_user_created` signal
        """

        user = models.HelmholtzUser.objects.create_aai_user(self.userinfo)

        # emit the aai_user_created signal after the user has been created
        signals.aai_user_created.send(
            sender=user.__class__,
            user=user,
            request=self.request,
            userinfo=userinfo,
        )
        return user

    def update_user(self):
        """Update the user from the userinfo provided by the Helmholtz AAI.

        Notes
        -----
        Emits the :attr:`~django_helmholtz_aai.signals.aai_user_updated` signal
        """
        to_update = {}

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
