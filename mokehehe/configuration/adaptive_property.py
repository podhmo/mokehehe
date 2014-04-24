# -*- coding:utf-8 -*-
import venusian
from functools import partial
from mokehehe.configuration.interfaces import IAdaptiveTransform

class Transformer(object):
    def __init__(self, iface, name=None):
        self.name = name
        self.iface = iface

    def transform(self, fn):
        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_transform(self.iface, self.name, fn)
        info = venusian.attach(fn, callback, category='mokehehe')
        return fn

    def transform_once(self, fn):
        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_transform_once(self.iface, self.name, fn)
        info = venusian.attach(fn, callback, category='mokehehe')
        return fn

    def __call__(self, obj, val):
        reg = self.get_registry(obj)
        u = reg.adapters.lookup([self.iface], IAdaptiveTransform, name=self.name)
        return u(val) if u else val

    def get_registry(self, obj):
        return obj.request.registry

class AdaptiveProperty(object):
    def __init__(self, val, name=None, iface=None):
        self.val = val
        self.transformer = Transformer(iface, name=name)

    def rename(self, name):
        self.transformer.name = name #xxx:

    def __get__(self, obj, type=None):
        if obj is None:
            return self.transformer
        else:
            return self.transformer(obj, self.val)

class AdaptivePropertyFactory(object):
    def __init__(self, iface):
        self.iface = iface

    def __call__(self, val, name=None):
        return AdaptiveProperty(val, name=name, iface=self.iface)

    def __getattr__(self, name):
        return partial(self.__call__, name=name)
