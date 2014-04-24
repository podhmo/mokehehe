# -*- coding:utf-8 -*-
from pyramid.view import view_config
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

class lazy_view_config(view_config): #sorry, i use inheritance
    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_lazy_view(view=ob, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped
