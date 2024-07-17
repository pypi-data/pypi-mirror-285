from importlib import import_module
from warnings import warn


def load_txt(*args, **kwargs):
    return load("TXT", *args, **kwargs)


def load_bin(*args, **kwargs):
    return load("BIN", *args, **kwargs)


_DEFAULT_BUNDLES = """\
asof20240717
asof20230204
asof20230201
asof20220201
asof20210201
asof20201127
asof20201118
""".split()


def load(type_, bundles=_DEFAULT_BUNDLES):
    for asof in bundles:
        try:
            mod = import_module("shukujitsu.%s" % asof)
        except ImportError as e:
            warn(repr(e), category=ImportWarning, stacklevel=2)
        else:
            return getattr(mod, type_)
    else:
        raise RuntimeError("No holidays data is available")
