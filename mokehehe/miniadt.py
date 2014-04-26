# -*- coding:utf-8 -*-
"""
## define mini adt
Result = ADTTypeFactory("Result")
Failure = Result("Failure", "code message")
Success = Result("Success", "value")

## use mini adt
@self.Result.validation
class match(Match):
    @dispatchmethod
    def Failure(code, message):
        return ["oops", code, message]

    @dispatchmethod
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

class ADTTypeFactory(object):
    def __init__(self, tag):
        self.tag = tag
        self.members = {}

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

    def __call__(self, name, fields):
        return self.as_member(namedtuple(name, fields))

    dispatchmethod = dispatchmethod

class Match(object):
    def __new__(cls, target):
        tag = target.__class__.__name__
        return getattr(cls, tag)(*target)

