try:
    from i18n import _
except ImportError:
    # i18n.py is not available when "caribou" module is imported by
    # tools/make_schema.py and srcdir != builddir.
    _ = lambda a: a

APP_NAME=_("Caribou")
