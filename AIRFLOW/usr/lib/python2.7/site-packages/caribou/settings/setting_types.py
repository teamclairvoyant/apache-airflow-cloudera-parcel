from gi.repository import GLib, GObject

ENTRY_DEFAULT=0
ENTRY_COMBO=1
ENTRY_COLOR=2
ENTRY_FONT=3
ENTRY_SPIN=4
ENTRY_SLIDER=5
ENTRY_CHECKBOX=6
ENTRY_RADIO=7

class Setting(GObject.GObject):
    __gsignals__ = {'value-changed' :
                    (GObject.SIGNAL_RUN_FIRST,
                     GObject.TYPE_NONE, 
                     (GObject.TYPE_PYOBJECT,)),
                    'sensitivity-changed' :
                    (GObject.SIGNAL_RUN_FIRST,
                     GObject.TYPE_NONE, 
                     (GObject.TYPE_BOOLEAN,))}
    def __init__(self, name, label, children=[]):
        GObject.GObject.__init__(self)
        self.name = name
        self.label = label
        self.children = children

    @property
    def sensitive(self):
        return getattr(self, '_sensitive', True)

    @sensitive.setter
    def sensitive(self, sensitive):
        changed = getattr(self, '_sensitive', sensitive) != sensitive
        self._sensitive = sensitive
        self.emit('sensitivity-changed', sensitive)

    def __len__(self):
        return len(self.children)

    def __getitem__(self, i):
        return self.children[i]

    def __setitem__(self, i, v):
        self.children[i] = v

    def __delitem__(self, i):
        del self.children[i]

    def __iter__(self):
        return self.children.__iter__()

class SettingsGroup(Setting):
    pass

class SettingsTopGroup(SettingsGroup):
    def __init__(self, label, path, schema_id, children=[]):
        SettingsGroup.__init__(self, "_top", label, children)
        self.path = path
        self.schema_id = schema_id
        self._manager = None

    def __call__(self):
        if self._manager is None:
            from caribou.settings.settings_manager import SettingsManager
            self._manager =  SettingsManager(self)
        return self._manager

class ValueSetting(Setting):
    variant_type = ''
    entry_type=ENTRY_DEFAULT
    def __init__(self, name, label, default, short_desc="", long_desc="",
                 allowed=[], entry_type=ENTRY_DEFAULT, sensitive=None,
                 user_visible=True, children=[],
                 insensitive_when_false=[], insensitive_when_true=[]):
        Setting.__init__(self, name, label, children)
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.allowed = allowed
        self.entry_type = entry_type or self.__class__.entry_type
        if sensitive is not None:
            self.sensitive = sensitive
        self.user_visible = user_visible
        self.default = default
        self.insensitive_when_false = insensitive_when_false
        self.insensitive_when_true = insensitive_when_true
        self.hush = False

    @property
    def value(self):
        return getattr(self, '_value', self.default)

    @value.setter
    def value(self, val):
        _val = self.convert_value(val)
        if self.allowed and _val not in [a for a, b in self.allowed]:
            raise ValueError("'%s' not a valid value" % _val)
        self._value = _val
        if not self.hush:
            self.emit('value-changed', _val)

    @property
    def gsettings_key(self):
        return self.name.replace('_', '-')

    @property
    def is_true(self):
        return bool(self.value)

    @property
    def gvariant(self):
        return GLib.Variant(self.variant_type, self.value)

class BooleanSetting(ValueSetting):
    variant_type = 'b'
    entry_type = ENTRY_CHECKBOX
    def convert_value(self, val):
        # Almost anything could be a boolean.
        return bool(val)

class IntegerSetting(ValueSetting):
    variant_type = 'i'
    entry_type = ENTRY_SPIN
    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('min', GObject.G_MININT)
        self.max = kwargs.pop('max', GObject.G_MAXINT)
        ValueSetting.__init__(self, *args, **kwargs)

    def convert_value(self, val):
        return int(val)

class FloatSetting(ValueSetting):
    variant_type = 'd'
    entry_type = ENTRY_SPIN
    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('min', GObject.G_MINFLOAT)
        self.max = kwargs.pop('max', GObject.G_MAXFLOAT)
        ValueSetting.__init__(self, *args, **kwargs)

    def convert_value(self, val):
        return float(val)

class StringSetting(ValueSetting):
    variant_type = 's'
    def convert_value(self, val):
        return str(val)

class ColorSetting(StringSetting):
    entry_type = ENTRY_COLOR

class FontSetting(StringSetting):
    entry_type = ENTRY_FONT
