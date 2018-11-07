# Tests for the dependency injection core
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

from .core import *
import unittest

def method_to_inject():
    pass

class BareFuncEnableTestCase(unittest.TestCase):
    @inject(injected_func = str.lower)
    def method(self, arg):
        return injected_func(arg)
    
class BareFuncTestCase(unittest.TestCase):
    @inject(injected_func = str.lower)
    def method(self, arg):
        return injected_func(arg)

    @inject(injected_func = method)
    def method2(self, arg):
        return injected_func(self, arg)
    
    def test_bare_inject(self):
        """Tests the injection to plain methods."""
        self.assertEqual("a", self.method("A"))

    def test_double_inject(self):
        """Tests the injection to two plain methods."""
        self.assertEqual("a", self.method2("A"))

    def test_inject_global_tainting(self):
        """Tests whether the global namespace is clean
           after the injection is done."""
        global injected_func
        injected_func = None
        self.method("A")
        self.assertEqual(None, injected_func)
        
    
@inject(injected_func = str.lower)
class Test(object):
    """Test fixture for class injection."""
    @usesclassinject
    def method(self, arg):
        return injected_func(arg)

    
@inject(injected_func = str.lower)
class TestInit(object):
    """Test fixture for injection to __init__."""
    @usesclassinject
    def __init__(self, arg):
        self.value = injected_func(arg)


@inject(injected_func = str.lower)
class TestCallable(object):
    """Test fixture for callable classes."""
    @usesclassinject
    def __call__(self, arg):
        return injected_func(arg)

class TestCallableSingle(object):
    """Test fixture for callable classes with
       simple method injection."""
    @inject(injected_func = str.lower)
    def __call__(self, arg):
        return injected_func(arg)
    
class ClassDITestCase(unittest.TestCase):
    
    def test_class_inject(self):
        """Test injection to instance method."""
        obj = Test()
        self.assertEqual("a", obj.method("A"))

    def test_named_register(self):
        """Test injection to instance method."""
        Test._inject_(method_to_inject)

    def test_class_init_inject(self):
        """Test injection to class constructor."""
        obj = TestInit("A")
        self.assertEqual("a", obj.value)

    def test_callable_class(self):
        """Test class injection to callable class."""
        obj = TestCallable()
        self.assertEqual("a", obj("A"))
        
    def test_callable_class_single(self):
        """Test method injection to callable class."""
        obj = TestCallableSingle()
        self.assertEqual("a", obj("A"))
        
if __name__ == "__main__":
    unittest.main()
