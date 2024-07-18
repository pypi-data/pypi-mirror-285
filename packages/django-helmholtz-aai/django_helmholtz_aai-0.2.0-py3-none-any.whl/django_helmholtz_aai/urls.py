# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2
# SPDX-License-Identifier: EUPL-1.2

"""URL config
----------

URL patterns of the django-helmholtz-aai to be included via::

    from django.urls import include, path

    urlpatters = [
        path("helmholtz-aai/", include("django_helmholtz_aai.urls")),
    ]
"""
from __future__ import annotations

from typing import Any, List

from django.urls import path

from django_helmholtz_aai import views
from django_helmholtz_aai.views.auth import registry

#: App name for the django-helmholtz-aai to be used in calls to
#: :func:`django.urls.reverse`
app_name = "django_helmholtz_aai"

#: urlpattern for the Helmholtz AAI
urlpatterns: List[Any] = [
    path("login/", views.HelmholtzLoginView.as_view(), name="login"),
] + registry.get_default_viewset().get_urls()
