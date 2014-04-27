# -*- coding:utf-8 -*-
import unittest
from mokehehe.interfaces import  IModelInformation
from mokehehe.langhelpers import DynamicInterfaceFactory
from zope.interface import implementer

_iface_factory = DynamicInterfaceFactory()
def make_iface(cls):
    iface = _iface_factory(cls)
    implementer(iface)(cls)
    return iface

class DummyModel(object):
    name = "dummy"
    id = -1

@implementer(IModelInformation)
class DummyModelInformation(object):
    def __init__(self, o):
        self.o = o

    @property
    def name(self):
        return self.o.__name__

    @property
    def display_name(self):
        return "display_name"

    @property
    def persistent_id(self):
        return self.o.id #hmm

    def get_route_name(self, action_name):
        return "dummy.{}".format(action_name)



class FlowTests(unittest.TestCase):
    def _makeRequest(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(registry=self.config.registry)
        return request

    @classmethod
    def setUpClass(cls):
        from pyramid.testing import setUp
        config = cls.config = setUp()
        config.include("mokehehe.modelinformation")
        config.bind_model_information(DummyModel, DummyModelInformation, iface_factory=make_iface)

        ## xxx:
        config.add_route("dummy.create", "dummy/create")
        config.add_route("dummy.list", "dummy/list")
        config.add_route("dummy.update", "dummy/update/{id}")
        config.add_route("dummy.delete", "dummy/delete/{id}")
        config.add_route("dummy.show", "dummy/show/{id}")

    @classmethod
    def tearDownClass(cls):
        from pyramid.testing import tearDown
        tearDown()

    def test_after_create__success(self):
        from mokehehe.flow import ModelCreateFlow, SuccessRedirect
        from pyramid.httpexceptions import HTTPFound
        request = self._makeRequest()
        dummy = DummyModel()
        result = ModelCreateFlow(SuccessRedirect(request, dummy))

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "/dummy/show/-1")

    def test_after_create_but_not_commit__success(self):
        from mokehehe.flow import ModelCreateFlow, SuccessRedirect
        from pyramid.httpexceptions import HTTPFound
        request = self._makeRequest()
        dummy = DummyModel()
        dummy.id = None
        result = ModelCreateFlow(SuccessRedirect(request, dummy))

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "/dummy/list")

    def test_after_update__success(self):
        from mokehehe.flow import ModelUpdateFlow, SuccessRedirect
        from pyramid.httpexceptions import HTTPFound
        request = self._makeRequest()
        dummy = DummyModel()
        result = ModelUpdateFlow(SuccessRedirect(request, dummy))

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "/dummy/show/-1")

    def test_after_delete__success(self):
        from mokehehe.flow import ModelDeleteFlow, SuccessRedirect
        from pyramid.httpexceptions import HTTPFound
        request = self._makeRequest()
        dummy = DummyModel()
        result = ModelDeleteFlow(SuccessRedirect(request, dummy))

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "/dummy/list")

