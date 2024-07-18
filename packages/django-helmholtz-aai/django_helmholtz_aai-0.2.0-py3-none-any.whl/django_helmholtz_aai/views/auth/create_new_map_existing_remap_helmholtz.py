# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""``create_new_map_existing_remap_helmholtz`` Strategy
----------------------------------------------------
"""

from typing import Any, Dict, Optional, Tuple

from django_helmholtz_aai import models

from .base import registry
from .create_new import AuthentificationViewset as AuthentificationViewsetBase
from .create_new_no_map_no_duplicated_helmholtz import CheckEmailMixin
from .mixins import MapUserMixin


class AuthentificationViewset(AuthentificationViewsetBase):
    """An authentication viewset.

    The following strategy is applied for new users:

    - when the email exists already:
        - when the user with the mail already has a helmholtz user:
            - map user
        - when the user with the mail does not have a helmholtz user:
            - map user
    - when the email does not exist:
        - create new user
    """

    class AuthentificationView(  # type: ignore[misc]
        MapUserMixin,
        CheckEmailMixin,
        AuthentificationViewsetBase.AuthentificationView,
    ):
        """An authentification view that creates new users upon request."""

        def handle_new_user(
            self, userinfo: Dict[str, Any]
        ) -> Tuple[Optional[models.HelmholtzUser], Any]:
            email = userinfo["email"]
            if self.email_exists(email):
                user = self.map_user()
            else:
                user = self.create_user()
            return user, None


registry.register_viewset(
    ["create-new", "map-existing", "remap-helmholtz"],
    AuthentificationViewset(),
)
