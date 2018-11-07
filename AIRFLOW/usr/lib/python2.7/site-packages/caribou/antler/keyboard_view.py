from caribou.settings.preferences_window import PreferencesDialog
from caribou.settings import CaribouSettings
from .antler_settings import AntlerSettings
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Caribou
import os
from math import ceil

class AntlerKey(Gtk.Button):
    def __init__(self, key, spacing=0):
        GObject.GObject.__init__(self)
        self.caribou_key = key.weak_ref()
        self.set_label(self._get_key_label())
        self._spacing = spacing

        label = self.get_child()
        label.set_use_markup(True)
        label.props.margin = 6

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-button")

        if key.get_extended_keys ():
            self._sublevel = AntlerSubLevel(self)

        key.connect('key-pressed', self._caribou_key_pressed)
        key.connect('key-released', self._caribou_key_released)

    def set_dwell_scan(self, dwell):
        if dwell:
            self.set_state_flags(Gtk.StateFlags.SELECTED, False)
        else:
            self.unset_state_flags(Gtk.StateFlags.SELECTED)

    def set_group_scan_active(self, active):
        if active:
            self.set_state_flags(Gtk.StateFlags.INCONSISTENT, False)
        else:
            self.unset_state_flags(Gtk.StateFlags.INCONSISTENT)

    def _get_key_label(self):
        label = self.caribou_key().props.label
        return "<b>%s</b>" % GLib.markup_escape_text(label)

    def _caribou_key_pressed (self, key, _key):
        self.set_state_flags(Gtk.StateFlags.ACTIVE, False)

    def _caribou_key_released (self, key, _key):
        self.unset_state_flags(Gtk.StateFlags.ACTIVE)

    def _press_caribou_key(self):
        if self.caribou_key():
            self.caribou_key().press()

    def _release_caribou_key(self):
        if self.caribou_key():
            self.caribou_key().release()

    def do_get_preferred_width(self):
        w = self.caribou_key().props.width
        h, _ = self.get_preferred_height()
        width = int(h * w + ceil(w - 1) * self._spacing)
        return (width, width)

    def do_pressed(self):
        self._press_caribou_key()

    def do_released(self):
        self._release_caribou_key()

    def do_enter(self):
        self.set_state_flags(Gtk.StateFlags.PRELIGHT, False)

    def do_leave(self):
        self.unset_state_flags(Gtk.StateFlags.PRELIGHT)

class AntlerSubLevel(Gtk.Window):
    def __init__(self, key):
        GObject.GObject.__init__(self, type=Gtk.WindowType.POPUP)

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_accept_focus(False)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-window")

        key.caribou_key().connect("notify::show-subkeys", self._on_show_subkeys)
        self._key = key

        layout = AntlerLayout()
        layout.add_row([key.caribou_key().get_extended_keys()])
        self.add(layout)

    def _on_show_subkeys(self, key, prop):
        parent = self._key.get_toplevel()
        if key.props.show_subkeys:
            self.set_transient_for(parent)
            parent.set_sensitive(False)
            self.show_all()
        else:
            parent.set_sensitive(True)
            self.hide()

class AntlerLayout(Gtk.Box):
    KEY_SPAN = 4

    def __init__(self, level=None, spacing=6):
        GObject.GObject.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(12)
        self._columns = []
        self._keys_map = {}
        self._active_scan_group = []
        self._dwelling_scan_group = []
        self._spacing = spacing

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-layout")

        if level:
            self.load_rows(level.get_rows ())
            level.connect("selected-item-changed", self._on_active_group_changed)
            level.connect("step-item-changed", self._on_dwelling_group_changed)
            level.connect("scan-cleared", self._on_scan_cleared)

    def add_column (self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_homogeneous(True)
        box.set_spacing(self._spacing)
        self.pack_start (box, True, True, 0)
        self._columns.append(box)
        return box

    def _on_scan_cleared (self, level):
        self._foreach_key(self._active_scan_group,
                          lambda x: x.set_group_scan_active (False))

        self._active_scan_group = []

        self._foreach_key(self._dwelling_scan_group,
                          lambda x: x.set_dwell_scan (False))

        self._dwelling_scan_group = []

    def _on_active_group_changed(self, level, active_item):
        self._foreach_key(self._active_scan_group,
                          lambda x: x.set_group_scan_active (False))

        if isinstance(active_item, Caribou.KeyModel):
            self._active_scan_group = [active_item]
        else:
            self._active_scan_group = active_item.get_keys()

        self._foreach_key(self._active_scan_group,
                          lambda x: x.set_group_scan_active (True))

    def _on_dwelling_group_changed(self, level, dwell_item):
        self._foreach_key(self._dwelling_scan_group,
                          lambda x: x.set_dwell_scan (False))

        if isinstance(dwell_item, Caribou.KeyModel):
            self._dwelling_scan_group = [dwell_item]
        else:
            self._dwelling_scan_group = dwell_item.get_keys()

        self._foreach_key(self._dwelling_scan_group,
                          lambda x: x.set_dwell_scan (True))

    def _foreach_key(self, keys, cb):
        for key in keys:
            try:
                cb(self._keys_map[key])
            except KeyError:
                continue

    def add_row(self, row, row_num=0):
        x = 0
        for c, col in enumerate(row):
            try:
                column = self._columns[c]
            except IndexError:
                column = self.add_column()

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            column.pack_start(box, True, True, 0)

            alignboxes = {}

            for i, key in enumerate(col):
                align = key.props.align
                if align not in alignboxes:
                    alignbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                    alignbox.set_spacing(self._spacing)
                    alignboxes[align] = alignbox
                    if align == "left":
                        box.pack_start(alignbox, False, False, 0)
                    elif align == "center":
                        box.pack_start(alignbox, True, False, 0)
                    elif align == "right":
                        box.pack_end(alignbox, False, False, 0)
                else:
                    alignbox = alignboxes[align]

                antler_key = AntlerKey(key, self._spacing)
                self._keys_map[key] = antler_key
                alignbox.pack_start (antler_key, True, True, 0);

    def load_rows(self, rows):
        for row_num, row in enumerate(rows):
            self.add_row([c.get_children() for c in row.get_columns()], row_num)

class AntlerKeyboardView(Gtk.Notebook):
    def __init__(self, keyboard_type='touch', keyboard_file=None,
                 keyboard_level=None):
        GObject.GObject.__init__(self)
        settings = AntlerSettings()
        self.set_show_tabs(False)

        ctx = self.get_style_context()
        ctx.add_class("antler-keyboard-window")

        use_system = settings.use_system
        use_system.connect("value-changed", self._on_use_system_theme_changed)

        self._app_css_provider = Gtk.CssProvider()
        self._load_style(
            self._app_css_provider, "style.css",
            [GLib.get_user_data_dir()] + list(GLib.get_system_data_dirs()))

        if not use_system.value:
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self._app_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._user_css_provider = Gtk.CssProvider()
        self._load_style(self._user_css_provider, "user-style.css",
                         [GLib.get_user_data_dir()])
        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self._user_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

        self.scanner = Caribou.Scanner()
        self.set_keyboard_model(keyboard_type, keyboard_file, keyboard_level)

    def set_keyboard_model(self, keyboard_type, keyboard_file, keyboard_level):
        self.keyboard_model = Caribou.KeyboardModel(keyboard_type=keyboard_type,
                                                    keyboard_file=keyboard_file)

        self.scanner.set_keyboard(self.keyboard_model)
        self.keyboard_model.connect("notify::active-group", self._on_group_changed)
        self.keyboard_model.connect("key-clicked", self._on_key_clicked)

        self.layers = {}

        for gname in self.keyboard_model.get_groups():
            group = self.keyboard_model.get_group(gname)
            self.layers[gname] = {}
            group.connect("notify::active-level", self._on_level_changed)
            for lname in group.get_levels():
                level = group.get_level(lname)
                layout = AntlerLayout(level)
                layout.show()
                self.layers[gname][lname] = self.append_page(layout, None)

        self._set_to_active_layer(keyboard_level=keyboard_level)

    def _on_key_clicked(self, model, key):
        if key.props.name == "Caribou_Prefs":
            p = PreferencesDialog(AntlerSettings())
            p.populate_settings(CaribouSettings())
            p.show_all()
            p.run()
            p.destroy()

    def _on_use_system_theme_changed(self, setting, value):
        if value:
            Gtk.StyleContext.remove_provider_for_screen(
                Gdk.Screen.get_default(), self._app_css_provider)
        else:
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self._app_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _load_style(self, provider, filename, search_path):
        spath = search_path[:]
        if "ANTLER_THEME_PATH" in os.environ:
            spath.insert(0, os.environ["ANTLER_THEME_PATH"])

        for directory in spath:
            fn = os.path.join(directory, "antler", filename)
            if os.path.exists(fn):
                provider.load_from_path(fn)
                break

    def _on_level_changed(self, group, prop):
        self._set_to_active_layer()

    def _on_group_changed(self, kb, prop):
        self._set_to_active_layer()

    def _set_to_active_layer(self, keyboard_level=None):
        active_group_name = self.keyboard_model.props.active_group
        active_group = self.keyboard_model.get_group(active_group_name)
        if keyboard_level:
            active_level_name = keyboard_level
        else:
            active_level_name = active_group.props.active_level

        self.set_current_page(self.layers[active_group_name][active_level_name])

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    w = Gtk.Window()
    w.set_accept_focus(False)

    kb = AntlerKeyboardView('touch')
    w.add(kb)

    w.show_all()

    Gtk.main()
