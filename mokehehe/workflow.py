# -*- coding:utf-8 -*-
import contextlib
from functools import partial
from zope.interface import implementer
from pyramid.interfaces import (
    IRequest, 
    IRouteRequest
)
from pyramid.exceptions import ConfigurationError
from pyramid.decorator import reify
from .interfaces import (
    IWorkflowRepository, 
    IWorkflowNode, 
    IWorkflowRelationRegister
)
from .langhelpers import first_of

@implementer(IWorkflowNode)
class MappedRoute(object):
    def __init__(self, request, name=""):
        self.request = request
        self.name = name

    def route_url(self, *args, **kwargs):
        return self.request.route_url(self.name, *args, **kwargs)

    def route_path(self, *args, **kwargs):
        return self.request.route_path(self.name, *args, **kwargs)


@implementer(IWorkflowRepository)
class FaceWorkFlowRepository(object):
    default_request_type = IRequest
    def __init__(self, request, route=None):
        self.request = request
        self.route = route or request.matched_route

    @reify
    def request_type(self):
        return first_of(self.request)[0] or self.default_request_type

    def __getitem__(self, iface):
        adapters = self.request.registry.adapters
        return adapters.lookup([iface, self.request_type], IWorkflowNode, self.route.name)(self.request)


@implementer(IWorkflowRelationRegister)
class WorkflowRelationRegister(object):
    def __init__(self, config, request_type=IRequest, validation=True, make_node=MappedRoute):
        self.config = config
        self.request_type = request_type
        self.used_route_name_set = set()
        self.validation = validation
        if validation:
            self.bind_validation()
        self.make_node = make_node

    def register(self, iface, from_route_name, to_route_name, request_type=None):
        request_type = request_type or self.request_type
        iface = self.config.maybe_dotted(iface)
        self.used_route_name_set.add(from_route_name)
        self.used_route_name_set.add(to_route_name)
        adapters = self.config.registry.adapters
        fn = partial(self.make_node, name=to_route_name)
        adapters.register([iface, request_type], IWorkflowNode, from_route_name, fn)

    @contextlib.contextmanager
    def sub(self, iface):
        yield partial(self.register, iface)

    def bind_validation(self):
        def validation():
            q = self.config.registry.queryUtility
            for name in self.used_route_name_set:
                if q(IRouteRequest, name=name) is None:
                    raise Exception("route name={name} is not found".format(name=name))
        self.config.action(None, validation, order=9999) #last of action list 


def get_workflow_repository(request):
    lookup = request.registry.adapters.lookup
    return lookup([IRequest], IWorkflowRepository)(request, request.matched_route)

def get_workflow_register(config):
    return config.registry.getUtility(IWorkflowRelationRegister)

def includeme(config):
    config.registry.adapters.register([IRequest], IWorkflowRepository, "", FaceWorkFlowRepository)
    config.registry.registerUtility(WorkflowRelationRegister(config), IWorkflowRelationRegister)
    config.add_request_method(get_workflow_repository, "workflow", reify=True)
    config.add_directive("get_workflow", get_workflow_register)
