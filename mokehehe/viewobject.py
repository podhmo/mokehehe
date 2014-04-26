# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import inspect
import venusian
from pyramid.httpexceptions import HTTPBadRequest
from .interfaces import IMappedViewObject
from .langhelpers import ClassStoreDecoratorFactory


"""
this is short hand view.
"""


viewobject_method = ClassStoreDecoratorFactory(
    cache_name="_viewobject_method_name_list", 
    cache_factory=set,
    cache_convert=lambda x : x.__name__,
    value_convert=lambda x : x
)

## this is class decorator
identity = lambda x : x


def parse_get(context, request):
    return request.GET

def parse_post(context, request):
    return request.POST

def parse_json_body(context, request):
    return request.json_body

def parse_params(context, request):
    return request.params


positional = object()
class Mapper(object):
    def __init__(self, begin=parse_params, end=identity, FailException=HTTPBadRequest):
        self.begin = begin
        self.end = end
        self.FailException = FailException

    def create_wrapped_initialize(self, vocls):
        try:
            spec = inspect.getargspec(vocls.__init__)
            name_type_paris = [[k, positional] for k in spec.args[1:]]
            if spec.defaults is not None:
                for i, t in enumerate(reversed(spec.defaults)):
                    name_type_paris[-(i+1)][1] = t

            original_init = vocls.__init__ #xxxx: too rubbish
            def wrapped_init(ob, context, request):
                kwargs = {}
                try:
                    for k, t in name_type_paris:
                        if t is positional:
                            kwargs[k] = request.matchdict[k]
                        elif callable(t):
                            kwargs[k] = t(request.matchdict[k])
                        else:
                            kwargs[k] = t
                    ob.context = context
                    ob.request = request
                except ValueError as e:
                    raise self.FailException(repr(e))
                return original_init(ob, **kwargs)
            return wrapped_init
        except TypeError:
            logger.debug("%s doesn't have __init__", vocls)
            def simple_init(ob, context, request):
                ob.context = context
                ob.request = request
            return simple_init

    def wrapping_method(self, method):
        def wrapped(vo, *args, **kwargs):
            parsed = self.begin(vo.context, vo.request, *args, **kwargs)
            result = method(vo, **parsed)
            return self.end(result)
        return wrapped

    def create_mapped_viewobject_class(self, vocls):
        init = self.create_wrapped_initialize(vocls)
        attrs = {"__init__": init}
        if hasattr(vocls, "__call__"):
            attrs["__call__"] = self.wrapping_method(getattr(vocls, "__call__"))
        for name in viewobject_method.get_candidates(vocls):
            attrs[name] = self.wrapping_method(getattr(vocls, name))
        mapped_class_name = "{}Proxy".format(vocls.__name__)
        mapped_class = type(mapped_class_name, (vocls, ), attrs)
        return mapped_class

    venusian = venusian #test

    def __call__(self, vocls):
        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_mapped_viewobject(self, vocls)
        info = self.venusian.attach(vocls, callback, category="mokehehe")
        return vocls


class MapperButModifyClass(Mapper):
    def __call__(self, vocls):
        return self.create_mapped_viewobject_class(vocls)

"""
@Mapper(parse_get, todict)
class FooViewObject(object):
    def foo(self, n):
        return "foo"*self.n
"""

def add_mapped_viewobject(config, mapper, clsname):
    vocls = config.maybe_dotted(clsname)
    mapped_class = mapper.create_mapped_viewobject_class(vocls)
    config.registry.registerUtility(mapped_class, IMappedViewObject, name=vocls.__name__) #xxx:
    return mapped_class

def get_mapped_viewobject(config, clsname): ##todo: fix dependents on calling orde.
    """
    vo = config.mapped_viewobject(".FooViewObject")
    config.add_view(vo, route_name="foo", attr="foo")
    """
    cls = config.maybe_dotted(clsname)
    return config.registry.getUtility(IMappedViewObject, name=cls.__name__)

def includeme(config):
    config.add_directive("mapped_viewobject", get_mapped_viewobject)
    config.add_directive("add_mapped_viewobject", add_mapped_viewobject)
