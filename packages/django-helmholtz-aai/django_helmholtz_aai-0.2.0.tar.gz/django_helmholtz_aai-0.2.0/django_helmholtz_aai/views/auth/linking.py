# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""User linking views
------------------

Mainly for the manual user linking implementation, this moduel defines the
views and the viewset mixin to link one helmholtz user to an existing django
user. It's copying the passwort reset implementation of
:mod:`django.contrib.auth`
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.forms import Form
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.functional import cached_property
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_protect

from django_helmholtz_aai import app_settings, forms
from django_helmholtz_aai import login as aai_login
from django_helmholtz_aai import models

from .mixins import UpdateUserMixin

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()  # pragma: no cover

INTERNAL_RESET_SESSION_TOKEN = "_link_user_token"


class UserLinkingContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.title,
                "subtitle": None,
                **(self.extra_context or {}),
            }
        )
        return context

    def get_user(self, uidb64, UserModel=User, **kwargs) -> Optional[User]:
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid, **kwargs)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user


class LinkingUserViewsetMixin:
    """A mixin to provide form to link a user."""

    class UserLinkingView(UserLinkingContextMixin, generic.edit.FormView):  # type: ignore[misc]
        email_template_name = "helmholtz_aai/link_user_email.html"
        extra_email_context = None
        form_class = forms.UserLinkingForm
        from_email = None
        html_email_template_name = None
        subject_template_name = "helmholtz_aai/link_user_subject.txt"
        template_name = "helmholtz_aai/link_user_form.html"
        title = _("Map Helmholtz AAI User")
        token_generator = forms.default_token_generator

        @method_decorator(csrf_protect)
        def dispatch(self, *args, **kwargs):
            return super().dispatch(*args, **kwargs)

        def get_success_url(self) -> str:
            new_uid = urlsafe_base64_encode(force_bytes(self.aai_user.pk))
            return resolve_url(
                "django_helmholtz_aai:link_user_done", new_uidb64=new_uid
            )

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["validlink"] = True
            context["new_user"] = self.aai_user
            return context

        @cached_property
        def aai_user(self) -> models.HelmholtzUser:
            """Get the user for the given ID."""
            user: models.HelmholtzUser = self.get_user(  # type: ignore
                self.kwargs["new_uidb64"], models.HelmholtzUser
            )
            if user is None:
                raise Http404("No user found with the given ID.")
            return user

        def get_form_kwargs(self) -> Dict[str, Any]:
            ret = super().get_form_kwargs()
            initial = ret.setdefault("initial", {})
            initial["new_user"] = self.aai_user
            return ret

        def form_valid(self, form):
            opts = {
                "use_https": self.request.is_secure(),
                "token_generator": self.token_generator,
                "from_email": self.from_email,
                "email_template_name": self.email_template_name,
                "subject_template_name": self.subject_template_name,
                "request": self.request,
                "html_email_template_name": self.html_email_template_name,
                "extra_email_context": self.extra_email_context,
            }
            form.save(**opts)
            return super().form_valid(form)

    class UserLinkingDoneView(  # type: ignore[misc]
        UserLinkingContextMixin, generic.TemplateView
    ):
        template_name = "helmholtz_aai/link_user_done.html"
        title = _("Mapping instructions sent")

    class UserLinkingConfirmView(  # type: ignore[misc]
        UserLinkingContextMixin,
        SuccessMessageMixin,
        UpdateUserMixin,
        generic.edit.FormView,
    ):
        form_class = Form
        post_mapping_login = True
        post_mapping_login_backend = None
        reset_url_token = "link-user"
        template_name = "helmholtz_aai/link_user_confirm.html"
        title = _("Confirm Helmholtz User Mapping")
        token_generator = forms.default_token_generator

        success_message = _("User accounts have been linked.")

        @cached_property
        def userinfo(self) -> Dict[str, Any]:  # type: ignore[override]
            return self.get_user(  # type: ignore
                self.kwargs["new_uidb64"], models.HelmholtzUser
            ).userinfo

        def dispatch(self, *args, **kwargs):
            if (
                "uidb64" not in kwargs
                or "new_uidb64" not in kwargs
                or "token" not in kwargs
            ):
                raise ImproperlyConfigured(
                    "The URL path must contain 'uidb64', 'new_uidb64' and "
                    "'token' parameters."
                )

            self.validlink = False
            self.user = self.get_user(kwargs["uidb64"])
            self.aai_user: models.HelmholtzUser = self.get_user(  # type: ignore
                kwargs["new_uidb64"],
                models.HelmholtzUser,
                is_active=False,
                is_temporary=True,
            )

            if self.user is not None and self.aai_user is not None:
                token = kwargs["token"]
                if token == self.reset_url_token:
                    session_token = self.request.session.get(
                        INTERNAL_RESET_SESSION_TOKEN
                    )
                    if self.token_generator.check_token(
                        self.user, self.aai_user, session_token
                    ):
                        # If the token is valid, display the password reset form.
                        self.validlink = True
                        return super().dispatch(*args, **kwargs)
                else:
                    if self.token_generator.check_token(
                        self.user, self.aai_user, token
                    ):
                        # Store the token in the session and redirect to the
                        # password reset form at a URL without the token. That
                        # avoids the possibility of leaking the token in the
                        # HTTP Referer header.
                        self.request.session[
                            INTERNAL_RESET_SESSION_TOKEN
                        ] = token
                        redirect_url = self.request.path.replace(
                            token, self.reset_url_token
                        )
                        return HttpResponseRedirect(redirect_url)

            # Display the "Password reset unsuccessful" page.
            return self.render_to_response(self.get_context_data())

        def update_user(self):
            """Update the VOs and attributes from the new user."""
            user = self.user
            new_user = self.aai_user

            user_id = new_user.helmholtzuser.eduperson_unique_id

            # replace the existing helmholtz user with the new one
            if hasattr(self.user, "helmholtzuser"):
                updated_user = self.aai_user = user.helmholtzuser
                updated_user.eduperson_unique_id = user_id
                updated_user.userinfo = self.userinfo
            else:
                fields = {
                    f.name: getattr(user, f.name)
                    for f in User._meta.fields
                    if not f.many_to_many
                }
                updated_user = self.aai_user = models.HelmholtzUser(
                    user_ptr=user,
                    eduperson_unique_id=user_id,
                    userinfo=self.userinfo,
                    **fields,
                )

            new_user.delete()
            updated_user.save()

            to_update = dict(
                eduperson_unique_id=user_id,
                userinfo=self.userinfo,
            )

            return super().update_user(**to_update)

        def form_valid(self, form):
            self.update_user()
            self.synchronize_vos()
            del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
            if self.post_mapping_login:
                self.aai_user.backend = app_settings.HELMHOLTZ_USER_BACKEND  # type: ignore
                aai_login(self.request, self.aai_user, self.userinfo)
            return super().form_valid(form)

        def get_success_url(self) -> str:
            if self.post_mapping_login:
                return self.request.session.pop(
                    "forward_after_aai_login", settings.LOGIN_REDIRECT_URL
                )
            else:
                return resolve_url("login")

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            if self.validlink:
                context["validlink"] = True
                context["existing_user"] = self.user
                context["new_user"] = self.aai_user
            else:
                context.update(
                    {
                        "form": None,
                        "title": _("User mapping unsuccessful"),
                        "validlink": False,
                    }
                )
            return context

    def get_urls(self):
        return super().get_urls() + [
            path(
                "link_user/<new_uidb64>/",
                self.UserLinkingView.as_view(),
                name="link_user",
            ),
            path(
                "link_user/<new_uidb64>/done/",
                self.UserLinkingDoneView.as_view(),
                name="link_user_done",
            ),
            path(
                "link_user/<new_uidb64>/<uidb64>/<token>/",
                self.UserLinkingConfirmView.as_view(),
                name="link_user_confirm",
            ),
        ]
