# -*- coding: utf-8 -*-

# slip.dbus.polkit -- convenience decorators and functions for using PolicyKit
# with dbus services and clients
#
# Copyright © 2008, 2009, 2012, 2013 Red Hat, Inc.
# Authors: Nils Philippsen <nils@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""This module contains convenience decorators and functions for using
PolicyKit with dbus services and clients."""

import dbus
from decorator import decorator

from constants import method_call_no_timeout

__all__ = ["require_auth", "enable_proxy", "AUTHFAIL_DONTCATCH",
           "NotAuthorizedException", "AreAuthorizationsObtainable",
           "IsSystemBusNameAuthorizedAsync"]

def require_auth(polkit_auth):
    """Decorator for DBus service methods.

    Specify that a user needs a specific PolicyKit authorization `polkit_auth´
    to execute it."""

    def require_auth_decorator(method):
        assert hasattr(method, "_dbus_is_method")

        setattr(method, "_slip_polkit_auth_required", polkit_auth)
        return method

    return require_auth_decorator


AUTH_EXC_PREFIX = "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException."

class AUTHFAIL_DONTCATCH(object):
    pass

def enable_proxy(func=None, authfail_result=AUTHFAIL_DONTCATCH, authfail_exception=None, authfail_callback=None):
    """Decorator for DBus proxy methods.

    Let's you (optionally) specify either a result value or an exception type
    and a callback which is returned, thrown or called respectively if a
    PolicyKit authorization doesn't exist or can't be obtained in the DBus
    mechanism, i.e. an appropriate DBus exception is thrown.

    An exception constructor may and a callback must accept an `action_id´
    parameter which will be set to the id of the PolicyKit action for which
    authorization could not be obtained.

    Examples:

    1) Return `False´ in the event of an authorization problem, and call
    `error_handler´:

        def error_handler(action_id=None):
            print "Authorization problem:", action_id

        class MyProxy(object):
            @polkit.enable_proxy(authfail_result=False,
                                 authfail_callback=error_handler)
            def some_method(self, ...):
                ...

    2) Throw a `MyAuthError´ instance in the event of an authorization problem:

        class MyAuthError(Exception):
            def __init__(self, *args, **kwargs):
                action_id = kwargs.pop("action_id")
                super(MyAuthError, self).__init__(*args, **kwargs)
                self.action_id = action_id

        class MyProxy(object):
            @polkit.enable_proxy(authfail_exception=MyAuthError)
            def some_method(self, ...):
                ..."""

    assert(func is None or callable(func))

    assert(authfail_result in (None, AUTHFAIL_DONTCATCH) or authfail_exception is None)
    assert(authfail_callback is None or callable(authfail_callback))
    assert(authfail_exception is None or issubclass(authfail_exception, Exception))

    def _enable_proxy(func, *p, **k):

        try:
            return func(*p, **k)
        except dbus.DBusException, e:
            exc_name = e.get_dbus_name()

            if not exc_name.startswith(AUTH_EXC_PREFIX):
                raise

            action_id = exc_name[len(AUTH_EXC_PREFIX):]

            if authfail_callback is not None:
                authfail_callback(action_id=action_id)

            if authfail_exception is not None:
                try:
                    af_exc = authfail_exception(action_id=action_id)
                except:
                    af_exc = authfail_exception()
                raise af_exc

            if authfail_result is AUTHFAIL_DONTCATCH:
                raise

            return authfail_result

    if func is not None:
        return decorator(_enable_proxy, func)
    else:
        def decorate(func):
            return decorator(_enable_proxy, func)
        return decorate

class NotAuthorizedException(dbus.DBusException):

    """Exception which a DBus service method throws if an authorization
    required for executing it can't be obtained."""

    _dbus_error_name = \
        "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException"

    def __init__(self, action_id, *p, **k):

        self._dbus_error_name = self.__class__._dbus_error_name + "."\
             + action_id
        super(NotAuthorizedException, self).__init__(*p, **k)


class PolKit(object):

    """Convenience wrapper around polkit."""

    _dbus_name = 'org.freedesktop.PolicyKit1'
    _dbus_path = '/org/freedesktop/PolicyKit1/Authority'
    _dbus_interface = 'org.freedesktop.PolicyKit1.Authority'

    __interface = None
    __bus = None
    __bus_name = None
    __signal_receiver = None

    @classmethod
    def _on_name_owner_changed(cls, name, old_owner, new_owner):
        if name == cls._dbus_name and PolKit.__bus:
            PolKit.__bus.remove_signal_receiver(PolKit.__signal_receiver)
            PolKit.__bus = None
            PolKit.__signal_receiver = None
            PolKit.__interface = None

    @property
    def _bus(self):
        if not PolKit.__bus:
            PolKit.__bus = dbus.SystemBus()
            PolKit.__signal_receiver = PolKit.__bus.add_signal_receiver(
                    handler_function = self._on_name_owner_changed,
                    signal_name='NameOwnerChanged',
                    dbus_interface='org.freedesktop.DBus')
        return PolKit.__bus

    @property
    def _bus_name(self):
        if not PolKit.__bus_name:
            PolKit.__bus_name = self._bus.get_unique_name()
        return PolKit.__bus_name

    @property
    def _interface(self):
        if not PolKit.__interface:
            try:
                PolKit.__interface = dbus.Interface(self._bus.get_object(
                    self._dbus_name, self._dbus_path),
                    self._dbus_interface)
            except dbus.DBusException:
                pass
        return PolKit.__interface

    @property
    def _polkit_present(self):
        return bool(self._interface)

    def __dbus_system_bus_name_uid(self, system_bus_name):
        bus_object = self._bus.get_object('org.freedesktop.DBus',
                '/org/freedesktop/DBus')
        bus_interface = dbus.Interface(bus_object, 'org.freedesktop.DBus')
        try:
            uid = bus_interface.GetConnectionUnixUser(system_bus_name)
        except:
            uid = None
        return uid

    def __authorization_is_obtainable(self, authorization):
        if not self._polkit_present:
            return True

        (is_authorized, is_challenge, details) = \
            self._interface.CheckAuthorization(
                    ("system-bus-name", {"name": self._bus_name}),
                    authorization, {}, 0, "")

        return is_authorized or is_challenge

    def AreAuthorizationsObtainable(self, authorizations):
        if not self._polkit_present:
            return True

        if isinstance(authorizations, basestring):
            authorizations = [authorizations]

        obtainable = \
            reduce(lambda x, y: x and self.__authorization_is_obtainable(y),
                   authorizations, True)

        return obtainable

    def IsSystemBusNameAuthorizedAsync(self, system_bus_name, action_id,
        reply_handler, error_handler,
        challenge=True, details={}):

        if not self._polkit_present:
            return reply_handler(action_id is None or
                    self.__dbus_system_bus_name_uid(system_bus_name) == 0)

        flags = 0
        if challenge:
            flags |= 0x1

        def reply_cb(args):
            (is_authorized, is_challenge, details) = args
            reply_handler(is_authorized)

        self._interface.CheckAuthorization(("system-bus-name",
            {"name": system_bus_name}),
            action_id, details, flags, "",
            reply_handler=reply_cb,
            error_handler=error_handler,
            timeout=method_call_no_timeout)


__polkit = PolKit()


def AreAuthorizationsObtainable(authorizations):
    return __polkit.AreAuthorizationsObtainable(authorizations)


def IsSystemBusNameAuthorizedAsync(system_bus_name, action_id,
    reply_handler, error_handler, challenge=True, details={}):

    return __polkit.IsSystemBusNameAuthorizedAsync(system_bus_name, action_id,
        reply_handler, error_handler, challenge, details)
