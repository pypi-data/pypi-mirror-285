"""Signals
-------

This module defines the signals that are fired by the views in
:mod:`django_helmholtz_aai.views` module.
"""

# Copyright (C) 2022 Helmholtz-Zentrum Hereon
# SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: EUPL-1.2

from django.dispatch import Signal

#: Signal that is fired when a user has been created via the Helmholtz AAI
#:
#: This signal is called by the
#: :class:`~django_helmholtz_aai.views.HelmholtzAuthentificationView` when a new
#: user has been created. Subscribers to this signal can accept the following
#: parameters.
#:
#: .. signal:: aai_user_created
#:
#: Parameters
#: ----------
#: sender: Type[django_helmholtz_aai.models.HelmholtzUser]
#:     The type who sent the signal (implemented for reasons of convention)
#: user: django_helmholtz_aai.models.HelmholtzUser
#:     The new user that has been created
#: request: Request
#:     The request holding the session of the user.
#: userinfo: Dict[str, Any]
#:     The userinfo as obtained from the Helmholtz AAI
#:
#: See Also
#: --------
#: django_helmholtz_aai.views.HelmholtzAuthentificationView.create_user
aai_user_created = Signal()


#: Signal that is fired when a user logs in via the Helmholtz AAI
#:
#: This signal is called by the
#: :class:`~django_helmholtz_aai.views.HelmholtzAuthentificationView` when a
#: user logged in via the Helmholtz AAI. Subscribers to this signal can accept
#: the following parameters.
#:
#: .. signal:: aai_user_logged_in
#:
#: Parameters
#: ----------
#: sender: Type[django_helmholtz_aai.models.HelmholtzUser]
#:     The type who sent the signal (implemented for reasons of convention)
#: user: django_helmholtz_aai.models.HelmholtzUser
#:     The user who just logged in
#: request: Request
#:     The request holding the session of the user.
#: userinfo: Dict[str, Any]
#:     The userinfo as obtained from the Helmholtz AAI
#:
#: See Also
#: --------
#: django_helmholtz_aai.login
#: django_helmholtz_aai.views.HelmholtzAuthentificationView.login_user
aai_user_logged_in = Signal()


#: Signal that is fired when a user receives an update via the Helmholtz AAI
#:
#: This signal is called by the
#: :class:`~django_helmholtz_aai.views.HelmholtzAuthentificationView` when a
#: user who does already have an account gets updated, e.g. because the email
#: of the ``preferred_username`` changed in the Helmholtz AAI. Subscribers to
#: this signal can accept the following parameters.
#:
#: .. signal:: aai_user_updated
#:
#: Parameters
#: ----------
#: sender: Type[django_helmholtz_aai.models.HelmholtzUser]
#:     The type who sent the signal (implemented for reasons of convention)
#: user: django_helmholtz_aai.models.HelmholtzUser
#:     The user that is supposed to be updated
#: request: Request
#:     The request holding the session of the user.
#: userinfo: Dict[str, Any]
#:     The userinfo as obtained from the Helmholtz AAI
#:
#: See Also
#: --------
#: django_helmholtz_aai.views.HelmholtzAuthentificationView.update_user
aai_user_updated = Signal()


#: Signal that is fired if a new Virtual Organization has been created
#:
#: This signal is called by the
#: :class:`~django_helmholtz_aai.views.HelmholtzAuthentificationView` when a
#: new virtual organization has been created from the Helmholtz AAI because a
#: of this VO registered on the website. Subscribers to
#: this signal can accept the following parameters.
#:
#: .. signal:: aai_vo_created
#:
#: Parameters
#: ----------
#: sender: Type[django_helmholtz_aai.models.HelmholtzUser]
#:     The type who sent the signal (implemented for reasons of convention)
#: user: django_helmholtz_aai.models.HelmholtzUser
#:     The user that is about to become a member of the new VO
#: vo: django_helmholtz_aai.models.HelmholtzVirtualOrganization
#:     The VO that has just been created
#: request: Request
#:     The request holding the session of the user.
#: userinfo: Dict[str, Any]
#:     The userinfo as obtained from the Helmholtz AAI
#: to_update: Dict[str, Any]
#:     A mapping from field name to value for the fields that have changed
#:     during the update.
#:
#: See Also
#: --------
#: django_helmholtz_aai.views.HelmholtzAuthentificationView.synchronize_vos
aai_vo_created = Signal()


#: Signal that is fired if a Helmholtz AAI user enteres a VO
#:
#: This signal is called by the
#: :class:`~django_helmholtz_aai.views.HelmholtzAuthentificationView` when a
#: user enters a virtual organization as the user is a member in the Helmholtz
#: AAI. Subscribers to this signal can accept the following parameters.
#:
#: .. signal:: aai_vo_entered
#:
#: Parameters
#: ----------
#: sender: Type[django_helmholtz_aai.models.HelmholtzUser]
#:     The type who sent the signal (implemented for reasons of convention)
#: user: django_helmholtz_aai.models.HelmholtzUser
#:     The user that entered the VO.
#: vo: django_helmholtz_aai.models.HelmholtzVirtualOrganization
#:     The VO that the user has just entered
#: request: Request
#:     The request holding the session of the user.
#: userinfo: Dict[str, Any]
#:     The userinfo as obtained from the Helmholtz AAI
#:
#: See Also
#: --------
#: django_helmholtz_aai.views.HelmholtzAuthentificationView.synchronize_vos
aai_vo_entered = Signal()


#: Signal that is fired if a Helmholtz AAI user left a VO
#:
#: This signal is called by the
#: :class:`~django_helmholtz_aai.views.HelmholtzAuthentificationView` when a
#: user leaves a virtual organization as the user is not anymore a member in
#: the Helmholtz AAI. Subscribers to this signal can accept the following
#: parameters.
#:
#: .. signal:: aai_vo_left
#:
#: Parameters
#: ----------
#: sender: Type[django_helmholtz_aai.models.HelmholtzUser]
#:     The type who sent the signal (implemented for reasons of convention)
#: user: django_helmholtz_aai.models.HelmholtzUser
#:     The user that entered the VO.
#: vo: django_helmholtz_aai.models.HelmholtzVirtualOrganization
#:     The VO that the user has just entered
#: request: Request
#:     The request holding the session of the user.
#: userinfo: Dict[str, Any]
#:     The userinfo as obtained from the Helmholtz AAI
#:
#: See Also
#: --------
#: django_helmholtz_aai.views.HelmholtzAuthentificationView.synchronize_vos
aai_vo_left = Signal()


#: Signal that is fired when a user does not have the permission to login
#:
#: This signal is called by the ``HelmholtzAuthentificationView`` when a
#: user is not allowed to login.
#:
#: One example usage of this signal might be to display the message to the
#: user::
#:
#:     from django.utils.safestring import mark_safe
#:
#:     @receiver(signals.login_denied)
#:     def add_reason_to_message(reason: str, msg: str, request, **kwargs):
#:         messages.error(request, mark_safe(msg))
#:
#: .. signal:: login_denied
#:
#: Parameters
#: ----------
#: sender: Type[django_helmholtz_aai.models.HelmholtzUser]
#:     The type who sent the signal (implemented for reasons of convention)
#: request: Request
#:     The request holding the session of the user.
#: userinfo: Dict[str, Any]
#:     The userinfo as obtained from the Helmholtz AAI
#: reason: str
#:     The reason identifier why the user is not allowed to login
#: msg: str
#:     The verbose reason why the user is not allowed to login.
login_denied = Signal()
