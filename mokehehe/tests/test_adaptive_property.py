# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

import unittest
from mokehehe.adaptive_property import Setting, AdaptivePropertyFactory
from mokehehe.tests.interfaces import IA

class A(Setting):
    def __init__(self, request):
        self.request = request
    adaptive_property = AdaptivePropertyFactory(IA)

    x = adaptive_property(["xxxx"])
    y = adaptive_property(["yyyy"])
    params = adaptive_property(["xxx"])

class AdaptivePropertyIntegrationTest(unittest.TestCase):
    def _getTarget(self):
        return A

    @classmethod
    def setUpClass(self):
        from pyramid.testing import setUp
        self.config = setUp()
        self.config.include("mokehehe.adaptive_property")
        self.config.scan("mokehehe.tests.adaptive_property_sample")
        self.config.commit()

    @classmethod
    def tearDownClass(self):
        from pyramid.testing import tearDown
        tearDown()

    def test_it(self):
        a = self._getTarget()(self.config)
        self.assertEqual(a.x, ["xxxx"])

    def test_it2(self):
        a = self._getTarget()(self.config)
        self.assertEqual(a.y, [["yyyy"], ["yyyy"]])

    def test_it3(self):
        a = self._getTarget()(self.config)
        self.assertEqual(a.params, ["xxx", "vvvv"])

