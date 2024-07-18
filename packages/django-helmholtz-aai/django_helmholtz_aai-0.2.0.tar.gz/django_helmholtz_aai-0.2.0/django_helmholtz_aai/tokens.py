# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

"""Token generation algorithm
--------------------------

This module defines a generator for tokens to map two different users. We
mimic the behaviour of the token generator of :mod:`django.contrib.auth.tokens`
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class UserLinkingTokenGenerator:
    """
    Strategy object used to generate and check tokens for the password
    reset mechanism.
    """

    key_salt = "django_helmholtz_aai.tokens.UserLinkingTokenGenerator"
    algorithm: str = "sha256"
    _secret: Optional[str] = None
    _secret_fallbacks: Optional[List[Union[str, bytes]]] = None

    def _get_secret(self) -> str:
        return self._secret or settings.SECRET_KEY

    def _set_secret(self, secret: str):
        self._secret = secret

    secret = property(_get_secret, _set_secret)

    def _get_fallbacks(self) -> List[Union[str, bytes]]:
        if self._secret_fallbacks is None:
            return getattr(settings, "SECRET_KEY_FALLBACKS", [])
        return self._secret_fallbacks

    def _set_fallbacks(self, fallbacks: Optional[List[Union[str, bytes]]]):
        self._secret_fallbacks = fallbacks

    secret_fallbacks = property(_get_fallbacks, _set_fallbacks)

    def make_token(self, user: User, new_user: User):
        """
        Return a token that can be used once to do a password reset
        for the given user.
        """
        return self._make_token_with_timestamp(
            user,
            new_user,
            self._num_seconds(self._now()),
            self.secret,
        )

    def check_token(self, user: User, new_user: User, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and new_user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                self._make_token_with_timestamp(user, new_user, ts, secret),
                token,
            ):
                break
        else:
            return False

        # Check the timestamp is within limit.
        if (
            self._num_seconds(self._now()) - ts
        ) > settings.PASSWORD_RESET_TIMEOUT:
            return False

        return True

    def _make_token_with_timestamp(
        self, user: User, new_user: User, timestamp, secret
    ):
        # timestamp is number of seconds since 2001-1-1. Converted to base 36,
        # this gives us a 6 digit string until about 2069.
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, new_user, timestamp),
            secret=secret,
            algorithm=self.algorithm,
        ).hexdigest()[
            ::2
        ]  # Limit to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, user: User, new_user: User, timestamp):
        """
        Hash the user's primary key, email (if available), and some user state
        that's sure to change after a password reset to produce a token that is
        invalidated when it's used:
        1. The password field will change upon a password reset (even if the
           same password is chosen, due to password salting).
        2. The last_login field will usually be updated very shortly after
           a password reset.
        Failing those things, settings.PASSWORD_RESET_TIMEOUT eventually
        invalidates the token.

        Running this data through salted_hmac() prevents password cracking
        attempts using the reset token, provided the secret isn't compromised.
        """
        # Truncate microseconds so that tokens are consistent even if the
        # database doesn't support microseconds.
        login_timestamp = (
            ""
            if user.last_login is None
            else user.last_login.replace(microsecond=0, tzinfo=None)
        )
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, "") or ""
        new_email = getattr(new_user, email_field, "") or ""
        return (
            f"{user.pk}{login_timestamp}{timestamp}{email}"
            f"{new_user.pk}{new_email}"
        )

    def _num_seconds(self, dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())

    def _now(self):
        # Used for mocking in tests
        return datetime.now()


default_token_generator = UserLinkingTokenGenerator()
