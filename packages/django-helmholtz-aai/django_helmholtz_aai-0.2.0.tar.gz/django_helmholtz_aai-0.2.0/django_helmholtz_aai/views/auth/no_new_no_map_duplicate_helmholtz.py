# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""``no_new_no_map_duplicate_helmholtz`` Strategy
----------------------------------------------
"""

from typing import Any, Dict, Optional, Tuple

from django_helmholtz_aai import models

from .base import registry
from .create_new import AuthentificationViewset as AuthentificationViewsetBase
from .mixins import CheckEmailMixin, MapUserMixin, NoUserExistsMixin


class AuthentificationViewset(AuthentificationViewsetBase):
    """An authentication viewset.

    The following strategy is applied for new users:

    - when the email exists already:
        - when the user with the mail already has a helmholtz user:
            - create new user
        - when the user with the mail does not have a helmholtz user:
            - prevent login
    - when the email does not exist:
        - prevent login
    """

    class AuthentificationView(  # type: ignore[misc]
        MapUserMixin,
        NoUserExistsMixin,
        CheckEmailMixin,
        AuthentificationViewsetBase.AuthentificationView,
    ):
        """An authentication view."""

        def has_permission(self) -> bool:
            if not self.is_new_user:
                return super().has_permission()
            elif super().has_permission():
                # test if the email already exists
                email = self.userinfo["email"]
                if self.is_new_user and self.email_exists(email):
                    if not self.email_exists(email, models.HelmholtzUser):
                        reasons = self.PermissionDeniedReasons
                        self.permission_denied_reason = reasons.email_exists  # type: ignore[assignment, attr-defined]
                        return False
                    else:
                        return True
                else:
                    reasons = self.PermissionDeniedReasons
                    self.permission_denied_reason = reasons.no_user_exists  # type: ignore[assignment, attr-defined]
                    return False
            else:
                return False

        def handle_new_user(
            self, userinfo: Dict[str, Any]
        ) -> Tuple[Optional[models.HelmholtzUser], Any]:
            email = userinfo["email"]
            if self.email_exists(email):
                if self.email_exists(email, models.HelmholtzUser):
                    user = self.create_user()
                else:
                    user = None
            else:
                user = None
            return user, None


registry.register_viewset(
    ["no-new", "no-map", "duplicate-helmholtz"],
    AuthentificationViewset(),
)
