import gettext
from gettext import gettext as _
import os

def C_(ctx, s):
    """Provide qualified translatable strings via context.
    (copied from Orca)"""
    translated = gettext.gettext('%s\x04%s' % (ctx, s))
    if '\x04' in translated:
        # no translation found, return input string
        return s
    return translated

gettext.bindtextdomain ("caribou",
                        os.path.join ("/usr", "share", "locale"))

gettext.textdomain("caribou")


