from datapick import filters, base
from .engine import BaseTestEngine

__all__ = ('TestFilters', 'TestProperty', 'TestSource',
           'TestPython')


class TestFilters(BaseTestEngine):
    async def test_eval_data_from_args(self):
        function = base.Filters(filters.RegReplace('hello', 'bye'))
        result = await function.eval(self.engine, "hello world")
        self.assertEqual(result, "bye world")

    async def test_eval_const(self):
        function = base.Filters("hello world", filters.RegReplace('hello', 'bye'))
        result = await function.eval(self.engine, "invalid hello")
        self.assertEqual(result, "bye world")


class TestProperty(BaseTestEngine):
    async def test_eval_resolve_source(self):
        function = base.Property("0.emma.name")
        result = await function.eval(self.engine)
        self.assertEqual(result, 'goldman')

    async def test_eval_const(self):
        function = base.Property(1312)
        result = await function.eval(self.engine)
        self.assertEqual(result, 1312)

    async def test_eval_cache(self):
        pass

    # test_eval_native_function


class TestSource(BaseTestEngine):
    async def test_fetch(self):
        pass

    async def test_eval_source(self):
        pass

    async def test_eval_source_fetching(self):
        pass


class TestPython(BaseTestEngine):
    async def test_eval(self):
        function = base.Python("2*2")
        result = await function.eval(self.engine)
        self.assertEqual(result, 4)

    async def test_eval_with_args(self):
        function = base.Filters(base.Python("data * data"))
        result = await function.eval(self.engine, data=2)
        self.assertEqual(result, 4)

