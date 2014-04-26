# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import inspect
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


##### todo: venusian
class Mapper(object):
    def __init__(self, begin=identity, end=identity):
        self.begin = begin
        self.end = end

    def create_wrapped_initialize(self, vocls):
        try:
            args = inspect.getargspec(vocls.__init__).args[1:]
            vocls._init__original__ = vocls.__init__ #xxxx: too rubbish
            def wrapped_init(ob, context, request):
                kwargs = {k: request.matchdict[k] for k in args}
                ob.context = context
                ob.request = request
                return ob._init__original__(**kwargs)
            return wrapped_init
        except TypeError:
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

    def __call__(self, vocls):
        if hasattr(vocls, "_init__original__"):
            raise Exception("oops, multiple call")

        init = self.create_wrapped_initialize(vocls)
        if init:
            vocls.__init__ = init

        if hasattr(vocls, "__call__"):
            setattr(vocls, "__call__", self.wrapping_method(getattr(vocls, "__call__")))
        for name in viewobject_method.get_candidates(vocls):
            setattr(vocls, name, self.wrapping_method(getattr(vocls, name)))
        return vocls


def parse_get(context, request):
    return request.GET

def parse_post(context, request):
    return request.POST

def parse_json_body(context, request):
    return request.json_body

def parse_params(context, request):
    return request.params

