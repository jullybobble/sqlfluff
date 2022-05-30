"""Templater Code."""

from sqlfluff.core.templaters.base import TemplatedFile

# Although these shouldn't usually be instantiated from here
# we import them to make sure they get registered.
from sqlfluff.core.templaters.base import RawTemplater
from sqlfluff.core.templaters.jinja import JinjaTemplater
from sqlfluff.core.templaters.python import PythonTemplater
from sqlfluff.core.templaters.placeholder import PlaceholderTemplater
from sqlfluff.core.templaters.hive import HiveTemplater


def core_templaters():
    """Returns the templater tuples for the core templaters."""
    yield from [RawTemplater, JinjaTemplater, PythonTemplater, PlaceholderTemplater, HiveTemplater]


__all__ = (
    "TemplatedFile",
    "RawTemplater",
    "JinjaTemplater",
    "PythonTemplater",
    "PlaceholderTemplater",
    "HiveTemplater",
    "core_templaters",
)
