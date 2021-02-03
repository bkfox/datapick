import asyncio
from enum import IntEnum
from itertools import accumulate

import yaml

from .base import Source

__all__ = ('File', 'Include', 'Http')


class File(Source):
    """ Data source fetched from file. """
    yaml_tag = '!file'
    chunk_size = 1024*256

    async def fetch(self, source):
        with open(source) as file:
            chunk = file.read(self.chunk_size)
            buffer = chunk
            while len(chunk) == self.chunk_size:
                await asyncio.sleep(0)
                chunk = file.read(self.chunk_size)
                buffer += chunk
            return buffer


class Include(File):
    """
    Include other datapick description file. Do not use it to load
    untrusted data.
    """
    yaml_tag = '!include'

    def __init__(self, path):
        self.path = path

    async def fetch(self, source):
        buffer = await super().fetch(source)
        return yaml.load(buffer, yaml.Loader)


class Http(Source):
    """ Data source fetched from Http request """
    yaml_tag = '!http'

    # FIXME: for multiple sources, save self.session

    async def fetch(self, source):
        with aiohttp.ClientSession() as session:
            async with session.get(source) as response:
                self.headers = response.headers
                return { "headers": response.headers,
                         "status": response.status,
                         "data": await response.text() }
                # TODO: handling redirections

