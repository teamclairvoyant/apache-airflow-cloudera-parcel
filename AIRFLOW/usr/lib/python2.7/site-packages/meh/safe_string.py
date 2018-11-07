#
# Copyright (C) 2013  Red Hat, Inc.
# All rights reserved.
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
# Author: Vratislav Podzimek <vpodzime@redhat.com>
#
#

"""
This module provides a SafeStr class.

@see: SafeStr

"""

class SafeStr(str):
    """
    String class that has a modified __add__ method so that ascii strings,
    binary data represented as a byte string and unicode objects can be
    safely appended to it (not causing traceback). BINARY DATA IS OMITTED.

    """

    def __add__(self, other):
        if not (isinstance(other, str) or isinstance(other, unicode)):
            if hasattr(other, "__str__"):
                other = other.__str__()
            else:
                other = "OMITTED OBJECT WITHOUT __str__ METHOD"

        if isinstance(other, unicode):
            ret = SafeStr(str.__add__(self, other.encode("utf-8")))
        else:
            try:
                # try to decode which doesn't cause traceback for utf-8 encoded
                # non-ascii string and ascii string
                other.decode("utf-8")
                ret = SafeStr(str.__add__(self, other))
            except UnicodeDecodeError:
                # binary data
                ret = SafeStr(str.__add__(self, "OMITTED BINARY DATA"))

        return ret
