# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""``create_new`` Strategy
-----------------------
"""

from typing import Any, Dict, Tuple, Union

from django_helmholtz_aai import models

from .base import AuthentificationViewsetBase, registry
from .mixins import CreateUserMixin


class AuthentificationViewset(AuthentificationViewsetBase):
    """An authentication viewset.

    The following strategy is applied for new users:

    - when the email exists already:
      - create new user
    - when the email does not exist:
      - create new user"""

    class AuthentificationView(  # type: ignore[misc]
        CreateUserMixin, AuthentificationViewsetBase.AuthentificationView
    ):
        """An authentification view."""

        def handle_new_user(
            self, userinfo: Dict[str, Any]
        ) -> Tuple[Union[models.HelmholtzUser, None], Any]:
            user = self.create_user()
            return user, None


registry.register_viewset("create-new", AuthentificationViewset())
