"""Template tags for the Helmholtz AAI."""

# Copyright (C) 2022 Helmholtz-Zentrum Hereon
# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

from urllib.parse import parse_qs, urlparse, urlunparse

from django import template
from django.urls import reverse
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def helmholtz_login_url(context) -> str:
    """Get the url to login to the Helmholtz AAI."""
    login_url = reverse("django_helmholtz_aai:login")

    request = context["request"]

    parts = urlparse(request.path)
    urlparams = parse_qs(request.GET.urlencode())
    url = urlunparse(
        [
            parts.scheme,
            parts.netloc,
            login_url,
            parts.params,
            urlencode(urlparams, doseq=True),
            parts.fragment,
        ]
    )

    return url
