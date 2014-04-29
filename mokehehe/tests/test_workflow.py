# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import unittest

from mokehehe.interfaces import IWorkflowWhen

class IAfterModelCreate(IWorkflowWhen):
    pass

class WorkflowRegistrationTests(unittest.TestCase):
    def test_it(self):
        from pyramid.testing import testConfig

        with testConfig(autocommit=False) as config:
            config.include("mokehehe.workflow")
            config.add_route("foo.list", "/foo/list")
            config.add_route("foo.create", "/foo/create")
            config.get_workflow().register(IAfterModelCreate, from_route_name="foo.create", to_route_name="foo.list")
            config.commit()

    def test_missing_both__exception(self):
        from pyramid.testing import testConfig
        from pyramid.exceptions import ConfigurationError

        with testConfig(autocommit=False) as config:
            config.include("mokehehe.workflow")
            config.get_workflow().register(IAfterModelCreate, "foo.create", "foo.list")
            with self.assertRaisesRegex(ConfigurationError, "route name"):
                config.commit()

    def test_missing_from_route__exception(self):
        from pyramid.testing import testConfig
        from pyramid.exceptions import ConfigurationError

        with testConfig(autocommit=False) as config:
            config.include("mokehehe.workflow")
            config.add_route("foo.list", "/foo/list")
            config.get_workflow().register(IAfterModelCreate, "foo.create", "foo.list")
            with self.assertRaisesRegex(ConfigurationError, "route name"):
                config.commit()

    def test_missing_to_route__exception(self):
        from pyramid.testing import testConfig
        from pyramid.exceptions import ConfigurationError

        with testConfig(autocommit=False) as config:
            config.include("mokehehe.workflow")
            config.add_route("foo.create", "/foo/create")
            config.get_workflow().register(IAfterModelCreate, "foo.create", "foo.list")
            with self.assertRaisesRegex(ConfigurationError, "route name"):
                config.commit()

    def test_bind_multiple(self):
        from pyramid.testing import testConfig

        class IFailure(IWorkflowWhen):
            pass

        with testConfig(autocommit=False) as config:
            config.include("mokehehe.workflow")
            config.add_route("failure", "failure")
            with config.get_workflow().sub(IFailure) as s:
                s("create", "failure")
                s("update", "failure")
                s("show", "failure")

            config.add_route("create", "create")
            config.add_route("update", "update")
            config.add_route("show", "show")
            config.commit()

class WorkflowRuntimeTests(unittest.TestCase):
    def _makeRequest(self, config, environ={}):
        from pyramid.request import Request
        from pyramid.interfaces import IRequestExtensions
        request = Request(environ)
        request.registry = config.registry
        request._set_extensions(config.registry.getUtility(IRequestExtensions))
        return request

    def test_it(self):
        """ on /foo/craete, success redirect is /foo/list """
        from pyramid.testing import testConfig

        with testConfig(autocommit=False) as config:
            config.include("mokehehe.workflow")
            config.add_route("foo.list", "/foo/list")
            config.add_route("foo.create", "/foo/create")
            config.get_workflow().register(IAfterModelCreate, from_route_name="foo.create", to_route_name="foo.list")
            config.commit()

            ## on request time
            request = self._makeRequest(config)
            class route:
                name = "foo.create"
            request.matched_route = route

            self.assertTrue(request.workflow)
            result = request.workflow[IAfterModelCreate].route_path()
            self.assertEqual(result, "/foo/list")
