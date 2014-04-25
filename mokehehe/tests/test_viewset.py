# -*- coding:utf-8 -*-
import unittest
import contextlib

class AddViewDelayedTests(unittest.TestCase):
    def callView(self, config, path):
        from pyramid.router import Router
        from pyramid.testing import DummyRequest

        router = Router(config.registry)
        request = DummyRequest(path=path, registry=config.registry)
        return router.handle_request(request)

    @contextlib.contextmanager
    def prepare(self):
        from pyramid.testing import testConfig
        with testConfig(autocommit=False) as config:
            config.include("mokehehe") #split modules?
            yield config

    def test_it__add_view_add_renderer__ok(self):
        with self.prepare() as config:
            def view(context, request):
                return {"hope": None}

            config.add_route("top", "/")
            config.add_delayed_view(view, route_name="top", renderer=":TBD:")
            config.add_delayed_renderer(":TBD:", "json")
            config.commit()

            ## call view actually 
            result = (self.callView(config, "/").body).decode("utf-8")
            self.assertEqual(result, u'{"hope": null}')


    def test_it__add_renderer_add_view__ok(self):
        with self.prepare() as config:
            def view(context, request):
                return {"hope": None}

            config.add_route("top", "/")
            config.add_delayed_renderer(":TBD:", "json")
            config.add_delayed_view(view, route_name="top", renderer=":TBD:")
            config.commit()

            ## call view actually 
            result = (self.callView(config, "/").body).decode("utf-8")
            self.assertEqual(result, u'{"hope": null}')


    def test_it__missing_renderer__raise_ConfigurationError(self):
        from pyramid.exceptions import ConfigurationError
        with self.prepare() as config:
            def view(context, request):
                return {"hope": None}

            config.add_route("top", "/")
            config.add_delayed_view(view, route_name="top", renderer=":TBD:")
            with self.assertRaisesRegex(ConfigurationError,  "not associated"):
                config.commit()

