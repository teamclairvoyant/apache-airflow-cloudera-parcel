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

class AbstractIntf(object):
    """The base class for Interfaces.  This is an abstract class.  It
       provides methods that create and run various kinds of windows.
       We provide a basic level of graphical and text oriented interfaces
       here, but it should be possible for things like anaconda to supply
       their own much more complicated ones with little effort.
    """
    def __init__(self, *args, **kwargs):
        """Create a new AbstractInterface instance.  This method need not
           be overridden by subclasses.
        """
        pass

    def enableNetwork(self, *args, **kwargs):
        """Display and run a dialog that brings up the network, if it is
           currently disabled.  This method must be provided by all subclasses,
           and should return False if unsuccessful.
        """
        raise NotImplementedError

    def exitWindow(self, title, message, *args, **kwargs):
        """Display and run a dialog that displays a message with the proper
           buttons and images for quitting afterwards.  This method must be
           provided by all subclasses.

           title   -- The window's title.
           message -- The window's text.
        """
        raise NotImplementedError

    def mainExceptionWindow(self, text, exnFile, *args, **kwargs):
        """Create and return an instance of the initial execption handling
           dialog.  This method must be provided by all subclasses.

           text    -- The short traceback (usually, just the stack trace).
           exnFile -- A file containing the output of ExceptionDump.write().
        """
        raise NotImplementedError

    def messageWindow(self, title, message, *args, **kwargs):
        """Display a generic informational message.  This can be an error,
           status update, and so forth.  It must be provided by all subclasses.

           title   -- The window's title.
           message -- The window's text.
        """
        raise NotImplementedError

    def saveExceptionWindow(self, exnFile, *args, **kwargs):
        """Create and return an instance of the exception saving dialog.  This
           method must be provided by all subclasses.
        """
        raise NotImplementedError

class AbstractMainExceptionWindow(object):
    """This abstract class describes the basic level of support required of
       any interface that supplies a main exception window.  The main exception
       window is the initial dialog displayed by the exception handler that
       provides the debug/save/quit options.
    """
    def __init__(self, shortTraceback=None, longTraceback=None, *args, **kwargs):
        """Create a new MainExceptionWindow instance.  This must handle
           creating the dialog and populating it with widgets, but must not
           run the dialog.  A self.dialog attribute should be created that
           refers to the dialog itself.

           shortTraceback    -- The short traceback (usually, just the stack
                                trace).
           longTraceback     -- The long traceback (full traceback and the main
                                object dump).
        """
        pass

    def destroy(self, *args, **kwargs):
        """Destroy the current dialog.  This method must be provided by all
           subclasses.
        """
        raise NotImplementedError

    def run(self, *args, **kwargs):
        """Run the window and set a return value.  This method does everything
           after the interface has been set up, but does not destroy it.  This
           method must be provided by all subclasses.
        """
        raise NotImplementedError

class AbstractExitWindow(object):
    """This abstract class describes the basic level of support required of
       a basic message dialog that should be displayed before the program
       exits.  All interfaces must provide this class.
    """
    def __init__(self, title, text, *args, **kwargs):
        """Create a new ExitWindow instance.  This must handle creating the
           dialog and putting the text into it, but must not run the dialog.
           This method must be provided by all subclasses.

           title -- The window's title.
           text  -- The window's text.
        """
        pass

    def destroy(self, *args, **kwargs):
        """Destroy the current dialog.  This method must be provided by all
           subclasses.
        """
        raise NotImplementedError

    def run(self, *args, **kwargs):
        """Run the window and set a return value.  This method does everything
           after the interface has been set up but does not destroy it.  This
           method must be provided by all subclasses.
        """
        raise NotImplementedError

class AbstractMessageWindow(object):
    """This abstract class describes the basic level of support required of
       a basic message dialog.  All interfaces must provide this class.
    """
    def __init__(self, title, text, *args, **kwargs):
        """Create a new MessageWindow instance.  This must handle creating the
           dialog and putting the text into it, but must not run the dialog.
           This method must be provided by all subclasses.

           title -- The window's title.
           text  -- The window's text.
        """
        pass

    def destroy(self, *args, **kwargs):
        """Destroy the current dialog.  This method must be provided by all
           subclasses.
        """
        raise NotImplementedError

    def run(self, *args, **kwargs):
        """Run the window and set a return value.  This method does everything
           after the interface has been set up but does not destroy it.  This
           method must be provided by all subclasses.
        """
        raise NotImplementedError

class AbstractSaveExceptionWindow(object):
    """This abstract class describes the basic level of support required of
       any interface that supplies an exception saving window.  The exception
       saving window is the dialog displayed if the user clicks "save" on the
       initial dialog, and presents multiple options for how the traceback
       should be saved.
    """
    def __init__(self, *args, **kwargs):
        """Create a new SaveExceptionWindow instance.  This must handle
           creating the dialog and populating it with widgets, but must not
           run the dialog.  A self.dialog attribute should be created that
           refers to the dialog itself.
        """
        pass

    def run(self, *args, **kwargs):
        """Run the window and set a return value.  This method does everything
           after the interface has been set up but does not destroy it.  This
           method must be provided by all subclasses.
        """
        raise NotImplementedError
