# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""Authentication viewsets
-----------------------

Authentication viewsets for the various creation strategy.
"""

from . import (  # noqa: F401
    create_new,
    create_new_map_existing_duplicate_helmholtz,
    create_new_map_existing_no_duplicated_helmholtz,
    create_new_map_existing_remap_helmholtz,
    create_new_no_map_duplicate_helmholtz,
    create_new_no_map_no_duplicated_helmholtz,
    manual_new_map_existing_no_duplicated_helmholtz,
    no_new,
    no_new_map_existing_no_duplicated_helmholtz,
    no_new_map_existing_remap_helmholtz,
    no_new_no_map_duplicate_helmholtz,
)
from .base import registry  # noqa: F401
