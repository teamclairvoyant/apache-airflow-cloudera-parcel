from caribou.settings.setting_types import *
from caribou import _

CaribouSettings = SettingsTopGroup(
    _("Caribou Preferences"), "/org/gnome/caribou/", "org.gnome.caribou",
    [SettingsGroup("scanning", _("Scanning"), [
                BooleanSetting(
                    "scan_enabled", _("Enable scanning"), False,
                    _("Enable switch scanning"),
                    insensitive_when_false=["scanning_general",
                                            "scanning_input"]),
                SettingsGroup("scanning_general", _("General"), [
                        IntegerSetting("scan_grouping", _("Scanning mode"),
                                       1,
                                       _("Scanning type, subgroups, rows or linear"),
                                       allowed=[(1, _("Subgroups")),
                                                (2, _("Rows")),
                                                (3, _("Linear"))],
                                       entry_type=ENTRY_COMBO),
                        FloatSetting("step_time", _("Step time"), 1.0,
                                     _("Time between key transitions"),
                                     min=0.1, max=60.0),
                        BooleanSetting("inverse_scanning",
                                       _("Inverse scanning"), False,
                                       _("Step with the switch, activate by dwelling")),
                        BooleanSetting(
                            "autorestart",
                            _("Auto-restart scanning"), False,
                            _("Automatically restart scanning after item activation")),
                        IntegerSetting("scan_cycles", _("Scan cycles"),
                                       1, allowed=[(1, _("One")),
                                                   (2, _("Two")),
                                                   (3, _("Three")),
                                                   (4, _("Four")),
                                                   (5, _("Five"))],
                                       entry_type=ENTRY_COMBO)
                        ]),
                SettingsGroup("scanning_input", _("Input"), [
                        StringSetting("switch_device", _("Switch device"),
                                      "keyboard",
                                      _("Switch device, keyboard or mouse"),
                                      entry_type=ENTRY_RADIO,
                                      allowed=[("keyboard", _("Keyboard")),
                                               ("mouse", _("Mouse"))],
                                      children=[
                                StringSetting("keyboard_key", _("Switch key"),
                                              "space",
                                              _("Key to use with scanning mode"),
                                              allowed=[
                                        ("Shift_R", _("Right shift")),
                                        ("Shift_L", _("Left shift")),
                                        ("space", _("Space")),
                                        ("ISO_Level3_Shift", _("Alt Gr")),
                                        ("Num_Lock", _("Num lock"))]),
                                IntegerSetting("mouse_button", _("Switch button"),
                                               2,
                                               _(
                                        "Mouse button to use in the scanning "
                                        "mode"), 
                                               allowed=[(1, _("Button 1")),
                                                        (2, _("Button 2")),
                                                        (3, _("Button 3"))],
                                               entry_type=ENTRY_COMBO)
                                ]),
                        ]),
                ])
        ])
