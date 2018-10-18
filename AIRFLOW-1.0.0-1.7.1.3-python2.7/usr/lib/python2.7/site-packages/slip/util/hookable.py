# -*- coding: utf-8 -*-

#
# Copyright © 2008 Red Hat, Inc.
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

"""This module contains variants of certain base types which call registered
hooks on changes."""

__all__ = ["Hookable", "HookableSet"]


class HookableType(type):

    def __new__(cls, name, bases, dct):

        if dct.has_key("_hookable_change_methods"):
            try:
                base = dct["_hookable_base_class"]
            except KeyError:
                base = None
                for base_candidate in filter(lambda x: x != Hookable, bases):
                    if base:
                        raise TypeError("too many base classes: %s" %
                                 str(bases))
                    else:
                        base = base_candidate

            for methodname in dct["_hookable_change_methods"]:
                dct[methodname] = HookableType.wrap_method(base, methodname)

        return type.__new__(cls, name, bases, dct)

    @classmethod
    def wrap_method(cls, base, methodname):
        func = getattr(base, methodname)

        def methodwrapper(self, *p, **k):
            retval = func(self, *p, **k)
            self._run_hooks()
            return retval

        methodwrapper.func_name = methodname
        return methodwrapper


class _HookEntry(object):

    def __init__(self, hook, args, kwargs):

        self.__hook = hook
        self.__args = args
        self.__kwargs = kwargs

    def __cmp__(self, obj):
        return self.__hook == obj.__hook and self.__args == obj.__args and \
             self.__kwargs == obj.__kwargs

    def __hash__(self):
        return self.__hook.__hash__() ^ self.__args.__hash__() ^ \
             self.__kwargs.iteritems().__hash__()

    def run(self):
        self.__hook(*self.__args, **self.__kwargs)


class Hookable(object):

    """An object which calls registered hooks on changes."""

    __metaclass__ = HookableType

    @property
    def __hooks__(self, *p, **k):
        if not hasattr(self, "__real_hooks__"):
            self.__real_hooks__ = set()
        return self.__real_hooks__

    def _get_hooks_enabled(self):
        if not hasattr(self, "__hooks_enabled__"):
            self.__hooks_enabled__ = True
        return self.__hooks_enabled__

    def _set_hooks_enabled(self, enabled):
        self.__hooks_enabled__ = enabled

    hooks_enabled = property(_get_hooks_enabled, _set_hooks_enabled)

    def _get_hooks_frozen(self):
        if not hasattr(self, "__hooks_frozen__"):
            self.__hooks_frozen__ = False
        return self.__hooks_frozen__

    def _set_hooks_frozen(self, freeze):
        if freeze == self.hooks_frozen:
            return

        self.__hooks_frozen__ = freeze

        if freeze:
            self.__hooks_frozen_entries__ = set()
        else:
            for hookentry in self.__hooks_frozen_entries__:
                hookentry.run()
            del self.__hooks_frozen_entries__

    hooks_frozen = property(_get_hooks_frozen, _set_hooks_frozen)

    def freeze_hooks(self):
        self.hooks_frozen = True

    def thaw_hooks(self):
        self.hooks_frozen = False

    def add_hook(self, hook, *args, **kwargs):

        assert callable(hook)
        hookentry = _HookEntry(hook, args, kwargs)
        self.__hooks__.add(hookentry)

    def remove_hook(self, hook, *args, **kwargs):

        self.__hooks__.remove(_HookEntry(hook, args, kwargs))

    def _run_hooks(self):
        if self.hooks_enabled:
            if not self.hooks_frozen:
                for hookentry in self.__hooks__:
                    hookentry.run()
            else:
                self.__hooks_frozen_entries__.update(self.__hooks__)


class HookableSet(set, Hookable):

    """A set object which calls registered hooks on changes."""

    _hookable_change_methods = ("add", "clear", "difference_update",
        "discard", "intersection_update", "pop", "remove",
        "symmetric_difference_update", "update")

    def copy(self):
        obj = set.copy(self)
        obj.__real_hooks__ = set()
        return obj


