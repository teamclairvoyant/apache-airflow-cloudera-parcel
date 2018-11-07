# -*- coding: utf-8 -*-

# slip.dbus.proxies -- slightly augmented dbus proxy classes
#
# Copyright © 2005-2007 Collabora Ltd. <http://www.collabora.co.uk/>
# Copyright © 2009, 2011 Red Hat, Inc.
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
#
# Authors:
# Nils Philippsen <nils@redhat.com>

"""This module contains D-Bus proxy classes which implement the default
timeout of the augmented bus classes in slip.dbus.bus."""

import dbus.proxies

import constants


class _ProxyMethod(dbus.proxies._ProxyMethod):

    _connections_default_timeouts = {}

    @property
    def default_timeout(self):
        if self._connection not in self._connections_default_timeouts:
            dt = getattr(self._proxy._bus, "default_timeout", None)
            if dt is None:
                dt = constants.method_call_no_timeout
            self._connections_default_timeouts[self._connection] = dt
        return self._connections_default_timeouts[self._connection]

    def __call__(self, *args, **kwargs):
        if kwargs.get('timeout') is None:
            kwargs["timeout"] = self.default_timeout

        return dbus.proxies._ProxyMethod.__call__(self, *args, **kwargs)


class ProxyObject(dbus.proxies.ProxyObject):

    ProxyMethodClass = _ProxyMethod


