# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""``no_new`` Strategy
-------------------
"""

from .base import AuthentificationViewsetBase, registry
from .mixins import NoUserExistsMixin


class AuthentificationViewset(AuthentificationViewsetBase):
    """An authentication viewset.

    The following strategy is applied for new users:

    - when the email exists already:
        - prevent login
    - when the email does not exist:
        - prevent login
    """

    class AuthentificationView(  # type: ignore[misc]
        NoUserExistsMixin,
        AuthentificationViewsetBase.AuthentificationView,
    ):
        """An authentication view."""

        def has_permission(self) -> bool:
            if super().has_permission():
                if self.is_new_user:
                    reasons = self.PermissionDeniedReasons
                    self.permission_denied_reason = reasons.no_helmholtz_user_exists  # type: ignore[assignment, attr-defined]
                    return False
                return True
            else:
                return False


registry.register_viewset("no-new", AuthentificationViewset())
