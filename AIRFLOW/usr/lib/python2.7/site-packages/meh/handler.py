# Copyright (C) 2009  Red Hat, Inc.
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
# Author(s): Chris Lumens <clumens@redhat.com>
#
from meh import *
import bdb
import os
from network import hasActiveNetDev
import signal
import sys
import report
import traceback

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

class NoNetwork(Exception):
    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return "No network is available"

class ExceptionHandler(object):
    def __init__(self, confObj, intfClass, exnClass):
        """Create a new ExceptionHandler instance.  Subclasses of this one may
           be created, provided they are careful to provide all the methods
           this one does.  Instance attributes:

           conf     -- A filled in Config instance.  At least the programName
                       and programVersion are required.
           exnClass -- An instance of ExceptionDump or a subclass of it.  This
                       is required to know how to represent the Python
                       exception internally.
           intfClass-- An instance of AbstractIntf.  This is required to know
                       what UI classes to use.
        """
        self.conf = confObj
        self.exnClass = exnClass
        self.intf = intfClass

        self._exitcode = 10
        self._exn = None
        self.exnText = ""

    def _setExitCode(self, code):
        self._exitcode = code

    exitcode = property(lambda s: s._exitcode,
                        lambda s, v: s._setExitCode(v))

    def _setExn(self, e):
        self._exn = e

    exn = property(lambda s: s._exn,
                   lambda s, v: s._setExn(v))

    def handleException(self, dump_info):
        """This is the main exception handling entry point.  When Python
           gets an exception it doesn't know how to handle, this method will
           be called.  It then saves the traceback and displays the main
           dialog asking the user what to do next.  Once this method is
           called, there's no good way to go back to what you were doing
           before.

           All arguments are passed in from the handler created by calling
           self.install().  This method should not usually be overridden by
           a subclass.

           :type dump_info: an instance of the meh.DumpInfo class

        """

        responseHash = {MAIN_RESPONSE_QUIT: self.runQuit,
                        MAIN_RESPONSE_DEBUG: self.runDebug,
                        MAIN_RESPONSE_SAVE: self.runSave}

        # Quit if we got an exception when running pdb.
        if isinstance(dump_info.exc_info.value, bdb.BdbQuit):
            sys.exit(self.exitcode)

        # Restore original exception handler.
        sys.excepthook = sys.__excepthook__

        self.preWriteHook(dump_info)

        # Save the exception to the filesystem first.
        self.exn = self.exnClass(dump_info.exc_info, self.conf)
        (fobj, self.exnFile) = self.openFile()
        self.exnText = self.exn.traceback_and_object_dump(dump_info.object)
        fobj.write(self.exnText)
        fobj.close()

        self.postWriteHook(dump_info)

        # Run initial UI screen, asking whether to save/debug/quit.
        while True:
            win = self.intf.mainExceptionWindow(str(self.exn), self.exnText)
            if not win:
                self.runQuit(dump_info.exc_info)

            rc = win.run()
            win.destroy()

            try:
                responseHash[rc](dump_info.exc_info)
            except KeyError:
                # This happens if (for example) the user hits Escape instead
                # of pressing a button.
                continue

        win.destroy()

    def preWriteHook(self, dump_info):
        """Subclasses may supply a function with this name that will be
           called immediately before the traceback is written to disk in
           order to have any sort of special pre-write processing that needs
           to be done.

           :type dump_info: an instance of the meh.DumpInfo class
        """
        pass

    def postWriteHook(self, dump_info):
        """Subclasses may supply a function with this name that will be
           called immediately after the traceback is written to disk, but
           immediately before the UI is run.  This is to provide a place for
           any special handling to happen once there is a file on disk.

           :type dump_info: an instance of the meh.DumpInfo class
        """
        pass

    def install(self, obj):
        """Install ourselves as the top level exception handler with Python.
           If this method is not called after an ExceptionHandler instance is
           created, none of the rest of this code will ever be called.

           obj -- A Python object that may be dumped to a file when the
                  exception is saved.  This should be something like the top
                  level object in a program.
        """
        sys.excepthook = lambda ty, value, tb: \
            self.handleException(DumpInfo(ExceptionInfo(ty, value, tb), obj))

    def openFile(self):
        """Create a randomly named output file to write the exception dump to.
           This requires a programName be set in the Config instance.  The
           return value is a (file descriptor, path) pair.  The file must be
           closed by the caller when writing is done.  Subclasses should not
           override this method unless they know what they're doing.
        """
        import tempfile
        (fd, path) = tempfile.mkstemp("", "%s-tb-" % self.conf.programName, "/tmp")
        fo = os.fdopen(fd, "w")
        return (fo, path)

    ### Methods called by the primary exception handling dialog.

    def runQuit(self, exc_info):
        """This method is called when the "Exit" button is clicked.  It may
           be overridden by a subclass, but the basic behavior of eventually
           quitting should be preserved.

           :type exc_info: an instance of the meh.ExceptionInfo class
        """
        sys.exit(self.exitcode)

    def runDebug(self, exc_info):
        """This method is called when the "Debug" button is clicked.  It may
           be overridden by a subclass if specialized behavior is required to
           enter debug mode.

           :type exc_info: an instance of the meh.ExceptionInfo class
        """

        print
        print "Use 'continue' command to quit the debugger and get back to "\
              "the main menu"
        import pdb
        pdb.post_mortem(exc_info.stack)
        #no need to quit here, let's just get back to the main dialog

    def runSave(self, exc_info):
        """This method is called when the "Save" button is clicked.  It may
           be overridden by a subclass, but that's going to be a lot of work.

           :type exc_info: an instance of the meh.ExceptionInfo class
        """

        params = dict()
        params.update(self.exn.environment_info)
        pkg_info = params.pop("pkg_info", None)

        #if rpmdb queries fail (anaconda), use self.conf.* values
        if "component" not in params:
            params["component"] = self.conf.programName

        if pkg_info:
            params["pkg_name"] = pkg_info.name
            params["pkg_version"] = pkg_info.version
            params["pkg_release"] = pkg_info.release
            params["pkg_epoch"] = pkg_info.epoch
            params["pkg_arch"] = pkg_info.arch
            params["package"] = "%s-%s-%s.%s" % (pkg_info.name, pkg_info.version,
                                                 pkg_info.release, pkg_info.arch)
        else:
            params["pkg_name"] = self.conf.programName
            parts = self.conf.programVersion.rsplit("-", 1)
            if len(parts) == 2:
                version, release = parts
            else:
                version = parts[0]
                # not given, make something up
                release = "1"
            params["pkg_version"] = version
            params["pkg_release"] = release
            # we don't support specifying epoch in the config object and only
            # the anaconda which is not using epochs doesn't have the RPMdb to
            # query
            params["pkg_epoch"] = "0"
            params["pkg_arch"] = self.conf.programArch
            params["package"] = "{0.programName}-{0.programVersion}".format(
                                                                      self.conf)

        params["hashmarkername"] = self.conf.programName
        params["duphash"] = self.exn.hash
        params["reason"] = self.exn.desc
        params["description"] = "The following was filed automatically by %s:\n%s" \
                                    % (self.conf.programName, str(self.exn))

        tb_item_name = "%s-tb" % self.conf.programName
        params[tb_item_name] = self.exnText

        # save data generated by callbacks
        for (item_name, (callback, _anc)) in self.conf.callbackDict.iteritems():
            try:
                params[item_name] = callback()
            except Exception as exc:
                params[item_name] = "Caused error: %s" % exc

        for fpath in self.conf.fileList:
            try:
                with open(fpath, "r") as fobj:
                    # would be better to use the full path here, but libreport
                    # doesn't allow '/' characters in the item name
                    filename = os.path.basename(fpath)
                    if filename not in params:
                        params[filename] = fobj.read()
                    else:
                        params[filename+"_file"] = fobj.read()
            except:
                #skip files we cannot read
                continue

        # tell ABRT some more things it requires
        params["analyzer"] = "Python"
        params["backtrace"] = "".join(traceback.format_exception(exc_info.type,
                                                                 exc_info.value,
                                                                 exc_info.stack))

        signature = report.createPythonUnhandledExceptionSignature(**params)

        # We don't want to automatically quit here since the user may wish to
        # save somewhere else, debug, etc.
        self.intf.saveExceptionWindow(signature)
