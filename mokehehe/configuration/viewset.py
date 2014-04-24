# -*- coding:utf-8 -*-
from pyramid.exceptions import ConfigurationError
from mokehehe.configuration.interfaces import ILazyTemplatePool, ILazyTemplate

LAST_OF_CONFIG = 9999

class LazyTemplate(object):
    def __init__(self, name, template):
        self.name = name
        self.template = template

    def __repr__(self):
        return "<LazyTemplate[{self.name}] => {self.template}>".format(self=self)

def prepare_lazy_template(config, marker_name):
    pool = config.registry.queryUtility(ILazyTemplatePool)
    if pool is None:
        pool = set()
        config.registry.registerUtility(set(), ILazyTemplatePool)

    name = marker_name
    lazy_template = config.registry.queryUtility(ILazyTemplatePool, name=name)
    if lazy_template is None:
        lazy_template = LazyTemplate(name=name, template=None)
        config.registry.registerUtility(lazy_template, ILazyTemplate, name=name)
        pool.add(lazy_template)
    return lazy_template

def add_lazy_template(config, name, template):
    lazy_template = prepare_lazy_template(config, name)
    lazy_template.template = template
    config.registry.registerUtility(lazy_template, ILazyTemplatePool, name=name)

def add_lazy_view(config, view=None, name="", **kwargs):
    name = kwargs["renderer"]
    lazy_template = prepare_lazy_template(config, name)

    def register():
        lazy_template = config.registry.queryUtility(ILazyTemplate, name=name)
        if lazy_template.template is None:
            raise ConfigurationError("{} is not associated".format(lazy_template))
        new_kwargs = kwargs.copy()
        new_kwargs["renderer"] = lazy_template.template
        config.add_view(view, name=name, **new_kwargs)
    config.action(None, register, order=LAST_OF_CONFIG)
