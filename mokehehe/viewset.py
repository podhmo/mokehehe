# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.exceptions import ConfigurationError
from mokehehe.interfaces import IDelayedRendererPool, IDelayedRenderer

class DelayedRenderer(object):
    def __init__(self, name, renderer):
        self.name = name
        self.renderer = renderer
        self.delayed_actions = []

    def __repr__(self):
        return "<DelayedRenderer[{self.name}] => {self.renderer}>".format(self=self)

    def execute_actions(self):
        for ac in self.delayed_actions:
            ac()
        self.delayed_actions = []

    def is_prepared(self):
        return self.renderer is not None

    def add_delayed(self, ac):
        self.delayed_actions.append(ac)


def prepare_delayed_renderer(config, marker_name):
    pool = config.registry.queryUtility(IDelayedRendererPool)
    if pool is None:
        pool = set()
        config.registry.registerUtility(set(), IDelayedRendererPool)

    name = marker_name
    delayed_renderer = config.registry.queryUtility(IDelayedRenderer, name=name)
    if delayed_renderer is None:
        delayed_renderer = DelayedRenderer(name=name, renderer=None)
        config.registry.registerUtility(delayed_renderer, IDelayedRenderer, name=name)
        pool.add(delayed_renderer)

    def validation():
        if len(delayed_renderer.delayed_actions) > 0:
            raise ConfigurationError("{} is not associated".format(delayed_renderer))
    config.action(None, validation)
    return delayed_renderer

def add_delayed_renderer(config, name, renderer):
    delayed_renderer = prepare_delayed_renderer(config, name)
    delayed_renderer.renderer = renderer
    config.registry.registerUtility(delayed_renderer, IDelayedRenderer, name=name)

    delayed_renderer.execute_actions()

def add_delayed_view(config, view=None, **kwargs):
    marker_name = kwargs["renderer"]
    delayed_renderer = prepare_delayed_renderer(config, marker_name)

    def register():
        new_kwargs = kwargs.copy()
        new_kwargs["renderer"] = delayed_renderer.renderer
        config.add_view(view, **new_kwargs)

    if delayed_renderer.is_prepared():
        register()
    else:
        delayed_renderer.add_delayed(register)

class delayed_view_config(view_config): #sorry, i use inheritance
    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_delayed_view(view=ob, **settings)

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

def includeme(config):
    config.add_directive("add_delayed_view", add_delayed_view)
    config.add_directive("add_delayed_renderer", add_delayed_renderer)
