# -*- coding: utf-8 -*-

# slip.dbus.bus -- augmented dbus buses
#
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

"""This module contains functions which create monkey-patched/augmented D-Bus
buses."""

import dbus
import proxies
import constants

for name in ("Bus", "SystemBus", "SessionBus", "StarterBus"):
    exec \
"""def %(name)s(*args, **kwargs):
    busobj = dbus.%(name)s(*args, **kwargs)
    busobj.ProxyObjectClass = proxies.ProxyObject
    busobj.default_timeout = %(default_timeout)s
    return busobj
""" % {"name": name, "modname": __name__,
       "default_timeout": constants.method_call_no_timeout}
