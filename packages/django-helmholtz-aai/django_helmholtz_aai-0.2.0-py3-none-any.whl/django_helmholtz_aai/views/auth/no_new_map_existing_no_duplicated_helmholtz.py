# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""``no_new_map_existing_no_duplicated_helmholtz`` Strategy
--------------------------------------------------------
"""

from typing import Any, Dict, Optional, Tuple

from django.db.models import Q

from django_helmholtz_aai import models

from .base import registry
from .create_new import AuthentificationViewset as AuthentificationViewsetBase
from .mixins import CheckEmailMixin, MapUserMixin, NoUserExistsMixin


class AuthentificationViewset(AuthentificationViewsetBase):
    """An authentication viewset.

    The following strategy is applied for new users:

    - when the email exists already:
        - when the user with the mail already has a helmholtz user:
            - prevent login
        - when the user with the mail does not have a helmholtz user:
            - map user
    - when the email does not exist:
        - prevent login
    """

    class AuthentificationView(  # type: ignore[misc]
        MapUserMixin,
        CheckEmailMixin,
        NoUserExistsMixin,
        AuthentificationViewsetBase.AuthentificationView,
    ):
        """An authentication view."""

        def has_permission(self) -> bool:
            if not self.is_new_user:
                return super().has_permission()
            elif super().has_permission():
                # test if the email already exists
                email = self.userinfo["email"]
                user_id = self.userinfo["eduperson_unique_id"]
                reasons = self.PermissionDeniedReasons
                if self.is_new_user and self.email_exists(email):
                    if self.user_exists(
                        Q(email__iexact=email)
                        & ~Q(eduperson_unique_id=user_id),
                    ):
                        self.permission_denied_reason = reasons.helmholtz_email_exists  # type: ignore[assignment]
                        return False
                    return True
                else:
                    self.permission_denied_reason = reasons.no_user_exists  # type: ignore[assignment]
                    return False
            else:
                return False

        def handle_new_user(
            self, userinfo: Dict[str, Any]
        ) -> Tuple[Optional[models.HelmholtzUser], Any]:
            user = self.map_user()
            return user, None


registry.register_viewset(
    ["no-new", "map-existing", "no-duplicated-helmholtz"],
    AuthentificationViewset(),
)
