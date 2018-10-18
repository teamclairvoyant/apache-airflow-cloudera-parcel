#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes and functions to easily access DBus introspection data."""

from xml.etree.ElementTree import ElementTree
from StringIO import StringIO

class IElemMeta(type):
    """Metaclass for introspection elements.

    Sets elemname class member automatically from class name if not set
    explicitly. Registers classes for their element names."""

    elemnames_to_classes = {}

    @classmethod
    def clsname_to_elemname(cls, clsname):
        elemname = ""
        for c in clsname:
            c_lower = c.lower()
            if c_lower != c:
                if len(elemname):
                    elemname += "_"
            elemname += c_lower
        return elemname

    def __new__(cls, name, bases, dct):
        if name == "IElem":
            return type.__new__(cls, name, bases, dct)

        if 'elemname' not in dct:
            if not name.startswith("IElem"):
                raise TypeError("Class '%s' needs to set elemname (or be "
                        "called 'IElem...'))" % name)
            dct['elemname'] = IElemMeta.clsname_to_elemname(name[5:])

        elemname = dct['elemname']

        if elemname in IElemMeta.elemnames_to_classes:
            raise TypeError("Class '%s' tries to register duplicate elemname "
                    "'%s'" % (name, elemname))

        kls = type.__new__(cls, name, bases, dct)

        IElemMeta.elemnames_to_classes[elemname] = kls

        return kls


class IElem(object):
    """Base class for introspection elements."""

    __metaclass__ = IElemMeta

    def __new__(cls, elem, parent=None):
        kls = IElemMeta.elemnames_to_classes.get(elem.tag,
                IElemMeta.elemnames_to_classes[None])
        return super(IElem, cls).__new__(kls, elem, parent)

    def __init__(self, elem, parent=None):
        self.elem = elem
        self.parent = parent
        self.child_elements = [ IElem(c, parent=self) for c in elem ]

    def __str__(self):
        s = "%s %r" % (self.elemname if self.elemname else "unknown:%s" %
                self.elem.tag, self.attrib)
        for c in self.child_elements:
            for cc in str(c).split("\n"):
                s+="\n  %s" % (cc)
        return s

    @property
    def attrib(self):
        return self.elem.attrib


class IElemUnknown(IElem):
    """Catch-all for unknown introspection elements."""

    elemname = None


class IElemNameMixin(object):
    """Mixin for introspection elements with names."""

    @property
    def name(self):
        return self.attrib['name']


class IElemNode(IElem, IElemNameMixin):
    """Introspection node."""

    def __init__(self, elem, parent=None):
        super(IElemNode, self).__init__(elem, parent)

        self.child_nodes = [ c for c in self.child_elements if isinstance(c, IElemNode) ]


class IElemInterface(IElem):
    """Introspection interface."""


class IElemMethod(IElem):
    """Introspection interface method."""


class IElemArg(IElem):
    """Introspection method argument."""


class IElemSignal(IElem, IElemNameMixin):
    """Introspection interface signal."""


def introspect(string_or_file):
    tree = ElementTree()
    # assume string if read() method doesn't exist, works for string, unicode,
    # dbus.String
    if not hasattr(string_or_file, "read"):
        string_or_file = StringIO(string_or_file)
    xml_root = tree.parse(string_or_file)
    elem_root = IElem(xml_root)
    return elem_root
