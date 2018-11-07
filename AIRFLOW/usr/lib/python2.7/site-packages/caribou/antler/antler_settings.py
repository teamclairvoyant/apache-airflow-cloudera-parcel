from caribou.settings.setting_types import *
from caribou import _

AntlerSettings = SettingsTopGroup(
    _("Antler Preferences"), "/org/gnome/antler/", "org.gnome.antler",
    [SettingsGroup("antler", _("Antler"), [
                SettingsGroup("appearance", _("Appearance"), [
                        StringSetting(
                            "keyboard_type", _("Keyboard Type"), "touch",
                            _("The keyboard geometry Caribou should use"),
                            _("The keyboard geometry determines the shape "
                              "and complexity of the keyboard, it could range from "
                              "a 'natural' look and feel good for composing simple "
                              "text, to a fullscale keyboard."),
                            # Translators: Keyboard type (similar to touch/tactile device)
                            allowed=[(('touch'), _('Touch')),
                                     # Translators: Keyboard type (conventional keyboard)
                                     (('fullscale'), _('Full scale')),
                                     # Translators: Keyboard type (scanned grid by rows/columns)
                                     (('scan'), _('Scan'))]),
                        BooleanSetting("use_system", _("Use System Theme"),
                                       False, _("Use System Theme")),
                        FloatSetting("min_alpha", _("Minimum Alpha"),
                                     0.2, _("Minimal opacity of keyboard"),
                                     min=0.0, max=1.0),
                        FloatSetting("max_alpha", _("Maximum Alpha"),
                                     1.0, _("Maximal opacity of keyboard"),
                                     min=0.0, max=1.0),
                        IntegerSetting("max_distance", _("Maximum Distance"),
                                       100, _("Maximum distance when keyboard is hidden"),
                                     min=0, max=1024)
                        ])
                ])
     ])
