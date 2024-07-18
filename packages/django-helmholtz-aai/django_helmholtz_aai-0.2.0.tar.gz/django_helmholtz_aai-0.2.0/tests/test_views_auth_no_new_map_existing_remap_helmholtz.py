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
from django_helmholtz_aai.views.auth.no_new_map_existing_remap_helmholtz import (
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
        userinfo: Dict[str, Any],
    ):
        """Test creating a user"""
        view = setup_authentification_view(self.auth_view_cls)

        with pytest.raises(PermissionDenied):
            view.dispatch(view.request)

        assert (
            view.permission_denied_reason
            == view.PermissionDeniedReasons.no_user_exists  # type: ignore[attr-defined]
        )

    def test_remap_helmholtz(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
    ):
        """Test creating a duplicated user."""
        self.setup_user(userinfo)
        user = models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )
        user.delete(keep_parents=True)

        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        user_id = view.userinfo["eduperson_unique_id"]

        assert models.HelmholtzUser.objects.get(eduperson_unique_id=user_id)

        # modify the user id and create a new one
        view.userinfo["eduperson_unique_id"] += "_test"

        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(
            eduperson_unique_id=user_id + "_test"
        )
        assert not models.HelmholtzUser.objects.filter(
            eduperson_unique_id=user_id
        ).exists()

    def test_map_user(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
    ):
        """Test mapping an existing user"""
        self.setup_user(userinfo)
        user = models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )
        user.delete(keep_parents=True)

        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )
