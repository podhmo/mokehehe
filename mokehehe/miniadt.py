# -*- coding:utf-8 -*-
"""
## define mini adt
Result = ADTTypeFactory("Result")
Failure = Result("Failure", "code message")
Success = Result("Success", "value")

## use mini adt
@Result.validation
class match0(Match):
    @dispatchmethod
    def Failure(code, message):
        return ["oops", code, message]

    @dispatchmethod
    def Success(value):
        return ["ok", value]

## or
@Result.as_match_class
class match0(object):
    @Result.dispatchmethod
    def Failure(code, message):
        return ["oops", code, message]

    @Result.dispatchmethod
    def Success(value):
        return ["ok", value]


match0(Failure(code=200, message=":)")) # => ["ok", ":)"]
"""

from collections import namedtuple
from .langhelpers import ClassStoreDecoratorFactory

class NotComprehensive(Exception):
    pass

dispatchmethod = ClassStoreDecoratorFactory(
    cache_name="_dispatch_method_name_list", 
    cache_factory=set,
    cache_convert=lambda x : x.__name__,
    value_convert=staticmethod
)

def match_dispatch(cls, target):
    tag = target.__class__.__name__
    return getattr(cls, tag)(*target)

class Match(object):
    __new__ = match_dispatch

class ADTTypeFactory(object):
    def __init__(self, tag, dispatch_function=match_dispatch):
        self.tag = tag
        self.members = {}
        self.dispatch_function = dispatch_function

    def as_member(self, cls):
        name = cls.__name__
        self.members[name] = cls
        return cls

    def is_comprehensive(self, candidates):
       return (all(m in candidates for m in self.members.keys())
               and len(candidates) == len(self.members))

    def validation(self, cls):
        candidates = list(dispatchmethod.get_candidates(cls))
        if not self.is_comprehensive(candidates):
            raise NotComprehensive("{} != {}".format(candidates, self.members.keys()))
        return cls

    def as_match_class(self, cls):  ##side effect!!
        cls.__new__ = self.dispatch_function
        return self.validation(cls)

    def __call__(self, name, fields):
        return self.as_member(namedtuple(name, fields))

    dispatchmethod = dispatchmethod

