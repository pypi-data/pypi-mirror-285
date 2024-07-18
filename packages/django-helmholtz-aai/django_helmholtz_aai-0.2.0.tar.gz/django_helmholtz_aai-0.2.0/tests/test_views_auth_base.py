# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""Test module for the base authentication view."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
)

from django.views.generic import View

from django_helmholtz_aai import app_settings, models
from django_helmholtz_aai.views.auth.base import AuthentificationViewsetBase

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    T = TypeVar("T", bound=View)

    class _CreateView(Protocol):
        def __call__(
            self,
            cls_: Type[T],
            request: Optional[Union[str, WSGIRequest]] = None,
        ) -> T:
            ...


class TestAuthenticationView:
    """Tests for the base authentication view."""

    auth_view_cls: ClassVar[
        Type[AuthentificationViewsetBase.AuthentificationView]
    ] = AuthentificationViewsetBase.AuthentificationView

    def setup_user(self, userinfo: Dict[str, Any]):
        return models.HelmholtzUser.objects.create(
            userinfo=userinfo,
            eduperson_unique_id=userinfo["eduperson_unique_id"],
            username=userinfo["preferred_username"],
            email=userinfo["email"],
            first_name=userinfo["given_name"],
            last_name=userinfo["family_name"],
        )

    def test_basic_get(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
        username: str,
    ):
        """Test basic login."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(username=username)

    def test_signal_user_logged_in(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
        patched_signals: list[str],
    ):
        """Test if the signal aai_user_created and aai_user_logged_in are fired."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        assert patched_signals[-1] == "aai_user_logged_in"

    def test_signal_vo_created(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
        patched_signals: list[str],
    ):
        """Test if the signal aai_vo_created is fired on user creation."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        # we have two VOs in the userinfo, so this signal should be triggered twice
        assert patched_signals[-5:-1:2] == ["aai_vo_created", "aai_vo_created"]

    def test_signal_vo_entered(
        self,
        setup_authentification_view: _CreateView,
        userinfo: Dict[str, Any],
        patched_signals: list[str],
    ):
        """Test if the signal aai_vo_entered is fired on user creation."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        # we have two VOs in the userinfo, so this signal should be triggered twice
        assert patched_signals[-4:-1:2] == ["aai_vo_entered", "aai_vo_entered"]

    def test_change_username(
        self,
        setup_authentification_view: _CreateView,
        username: str,
        userinfo: dict[str, Any],
        patched_signals: list[str],
        monkeypatch,
    ):
        """Test what happens if the username changes."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        view.is_new_user = False

        view.userinfo["preferred_username"] = "max.mustermann"

        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(username="max.mustermann")

        assert patched_signals[-2:] == [
            "aai_user_updated",
            "aai_user_logged_in",
        ]

        # now test if we can prevent changing the username
        monkeypatch.setattr(
            app_settings,
            "HELMHOLTZ_UPDATE_USERNAME",
            False,
        )

        userinfo["preferred_username"] = "newusername"

        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(username="max.mustermann")

    def test_change_email(
        self,
        setup_authentification_view: _CreateView,
        username: str,
        userinfo: dict[str, Any],
        patched_signals: list[str],
        monkeypatch,
    ):
        """Test what happens if the username changes."""
        self.setup_user(userinfo)
        view = setup_authentification_view(self.auth_view_cls)
        view = setup_authentification_view(self.auth_view_cls)
        view.dispatch(view.request)

        view.is_new_user = False

        new_mail = "someothermail@somewhere.com"
        userinfo["email"] = new_mail

        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(email=new_mail)

        assert patched_signals[-2:] == [
            "aai_user_updated",
            "aai_user_logged_in",
        ]

        # now test if we can prevent changing the username
        monkeypatch.setattr(
            app_settings,
            "HELMHOLTZ_UPDATE_EMAIL",
            False,
        )

        userinfo["email"] = "againanothermail@somewhere.com"

        view.dispatch(view.request)

        assert models.HelmholtzUser.objects.get(email=new_mail)
