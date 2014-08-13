# -*- coding: utf-8 -*-
#from cStringIO import StringIO
import pprint
# from django.utils.html import escape
from pkgutil import iter_modules
from importlib import import_module
import inspect


def unpack(dct, *keys):
    if not keys:
        keys = dct.keys()
    return (dct.get(k, None) for k in keys)


def model_field(model, *fieldnames):
    if not fieldnames:
        return model._meta.fields

    fields = [field for field in model._meta.fields if field.name in fieldnames]
    return fields if len(fields) > 1 else fields.pop()


def pretty_string(s):
    #stream = StringIO()  # note: use finally stream.close()
    def ascii_format(object_, context, maxlevels, level):
        typ = pprint._type(object_)
        if typ is unicode:
            object_ = str(object_).replace('"', '\\"')  # replace " to '
            rep = "\"%s\"" % object_  # repr(object_)
            return rep, (rep and not rep.startswith('<')), False

        return pprint._safe_repr(object_, context, maxlevels, level)

    printer = pprint.PrettyPrinter(indent=2)
    printer.format = ascii_format
    return printer.pformat(s).replace("'", '"')


def walk_modules(path):
    """Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.

    For example: walk_modules('scrapy.utils')
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def iter_classes(module_name, base_type=None):
    for module in walk_modules(module_name):
        for obj in vars(module).itervalues():
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                if base_type and not issubclass(obj, base_type):
                    continue
                yield obj


def load_class(path):
    mod_name, cls_name = path.rsplit('.', 1)
    module = __import__(mod_name, fromlist=[cls_name])
    return getattr(module, cls_name)


def make_shortcut(module_path, module_members=False):
    """
    Extract the shortcut from full module locator:
    blogspot.spiders.default -> blogspot.default

    If module_members is True, then shortcut will be another:
    publisher.filters.default.<some member> -> default.<some member>
    """
    pieces = module_path.split('.')
    cut = pieces[-2:] if module_members else pieces[::2]
    return '.'.join(cut)