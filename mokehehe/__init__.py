# -*- coding:utf-8 -*-
from mokehehe.interfaces import IAdaptiveTransform

def includeme(config):
    config.add_directive("add_transform", ".adaptive_property.add_transform")
    config.add_directive("add_transform_once", ".adaptive_property.add_transform_once")

    config.add_directive("add_delayed_view", ".viewset.add_delayed_view")
    config.add_directive("add_delayed_renderer", ".viewset.add_delayed_renderer")
