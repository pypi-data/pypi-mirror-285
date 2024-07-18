# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2
# SPDX-License-Identifier: EUPL-1.2

"""Admin interfaces
----------------

This module defines the django Helmholtz AAI Admin interfaces, based upon the
interfaces from :mod:`django.contrib.auth.admin`.
"""


from copy import deepcopy

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from django_helmholtz_aai import models


@admin.register(models.HelmholtzUser)
class HelmholtzAAIUserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "eduperson_unique_id",
        "is_staff",
    )

    fieldsets = deepcopy(UserAdmin.fieldsets)

    fieldsets[1][1]["fields"] = fieldsets[1][1]["fields"] + (  # type: ignore[index, operator]
        "eduperson_unique_id",
        "userinfo",
    )


@admin.register(models.HelmholtzVirtualOrganization)
class HelmholtzVirtualOrganizationAdmin(GroupAdmin):
    list_display = ("name", "eduperson_entitlement", "users")

    search_fields = ["name", "eduperson_entitlement"]

    def users(self, obj: models.HelmholtzVirtualOrganization):
        return str(obj.user_set.count())
