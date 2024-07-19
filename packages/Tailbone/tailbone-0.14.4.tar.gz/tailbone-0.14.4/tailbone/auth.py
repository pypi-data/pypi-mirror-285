# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Authentication & Authorization
"""

import logging
import re

from rattail.util import prettify, NOTSET

from zope.interface import implementer
from pyramid.authentication import SessionAuthenticationHelper
from pyramid.request import RequestLocalCache
from pyramid.security import remember, forget

from tailbone.db import Session


log = logging.getLogger(__name__)


def login_user(request, user, timeout=NOTSET):
    """
    Perform the steps necessary to login the given user.  Note that this
    returns a ``headers`` dict which you should pass to the redirect.
    """
    config = request.rattail_config
    app = config.get_app()
    user.record_event(app.enum.USER_EVENT_LOGIN)
    headers = remember(request, user.uuid)
    if timeout is NOTSET:
        timeout = session_timeout_for_user(config, user)
    log.debug("setting session timeout for '{}' to {}".format(user.username, timeout))
    set_session_timeout(request, timeout)
    return headers


def logout_user(request):
    """
    Perform the logout action for the given request.  Note that this returns a
    ``headers`` dict which you should pass to the redirect.
    """
    app = request.rattail_config.get_app()
    user = request.user
    if user:
        user.record_event(app.enum.USER_EVENT_LOGOUT)
    request.session.delete()
    request.session.invalidate()
    headers = forget(request)
    return headers


def session_timeout_for_user(config, user):
    """
    Returns the "max" session timeout for the user, according to roles
    """
    app = config.get_app()
    auth = app.get_auth_handler()

    authenticated = auth.get_role_authenticated(Session())
    roles = user.roles + [authenticated]
    timeouts = [role.session_timeout for role in roles
                if role.session_timeout is not None]

    if timeouts and 0 not in timeouts:
        return max(timeouts)


def set_session_timeout(request, timeout):
    """
    Set the server-side session timeout to the given value.
    """
    request.session['_timeout'] = timeout or None


class TailboneSecurityPolicy:

    def __init__(self, api_mode=False):
        self.api_mode = api_mode
        self.session_helper = SessionAuthenticationHelper()
        self.identity_cache = RequestLocalCache(self.load_identity)

    def load_identity(self, request):
        config = request.registry.settings.get('rattail_config')
        app = config.get_app()
        user = None

        if self.api_mode:

            # determine/load user from header token if present
            credentials = request.headers.get('Authorization')
            if credentials:
                match = re.match(r'^Bearer (\S+)$', credentials)
                if match:
                    token = match.group(1)
                    auth = app.get_auth_handler()
                    user = auth.authenticate_user_token(Session(), token)

        if not user:

            # fetch user uuid from current session
            uuid = self.session_helper.authenticated_userid(request)
            if not uuid:
                return

            # fetch user object from db
            model = app.model
            user = Session.get(model.User, uuid)
            if not user:
                return

        # this user is responsible for data changes in current request
        Session().set_continuum_user(user)
        return user

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        user = self.identity(request)
        if user is not None:
            return user.uuid

    def remember(self, request, userid, **kw):
        return self.session_helper.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.session_helper.forget(request, **kw)

    def permits(self, request, context, permission):
        # nb. root user can do anything
        if request.is_root:
            return True

        config = request.registry.settings.get('rattail_config')
        app = config.get_app()
        auth = app.get_auth_handler()

        user = self.identity(request)
        return auth.has_permission(Session(), user, permission)


def add_permission_group(config, key, label=None, overwrite=True):
    """
    Add a permission group to the app configuration.
    """
    def action():
        perms = config.get_settings().get('tailbone_permissions', {})
        if key not in perms or overwrite:
            group = perms.setdefault(key, {'key': key})
            group['label'] = label or prettify(key)
        config.add_settings({'tailbone_permissions': perms})
    config.action(None, action)


def add_permission(config, groupkey, key, label=None):
    """
    Add a permission to the app configuration.
    """
    def action():
        perms = config.get_settings().get('tailbone_permissions', {})
        group = perms.setdefault(groupkey, {'key': groupkey})
        group.setdefault('label', prettify(groupkey))
        perm = group.setdefault('perms', {}).setdefault(key, {'key': key})
        perm['label'] = label or prettify(key)
        config.add_settings({'tailbone_permissions': perms})
    config.action(None, action)
