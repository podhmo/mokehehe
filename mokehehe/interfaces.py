# -*- coding:utf-8 -*-
from zope.interface import Interface


class ISequence(Interface):
    def __iter__():
        pass

class IAdaptiveTransform(Interface):
    pass

class ILazyTemplate(Interface):
    pass

class ILazyTemplatePool(ISequence):
    pass
