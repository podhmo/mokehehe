# -*- coding:utf-8 -*-
from mokehehe.configuration.interfaces import IAdaptiveTransform

def includeme(config):
    config.add_directive("add_transform", ".adaptive_property.add_transform")
    config.add_directive("add_transform_once", ".adaptive_property.add_transform_once")

    config.add_directive("add_lazy_view", ".viewset.add_lazy_view")
    config.add_directive("add_lazy_template", ".viewset.add_lazy_template")
