# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import contextlib
import operator as op
from zope.interface import (
    implementer,
    provider,
    directlyProvides, 
    Interface
)
from pyramid.decorator import reify

from .interfaces import (
    IRegisteringNode, 
    IRegisteringNodeFactory, 
    INaming, 
    IRegisteringExecution, 
    ISubRegisterFactory, 
    IRegisteringBuilderRepository
)
from .langhelpers import (
    first_of, 
    merged
)

class _IRoot(Interface):
    pass

class IResourceRegister(IRegisteringNode):
    pass

class IRouteRegister(IRegisteringNode):
    pass

class IViewRegister(IRegisteringNode):
    pass


@implementer(IRegisteringNodeFactory)
class RegisteringNodeFactory(object):
    def __init__(self, cls, iface):
        self.cls = cls
        self.iface = iface

    def __call__(self, *args, **kwargs):
        node = self.cls(*args, **kwargs)
        directlyProvides(node, self.iface) #xxx: alsoProvides?
        return node


@implementer(IRegisteringNode)
class RegisteringNode(object):
    def __init__(self, config, name, parent=None, factory_options=None, k=""):
        self.config = config
        self.name = name
        self.parent = parent
        self.registers = []
        self.factory_options = factory_options or {}
        self.k = k
        self.options = {}

    def update(self, **kwargs):
        self.options.update(kwargs)

    def __repr__(self):
        return "<{self.__class__.__name__!r}{iface!r}>".format(self=self, iface=first_of(self))


    def register(self, sub_register):
        self.registers.append(sub_register)

    @reify
    def fullname(self):
        naming = self.config.registry.adapters.lookup(first_of(self), INaming)
        return naming(self)

    def execute(self, config, target, kwargs):
        factory = config.registry.adapters.lookup(first_of(self), IRegisteringExecution, self.k)
        fn = factory(**self.factory_options)
        return fn(config, self.fullname, target, **kwargs)

    def __call__(self, config, target, kwargs, options):
        if options is None:
            child_kwargs = self.execute(config, target, merged(self.options, kwargs))
            for sub_register in self.registers:
                sub_register(config, target, child_kwargs, options=None)
        else:
            child_kwargs = self.execute(config, target, merged(self.options, kwargs, options.get("_this", {})))
            for sub_register in self.registers:
                sub_options = options.get(sub_register.name)
                sub_register(config, target, child_kwargs, options=sub_options)


@provider(INaming)
def toplevel_naming(self):
    return self.name

@provider(INaming)
def nested_naming(self):
    return "{self.parent.fullname}.{self.name}".format(self=self)


@implementer(IRegisteringExecution)
class CreateResourceExecute(object):
    def __init__(self, resource_factory):
        self.resource_factory = resource_factory

    def __call__(self, config, name, target, **kwargs):
        return {"factory": self.resource_factory(target, **kwargs)}

@implementer(IRegisteringExecution)
class AddRouteExecute(object):
    def __init__(self, 
                 route_name_craete, 
                 path_create
    ):
        self.route_name_craete = route_name_craete
        self.path_create = path_create

    def __call__(self, config, name, target, **kwargs):
        route = self.route_name_craete(target, name)
        path = self.path_create(target, name)
        logger.debug("registering.. route=%s, path=%s", route, path)
        config.add_route(route, path, **kwargs)
        return {"route_name": route}

@implementer(IRegisteringExecution)
class AddViewExecute(object):
    add_view = op.attrgetter("add_view")
    def __init__(self, view, callback=None):
        self.view = view
        self.callback = callback

    def __call__(self, config, name, target, **kwargs):
        if self.callback:
            view = self.callback(self.view, target)
        else:
            view = self.view
        self.add_view(config)(view, **kwargs)
        return {}


class AddDelayedViewExecute(AddViewExecute):
    add_view = op.attrgetter("add_delayed_view")

TopResourceRegisteringNode = RegisteringNodeFactory(RegisteringNode, IResourceRegister)
MiddleRouteRegisteringNode = RegisteringNodeFactory(RegisteringNode, IRouteRegister)
BottomViewRegisteringNode = RegisteringNodeFactory(RegisteringNode, IViewRegister)

class NestedBuilder(object):
    def __init__(self, config, register, k=""):
        self.config = config
        self.register = register
        self.k = k

    def _build(self, name, **kwargs):
        adapters = self.config.registry.adapters
        create_sub_register = adapters.lookup(first_of(self.register), ISubRegisterFactory, self.k)
        sub_register = create_sub_register(self.config,
                                   name,
                                   parent=self.register,
                                   factory_options=kwargs)
        self.register.register(sub_register)
        return sub_register

    def build(self, *args, **kwargs):
        return self._build("", **kwargs)

    @contextlib.contextmanager
    def sub(self, name, **kwargs): #xxx:
        sub_register = self._build(name, **kwargs)
        yield self.__class__(self.config, sub_register, self.k)

    def __call__(self, target, **options):
        self.register(self.config, target, {}, options)

    def register(self, *args, **kwargs):
        self.register.register(*args, **kwargs)

    @reify
    def fullname(self):
        return self.register.fullname

def add_registering_builder(config, name, k="", **factory_options):
    repository = config.registry.queryUtility(IRegisteringBuilderRepository)
    if repository is None:
        repository = {}
        config.registry.registerUtility(repository, IRegisteringBuilderRepository)
    try:
        return repository[name]
    except KeyError:
        logger.debug("builder create name=%s, k=%s", name, k)
        register_factory = config.registry.adapters.lookup([_IRoot], ISubRegisterFactory)
        register = register_factory(config, name, parent=None, factory_options=factory_options, k=k)
        builder = NestedBuilder(config, register, k=k)
        repository[name] = builder
        return builder


def includeme(config):
    adapters = config.registry.adapters
    ### default convension

    adapters.register([IResourceRegister], INaming, "", toplevel_naming)
    adapters.register([IRouteRegister], INaming, "", nested_naming)
    adapters.register([IViewRegister], INaming, "", nested_naming)

    adapters.register([_IRoot], ISubRegisterFactory, "", TopResourceRegisteringNode)
    adapters.register([IResourceRegister], ISubRegisterFactory, "", MiddleRouteRegisteringNode)
    adapters.register([IRouteRegister], ISubRegisterFactory, "", BottomViewRegisteringNode)

    adapters.register([IResourceRegister], IRegisteringExecution, "", CreateResourceExecute)
    adapters.register([IRouteRegister], IRegisteringExecution, "", AddRouteExecute)
    adapters.register([IViewRegister], IRegisteringExecution, "", AddViewExecute)

    adapters.register([IResourceRegister], IRegisteringExecution, "delayed", CreateResourceExecute)
    adapters.register([IRouteRegister], IRegisteringExecution, "delayed", AddRouteExecute)
    adapters.register([IViewRegister], IRegisteringExecution, "delayed", AddDelayedViewExecute)

    config.add_directive("registering_builder", add_registering_builder)

