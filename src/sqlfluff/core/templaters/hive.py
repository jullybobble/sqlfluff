"""Defines the placeholder template."""
import copy
import logging

import regex
from typing import Dict, Optional, Tuple

from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.templaters import PlaceholderTemplater

from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFile,
    TemplatedFileSlice,
)

from sqlfluff.core.templaters.base import RawTemplater

# Instantiate the templater logger
from sqlfluff.core.templaters import placeholder

templater_logger = logging.getLogger("sqlfluff.templater")


class HiveTemplater(RawTemplater):
    """A templater for hivevar with dollar placeholders.

    It parses and substitute hive variable definition of the form

    ```
    SET hivevar:v = 1;
    SEECT ${v};
    ```
    """

    name = "hive"

    def __init__(self, override_context=None, **kwargs):
        self.override_context = override_context or {}

    def process(
        self, *, in_str: str, fname: str, config=None, formatter=None
    ) -> Tuple[Optional[TemplatedFile], list]:
        context = self.get_context(in_str=in_str, config=config)
        print(f'{context=}')
        in_str_without_sets = regex.sub(self.set_pattern, '', in_str, flags=self.flags)

        re = regex.compile(r"\${(?P<param_name>[\w_]+)}|\$(?P<param_name>[\w_]+)", regex.UNICODE)
        assert re

        return PlaceholderTemplater.process_with_context(in_str=in_str_without_sets, fname=fname,
                                                         regex=re, context=context)

    set_pattern = r'SET\s+hivevar:(\w+)\s*=\s*([^;]*);\n?'
    flags = regex.IGNORECASE + regex.DOTALL + regex.UNICODE

    def get_context(self, in_str: str, config: Optional[FluffConfig]):
        # context from config
        if config:
            section = config.get_section((self.templater_selector, self.name, "context"))
            context = (
                # we do a deepcopy in order to avoid modifying the config passed as parameter
                copy.deepcopy(section)
                or {}
            )
        else:
            context = {}

        # update with overrides
        context.update(self.override_context)

        # update the context by iteratively parsing SET hivevar statements and using variables
        # previously defined is any is referenced in the variable definitions

        set_statements = regex.finditer(self.set_pattern, in_str, flags=self.flags)
        inline_var_definitions = dict(set.groups() for set in set_statements)

        def substitute_variables(text):
            """substitute all previously defined variables that might be referenced in the given text"""
            for var_name, var_value in context.items():
                var_regex = r'\$\{' + var_name + r'\}|\$' + var_name
                text = regex.sub(var_regex, str(var_value), str(text))
            return text

        for inline_var_name, inline_var_value in inline_var_definitions.items():
            context[inline_var_name] = substitute_variables(inline_var_value)

        return context
