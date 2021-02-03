"""
Functions taking `data` as input, and returning transformed value.
"""
import itertools
import re

from .base import Function


__all__ = (
    'Join', 'Map', 'Schema',
    'RegSearch', 'RegReplace',
    'Json', 'Yaml', 'Xml',
)


class Join(Function):
    """ Join multiple iterables (to provided data if any) """
    yaml_tag = '!iter.join'

    iters = None
    before = False

    def __init__(self, *iterables, before=False):
        self.iters = iterables

    async def eval(self, engine, data=None, **kwargs):
        def extend(result, iterable):
            result.extend(iterable)
            return result

        result = itertools.accumulate(self.iterables, extend, [])
        return result if data is None else\
            extend(list(data), result) if self.before else \
            extend(result, data)


class Map(Function):
    """
    Map function to iterable value.

    On dict, mapper is called on value.
    On non iterable, mapper is called on complete data value.
    """
    yaml_tag = '!iter.map'

    func = None

    def __init__(self, func):
        self.func = func

    async def eval(self, engine, data=None, **kwargs):
        func = self.func
        if isinstance(data, dict):
            return { k: func.eval(engine, data=v) for k, v in data.items() }
        if hasattr(data, '__iter__') and not isinstance(data, str):
            return [ func.eval(engine, data=v) for k, v in data ]
        return func.eval(engine, data=data)


class Schema(Function):
    """
    Transform data into dict. Fields are specified as `(key, filter)`
    and generated using `filter`.
    """
    yaml_tag = '!dict.schema'

    fields = []

    def __init__(self, fields):
        self.fields = fields

    async def eval(self, engine, data, **kwargs):
        return {key: filter.eval(engine, data=data) for key, filter in self.fields}


class RegSearch(Function):
    """ Search through input text matching provided regular expression. """
    yaml_tag = '!re.search'

    search = ''
    named_groups = False

    def __init__(self, search, named_groups=False):
        self.search, self.named_groups = re.compile(search), named_groups

    def __setstate__(self, d):
        if isinstance(d.get('search'), str):
            d['search'] = re.compile(d['search'])
        super().__setstate__(d)

    async def eval(self, engine, data, **kwargs):
        data = self.search.search(data)
        return None if data is None else \
            data.groupdict() if self.named_groups else data.groups()


class RegReplace(RegSearch):
    """ Search and replace using regular expression. """
    yaml_tag = '!re.replace'

    search = ''
    replace = ''

    def __init__(self, search, replace):
        self.replace = replace
        super().__init__(search)

    async def eval(self, engine, data, **kwargs):
        return self.search.sub(self.replace, data)


class Json(Function):
    """ Parse text from json into data. """
    yaml_tag = '!parse.json'

    async def eval(self, engine, data, **kwargs):
        import json
        return json.loads(data)


class Yaml(Function):
    """ Parse text from yaml into data. """
    yaml_tag = '!parse.yaml'

    async def eval(self, engine, data, **kwargs):
        import yaml
        return yaml.load(data, yaml.SafeLoader)


class Xml:
    """
    Parse XML returning corresponding ElementTree. XPath to children
    object to return can be provided.

    Important!
    About security: https://docs.python.org/3/library/xml.html#xml-vulnerabilities
    About XPath: https://docs.python.org/3/library/xml.etree.elementtree.html#supported-xpath-syntax
    """
    yaml_tag = '!parse.xml'

    path = ''

    def __init__(self, path=''):
        self.path = path

    async def eval(self, engine, data, **kwargs):
        import xml.etree.ElementTree as ET
        root = ET.fromstring(data)
        return root.findall(self.path) if self.path else root

