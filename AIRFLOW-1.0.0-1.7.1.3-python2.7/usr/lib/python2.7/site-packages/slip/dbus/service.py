# -*- coding: utf-8 -*-

# slip.dbus.service -- convenience functions for using dbus-activated
# services
#
# Copyright © 2008, 2009 Red Hat, Inc.
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

"""This module contains convenience functions for using dbus-activated services."""

import dbus
import dbus.service

from slip._wrappers import _gobject as GObject

import polkit

__all__ = ["Object", "InterfaceType", "set_mainloop"]

__mainloop__ = None


def __glib_quit_cb__():
    global __mainloop__

    # assume a Glib mainloop

    __mainloop__.quit()


__quit_cb__ = __glib_quit_cb__


def set_mainloop(mainloop):
    global __mainloop__
    __mainloop__ = mainloop


def set_quit_cb(quit_cb):
    global __quit_cb__
    __quit_cb__ = quit_cb


def quit_cb():
    global __quit_cb__
    __quit_cb__()


SENDER_KEYWORD = "__slip_dbus_service_sender__"
ASYNC_CALLBACKS = ("__slip_dbus_service_reply_cb__",
                   "__slip_dbus_service_error_cb__")


def wrap_method(method):
    global SENDER_KEYWORD
    global ASYNC_CALLBACKS

    if method._dbus_sender_keyword is not None:
        sender_keyword = method._dbus_sender_keyword
        hide_sender_keyword = False
    else:
        sender_keyword = SENDER_KEYWORD
        hide_sender_keyword = True

    if method._dbus_async_callbacks is not None:
        async_callbacks = method._dbus_async_callbacks
        method_is_async = True
    else:
        async_callbacks = ASYNC_CALLBACKS
        method_is_async = False
    hide_async_callbacks = not method_is_async

    def wrapped_method(self, *p, **k):
        sender = k.get(sender_keyword)
        if sender is not None:
            # i.e. called over the bus, not locally
            reply_cb = k[async_callbacks[0]]
            error_cb = k[async_callbacks[1]]

            if hide_sender_keyword:
                del k[sender_keyword]

            if hide_async_callbacks:
                del k[async_callbacks[0]]
                del k[async_callbacks[1]]

            self.sender_seen(sender)

        action_id = getattr(method, "_slip_polkit_auth_required",
                            getattr(self, "default_polkit_auth_required",
                                    None))

        if sender is not None and action_id:

            def reply_handler(is_auth):
                if is_auth:
                    if method_is_async:

                        # k contains async callbacks, simply pass on reply_cb
                        # and error_cb

                        method(self, *p, **k)
                    else:

                        # execute the synchronous method ...

                        error = None
                        try:
                            result = method(self, *p, **k)
                        except Exception, e:
                            error = e

                        # ... and call the reply or error callback

                        if error:
                            error_cb(error)
                        else:

                            # reply_cb((None,)) != reply_cb()

                            if result is None:
                                reply_cb()
                            else:
                                reply_cb(result)
                else:
                    error_cb(polkit.NotAuthorizedException(action_id))
                self.timeout_restart()

            def error_handler(error):
                error_cb(error)
                self.timeout_restart()

            polkit.IsSystemBusNameAuthorizedAsync(sender, action_id,
                    reply_handler=reply_handler, error_handler=error_handler)
        else:
            # no action id, or run locally, no need to do anything fancy
            retval = method(self, *p, **k)
            self.timeout_restart()
            return retval

    for attr in filter(lambda x: x[:6] == "_dbus_", dir(method)):
        if attr == "_dbus_sender_keyword":
            wrapped_method._dbus_sender_keyword = sender_keyword
        elif attr == "_dbus_async_callbacks":
            wrapped_method._dbus_async_callbacks = async_callbacks
        else:
            setattr(wrapped_method, attr, getattr(method, attr))

        # delattr (method, attr)

    wrapped_method.func_name = method.func_name

    return wrapped_method


class InterfaceType(dbus.service.InterfaceType):

    def __new__(cls, name, bases, dct):

        for (attrname, attr) in dct.iteritems():
            if getattr(attr, "_dbus_is_method", False):
                dct[attrname] = wrap_method(attr)
        return super(InterfaceType, cls).__new__(cls, name, bases, dct)


class Object(dbus.service.Object):

    __metaclass__ = InterfaceType

    # timeout & persistence

    persistent = False
    default_duration = 5
    duration = default_duration
    current_source = None
    senders = set()
    connections_senders = {}
    connections_smobjs = {}

    # PolicyKit

    default_polkit_auth_required = None

    def __init__(self, conn=None, object_path=None, bus_name=None,
        persistent=None):

        super(Object, self).__init__(conn, object_path, bus_name)
        if persistent == None:
            self.persistent = self.__class__.persistent
        else:
            self.persistent = persistent

    def _timeout_cb(self):
        if not self.persistent and len(Object.senders) == 0:
            quit_cb()
            return False

        Object.current_source = None
        Object.duration = self.default_duration

        return False

    def _name_owner_changed(self, name, old_owner, new_owner):

        conn = self.connection

        if not new_owner and (old_owner, conn) in Object.senders:
            Object.senders.remove((old_owner, conn))
            Object.connections_senders[conn].remove(old_owner)

            if len(Object.connections_senders[conn]) == 0:
                Object.connections_smobjs[conn].remove()
                del Object.connections_senders[conn]
                del Object.connections_smobjs[conn]

            if not self.persistent and len(Object.senders) == 0 and \
                    Object.current_source == None:
                quit_cb()

    def timeout_restart(self, duration=None):
        if not duration:
            duration = self.__class__.default_duration
        if not Object.duration or duration > Object.duration:
            Object.duration = duration
        if not self.persistent or len(Object.senders) == 0:
            if Object.current_source:
                GObject.source_remove(Object.current_source)
            Object.current_source = \
                GObject.timeout_add(Object.duration * 1000,
                                    self._timeout_cb)

    def sender_seen(self, sender):
        if (sender, self.connection) not in Object.senders:
            Object.senders.add((sender, self.connection))
            if self.connection not in Object.connections_senders.keys():
                Object.connections_senders[self.connection] = set()
                Object.connections_smobjs[self.connection] = \
                    self.connection.add_signal_receiver(
                        handler_function=self._name_owner_changed,
                        signal_name="NameOwnerChanged",
                        dbus_interface="org.freedesktop.DBus")
            Object.connections_senders[self.connection].add(sender)


