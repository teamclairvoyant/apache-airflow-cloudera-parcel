# DI library for Python - core functionality
#
# Copyright (C) 2012  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# Red Hat Author(s): Martin Sivak <msivak@redhat.com>
#

"""This module implements dependency injection mechanisms."""

__author__ = "Martin Sivak <msivak@redhat.com>"
__all__ = ["DI_ENABLE", "di_enable", "inject", "usesclassinject"]

from functools import wraps, partial
from types import FunctionType

DI_ENABLE = True

def di_enable(method):
    """This decorator enables DI mechanisms in an environment
       where DI is disabled by default. Must be the outermost
       decorator.

       Can be used only on methods or simple functions.
    """
    @wraps(method)
    def caller(*args, **kwargs):
        """The replacement method doing the DI enablement.
        """
        global DI_ENABLE
        old = DI_ENABLE
        DI_ENABLE = True
        ret = method(*args, **kwargs)
        DI_ENABLE = old
        return ret

    return caller

class DiRegistry(object):
    """This class is the internal core of the DI engine.
       It records the injected objects, handles the execution
       and cleanup tasks associated with the DI mechanisms.
    """

    
    def __init__(self, obj):
        object.__setattr__(self, "_DiRegistry__obj", obj)
        object.__setattr__(self, "_DiRegistry__used_objects", {})
        for name in ["__name__", "__module__", "__doc__"]:
            object.__setattr__(self, name, getattr(obj, name, getattr(self, name)))
        self.__obj._di_ = self.__used_objects

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return partial(self.__call__, obj)
        
    def _inject_(self, *args, **kwargs):
        """Add registered injections to the instance of DiRegistry
        """
        self.__used_objects.update(kwargs)
        for used_object in args:
            if hasattr(used_object, "__name__"):
                self.__used_objects[used_object.__name__] = used_object
            elif isinstance(used_object, basestring):
                pass # it is already global, so this is just an annotation
            else:
                raise ValueError("%s is not a string or object with __name__" % used_object)
                
    def __call__(self, *args, **kwargs):
        if not issubclass(type(self.__obj), FunctionType):
            # call constructor or callable class
            # (which use @usesclassinject if needed)
            return self.__obj(*args, **kwargs)
        else:
            return di_call(self.__used_objects, self.__obj,
                           *args, **kwargs)
        
    def __getattr__(self, name):
        return getattr(self.__obj, name)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            object.__setattr__(self, name, value)
        else:
            setattr(self.__obj, name, value)

def func_globals(func):
    """Helper method that allows access to globals
       depending on the Python version.
    """
    if hasattr(func, "func_globals"):
        return func.func_globals # Python 2
    else:
        return func.__globals__ # Python 3

def di_call(di_dict, method, *args, **kwargs):
    """This method is the core of dependency injection framework.
       It modifies methods global namespace to define all the injected
       variables, executed the method under test and then restores
       the global namespace back.
       
       This variant is used on plain functions.
       
       The modified global namespace is discarded after the method finishes
       so all new global variables and changes to scalars will be lost.
    """
    # modify the globals
    new_globals = func_globals(method).copy()
    new_globals.update(di_dict)

    # create new func with modified globals
    new_method = FunctionType(method.func_code,
                              new_globals, method.func_name,
                              method.func_defaults, method.func_closure)
        
    # execute the method and return it's ret value
    return new_method(*args, **kwargs)

        
def inject(*args, **kwargs):
    """Decorator that registers all the injections we want to pass into
       a unit possibly under test.

       It can be used to decorate class, method or simple function, but
       if it is a decorated class, it's methods has to be decorated with
       @usesinject to use the DI mechanism.
    """
    def inject_decorate(obj):
        """The actual decorator generated by @inject."""
        if not DI_ENABLE:
            return obj
        
        if not isinstance(obj, DiRegistry):
            obj = DiRegistry(obj)
            
        obj._inject_(*args, **kwargs)
        return obj
    
    return inject_decorate
    
def usesclassinject(method):
    """This decorator marks a method inside of @inject decorated
       class as a method that should use the dependency injection
       mechanisms.
    """
    if not DI_ENABLE:
        return method    

    @wraps(method)
    def call(*args, **kwargs):
        """The replacement method acting as a proxy to @inject
           decorated class and it's DI mechanisms."""
        self = args[0]
        return di_call(self._di_, method, *args, **kwargs)

    return call

