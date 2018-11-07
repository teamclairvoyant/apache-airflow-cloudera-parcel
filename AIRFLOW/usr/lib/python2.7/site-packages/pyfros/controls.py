## Copyright (C) 2013 ABRT team <abrt-devel-list@redhat.com>
## Copyright (C) 2013 Red Hat, Inc.

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Suite 500, Boston, MA  02110-1335  USA

# pylint has troubles importing from gi.repository because
# it uses introspection
# pylint: disable=E0611
#from gi.repository import GLib
from gi.repository import Gtk
# pylint: disable=F0401
from gi.repository.Gtk import SizeGroupMode
from gi.repository import Gdk

from pyfros.i18n import _
from pyfros.froslogging import info

class Controls(Gtk.Window):
    #  selected plugin
    controller = None

    def _update_progressbar(self, percent):
        self.progress.set_visible(True)  # don't check, just make sure it's visible
        self.progress.set_fraction(percent / 100)  # progressbar uses promiles
        # xgettext:no-c-format
        self.progress.set_text("Encoding: {0!s}% complete".format(percent))

    def _area_selected(self, result):
        if result is True:
            self.rec_button.set_sensitive(True)

    def __init__(self, controller):
        Gtk.Window.__init__(self)
        self.controller = controller
        self.controller.SetProgressUpdate(self._update_progressbar)
        buttons_size_group = Gtk.SizeGroup(SizeGroupMode.BOTH)
        main_vbox = Gtk.VBox()
        main_hbox = Gtk.HBox()
        # pylint: disable=E1101
        self.add(main_vbox)
        # pylint: disable=E1101
        self.set_decorated(False)

        # move away from the UI!
        self.wroot = Gdk.get_default_root_window()
        self.wwidth = self.wroot.get_width()
        self.wheight = self.wroot.get_height()

        #progress bar
        self.progress = Gtk.ProgressBar()
        self.progress.set_no_show_all(True)

        #stop button
        self.stop_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_STOP)
        self.stop_button.connect("clicked", self._stop_recording)
        self.stop_button.set_sensitive(False)
        buttons_size_group.add_widget(self.stop_button)
        main_hbox.pack_start(self.stop_button, False, False, 0)

        #start button
        self.rec_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_RECORD)
        self.rec_button.connect("clicked", self._start_recording)
        # have to select window first
        self.rec_button.set_sensitive(False)
        buttons_size_group.add_widget(self.rec_button)
        main_hbox.pack_start(self.rec_button, False, False, 0)

        # select button
        select_button = Gtk.Button(_("Select window"))
        select_button.connect("clicked", self.controller.SelectArea, self._area_selected)
        buttons_size_group.add_widget(select_button)
        main_hbox.pack_start(select_button, False, False, 0)

        # close button
        close_button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
        close_button.connect("clicked", Gtk.main_quit)
        buttons_size_group.add_widget(close_button)
        main_hbox.pack_start(close_button, False, False, 0)

        main_vbox.pack_start(main_hbox, True, True, 0)
        main_vbox.pack_start(self.progress, True, True, 0)

        self.connect("destroy", Gtk.main_quit)

    def _stop_recording(self, button):
        self.controller.StopScreencast(Gtk.main_quit)
        button.set_sensitive(False)
        self.rec_button.set_sensitive(True)

    def _start_recording(self, button):
        info("start recording")
        res = self.controller.Screencast()
        if res.success:
            info("Capturing screencast to {0}".format(res.filename))
            button.set_sensitive(False)
            self.stop_button.set_sensitive(True)

    def show_all(self, *args, **kwargs):
        # pylint: disable=E1101
        super(Controls, self).show_all(*args, **kwargs)
        # pylint: disable=E1101
        width, height = self.get_size()
        # pylint: disable=E1101
        self.move(self.wwidth - (width + 50), self.wheight - (height + 50))
        # pylint: disable=E1101
        self.present()  # move it on top or do some magic to drag the attention
