# -*- coding:utf-8 -*-
import unittest

class RegisteringComponentIntegrationTests(unittest.TestCase):
    def test_call_directive_manytimes(self):
        from pyramid.testing import testConfig

        with testConfig() as config:
            config.include("mokehehe.registering")

            builder = config.registering_builder("foo", resource_factory=object())
            builder2 = config.registering_builder("foo", resource_factory=object())
            self.assertEqual(builder2, builder)


    def test_it(self):
        from pyramid.testing import testConfig
        from pyramid.interfaces import IRouteRequest, IViewClassifier, IView
        from zope.interface import Interface

        class model:
            name = "model"

        def resource_factory(target):
            self.assertEqual(target, model)
            return target

        def create_route_name(target, fullname):
            return "{}.{}".format(fullname, target.name)

        def create_path(target, fullname):
            return "/{}/{}".format(fullname.replace(".", "/"), target.name)

        def myview(context, request):
            return "ok"

        with testConfig() as config:
            config.include("mokehehe.registering")
            builder = config.registering_builder("foo", resource_factory=resource_factory)
            with builder.sub("bar", route_name_craete=create_route_name, path_create=create_path) as view_builder:
                view_builder.build(view=myview).update(renderer="json")

            ## call
            builder(model)


            self.assertEqual(len(config.get_routes_mapper().get_routes()), 1)

            for route in config.get_routes_mapper().get_routes():
                ## route is defined?
                self.assertEqual(route.name, "foo.bar.model")
                self.assertEqual(route.pattern, "/foo/bar/model")

                ## view is defined?
                request_iface = config.registry.queryUtility(IRouteRequest, name=route.name)
                self.assertTrue(request_iface)

                discliminator = (IViewClassifier, request_iface, Interface)
                view_callable = config.registry.adapters.lookup(discliminator, IView, name='', default=None)
                self.assertTrue(view_callable)



    def test_multiple(self):
        from pyramid.testing import testConfig

        class model:
            name = "model"
        class model2:
            name = "model2"

        def resource_factory(target):
            return target

        def create_route_name(target, fullname):
            return "{}.{}".format(fullname, target.name)

        def create_path(target, fullname):
            return "/{}/{}".format(fullname.replace(".", "/"), target.name)

        def myview(context, request):
            return "ok"

        with testConfig() as config:
            config.include("mokehehe.registering")
            builder = config.registering_builder("foo", resource_factory=resource_factory)
            with builder.sub("bar", route_name_craete=create_route_name, path_create=create_path) as view_builder:
                view_builder.build(view=myview).update(renderer="json")

            ## call
            builder(model)
            builder(model2)

            self.assertEqual(len(config.get_routes_mapper().get_routes()), 2)


