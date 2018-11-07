#
# __init__.py - Basic stuff for exception handling
#
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

from collections import namedtuple

# These constants represent the return values of buttons on the initial
# exception handling dialog - the dialog that first pops up when an
# exception is hit.
MAIN_RESPONSE_DEBUG = 0
MAIN_RESPONSE_SAVE = 1
MAIN_RESPONSE_QUIT = 2
MAIN_RESPONSE_NONE = 3

# And these constants represent the return values of buttons on the exception
# saving dialog.
SAVE_RESPONSE_OK = 0
SAVE_RESPONSE_CANCEL = 1

class ConfigError(Exception):
    """Exception class for the configuration related errors."""

    pass

class Config(object):
    """Hold configuration info useful throughout the exception handling
       classes.  This prevents having to pass a bunch of arguments to a
       bunch of different functions.  A Config instance must be created
       before creating an ExceptionHandler instance.
    """
    def __init__(self, *args, **kwargs):
        """Create a new Config instance.  Arguments may be passed in to
           set any of the configuration values.  Unknown arguments will
           be ignored.  Instance attributes:

           attrSkipList   -- A list of strings.  When handling a traceback,
                             any attributes found with the same name as an
                             element of this list will not be written to
                             the dump.  This is to prevent writing potentially
                             sensitive information like passwords.  The names
                             must be given without the leading name of the
                             object passed to handler.install().  For instance,
                             if handler.install() gets an Anaconda instance
                             with the name "anaconda" and you want to skip
                             anaconda.id.rootPassword, "id.rootPassword" should
                             be listed in attrSkipList.
           fileList       -- A list of files to find on the system and add
                             to the traceback dump.
           localSkipList  -- A list of strings.  When handling a traceback,
                             any local variables found with the same name as
                             an element of this list will not be written to
                             the dump.  This is subtely different from
                             attrSkipList.
           callbackDict   -- A dictionary having item names as keys and pairs
                             (function, attchmnt_only) as values.
                             @see register_callback
           programName    -- The name of the erroring program.
           programVersion -- The version number of the erroring program.
                             Both programName and programVersion are used
                             throughout the exception handler, so must be
                             set.
           programArch    -- The architecture of the erroring program.
        """
        self.attrSkipList = []
        self.fileList = []
        self.localSkipList = []
        self.callbackDict = dict()
        self.programName = None
        self.programVersion = None
        self.programArch = None

        # Override the defaults set above with whatever's passed in as an
        # argument.  Unknown arguments get thrown away.
        for (key, val) in kwargs.iteritems():
            if self.__dict__.has_key(key):
                self.__dict__[key] = val

        # Make sure required things are set.
        if not self.programName:
            raise ValueError("programName must be set.")

        if not self.programVersion:
            raise ValueError("programVersion must be set.")

    def register_callback(self, item_name, callback, attchmnt_only=False,
                          override=False):
        """
        Register new callback that will be called when data about the
        crash is collected. The returned value will be included as the
        'item_name' item.

        :param item_name: name of the item storing the value returned by the
                          'callback' function
        :type item_name: string
        :param callback: a function to be called
        :type callback: a function of type: () -> string
        :param attchmnt_only: whether the returned valued should be included only
                             as an attachment or also in the main '*-tb' file
                             (defaults to False)
        :type attchmnt_only: bool
        :param override: whether to override the previously registered callback
                         with the same item name or not (may raise exception)
        :type override: bool

        :raise ConfigError: if callback with the 'item_name' has already been
                            registered and 'override' is not set to True
        :return: None

        """

        if item_name not in self.callbackDict or override:
            self.callbackDict[item_name] = (callback, attchmnt_only)
        else:
            msg = "Callback with name '%s' already registered" % item_name
            raise ConfigError(msg)

# type, value and stack are items provided by Python for the exception handler
ExceptionInfo = namedtuple("ExceptionInfo", ["type", "value", "stack"])

# ExceptionInfo instance plus the object that should be dumped
DumpInfo = namedtuple("DumpInfo", ["exc_info", "object"])

# information about a package (as provided e.g. by rpm)
PackageInfo = namedtuple("PackageInfo", ["name", "version", "release", "epoch",
                                         "arch"])
