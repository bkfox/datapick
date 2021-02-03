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

    def __init__(self, path):
        self.path = path

    async def fetch(self):
        with open(self.path) as file:
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

    async def fetch(self):
        buffer = await super().fetch()
        return yaml.load(buffer, yaml.Loader)


class Http(Source):
    """ Data source fetched from Http request """
    yaml_tag = '!http'

    session = None
    url = None
    headers = None

    def __init__(self, url):
        self.url = url

    async def fetch(self):
        with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                self.headers = response.headers
                if response.status == 200:
                    return await response.text()
                # TODO: handling redirections
                raise ConnectionError(response.status, "http response error")

