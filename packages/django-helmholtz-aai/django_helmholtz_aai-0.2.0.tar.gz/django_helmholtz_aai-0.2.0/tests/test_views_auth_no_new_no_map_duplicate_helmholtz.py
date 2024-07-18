# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import pytest
from django.core.exceptions import PermissionDenied
from test_views_auth_base import (
    TestAuthenticationView as BaseTestAuthenticationView,
)

from django_helmholtz_aai import models
from django_helmholtz_aai.views.auth.no_new_no_map_duplicate_helmholtz import (
    AuthentificationViewset,
)

if TYPE_CHECKING:
    from test_views_auth_base import _CreateView


class TestAuthenticationView(BaseTestAuthenticationView):
    """Test the base authentication view."""

    auth_view_cls = AuthentificationViewset.AuthentificationView

    def test_no_new_permission_denied_message(
        self,
        setup_authentification_view: _CreateView,
    ):
        """Test creating a user"""
        view = setup_authentification_view(self.auth_view_cls)

        with pytest.raises(PermissionDenied):
            view.dispatch(view.request)

        assert (
            view.permission_denied_reason
            == view.PermissionDeniedReasons.no_user_exists  # type: ignore[attr-defined]
        )

    def test_no_map(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
    ):
        """Test creating a user"""
        self.setup_user(userinfo)
        helmholtz_user = models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )
        helmholtz_user.delete(keep_parents=True)

        view = setup_authentification_view(self.auth_view_cls)

        with pytest.raises(PermissionDenied):
            view.dispatch(view.request)

        assert (
            view.permission_denied_reason
            == view.PermissionDeniedReasons.email_exists  # type: ignore[attr-defined]
        )

    def test_create_duplicated_helmholtz_user(
        self,
        setup_authentification_view: _CreateView,
        patched_signals: list[str],
        userinfo: Dict[str, Any],
    ):
        """Test if the signal aai_user_created and aai_user_logged_in are fired."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)
        assert patched_signals[-1] == "aai_user_logged_in"

        patched_signals.clear()

        # test creation of a new user with the different id but all the rest is
        # the same
        userinfo["eduperson_unique_id"] += "_test"
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        assert patched_signals[0] == "aai_user_created"
        assert patched_signals[-1] == "aai_user_logged_in"
