# -*- coding:utf-8 -*-
from mokehehe.configuration.interfaces import IAdaptiveTransform
from mokehehe.configuration.adaptive_property import AdaptivePropertyFactory

class SettingMeta(type):
    def __new__(self, name, bases, attrs):
        for k, v in attrs.items():
            if hasattr(v, "rename"):
                v.rename(k)
        return type.__new__(self, name, bases, attrs)

class Setting(object, metaclass=SettingMeta):
    pass

class OnceCall(object):
    def __init__(self, fn):
        self.fn = fn
        self.value = None

    def __call__(self, val):
        if self.value is None:
            self.value = self.fn(val)
        return self.value

def add_transform(config, isource, name, fn):
    config.registry.adapters.register([isource], IAdaptiveTransform, name, fn)

def add_transform_once(config, isource, name, fn):
    return add_transform(config, isource, name, OnceCall(fn))

def includeme(config):
    config.add_directive("add_transform", add_transform)
    config.add_directive("add_transform_once", add_transform_once)
