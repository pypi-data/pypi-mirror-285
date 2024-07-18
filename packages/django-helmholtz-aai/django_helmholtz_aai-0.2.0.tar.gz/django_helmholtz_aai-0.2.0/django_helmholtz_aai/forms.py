# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""Forms
-----

Forms for the :mod:`django_helmholtz_aai.views`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from django_helmholtz_aai import models
from django_helmholtz_aai.tokens import (
    UserLinkingTokenGenerator,
    default_token_generator,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()  # type: ignore


class UserLinkingForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        required=True,
    )

    new_user = forms.ModelChoiceField(
        models.HelmholtzUser.objects.filter(is_active=False),
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["new_user"].disabled = True

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject, body, from_email, [to_email]
        )
        if html_email_template_name is not None:
            html_email = loader.render_to_string(
                html_email_template_name, context
            )
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()

    def get_users(self, email: str, **kwargs):
        """Given an email, return matching user(s)."""
        email_field_name = User.get_email_field_name()
        kwargs.update(
            {"is_active": True, "%s__iexact" % email_field_name: email}
        )
        return list(User._default_manager.filter(**kwargs))

    def save(
        self,
        domain_override=None,
        subject_template_name="helmholtz_aai/link_user_subject.txt",
        email_template_name="helmholtz_aai/link_user_email.html",
        use_https=False,
        token_generator: UserLinkingTokenGenerator = default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        new_user = self.cleaned_data["new_user"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = User.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "new_uid": urlsafe_base64_encode(force_bytes(new_user.pk)),
                "user": user,
                "new_user": new_user,
                "token": token_generator.make_token(user, new_user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )


class NoDuplicatesUserLinkingForm(UserLinkingForm):
    """A User Linking Form that prevents users with associated helmholtz users."""

    def get_users(self, email: str, **kwargs):
        return super().get_users(email, helmholtzuser__isnull=True, **kwargs)


class MapUserForm(forms.Form):
    """
    A form that lets a user set their password without entering the old
    password
    """

    def save(self, commit=True):
        user = self.user
        new_user = self.new_user
        if hasattr(self.user, "helmholtzuser"):
            user_id = new_user.helmholtzuser.eduperson_unique_id
            updated_user = user.helmholtzuser
            updated_user.eduperson_unique_id = user_id
        else:
            fields = {
                f.name: getattr(user, f.name)
                for f in User._meta.fields
                if not f.many_to_many
            }
            updated_user = models.HelmholtzUser(
                user_ptr=user, eduperson_unique_id=user_id, **fields
            )
        if commit:
            new_user.delete()
            updated_user.save()
        return self.user
