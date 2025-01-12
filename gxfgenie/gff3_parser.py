"""
GFF3 parser
"""
# Copyright 2025-2025 Mark Diekhans

import re
from gxfgenie.errors import GxfGenieParseError
from gxfgenie.gxf_rec import GxfAttrs
from gxfgenie.gxf_parser import GxfParser

# split attributes field
split_attr_col_re = re.compile(r"; *")

# Parses `attr=val`
_split_attr_re = re.compile(r"^([a-zA-Z_]+)=(.+)$")

# splits multi-value attributes
_split_multi_var_re = re.compile(",")


class Gff3Parser(GxfParser):
    """
    """

    def _split_multi_val_attr(self, val_str):
        vals = []
        for val in _split_multi_var_re.split(val_str):
            vals.append(val)
        return tuple(vals)

    def _parse_attr_val(self, attr_str, attrs):
        match = self.split_attr_re.match(attr_str)
        if match is None:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"Can't parse attribute/value: `{attr_str}'")
        attr = match.group(1)
        val = match.group(2)
        if ',' in val:
            val = self._split_multi_val_attr(val)
        setattr(attrs, attr, val)

    def parse_attrs(self, attrs_str):
        """
        Parse the attributes and values.
        """
        attrs = GxfAttrs()
        for attr_str in self.split_attr_col_re.split(attrs_str):
            if len(attr_str) > 0:
                self.__parse_attr_val(attr_str, attrs)
        return attrs
