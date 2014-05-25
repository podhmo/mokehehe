# -*- coding:utf-8 -*-
import unittest


class ViewObjectNoChange(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from mokehehe.viewobject import Mapper
        return Mapper(*args, **kwargs)

    def test_it(self):
        from mokehehe.viewobject import parse_get

        class Ob(object):
            def __init__(self, n):
                self.n = n

            def foo(self):
                return "foo" * self.n

        MappedOb = self._makeOne(parse_get)(Ob)

        target = MappedOb(3)
        self.assertEqual(target.n, 3)
        self.assertEqual(target.foo(), "foofoofoo")


class ViewObjectTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from mokehehe.viewobject import MapperButModifyClass
        return MapperButModifyClass(*args, **kwargs)

    def test_match_dict_values__are_instance_attribute(self):
        from mokehehe.viewobject import parse_get

        class Ob(object):
            def __init__(self, x):
                self.x = x
        MappedOb = self._makeOne(parse_get)(Ob)

        class request(object):
            matchdict = {"x": 10}

        context = None
        target = MappedOb(context, request)
        self.assertEqual(target.x, 10)

    def test_type_converter(self):
        from mokehehe.viewobject import parse_get

        class Ob(object):
            def __init__(self, x=int):
                self.x = x
        MappedOb = self._makeOne(parse_get)(Ob)

        class request(object):
            matchdict = {"x": "10"}

        context = None
        target = MappedOb(context, request)
        self.assertEqual(target.x, 10)

    def test_begin_parse_reading_request_GET(self):
        from mokehehe.viewobject import parse_get

        test = self
        marker = object()

        class Ob(object):
            def __call__(self, x):
                test.assertEqual(x, 10)
                return marker
        MappedOb = self._makeOne(begin=parse_get)(Ob)

        class request(object):
            GET = {"x": 10}
        context = None

        target = MappedOb(context, request)
        result = target()
        self.assertEqual(result, marker)

    def test_end_response_Branching(self):
        from mokehehe.viewobject import parse_get
        from miniadt import ADTTypeProvider, dispatchfunction

        Result = ADTTypeProvider("Result")
        Success = Result("Success", "val")
        Failure = Result("Failure", "val")

        @Result.match
        class ResultDispatch(object):
            @dispatchfunction
            def Success(val):
                return {"val": val, "status": 200}

            @dispatchfunction
            def Failure(val):
                return {"val": val, "status": 400}

        class Ob(object):
            def __call__(self, x):
                return Success(val=x * x)

        MappedOb = self._makeOne(parse_get, ResultDispatch)(Ob)

        class request(object):
            GET = {"x": 10}
        context = None

        target = MappedOb(context, request)
        result = target()

        self.assertEqual(result, {"val": 100, "status": 200})

    def test_initialize_begin_end(self):
        from mokehehe.viewobject import parse_json_body

        class Ob(object):
            def __init__(self, object_id):
                self.object_id = object_id

            def __call__(self, x):
                return self.object_id * x

        def tojson(v):
            return {"value": v}

        MappedOb = self._makeOne(parse_json_body, tojson)(Ob)

        class request(object):
            matchdict = {"object_id": 10}
            json_body = {"x": 2}

        context = None

        target = MappedOb(context, request)
        result = target()
        self.assertEqual(result, {"value": 20})


from zope.interface import Interface, directlyProvides

class INihongoRequest(Interface):
    pass


class IntegrationWithConfiguratorTests(unittest.TestCase):
    def callView(self, config, path, matchdict=None, GET=None, POST=None, iface=None):
        from pyramid.router import Router
        from pyramid.testing import DummyRequest

        router = Router(config.registry)
        request = DummyRequest(path=path, registry=config.registry)
        request.matchdict = matchdict or {}
        if GET:
            request.GET = GET
        if POST:
            request.POST = POST
        if iface:
            directlyProvides(request, iface)
        return router.handle_request(request)

    def test_it(self):
        from pyramid.testing import testConfig
        from mokehehe.viewobject import Mapper, parse_get, viewobject_method

        def todict(v):
            return {"value": v}

        with testConfig() as config:
            class Ob(object):
                def __call__(self, message):
                    return message * 2

                @viewobject_method
                def nihongo(self):
                    return "hai"

            config.include("mokehehe.viewobject")
            config.add_route("hello", "/")
            MOb = config.add_mapped_viewobject(Mapper(parse_get, todict), Ob)
            self.assertIsNotNone(MOb)
            config.add_view(MOb, route_name="hello", renderer="json")
            config.add_view(MOb, route_name="hello", request_type=INihongoRequest, attr="nihongo", renderer="json")
            config.commit()

            result = self.callView(config, "/hello", GET={"message": "hello"})
            self.assertEqual(result.body.decode("utf-8"), u'{"value": "hellohello"}')

            result = self.callView(config, "/hello", iface=INihongoRequest, GET={})
            self.assertEqual(result.body.decode("utf-8"), u'{"value": "hai"}')

