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
from meh.ui import *
import os
import report
from gi.repository import Gtk

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

def find_glade_file(file):
    path = os.environ.get("GLADEPATH", "./:ui/:/tmp/updates/:/tmp/updates/ui/:/usr/share/python-meh/")
    for d in path.split(":"):
        fn = d + file
        if os.access(fn, os.R_OK):
            return fn
    raise RuntimeError, "Unable to find glade file %s" % file

class GraphicalIntf(AbstractIntf):
    def __init__(self, *args, **kwargs):
        AbstractIntf.__init__(self, *args, **kwargs)

    def enableNetwork(self, *args, **kwargs):
        """Should be provided by the inheriting class."""

        return False

    def exitWindow(self, title, message, *args, **kwargs):
        win = ExitWindow(title, message, *args, **kwargs)
        win.run()
        win.destroy()

    def mainExceptionWindow(self, text, exnFile, *args, **kwargs):
        win = MainExceptionWindow(text, exnFile, *args, **kwargs)
        return win

    def messageWindow(self, title, message, *args, **kwargs):
        win = MessageWindow(title, message, *args, **kwargs)
        win.run()
        win.destroy()

    def saveExceptionWindow(self, signature, *args, **kwargs):
        win = SaveExceptionWindow(signature)
        win.run()

class SaveExceptionWindow(AbstractSaveExceptionWindow):
    def __init__(self, signature, *args, **kwargs):
        self.signature = signature

    def run(self, *args, **kwargs):
        # Don't need to check the return value of report since it will
        # handle all the UI reporting for us.
        report.report_problem_in_memory(self.signature, report.LIBREPORT_WAIT)

class MainExceptionWindow(AbstractMainExceptionWindow):
    def __init__(self, shortTraceback=None, longTraceback=None, *args, **kwargs):
        AbstractMainExceptionWindow.__init__(self, shortTraceback, longTraceback,
                                             *args, **kwargs)

        builder = Gtk.Builder()
        glade_file = find_glade_file("exception-dialog.glade")
        builder.add_from_file(glade_file)
        builder.connect_signals(self)

        self._main_window = builder.get_object("exceptionWindow")

        self._traceback_buffer = builder.get_object("tracebackBuffer")

        self._traceback_buffer.set_text(longTraceback)
        self._response = MAIN_RESPONSE_QUIT

    @property
    def main_window(self):
        return self._main_window

    def destroy(self, *args, **kwargs):
        self._main_window.destroy()

    def run(self, *args, **kwargs):
        self._main_window.show_all()
        Gtk.main()
        self.destroy()
        return self._response

    def on_report_clicked(self, button):
        self._response = MAIN_RESPONSE_SAVE
        Gtk.main_quit()

    def on_quit_clicked(self, button):
        self._response = MAIN_RESPONSE_QUIT
        Gtk.main_quit()

    def on_debug_clicked(self, button):
        self._response = MAIN_RESPONSE_DEBUG
        Gtk.main_quit()

    def on_expander_activated(self, expander, *args):
        if not expander.get_expanded():
            self._main_window.resize(600, 400)
        else:
            #resize the window back to the default size when expander is
            #minimized
            self._main_window.resize(600, 1)

    def on_main_window_deleted(self, *args):
        self._response = MAIN_RESPONSE_NONE
        self.destroy()
        Gtk.main_quit()

class MessageWindow(AbstractMessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        AbstractMessageWindow.__init__(self, title, text, *args, **kwargs)
        self.dialog = Gtk.MessageDialog(buttons=Gtk.ButtonsType.OK,
                                        type=Gtk.MessageType.INFO,
                                        message_format=text)
        self.dialog.set_title(title)
        self.dialog.set_position(Gtk.WindowPosition.CENTER)

    def destroy(self, *args, **kwargs):
        self.dialog.destroy()

    def run(self, *args, **kwargs):
        self.dialog.show_all()
        self.rc = self.dialog.run()
        self.dialog.destroy()

class ExitWindow(MessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        self.dialog = Gtk.MessageDialog(buttons=Gtk.ButtonsType.NONE,
                                        type=Gtk.MessageType.INFO,
                                        message_format=text)
        self.dialog.set_title(title)
        self.dialog.add_button(_("_Exit"), 0)
        self.dialog.set_position(Gtk.WindowPosition.CENTER)
