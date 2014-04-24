# -*- coding:utf-8 -*-
import unittest

class AddViewLazyTests(unittest.TestCase):
    def callView(self, config, path):
        from pyramid.router import Router
        from pyramid.testing import DummyRequest

        router = Router(config.registry)
        request = DummyRequest(path=path, registry=config.registry)
        return router.handle_request(request)

    def test_it__add_view_add_template(self):
        from pyramid.testing import testConfig
        with testConfig(autocommit=False) as config:
            config.include("mokehehe.configuration") #split modules?
            def view(context, request):
                return {"hope": None}

            config.add_route("top", "/")
            config.add_lazy_view(view, route_name="top", renderer=":TBD:")
            config.add_lazy_template(":TBD:", "json")
            config.commit()

            self.callView(config, "/")

    def test_it__add_template_add_view(self):
        from pyramid.testing import testConfig
        with testConfig(autocommit=False) as config:
            config.include("mokehehe.configuration") #split modules?
            def view(context, request):
                return {"hope": None}

            config.add_route("top", "/")
            config.add_lazy_template(":TBD:", "json")
            config.add_lazy_view(view, route_name="top", renderer=":TBD:")
            config.commit()

            self.callView(config, "/")

    def test_it__missing_template(self):
        from pyramid.testing import testConfig
        from pyramid.exceptions import ConfigurationError

        with testConfig(autocommit=False) as config:
            config.include("mokehehe.configuration") #split modules?
            def view(context, request):
                return {"hope": None}

            config.add_route("top", "/")
            config.add_lazy_view(view, route_name="top", renderer=":TBD:")
            with self.assertRaisesRegex(ConfigurationError,  "not associated"):
                config.commit()

