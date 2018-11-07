#
# dump.py - general exception formatting and saving
#
# Copyright (C) 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2009  Red Hat, Inc.
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
# Author(s): Matt Wilson <msw@redhat.com>
#            Erik Troan <ewt@redhat.com>
#            Chris Lumens <clumens@redhat.com>
#
import copy
import inspect
from string import joinfields
import os
import traceback
import types
import sys
import codecs
from meh import PackageInfo
from meh.safe_string import SafeStr

class ExceptionDump(object):
    """This class represents a traceback and contains several useful methods
       for manipulating a traceback.  In general, clients should not have to
       use this class.  It is mainly for internal use.
    """
    def __init__(self, exc_info, config_obj):
        """Create a new ExceptionDump instance.  Instance attributes:

           :param exc_info: info about the exception provided by Python
           :type exc_info: an instance of the meh.ExceptionInfo class
           :param config_obj: configuration for python-meh
           :type config_obj: an instance of the meh.Config class
        """

        if inspect.istraceback(exc_info.stack):
            self.stack = inspect.getinnerframes(exc_info.stack)
        else:
            self.stack = exc_info.stack

        self.conf = config_obj
        self.type = exc_info.type
        self.value = exc_info.value

        self._dumpHash = {}

    @property
    def desc(self):
        # The description is a single line of text that should be used anywhere
        # the bug needs to quickly be summarized.  The most obvious example of
        # this is when saving to bugzilla.  We can populate the UI with this
        # string so the user doesn't need to come up with one.
        if self.type and self.value:
            return traceback.format_exception_only(self.type, self.value)[0].strip()
        else:
            return ""

    def _get_environment_info(self):
        """
        Returns dictionary containing these items for a bugreport header

        architecture
        cmdline
        component
        executable
        kernel
        package
        release
        other involved packages

        :rtype: dict (string -> string)
        """

        RELEASE_NAME_FILE = "/etc/system-release"

        class RPMinfoError(Exception):
            """Exception for errors in rpm queries"""
            pass

        def get_python_opts():
            """
            Returns python's command line options

            :return: list of python's command line options
            :rtype: list

            """

            flags_to_opts = {
                    "debug": "-d",
                    "py3k_warning": "-3",
                    "division_new": "-Qnew",
                    "division_warning": "-Q",
                    "inspect": "-i",
                    "interactive": "-i",
                    "optimize": "-O",
                    "dont_write_bytecode": "-B",
                    "no_user_site": "-s",
                    "no_site": "-S",
                    "ignore_environment": "-E",
                    "tabcheck": "-t",
                    "verbose": "-v",
                    "unicode": "-u",
                    "bytes_warning": "-b",
                    }

            ret = set()
            for flag in flags_to_opts.keys():
                if getattr(sys.flags, flag):
                    ret.add(flags_to_opts[flag])
            ret = list(ret)
            return ret

        def get_package_and_component(file_=sys.argv[0]):
            """
            Returns package and component names for file (by default for script itself).

            :param file_: filename
            :type file_: string
            :return: tuple containing package info and component name for the file
            :rtype: (PackageInfo, str)
            :raise RPMinfoError: if package and component for the file cannot be found

            """

            import rpm
            ts = rpm.TransactionSet()
            mi = ts.dbMatch("basenames", file_)
            try:
                header = mi.next()
            except StopIteration:
                raise RPMinfoError("Cannot get package and component for file "+
                        "{0}".format(file_))
            pkg_info = PackageInfo(header["name"], header["version"],
                                   header["release"], header["epoch"] or "0",
                                   header["arch"])

            # cuts the name from the NVR format: foo-blah-2.8.8-2.fc17.src.rpm
            name_end = len(header["sourcerpm"])
            try:
                name_end = header["sourcerpm"].rindex('-')
                name_end = header["sourcerpm"][:name_end].rindex('-')
            except ValueError as e:
                # expected exception
                pass

            component = header["sourcerpm"][:name_end]

            return (pkg_info, component)

        def get_release_version():
            """Returns release version (according to RELEASE_NAME_FILE)"""
            try:
                with open(RELEASE_NAME_FILE, "r") as file_:
                    return file_.readline().rstrip()
            except IOError:
                return "Cannot get release name."

        def get_other_packages(self):
            """
            Returns a set of additional packages whose files appear in
            traceback.

            :rtype: set

            """
            packages = set()
            if not self.stack:
                return packages

            for (frame, fn, lineno, func, ctx, idx) in self.stack:
                try:
                    pkg_info = get_package_and_component(fn)[0]
                    package = "{0.name}-{0.version}-{0.release}.{0.arch}".format(
                                                        pkg_info)
                    packages.add(package)
                except RPMinfoError:
                    continue

            try:
                pkg_info = get_package_and_component()[0]
                package = "{0.name}-{0.version}-{0.release}.{0.arch}".format(
                    pkg_info)
                packages.discard(package)
            except RPMinfoError:
                pass
            return packages

        def get_environment_variables():
            """
            Returns a list of strings containing defined environment
            variables and their values in the following format:

            VARIABLE=VALUE

            :rtype: list

            """

            ret = list()
            for (key, value) in os.environ.iteritems():
                ret.append("{0}={1}".format(key, value))

            return ret


        #--begining of the method _get_environment_info--
        try:
            pkg_info, component = get_package_and_component()
        except RPMinfoError as rpmierr:
            pkg_info = None
            component = None

        release_ver = get_release_version()
        other_packages = ", ".join(get_other_packages(self))

        ret = dict()
        ret["architecture"] = os.uname()[4]
        ret["cmdline"] = "{0} {1} {2}".format(sys.executable,
                    " ".join(get_python_opts()),
                    " ".join(sys.argv))
        if component:
            ret["component"] = component
        ret["executable"] = sys.argv[0]
        ret["kernel"] = os.uname()[2]
        if pkg_info:
            ret["pkg_info"] = pkg_info
        ret["release"] = get_release_version()
        if other_packages:
            ret["other involved packages"] = other_packages
        ret["environ"] = "\n".join(get_environment_variables())

        return ret

    @property
    def environment_info(self):
        return self._get_environment_info()

    def __str__(self):
        lst = self._format_stack()

        lst.insert(0, "%s %s exception report\n" % (self.conf.programName, self.conf.programVersion))
        lst.insert(1, "Traceback (most recent call last):\n")

        if self.type is not None and self.value is not None:
            lst.extend(traceback.format_exception_only(self.type, self.value))

        return joinfields(lst, "")

    def _format_stack(self):
        if not self.stack:
            return []

        frames = []
        for (frame, fn, lineno, func, ctx, idx) in self.stack:
            if type(ctx) == type([]):
                code = "".join(ctx)
            else:
                code = ctx

            frames.append((fn, lineno, func, code))

        return traceback.format_list(frames)

    # Create a string representation of a class.  This method will recursively
    # handle all attributes of the base given class.
    def _dumpClass(self, instance, level=0, parentkey="", skipList=[]):
        # This is horribly cheesy, and bound to require maintainence in the
        # future.  The problem is that anything subclassed from object fails
        # the types.InstanceType test we used to have which means those
        # objects never get dumped.  However, most everything basic in
        # python is derived from object so we can't just check for the super
        # class.  Any instances of the following types will just be printed
        # out, and everything else will be assumed to be something that
        # needs to be recursed on.
        def __isSimpleType(instance):
            return type(instance) in [types.BooleanType, types.ComplexType, types.FloatType,
                                      types.IntType, types.LongType, types.NoneType,
                                      types.StringType, types.UnicodeType] or \
                   not hasattr(instance, "__class__") or \
                   not hasattr(instance, "__dict__")

        ret = SafeStr()

        # protect from loops
        try:
            # Store the id(), not the instance name to protect against
            # instances that cannot be hashed.
            if not self._dumpHash.has_key(id(instance)):
                self._dumpHash[id(instance)] = None
            else:
                ret += "Already dumped (%s instance)\n" % instance.__class__.__name__
                return ret
        except TypeError:
            ret += "Cannot dump object\n"
            return ret

        if (instance.__class__.__dict__.has_key("__str__") or
            instance.__class__.__dict__.has_key("__repr__")):
            try:
                ret += "%s\n" % (instance,)
            except:
                ret += "\n"

            return ret

        ret += "%s instance, containing members:\n" %\
                (instance.__class__.__name__)
        pad = ' ' * ((level) * 2)

        for key, value in instance.__dict__.items():
            if key.startswith("_%s__" % instance.__class__.__name__):
                continue

            if parentkey != "":
                curkey = parentkey + "." + key
            else:
                curkey = key

            # Don't dump objects that are in our skip list, though ones that are
            # None are probably okay.
            if eval("instance.%s is not None" % key) and \
               eval("id(instance.%s)" % key) in skipList:
                ret += "%s%s: Skipped\n" % (pad, curkey)
                continue

            if type(value) == types.ListType:
                ret += "%s%s: [" % (pad, curkey)
                first = 1
                for item in value:
                    if not first:
                        ret += ", "
                    else:
                        first = 0

                    if __isSimpleType(item):
                        ret += "%s" % (item,)
                    else:
                        ret += self._dumpClass(item, level + 1, skipList=skipList)
                ret += "]\n"
            elif type(value) == types.DictType:
                ret += "%s%s: {" % (pad, curkey)
                first = 1
                for k, v in value.items():
                    if not first:
                        ret += ", "
                    else:
                        first = 0
                    if type(k) == types.StringType:
                        ret += "'%s': " % (k,)
                    else:
                        ret += "%s: " % (k,)

                    if __isSimpleType(v):
                        ret += "%s" % (v,)
                    else:
                        ret += self._dumpClass(v, level + 1, parentkey = curkey, skipList=skipList)
                ret += "}\n"
            elif __isSimpleType(value):
                ret += "%s%s: %s\n" % (pad, curkey, value)
            else:
                ret += "%s%s: " % (pad, curkey)
                ret += self._dumpClass(value, level + 1, parentkey=curkey, skipList=skipList)

        return ret

    def dump(self, obj):
        """Dump the local variables and all attributes of a given object.
           The lists of files and attrs to ignore are all taken from a
           Config object instance provided when the ExceptionDump class was
           created.

           obj -- Any Python object.  This object will have all its attributes
                  written out, except for those mentioned in the attrSkipList.
        """
        idSkipList = []
        ret = SafeStr()

        # We need to augment the environment eval() will run in with the
        # bindings that were local when the traceback happened so that the
        # idSkipList can be populated.  However since we're not allowed to
        # modify the results of locals(), we'll have to make a copy first.
        localVars = copy.copy(locals())
        if self.stack:
            localVars.update(self.stack[-1][0].f_locals)

        # Catch attributes that do not exist at the time we do the exception dump
        # and ignore them.
        for k in self.conf.attrSkipList:
            try:
                eval("idSkipList.append(id(obj.%s))" % k, None, localVars)
            except:
                pass

        # Write local variables to the given file descriptor, ignoring any of
        # the local skips.
        if self.stack:
            frame = self.stack[-1][0]
            ret += "\nLocal variables in innermost frame:\n"
            try:
                for (key, value) in frame.f_locals.items():
                    loweredKey = key.lower()
                    if len(filter(lambda s: loweredKey.find(s) != -1,
                                  self.conf.localSkipList)) > 0:
                        continue

                    ret += "%s: %s\n" % (key, value)
            except:
                pass

        # And now dump the object's attributes.
        try:
            ret += "\n\n"
            ret += self._dumpClass(obj, skipList=idSkipList)
        except:
            ret += "\nException occurred during state dump:\n"
            ret += traceback.format_exc(None)

        # Filter out item names and callbacks that should appear
        # only as attachments
        items_callbacks = ((name, cb) for (name, (cb, attchmnt_only))
                               in self.conf.callbackDict.iteritems()
                               if not attchmnt_only)

        # And now add data returned by the registered callbacks
        ret += "Registered callbacks:\n"
        for (item_name, callback) in items_callbacks:
            try:
                ret += "%s:\n%s\n" % (item_name, callback())
            except Exception as exc:
                ret += "%s: Caused error: %s\n" % (item_name, exc)

        # And finally, write a bunch of files into the dump too.
        for fname in self.conf.fileList:
            try:
                with codecs.open(fname, "r", "utf-8", "ignore") as fobj:
                    ret += "\n\n%s:\n" % (fname,)
                    for line in fobj:
                        ret += line.encode("utf-8")
            except IOError:
                pass
            except:
                ret += "\nException occurred during %s file copy:\n" % (fname,)
                ret += traceback.format_exc(None)

        return ret

    @property
    def hash(self):
        """Create a hash for this traceback object.  This is most suitable for
           searching bug filing systems for duplicates.  The hash is composed
           of the basename of each file in the stack, the method names, and
           the bit of code.  Line numbers and the actual exception message
           itself are left out.
        """
        import hashlib
        s = ""

        if self.stack:
            for (file, lineno, func, text) in [f[1:5] for f in self.stack]:
                if type(text) == type([]):
                    text = "".join(text)
                s += "%s %s %s\n" % (os.path.basename(file), func, text)
        else:
            s = "%s %s" % (self.type, self.value)

        return hashlib.sha256(s).hexdigest()

    def traceback_and_object_dump(self, obj):
        """
        Return the traceback and a text representation of an object.

        :param obj: Any Python object. This object will have all its attributes
                    written out, except for those mentioned in the attrSkipList.

        """

        ret = SafeStr(str(self))
        ret += self.dump(obj)

        return ret

class ReverseExceptionDump(ExceptionDump):
    """This class provides an alternate representation of an exception.  In
       this representation, the traceback is printed with the most recent call
       at the top of the stack, and the most generic call at the bottom.  Note
       that this order does not affect the hash at all.
    """
    def __str__(self):
        lst = self._format_stack()
        lst.reverse()

        lst.insert(0, "%s %s exception report\n" % (self.conf.programName, self.conf.programVersion))
        lst.insert(1, "Traceback (most recent call first):\n")

        if self.type is not None and self.value is not None:
            lst.extend(traceback.format_exception_only(self.type, self.value))

        return joinfields(lst, "")
