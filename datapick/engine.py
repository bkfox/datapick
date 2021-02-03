import asyncio
from enum import IntEnum
import yaml

from .base import *

__all__ = ('Engine',)


class Engine:
    """
    Engine reading YAML description and evaluating functions.
    """
    documents = None

    def __init__(self, source=None):
        if source:
            self.load(source)

    def load(self, source):
        self.documents = list(yaml.load_all(source, yaml.Loader))

    def dump(self, source):
        pass

    async def resolve(self, path, no_cache=False, data=None):
        """
        Return item based on path, evaluating properties when required to
        access members.

        Path is a list of parent-child selectors joined by '.'. Selectors
        can be:
        - public attribute name
        - `__getitem__` argument (string or int)
        """
        names = path.split('.')
        data = self.documents if data is None else data
        for name in names:
            if isinstance(data, Property):
                data = await data.eval(self, no_cache=no_cache)

            if name.isdigit():
                data = data[int(name)]
            elif hasattr(data, '__getitem__'):
                data = data[name]
            elif hasattr(data, name):
                if name.startswith('_'):
                    raise KeyError(f'can not access protected member {name}')
                data = getattr(data, name)
            else:
                raise KeyError(f'attribute {name} not found')

        return data

    async def eval(self, data, *args, no_cache=False, flat=False, **kwargs):
        """
        Evaluates provided data, calling `Function`s and callables with
        provided `*args` and `**kwargs`.

        Cache is not used when `no_cache`.
        Result is recursively evaluated when `flat`.
        """
        key = kwargs.pop('_key', None) # protected, used to flatten dicts
        value = await data.eval(self, *args, **kwargs) \
            if isinstance(data, Function) else \
            data(self, *args, **kwargs) if callable(data) else data

        if flat:
            if isinstance(value, dict):
                values = await asyncio.gather(*(
                    self.eval(item, no_cache=no_cache, flat=flat, _key=key)
                    for key, item in value.items()))
                value = { k: v for k, v in values }
            elif isinstance(value, (list, tuple)):
                value = await asyncio.gather(*(
                    self.eval(item, no_cache=no_cache, flat=flat)
                    for item in value))
        return value if key is None else (key, value)

    async def eval_path(self, path, *args, no_cache=False, data=None, **kwargs):
        """
        Evaluate all functions targeted by path.

        If `flat` is true, evaluate all nested Properties before returning
        result.
        """
        data = await self.resolve(path, no_cache=no_cache, data=data)
        return await self.eval(data, *args, no_cache=no_cache, **kwargs)

