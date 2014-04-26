# -*- coding:utf-8 -*-
from zope.interface import (
    Interface, 
    Attribute
)
from pyramid.interfaces import IDict

class ISequence(Interface):
    def __iter__():
        pass

## adaptive_property
class IAdaptiveTransform(Interface):
    pass

## delayed_view
class IDelayedRenderer(Interface):
    pass

class IDelayedRendererPool(ISequence):
    pass

## regisering
class IRegisteringExecution(Interface):
    def __call__(config, fullname, target, *args, **kwargs):
        pass

class INaming(Interface):
    def __call__(obj):
        """return string"""

class ISubRegisterFactory(Interface):
    def __call__(config, name, parent):
        """return IRegister"""

class IRegisteringNodeFactory(Interface):
    def __call__(config, *args, **kwargs):
        """return IRegisteringNode object"""

class IRegisteringNode(Interface):
    name = Attribute("")
    parent = Attribute("")
    registers = Attribute("subregister of collection")
    fullnaming = Attribute("INaming")

    def register(sub_register):
        pass

    def __call__(config, subject, options, *args, **kwrgs):
        pass

class IRegisteringBuilderRepository(IDict):
    pass

##
class IMappedViewObject(Interface):
    pass
