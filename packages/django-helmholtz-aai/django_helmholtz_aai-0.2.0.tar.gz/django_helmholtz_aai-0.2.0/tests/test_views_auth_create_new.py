# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from test_views_auth_base import (
    TestAuthenticationView as BaseTestAuthenticationView,
)

from django_helmholtz_aai import models
from django_helmholtz_aai.views.auth.create_new import AuthentificationViewset

if TYPE_CHECKING:
    from django.contrib.auth.models import User
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

    def test_create_duplicated_user(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
        patched_signals: list[str],
    ):
        """Test if the signal aai_user_created and aai_user_logged_in are fired."""
        super().setup_user(userinfo)
        helmholtz_user = models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )
        user: User = helmholtz_user.user_ptr  # type: ignore[attr-defined]
        helmholtz_user.delete(keep_parents=True)

        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)
        assert patched_signals[0] == "aai_user_created"
        assert patched_signals[-1] == "aai_user_logged_in"

        helmholtz_user = models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        )

        assert helmholtz_user.pk != user.pk

    def test_create_duplicated_helmholtz_user(
        self,
        setup_authentification_view: _CreateView,
        patched_signals: list[str],
    ):
        """Test if the signal aai_user_created and aai_user_logged_in are fired."""
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)
        assert patched_signals[0] == "aai_user_created"
        assert patched_signals[-1] == "aai_user_logged_in"

        # test creation of a new user with the different id but all the rest is
        # the same
        view.userinfo["eduperson_unique_id"] += "_test"
        view.dispatch(view.request)

        assert patched_signals[0] == "aai_user_created"
        assert patched_signals[-1] == "aai_user_logged_in"
