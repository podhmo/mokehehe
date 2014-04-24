# -*- coding:utf-8 -*-
from pyramid.exceptions import ConfigurationError
from mokehehe.configuration.interfaces import ILazyTemplatePool, ILazyTemplate

class LazyTemplate(object):
    def __init__(self, name, template):
        self.name = name
        self.template = template
        self.delayed_actions = []

    def __repr__(self):
        return "<LazyTemplate[{self.name}] => {self.template}>".format(self=self)

    def execute_actions(self):
        for ac in self.delayed_actions:
            ac()
        self.delayed_actions = []

    def is_prepared(self):
        return self.template is not None

    def add_delayed(self, ac):
        self.delayed_actions.append(ac)


def prepare_lazy_template(config, marker_name):
    pool = config.registry.queryUtility(ILazyTemplatePool)
    if pool is None:
        pool = set()
        config.registry.registerUtility(set(), ILazyTemplatePool)

    name = marker_name
    lazy_template = config.registry.queryUtility(ILazyTemplate, name=name)
    if lazy_template is None:
        lazy_template = LazyTemplate(name=name, template=None)
        config.registry.registerUtility(lazy_template, ILazyTemplate, name=name)
        pool.add(lazy_template)

    def validation():
        if len(lazy_template.delayed_actions) > 0:
            raise ConfigurationError("{} is not associated".format(lazy_template))
    config.action(None, validation)
    return lazy_template

def add_lazy_template(config, name, template):
    lazy_template = prepare_lazy_template(config, name)
    lazy_template.template = template
    config.registry.registerUtility(lazy_template, ILazyTemplate, name=name)

    lazy_template.execute_actions()

def add_lazy_view(config, view=None, **kwargs):
    marker_name = kwargs["renderer"]
    lazy_template = prepare_lazy_template(config, marker_name)

    def register():
        new_kwargs = kwargs.copy()
        new_kwargs["renderer"] = lazy_template.template
        config.add_view(view, **new_kwargs)

    if lazy_template.is_prepared():
        register()
    else:
        lazy_template.add_delayed(register)

