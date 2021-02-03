import asyncio
from enum import IntEnum
import yaml

__all__ = ('Function', 'Filters', 'Property',
           'Status', 'Source',
           'Eval', 'PyEval')


class Function(yaml.YAMLObject):
    """ Object whose can be evaluated by the engine. """
    yaml_tag = '!function'
    result = None

    @classmethod
    def from_yaml(cls, loader, node):
        value = node.value
        if isinstance(node.value, str):
            return cls(node.value)
        elif hasattr(node.value, '__iter__'):
            values = (
                loader.construct_object(v) if isinstance(v, yaml.Node) else v
                for v in node.value
            )
            return cls(*values)
        return super().from_yaml(loader, node)

    @classmethod
    def to_yaml(cls, dumper, data):
        pass
        # note: bug with __reduce__ex__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __getstate__(self):
        return self.__dict__

    async def eval(self, engine, **kwargs):
        """ Evaluate function and return computed value.  """
        return None


class Filters(Function):
    """
    Function chaining multiple filters evaluation on the provided `data`.
    """
    yaml_tag = '!filters'
    filters = None

    def __init__(self, *filters):
        self.filters = filters

    async def eval(self, engine, data=None, **kwargs):
        for filter in self.filters:
            if isinstance(filter, Function):
                data = await filter.eval(engine, data=data, **kwargs)
            else:
                data = filter
        return data


class Property(Filters):
    """
    From a source (data path or Source), retrieve and apply filters to
    result.

    Property must be evaluable without calling arguments.

    Source is evaluated using `eval(*self.args, **self.kwargs)`.
    """
    yaml_tag = '!property'
    source = None
    args, kwargs = None, None
    result = None

    def __init__(self, source, *filters, args=None, kwargs=None):
        self.source = source
        self.args, self.kwargs = args or {}, kwargs or {}
        super().__init__(*filters)

    async def eval_source(self, engine, no_cache=True, **kwargs):
        source = await engine.resolve(self.source, no_cache=no_cache) \
            if isinstance(self.source, str) else self.source
        return await engine.eval(source, *self.args, no_cache=no_cache,
                                 **self.kwargs)

    async def eval(self, engine, no_cache=True, **kwargs):
        if no_cache or self.result is None:
            data = await self.eval_source(engine, no_cache=no_cache, **kwargs)
            self.result = await super().eval(engine, data)
        return self.result


class Status(IntEnum):
    Fetching = 0x01
    Fetched = 0x02
    Error = 0x10


class Source(Property):
    """
    Provides data from an external source.
    """
    status = Status.Empty

    async def fetch(self, source):
        """
        Fetch and return data from source. Raise `Status` when an error
        occurs.
        """
        return None

    async def eval_source(self, engine, **kwargs):
        if self.status == Status.Fetching:
            # if already fetching, await for the result to be fetched
            while self.status == Status.Fetching:
                await asyncio.sleep(0)
            return self.result

        self.status = Status.Fetching
        try:
            # TODO: source from arg
            self.status = Status.Fetched
            return await self.fetch(self.source)
        except Exception as err:
            self.status = Status.Error
            raise err


class Eval(Function):
    """ Evaluate a function by path. """
    yaml_tag = '!eval'
    path = ''

    def __init__(self, path):
        self.path = path

    async def eval(self, engine, **kwargs):
        return await engine.eval_path(self.path, *args, **kwargs)


class PyEval(Function):
    """
    Compile and call python expression, eval's `kwargs` will be used as
    local namespace.
    """
    yaml_tag = '!python'
    code = None

    def __init__(self, code, filename='<string>'):
        self.code = compile(code, filename, 'eval')

    def __setstate__(self, d):
        if isinstance(d.get('code'), str):
            d['code'] = compile(d['code'], d.get('filename', '<string>'),
                                'eval')
        super().__setstate__(d)

    async def eval(self, engine, **kwargs):
        return eval(self.code, globals(), kwargs)



