# -*- coding:utf-8 -*-
from zope.interface import Interface

class Transformer(object):
    def __init__(self, iface):
        self.iface = iface
        self.fn = lambda x:x

    def define(self, fn):
        self.fn = fn
        return fn

    def define_once(self, fn):
        def wrapper(val):
            result = fn(val)
            self.fn = lambda _ : val
            return result
        self.fn = wrapper
        return fn

    def __call__(self, val):
        return self.fn(val)

class AdaptiveProperty(object):
    def __init__(self, val, iface):
        self.val = val
        self.transformer = Transformer(iface)

    def __get__(self, obj, type=None):
        if obj is None:
            return self.transformer
        else:
            return self.transformer(self.val)

class AdaptivePropertyFactory(object):
    def __init__(self, iface):
        self.iface = iface

    def __call__(self, val):
        return AdaptiveProperty(val, self.iface)


class IA(Interface):
    pass

class A(object):
    adaptive_property = AdaptivePropertyFactory(IA)
    x = adaptive_property(["xxxx"])
    y = adaptive_property(["yyyy"])
    params = adaptive_property(["xxx"])

@A.y.define
def y(val):
    return [val, val]

@A.params.define_once
def params(params):
    params.append("vvvv")
    return params

print(A().x)
print(A().y)
print(A().params)
print(A().params)
print(A().params)
print(A().params)
