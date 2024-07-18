# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2
# SPDX-License-Identifier: EUPL-1.2

"""Helmholtz AAI Django App

A generic Django app to login via Helmholtz AAI
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth import login as auth_login

from django_helmholtz_aai import signals

from . import _version

if TYPE_CHECKING:
    from django_helmholtz_aai import models

__version__ = _version.get_versions()["version"]

__author__ = "Philipp S. Sommer, Housam Dibeh, Hatef Takyar"
__copyright__ = "2022-2023 Helmholtz-Zentrum hereon GmbH"
__credits__ = [
    "Philipp S. Sommer",
    "Housam Dibeh",
    "Hatef Takyar",
]
__license__ = "EUPL-1.2"

__maintainer__ = "Philipp S. Sommer"
__email__ = (
    "philipp.sommer@hereon.de, hcdc_support@hereon.de, hcdc_support@hereon.de"
)

__status__ = "Production"


def login(request, user: models.HelmholtzUser, userinfo: dict[str, Any]):
    """Login the helmholtz user into django.

    Notes
    -----
    Emits the :attr:`~django_helmholtz_aai.signals.aai_user_logged_in` signal
    """
    auth_login(request, user)

    # emit the aai_user_logged_in signal as an existing user has been
    # logged in
    signals.aai_user_logged_in.send(
        sender=user.__class__,
        user=user,
        request=request,
        userinfo=userinfo,
    )
