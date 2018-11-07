# -*- coding: utf-8 -*-

# slip.dbus.constants -- constant values
#
# Copyright © 2011 Red Hat, Inc.
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

"""This module contains some constant values."""

# The maximum value of a 32bit signed integer is the magic value to indicate an
# infinite timeout for dbus. Unlike the C interface which deals with
# milliseconds as integers, the python interface uses seconds as floats for the
# timeout. Therefore we need to use the Python float (C double) value that
# gives 0x7FFFFFFF if multiplied by 1000.0 and cast into an integer.
#
# This calculation should be precise enough to get a value of 0x7FFFFFFF on the
# C side. If not, it will still amount to a very long time (not quite 25 days)
# which should be enough for all intents and purposes.
method_call_no_timeout = 0x7FFFFFFF / 1000.0
