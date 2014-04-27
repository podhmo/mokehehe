# -*- coding:utf-8 -*-
import sys
from zope.interface.interface import InterfaceClass
from zope.interface import (
    providedBy,
    implementer
)


inPy3k = sys.version_info[0] == 3

class OldStyleClass:
    pass
ClassType = type(OldStyleClass)

ClassTypes = (type,)
if not inPy3k:
    ClassTypes = (type, ClassType)


## utility
def merged(*args):
    d0 = {}
    for d1 in args:
        d0.update(d1)
    return d0

def first_of(ob):
    try:
        return [iter(providedBy(ob)).__next__()]
    except StopIteration:
        return []

class DynamicInterfaceFactory(object):
    def __init__(self):
        self.cache = {}

    def __call__(self, cls):
        try:
            return self.cache[id(cls)]
        except KeyError:
            iface = self.create(cls)
            self.cache[id(cls)] = iface
            return iface

    def implementer(self, cls):
        return implementer(self.__call__(cls))(cls)

    def create(self, cls):
        return dynamic_interface(cls)

def dynamic_interface(cls):
    name = "I{}".format(cls.__name__)
    return InterfaceClass(name)

_iface_factory = None
def make_interface_from_class(cls):
    global _iface_factory
    if _iface_factory is None:
        _iface_factory = DynamicInterfaceFactory()
    return _iface_factory(cls)

class ClassStoreDecoratorFactory(object):
    def __init__(self, cache_name, cache_factory, cache_convert, value_convert):
        self.cache_name = cache_name
        self.cache_factory = cache_factory
        self.cache_convert =  cache_convert
        self.value_convert = value_convert

    def on_classmethod(self, fn):
        f = sys._getframe()
        class_env = f.f_back.f_locals
        if not self.cache_name in class_env:
            class_env[self.cache_name] = self.cache_factory()
        class_env[self.cache_name].add(self.cache_convert(fn))
        return self.value_convert(fn)
    __call__ = on_classmethod

    def with_class_attributes(self, fn, class_env, name=None):
        if not self.cache_name in class_env:
            class_env[self.cache_name] = self.cache_factory()
        if name is None:
            class_env[self.cache_name].add(self.cache_convert(fn))
        else:
            class_env[self.cache_name].add(name)
        return self.value_convert(fn)


    def get_candidates(self, module_class):
        if hasattr(module_class, self.cache_name):
            for name in getattr(module_class, self.cache_name):
                yield name

