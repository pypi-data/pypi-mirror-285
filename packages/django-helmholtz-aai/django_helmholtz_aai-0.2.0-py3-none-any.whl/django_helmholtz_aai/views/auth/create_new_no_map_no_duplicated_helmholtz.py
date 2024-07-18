# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""``create_new_no_map_no_duplicated_helmholtz`` Strategy
------------------------------------------------------
"""

from typing import Any, Dict, Optional, Tuple

from django_helmholtz_aai import models

from .base import registry
from .create_new import AuthentificationViewset as AuthentificationViewsetBase
from .mixins import CheckEmailMixin


class AuthentificationViewset(AuthentificationViewsetBase):
    """An authentication viewset.

    The following strategy is applied for new users:

    - when the email exists already:
      - prevent login
    - when the email does not exist:
      - create new user
    """

    class AuthentificationView(  # type: ignore[misc]
        CheckEmailMixin, AuthentificationViewsetBase.AuthentificationView
    ):
        """An authentification view."""

        def has_permission(self) -> bool:
            if not self.is_new_user:
                return super().has_permission()
            elif super().has_permission():
                # test if the email already exists
                email = self.userinfo["email"]
                if self.is_new_user and self.email_exists(email):
                    reasons = self.PermissionDeniedReasons
                    self.permission_denied_reason = reasons.helmholtz_email_exists  # type: ignore[assignment]
                    return False
                else:
                    return True
            else:
                return False

        def handle_new_user(
            self, userinfo: Dict[str, Any]
        ) -> Tuple[Optional[models.HelmholtzUser], Any]:
            user = self.create_user()
            return user, None


registry.register_viewset(
    ["create-new", "no-map", "no-duplicated-helmholtz"],
    AuthentificationViewset(),
)
