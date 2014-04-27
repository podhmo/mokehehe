# -*- coding:utf-8 -*-
## tooo experimental
## this module is layed in different layer?(more concretely)

from functools import partial
from pyramid.response import Response
from .miniadt import ADTTypeProvider, dispatchmethod
from .interfaces import IModelInformation
from .langhelpers import first_of

def flow_dispatch(cls, target):
    if isinstance(target, dict):
        return target
    elif isinstance(target, Response):
        return target
    else:
        tag = target.__class__.__name__
        return getattr(cls, tag)(*target)

FlowTypeProvider = partial(ADTTypeProvider, dispatch_function=flow_dispatch)

## default
RedirectType = FlowTypeProvider("Redirect")

SuccessRedirect = RedirectType("SuccessRedirect", "request subject")
FailureRedirect = RedirectType("FailureRedirect", "request subject")


## these are too boilerplate?
"""
| route name           | path                       |
|----------------------+----------------------------|
| model.list           | /model/list                |
| model.create         | /model/create              |
| model.show           | /model/show/{id}           |
| model.edit           | /model/edit/{id}           |
| model.delete         | /model/delete/{id}         |

"""
from pyramid.httpexceptions import (
    HTTPBadRequest, 
    HTTPFound
)

@RedirectType.as_match_class
class ModelCreateFlow(object):
    @dispatchmethod
    def SuccessRedirect(request, subject):
        adapters = request.registry.adapters
        model_info = adapters.lookup(first_of(subject), IModelInformation)(subject)

        if model_info.persistent_id:
            return HTTPFound(request.route_path(model_info.get_route_name("show"), id=model_info.persistent_id))
        else:
            return HTTPFound(request.route_path(model_info.get_route_name("list")))

    @dispatchmethod
    def FailureRedirect(request, subject):
        raise HTTPBadRequest("oh")

@RedirectType.as_match_class
class ModelUpdateFlow(object):
    @dispatchmethod
    def SuccessRedirect(request, subject):
        adapters = request.registry.adapters
        model_info = adapters.lookup(first_of(subject), IModelInformation)(subject)
        return HTTPFound(request.route_path(model_info.get_route_name("show"), id=model_info.persistent_id))

    @dispatchmethod
    def FailureRedirect(request, subject):
        raise HTTPBadRequest("oh")

@RedirectType.as_match_class
class ModelDeleteFlow(object):
    @dispatchmethod
    def SuccessRedirect(request, subject):
        adapters = request.registry.adapters
        model_info = adapters.lookup(first_of(subject), IModelInformation)(subject)
        return HTTPFound(request.route_path(model_info.get_route_name("list")))

    @dispatchmethod
    def FailureRedirect(request, subject):
        raise HTTPBadRequest("oh")
