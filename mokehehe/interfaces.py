# -*- coding:utf-8 -*-
from zope.interface import Interface


class ISequence(Interface):
    def __iter__():
        pass

class IAdaptiveTransform(Interface):
    pass

class IDelayedRenderer(Interface):
    pass

class IDelayedRendererPool(ISequence):
    pass
