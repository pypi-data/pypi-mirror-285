# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: CC0-1.0
# SPDX-License-Identifier: EUPL-1.2

from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from django.conf import settings

if TYPE_CHECKING:
    import environ


engines = {
    "sqlite": "django.db.backends.sqlite3",
    "postgresql": "django.db.backends.postgresql",
    "mysql": "django.db.backends.mysql",
}


def config(env: environ.Env) -> Dict:
    service_name = (
        env("DATABASE_SERVICE_NAME", default="").upper().replace("-", "_")
    )
    if service_name:
        engine = engines.get(
            env("DATABASE_ENGINE", default="sqlite"), engines["sqlite"]
        )
    else:
        engine = engines["sqlite"]
    name = env(f"{service_name}_DATABASE", default="")
    if not name and engine == engines["sqlite"]:
        name = settings.BASE_DIR / "db.sqlite3"
    elif not name:
        name = "django_db"
    return {
        "ENGINE": engine,
        "NAME": name,
        "USER": env(f"{service_name}_USER", default="django_user"),
        "PASSWORD": env(f"{service_name}_PASSWORD", default="changeme!"),
        "HOST": env(f"{service_name}_SERVICE_HOST", default="localhost"),
        "PORT": env(f"{service_name}_SERVICE_PORT", default="5432"),
    }
