# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""Base viewset for authentication
-------------------------------

This module defines the base viewset for handling authentication and user
creation. Furthermore it defines a registry to register the viewsets for a
given key.
"""

from __future__ import annotations

import importlib
from itertools import product
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from authlib.integrations.django_client import OAuth
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import path
from django.utils.functional import cached_property
from django.views import generic

from django_helmholtz_aai import app_settings, models

from .mixins import (
    LoginUserMixin,
    PermissionDeniedReasonsClass,
    PermissionRequiredReasoningMixin,
    UpdateUserMixin,
)

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


class AuthenticationViewsetRegistry:
    """A registry for authentication viewsets."""

    viewsets: Dict[Tuple, AuthentificationViewsetBase] = {}

    def __init__(self) -> None:
        self.viewsets = {}

    def register_viewset(
        self, key: Union[str, List[str]], viewset: AuthentificationViewsetBase
    ):
        sorted_key = self._standardize_key(key)
        if sorted_key in self.viewsets:
            raise ValueError(
                f"A viewset with the key {key} is already registered. Please "
                "unregister first"
            )
        self.viewsets[sorted_key] = viewset

    def unregister_viewset(
        self, key: Union[str, List[str]]
    ) -> Optional[AuthentificationViewsetBase]:
        """Unregister a viewset for the given key."""
        sorted_key = self._standardize_key(key)
        return self.viewsets.pop(sorted_key, None)

    def get_default_viewset(self) -> AuthentificationViewsetBase:
        """Get the viewset from the :mod:`~django_helmholtz_aai.app_settings."""
        strategy = app_settings.HELMHOLTZ_CREATE_USERS_STRATEGY
        if isinstance(strategy, str):
            if "." in strategy:
                module_name, attr = strategy.rsplit(".", 1)
                try:
                    module = importlib.import_module(module_name)
                except ImportError:
                    raise ValueError(
                        f"Module {module_name} specified in the "
                        "HELMHOLTZ_CREATE_USERS_STRATEGY could not be "
                        "imported."
                    )
                else:
                    try:
                        return getattr(module, attr)
                    except AttributeError:
                        raise ValueError(
                            f"Module {module_name} specified in the "
                            "HELMHOLTZ_CREATE_USERS_STRATEGY does not have a "
                            f"member called {attr}"
                        )
            else:
                return self.get_viewset([strategy])
        else:
            return self.get_viewset(strategy)

    def _standardize_key(self, key: Union[str, List[str]]) -> Tuple:
        if isinstance(key, str):
            return (key,)
        else:
            return tuple(sorted(key))

    def get_viewset(
        self, key: Union[str, List[str]]
    ) -> AuthentificationViewsetBase:
        """Get the viewset for a given key."""
        sorted_key = self._standardize_key(key)
        return self.viewsets[sorted_key]


class AuthentificationViewsetBase:
    """A viewset for authentications."""

    class AuthentificationView(
        PermissionRequiredReasoningMixin,
        LoginUserMixin,
        UpdateUserMixin,
        generic.View,
        metaclass=PermissionDeniedReasonsClass,
    ):
        """A view for handling the user authentication"""

        @cached_property
        def userinfo(self) -> Dict[str, Any]:  # type: ignore[override]
            """The userinfo as obtained from the Helmholtz AAI.

            The attributes of this dictionary are determined by the
            Helmholtz AAI, see  https://hifis.net/doc/helmholtz-aai/attributes/
            """
            token = oauth.helmholtz.authorize_access_token(self.request)
            return oauth.helmholtz.userinfo(request=self.request, token=token)

        @cached_property
        def is_new_user(self) -> bool:
            """True if the Helmholtz AAI user has never logged in before."""
            user_id = self.userinfo["eduperson_unique_id"]
            try:
                self.aai_user = models.HelmholtzUser.objects.get(
                    eduperson_unique_id=user_id, is_temporary=False
                )
            except models.HelmholtzUser.DoesNotExist:
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
                    self.permission_denied_reason = reasons.vo_not_allowed  # type: ignore[attr-defined]
                    return False
            elif app_settings.HELMHOLTZ_ALLOWED_VOS_REGEXP:
                return False

            # check for email verification
            if not userinfo["email_verified"]:
                self.permission_denied_reason = reasons.email_not_verified  # type: ignore[attr-defined]
                return False
            return True

        def handle_new_user(
            self, userinfo: Dict[str, Any]
        ) -> Tuple[Optional[models.HelmholtzUser], Any]:
            """Handle the registration of a new user."""
            raise NotImplementedError

        def get(self, request):
            """Login the Helmholtz AAI user and update the data.

            This method logs in the aai user (or creates one if it does not exist
            already). Afterwards we update the user info from the information on
            the Helmholtz AAI using the :meth:`update_user` and
            :meth:`synchronize_vos` methods.
            """
            if self.is_new_user:
                self.aai_user, response = self.handle_new_user(self.userinfo)
            else:
                self.update_user()
                response = None

            if self.aai_user:
                self.synchronize_vos()

                if not self.disable_user:
                    self.login_user(self.aai_user)

            if response:
                return response
            else:
                return redirect(self.get_success_url())

    def get_urls(self):
        return [
            path("auth/", self.AuthentificationView.as_view(), name="auth"),
        ]


registry = AuthenticationViewsetRegistry()
