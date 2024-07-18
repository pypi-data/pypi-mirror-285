# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from test_views_auth_base import (
    TestAuthenticationView as BaseTestAuthenticationView,
)

from django_helmholtz_aai import models
from django_helmholtz_aai.views.auth.create_new_map_existing_remap_helmholtz import (
    AuthentificationViewset,
)

if TYPE_CHECKING:
    from test_views_auth_base import _CreateView


class TestAuthenticationView(BaseTestAuthenticationView):
    """Test the base authentication view."""

    auth_view_cls = AuthentificationViewset.AuthentificationView

    def setup_user(self, userinfo: Dict[str, Any]):
        # The user is created by the view
        pass

    def test_signal_user_created(
        self,
        setup_authentification_view: _CreateView,
        patched_signals: list[str],
    ):
        """Test if the signal aai_user_created and aai_user_logged_in are fired."""
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)
        assert patched_signals[0] == "aai_user_created"
        assert patched_signals[-1] == "aai_user_logged_in"

    def test_map_user(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
    ):
        """Test mapping an existing user"""
        super().setup_user(userinfo)
        helmholtz_user = models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )
        helmholtz_user.delete(keep_parents=True)

        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )

    def test_remap_helmholtz(
        self,
        setup_authentification_view: _CreateView,
    ):
        """Test creating a duplicated user."""
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
