# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2
# SPDX-License-Identifier: EUPL-1.2

"""App config
----------

App config for the django_helmholtz_aai app.
"""

from django.apps import AppConfig


class DjangoHelmholtzAaiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_helmholtz_aai"
