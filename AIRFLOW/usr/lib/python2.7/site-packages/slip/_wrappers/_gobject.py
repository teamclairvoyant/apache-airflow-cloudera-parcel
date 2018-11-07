# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
# Authors:
# Nils Philippsen <nils@redhat.com>
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

"""This module lets some other slip modules cooperate with either the gobject
or the gi.repository.GObject modules."""

import sys

__all__ = ['MainLoop', 'source_remove', 'timeout_add']

_self = sys.modules[__name__]

_mod = None

while _mod is None:
    if 'gobject' in sys.modules:
        _mod = sys.modules['gobject']
    elif 'gi.repository.GObject' in sys.modules:
        _mod = sys.modules['gi.repository.GObject']
    # if not yet imported, try to import gobject first, then
    # gi.repository.GObject ...
    if _mod is None:
        try:
            import gobject
        except ImportError:
            import gi.repository.GObject
    # ... then repeat.

for what in __all__:
    if what not in dir(_self):
        setattr(_self, what, getattr(_mod, what))
