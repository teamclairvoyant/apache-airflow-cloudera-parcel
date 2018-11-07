import os
from gi.repository import Gio
from caribou.settings.setting_types import *

class SettingsManager(object):
    def __init__(self, settings):
        self.groups = settings
        self._gsettings = Gio.Settings(settings.schema_id)
        self._gsettings.connect("changed", self._gsettings_changed_cb)
        self._settings_map = {}
        self._map_settings(self.groups)

        self._setup_settings()

    def __getattr__(self, name):
        try:
            return self._settings_map[name]
        except KeyError:
            raise AttributeError("no setting named '%s'" % name)

    def _map_settings(self, setting):
        if setting.name in self._settings_map:
            raise ValueError("more than one setting has the name '%s'" % setting.name)
        self._settings_map[setting.name] = setting
        
        for s in setting:
            self._map_settings(s)

    def _setup_settings(self):
        for setting in list(self._settings_map.values()):
            if isinstance(setting, SettingsGroup):
                continue
            setting.value = \
                self._gsettings.get_value(setting.gsettings_key).unpack()

            self._change_dependant_sensitivity(setting)

            setting.connect('value-changed', self._on_value_changed)

    def _change_dependant_sensitivity(self, setting):
        for name in setting.insensitive_when_false:
            self._settings_map[name].sensitive = setting.is_true
        for name in setting.insensitive_when_true:
            self._settings_map[name].sensitive = not setting.is_true
        if setting.allowed:
            index = [a for a, b in setting.allowed].index(setting.value)
            for i, child in enumerate(setting.children):
                child.sensitive = i == index

    def _on_value_changed(self, setting, value):
        if value != \
                self._gsettings.get_value(setting.gsettings_key).unpack():
            self._gsettings.set_value(setting.gsettings_key, setting.gvariant)
            self._change_dependant_sensitivity(setting)

    def _gsettings_changed_cb(self, gsettings, key):
        setting = getattr(self, key.replace('-', '_'))
        new_value = gsettings.get_value(key).unpack()
        if setting.value != new_value:
            setting.hush = True
            setting.value = new_value
            setting.hush = False

    def __call__(self):
        return self
