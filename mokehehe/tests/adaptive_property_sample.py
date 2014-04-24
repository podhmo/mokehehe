# -*- coding:utf-8 -*-
from .test_adaptive_property import A

@A.y.transform
def y(val):
    return [val, val]

@A.params.transform_once
def params(params):
    params.append("vvvv")
    return params

