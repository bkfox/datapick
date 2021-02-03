import os
from unittest import IsolatedAsyncioTestCase

from datapick.engine import *
import datapick.filters


__all__ = ('TestEngine',)


class BaseTestEngine(IsolatedAsyncioTestCase):
    yaml_path = os.path.join(os.path.dirname(__file__), 'test.yaml')
    yaml_source = ''
    engine = None

    def setUp(self):
        if not self.yaml_source:
            with open(self.yaml_path) as source:
                self.yaml_source = source.read()
        self.engine = Engine(self.yaml_source)


class TestEngine(BaseTestEngine):
    emma = None
    shadow = None

    def setUp(self):
        super().setUp()
        self.emma = self.engine.documents[0]['emma']
        self.alexander = self.engine.documents[0]['alexander']
        self.shadow = self.engine.documents[0]['shadow']

    async def test_eval(self):
        result = await self.engine.eval(self.shadow)
        self.assertEqual(result, self.emma)

    async def test_eval_flat(self):
        shadow = await self.engine.eval(self.shadow, flat=True)
        self.assertEqual(shadow["name"], self.emma["name"])
        self.assertEqual(shadow["age"], self.emma["age"])
        self.assertEqual(shadow["friends"][0]["name"], self.alexander["name"])

    async def test_resolve(self):
        item = await self.engine.resolve('0.emma.name')
        self.assertEqual(item, self.emma['name'])

    async def test_resolve_with_eval(self):
        item = await self.engine.resolve('0.shadow.friends.0')
        self.assertEqual(item, self.emma['friends'][0])

        item = await self.engine.resolve('0.shadow.name')
        self.assertEqual(item, self.emma['name'])

    async def test_eval_path(self):
        result = await self.engine.eval_path('0.emma.name')
        self.assertEqual(result, "goldman")

    async def test_filters(self):
        result = await self.engine.eval_path('0.alexander.friends')
        self.assertEqual(result, "johann betrayed")

