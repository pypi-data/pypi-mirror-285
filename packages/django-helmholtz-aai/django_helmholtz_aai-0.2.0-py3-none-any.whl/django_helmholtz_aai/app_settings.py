# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2
# SPDX-License-Identifier: EUPL-1.2

"""App settings
------------

This module defines the settings options for the ``django_helmholtz_aai`` app.
"""


from __future__ import annotations

import re
import warnings
from typing import List, Optional, Union

from django.conf import settings


def _transform_deprecated_settings(
    create_users: bool, map_accounts: bool, email_duplicates_allowd: bool
) -> List[str]:
    """Transform the deprecated settings to the user creation strategy."""

    settings_map = {
        (True, True, True): [
            "create-new",
            "map-existing",
            "duplicate-helmholtz",
        ],
        (True, False, True): ["create-new", "no-map", "duplicate-helmholtz"],
        (True, False, False): [
            "create-new",
            "no-map",
            "no-duplicated-helmholtz",
        ],
        (False, False, False): ["no-new"],
        (True, True, False): [
            "create-new",
            "map-existing",
            "remap-helmholtz",
        ],
        (False, True, False): [
            "no-new",
            "map-existing",
            "remap-helmholtz",
        ],
        (False, False, True): ["no-new", "no-map", "duplicate-helmholtz"],
    }
    return settings_map[(create_users, map_accounts, email_duplicates_allowd)]


#: A string of lists specifying which VOs are allowed to log into the website.
#:
#: By default, this is an empty list meaning that each and every user
#: is allowed to login via the Helmholtz AAI. Each string in this list will be
#: interpreted as a regular expression and added to :attr:`HELMHOLTZ_ALLOWED_VOS_REGEXP`
#:
#: .. setting:: HELMHOLTZ_ALLOWED_VOS
#:
#: Examples
#: --------
#: Assume you only want to allow people from the Hereon VO to login to the
#: website. Then you can add the following to your ``settings.py``::
#:
#:     HELMHOLTZ_ALLOWED_VOS = [
#:         "urn:geant:helmholtz.de:group:hereon#login.helmholtz.de",
#:     ]
#:
#: or use a regex, e.g. something like::
#:
#:     HELMHOLTZ_ALLOWED_VOS = [
#:         r".*helmholtz.de:group:hereon#login.helmholtz.de",
#:     ]
HELMHOLTZ_ALLOWED_VOS: list[str] = getattr(
    settings, "HELMHOLTZ_ALLOWED_VOS", []
)

#: Regular expressions for VOs that are allowed to login to the website.
#:
#: This attribute is created from the :attr:`HELMHOLTZ_ALLOWED_VOS` setting.
#:
#: .. setting:: HELMHOLTZ_ALLOWED_VOS_REGEXP
HELMHOLTZ_ALLOWED_VOS_REGEXP: list[re.Pattern] = getattr(
    settings, "HELMHOLTZ_ALLOWED_VOS_REGEXP", []
)

HELMHOLTZ_ALLOWED_VOS_REGEXP.extend(
    map(re.compile, HELMHOLTZ_ALLOWED_VOS)  # type: ignore
)

#: openid configuration url of the Helmholtz AAI
#:
#: Can also be overwritten using the :attr:`HELMHOLTZ_CLIENT_KWS` setting.
#:
#: .. setting:: HELMHOLTZ_AAI_CONF_URL
HELMHOLTZ_AAI_CONF_URL: str = (
    getattr(
        settings,
        "HELMHOLTZ_AAI_CONF_URL",
        None,
    )
    or "https://login.helmholtz.de/oauth2/.well-known/openid-configuration"
)


#: Client id for the Helmholtz AAI
#:
#: This is the username you use to login at
#: https://login.helmholtz.de/oauthhome/, see [client-registration]_ for how to
#: create a client
#:
#: .. setting:: HELMHOLTZ_CLIENT_ID
#:
#: See Also
#: --------
#: HELMHOLTZ_CLIENT_SECRET
HELMHOLTZ_CLIENT_ID: str = getattr(settings, "HELMHOLTZ_CLIENT_ID", "")


#: Client secret for the Helmholtz AAI
#:
#: This is the password you use to login at
#: https://login.helmholtz.de/oauthhome/, see[client-registration]_ for how to
#: create a client
#:
#: .. setting:: HELMHOLTZ_CLIENT_SECRET
#:
#: See Also
#: --------
#: HELMHOLTZ_CLIENT_ID
HELMHOLTZ_CLIENT_SECRET: str = getattr(settings, "HELMHOLTZ_CLIENT_SECRET", "")


if not HELMHOLTZ_CLIENT_ID:
    warnings.warn(
        "No client ID configured for the Helmholtz AAI. The authentification "
        "agains the Helmholtz AAI will not work! Please register a client and "
        "specify set the username as HELMHOLTZ_CLIENT_ID in settings.py.\n"
        "See https://hifis.net/doc/helmholtz-aai/howto-services/ for more "
        "information."
    )


if not HELMHOLTZ_CLIENT_SECRET:
    warnings.warn(
        "No client secret configured for the Helmholtz AAI. The "
        "authentification against the Helmholtz AAI will not work! Please "
        "register a client and set the secret as HELMHOLTZ_CLIENT_SECRET in "
        "settings.py.\n"
        "See https://hifis.net/doc/helmholtz-aai/howto-services/ for more "
        "information."
    )


#: Keyword argument for the oauth client to connect with the helmholtz AAI.
#:
#: Can also be overwritten using the :attr:`HELMHOLTZ_CLIENT_KWS` setting.
#:
#: .. setting:: HELMHOLTZ_CLIENT_KWS
HELMHOLTZ_CLIENT_KWS = dict(
    client_id=HELMHOLTZ_CLIENT_ID,
    client_secret=HELMHOLTZ_CLIENT_SECRET,
    server_metadata_url=HELMHOLTZ_AAI_CONF_URL,
    client_kwargs={"scope": "profile email eduperson_unique_id"},
)

for key, val in getattr(settings, "HELMHOLTZ_CLIENT_KWS", {}).items():
    HELMHOLTZ_CLIENT_KWS[key] = val

#: Deprecated. See :setting:`HELMHOLTZ_CREATE_USERS_STRATEGY`
#:
#: .. setting:: HELMHOLTZ_EMAIL_DUPLICATES_ALLOWED
HELMHOLTZ_EMAIL_DUPLICATES_ALLOWED: bool = getattr(
    settings, "HELMHOLTZ_EMAIL_DUPLICATES_ALLOWED", False
)


#: Username fields in the userinfo
#:
#: This setting determines how to get the username. By default, we use the
#: ``preferred_username`` that the user can configure at
#: https://login.helmholtz.de/oauthhome. If this is already taken, we use the
#: unique ``eduperson_unique_id`` from the Helmholtz AAI. You can add more
#: variables to this list but you should always include the
#: ``eduperson_unique_id`` to make sure you do not end up with duplicated
#: usernames.
#:
#: .. setting:: HELMHOLTZ_USERNAME_FIELDS
#:
#: Examples
#: --------
#: You can use the email instead of the ``preferred_username`` via::
#:
#:     HELMHOLTZ_USERNAME_FIELDS = ["email", "eduperson_unique_id"]
HELMHOLTZ_USERNAME_FIELDS: list[str] = getattr(
    settings,
    "HELMHOLTZ_USERNAME_FIELDS",
    ["preferred_username", "eduperson_unique_id"],
)


#: Flag whether usernames should be updated from the Helmholtz AAI
#:
#: Use this setting to control, whether the usernames are updated automatically
#: on every login. If this is true, we will check the fields specified in the
#: :attr:`HELMHOLTZ_USERNAME_FIELDS` setting variable on every login and update
#: the username accordingly. If the user, for instance, changes his or her
#: ``preferred_username`` on https://login.helmholtz.de/, we will update the
#: username of the django user as well (if ``preferred_username`` is in the
#: :attr:`HELMHOLTZ_USERNAME_FIELDS`).
#:
#: .. setting:: HELMHOLTZ_UPDATE_USERNAME
HELMHOLTZ_UPDATE_USERNAME: bool = getattr(
    settings, "HELMHOLTZ_UPDATE_USERNAME", True
)


#: Flag whether emails should be updated from the Helmholtz AAI
#:
#: Use this setting to control, whether the emails of the user are updated
#: on every login. If this is true, we will check the email on every login and
#: update email of the user accordingly.
#:
#: .. setting:: HELMHOLTZ_UPDATE_EMAIL
HELMHOLTZ_UPDATE_EMAIL: bool = getattr(
    settings, "HELMHOLTZ_UPDATE_EMAIL", True
)


#: Deprecated. See :setting:`HELMHOLTZ_CREATE_USERS_STRATEGY`
#:
#: .. setting:: HELMHOLTZ_MAP_ACCOUNTS
HELMHOLTZ_MAP_ACCOUNTS: bool = getattr(
    settings, "HELMHOLTZ_MAP_ACCOUNTS", False
)

#: Deprecated. See :setting:`HELMHOLTZ_CREATE_USERS_STRATEGY`
#:
#: .. setting:: HELMHOLTZ_CREATE_USERS
HELMHOLTZ_CREATE_USERS: bool = getattr(
    settings, "HELMHOLTZ_CREATE_USERS", True
)

#: The backend that is used to login the user. By default, we use the Django
#: default, i.e. :class:`django.contrib.auth.backends.ModelBackend`
HELMHOLTZ_USER_BACKEND: str = getattr(
    settings,
    "HELMHOLTZ_USER_BACKEND",
    "django.contrib.auth.backends.ModelBackend",
)

#: Root url for the django application
#:
#: The login requires a redirect url that is derived from the
#: view with the name ``"django_helmholtz_aai:auth"`` and the protocoll and
#: host name of your application. In case your application is behind a
#: reverse proxy that does not forward correct host or protocoll, you can use
#: this setting to set the URL manually.
#:
#: Examples
#: --------
#: If this app is included via
#: ``path("helmholtz-aai/", include("django_helmholtz_aai.urls"))`` in your
#: url-config and available at ``https://example.com/helmholtz-aai/``,
#: then the ``ROOT_URL`` in your ``settings.py`` should be
#: ``https://example.com``
ROOT_URL: Optional[str] = getattr(settings, "ROOT_URL", None)


_deprecated_settings = [
    "HELMHOLTZ_CREATE_USERS",
    "HELMHOLTZ_MAP_ACCOUNTS",
    "HELMHOLTZ_EMAIL_DUPLICATES_ALLOWED",
]

if any(hasattr(settings, setting) for setting in _deprecated_settings):
    default_strategy = _transform_deprecated_settings(
        HELMHOLTZ_CREATE_USERS,
        HELMHOLTZ_MAP_ACCOUNTS,
        HELMHOLTZ_EMAIL_DUPLICATES_ALLOWED,
    )
    warnings.warn(
        "The settings HELMHOLTZ_CREATE_USERS and HELMHOLTZ_MAP_ACCOUNTS are "
        "deprecated in favor of HELMHOLTZ_CREATE_USERS_STRATEGY Your settings "
        "are best represented by the following setting:\n\n"
        f"HELMHOLTZ_CREATE_USERS_STRATEGY = {default_strategy}",
        DeprecationWarning,
    )
else:
    default_strategy = [
        "create-new",
        "no-map",
        "no-duplicated-helmholtz",
    ]


#: Strategy how to onboard new users from the Helmholtz AAI
#:
#: This setting determines, how new users from the Helmholtz AAI are treated
#: in this application. Various strategies are available, see
#: :ref:`implemented-strategies`. By default, we use the following strategy::
#:
#:     ["create-new", "no-map", "no-duplicated-helmholtz"]
#:
#: Meaning that new users are created, but only when there is not already any
#: user with the same email address.
#:
#: .. setting:: HELMHOLTZ_CREATE_USERS_STRATEGY
HELMHOLTZ_CREATE_USERS_STRATEGY: Union[str, List[str]] = getattr(
    settings, "HELMHOLTZ_CREATE_USERS_STRATEGY", default_strategy
)
