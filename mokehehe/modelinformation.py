# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import IModelInformation
from .langhelpers import (
    make_interface_from_class, 
    first_of
)

@implementer(IModelInformation)
class DefaultModelInformation(object):
    def __init__(self, o, display_name=None):
        self.o = o
        self._display_name = display_name

    @property
    def name(self):
        return self.o.__name__

    @property
    def display_name(self):
        return self._display_name or self.name

    @property
    def persistent_id(self):
        return self.o.id #hmm

    def get_route_name(self, action_name):
        return "{}.{}".format(self.name, action_name)

def bind_model_information(config, model, minfo, iface_factory=make_interface_from_class):
    source_iface = [iface_factory(model)]
    config.registry.adapters.register(source_iface, IModelInformation, "", minfo)
    assert config.registry.adapters.lookup(source_iface, IModelInformation)

def includeme(config):
    config.add_directive("bind_model_information", bind_model_information)
