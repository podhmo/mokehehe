# -*- coding:utf-8 -*-
import unittest

class VariantTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mokehehe.miniadt import ADTTypeFactory
        cls.Result = ADTTypeFactory("Result")
        cls.Failure = cls.Result("Failure", "code message")
        cls.Success = cls.Result("Success", "value")

    def _getTarget(self):
        from mokehehe.miniadt import dispatchmethod, Match
        @self.Result.validation
        class Match0(Match):
            @dispatchmethod
            def Failure(code, message):
                return ["oops", code, message]

            @dispatchmethod
            def Success(value):
                return ["ok", value]
        return Match0


    def test_comprehesive(self):
        self.assertTrue(self.Result.is_comprehensive(["Failure", "Success"]))

    def test_comprehesive__include_missing_type(self):
        self.assertFalse(self.Result.is_comprehensive(["Failure", "Success", "Another"]))

    def test_success(self):
        target = self._getTarget()
        result = target(self.Success('{"result": "good"}'))
        self.assertEqual(result, ["ok", '{"result": "good"}'])

    def test_failure(self):
        target = self._getTarget()
        result = target(self.Failure(404, "not found"))
        self.assertEqual(result, ["oops", 404, "not found"])

    def test_validation__failure(self):
        from mokehehe.miniadt import ADTTypeFactory, NotComprehensive

        target = self._getTarget()

        Another = ADTTypeFactory("Another")
        Another("Item", "name value")

        with self.assertRaises(NotComprehensive):
            Another.validation(target)

