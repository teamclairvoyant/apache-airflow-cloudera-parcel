#
# network.py - network configuration install data
#
# Copyright (C) 2008, 2009  Red Hat, Inc.
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s): David Cantrell <dcantrell@redhat.com>
#
import dbus

# This code was taken from anaconda, and slightly adapted to not rely
# on isys.
NM_SERVICE = "org.freedesktop.NetworkManager"
NM_MANAGER_PATH = "/org/freedesktop/NetworkManager"

NM_STATE_CONNECTED = 3

DBUS_PROPS_IFACE = "org.freedesktop.DBus.Properties"

def hasActiveNetDev():
    """Does the system have an enabled network interface?"""
    try:
        bus = dbus.SystemBus()
        nm = bus.get_object(NM_SERVICE, NM_MANAGER_PATH)
        props = dbus.Interface(nm, DBUS_PROPS_IFACE)
        state = props.Get(NM_SERVICE, "State")

        if int(state) == NM_STATE_CONNECTED:
            return True
        else:
            return False
    except:
        return False
