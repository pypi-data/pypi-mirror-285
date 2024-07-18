# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Dict

import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from test_views_auth_base import (
    TestAuthenticationView as BaseTestAuthenticationView,
)

from django_helmholtz_aai import models
from django_helmholtz_aai.views.auth.manual_new_map_existing_no_duplicated_helmholtz import (
    AuthentificationViewset,
)

if TYPE_CHECKING:
    from test_views_auth_base import _CreateView


class TestAuthenticationView(BaseTestAuthenticationView):
    """Test the base authentication view."""

    auth_view_cls = AuthentificationViewset.AuthentificationView

    def test_basic_new_user(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
    ):
        """Test creating a user"""
        view = setup_authentification_view(self.auth_view_cls)

        response = view.dispatch(view.request)

        assert isinstance(response, HttpResponseRedirect)
        assert re.match(r"^/helmholtz-aai/link_user/.+/$", response.url)

        assert models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"],
            is_active=False,
        )

    def test_manual_user_map(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
        client,
        mailoutbox,
        patched_signals,
    ):
        """Test manual mapping of a user to a new user."""
        view = setup_authentification_view(self.auth_view_cls)

        response = view.dispatch(view.request)

        assert isinstance(response, HttpResponseRedirect)
        assert re.match(r"^/helmholtz-aai/link_user/.+/$", response.url)

        user = models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"],
            is_active=False,
        )

        user.is_active = True
        user.save()

        # delete helmholtz user
        models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"]
        ).delete(keep_parents=True)

        user_email = view.userinfo["email"]
        new_email = "sometest@somewhere.com"

        view.userinfo["email"] = new_email

        response = view.dispatch(view.request)

        assert isinstance(response, HttpResponseRedirect)
        assert re.match(r"^/helmholtz-aai/link_user/.+/$", response.url)

        response = client.post(response.url, {"email": user_email})

        assert len(mailoutbox) == 1
        body = mailoutbox[0].body

        token_patt = r"/helmholtz-aai/link_user/.*/.*/.*/"

        assert re.search(token_patt, body)

        token_uri = re.search(token_patt, body).group()  # type: ignore[union-attr]

        response = client.get(token_uri)

        assert isinstance(response, HttpResponseRedirect)

        patched_signals.clear()

        response = client.post(response.url)

        assert isinstance(response, HttpResponseRedirect)

        assert models.HelmholtzUser.objects.get(
            eduperson_unique_id=userinfo["eduperson_unique_id"],
            email=new_email,
        )

        assert patched_signals == ["aai_user_updated", "aai_user_logged_in"]

    def test_no_duplicated_helmholtz_message(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
    ):
        """Test creating a duplicated user."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        # modify the user id and create a new one

        view.userinfo["eduperson_unique_id"] += "_test"
        view = setup_authentification_view(self.auth_view_cls)

        with pytest.raises(PermissionDenied):
            view.dispatch(view.request)

        assert (
            view.permission_denied_reason
            == view.PermissionDeniedReasons.helmholtz_email_exists  # type: ignore[attr-defined]
        )

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
