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

from django_helmholtz_aai.views.auth.no_new import AuthentificationViewset

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
            == view.PermissionDeniedReasons.no_helmholtz_user_exists  # type: ignore[attr-defined]
        )
