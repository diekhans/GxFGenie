"""
GTF parser
"""
# Copyright 2025-2025 Mark Diekhans
import re
from gxfgenie.errors import GxfGenieParseError
from gxfgenie.gxf_rec import GxfAttrs
from gxfgenie.gxf_parser import GxfParser

# split attributes field
# Will not currently work if attr has quoted space or ;
_split_attr_col_re = re.compile(r"; *")

# Parses `attr "strval"' or `attr numval'.
_split_attr_re = re.compile(r"^([a-zA-Z_]+) +((\"(.+)\")|([0-9]+))$")

class GtfParser(GxfParser):
    """
    Parse GTF records.
    """

    def _parse_attr_val(self, attr_str, attrs):
        match = _split_attr_re.match(attr_str)
        if match is None:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"Can't parse attribute/value: `{attr_str}'")
        attr = match.group(1)
        val = match.group(5) if match.group(5) is not None else match.group(4)
        setattr(attrs, attr, val)

    def parse_attrs(self, attrs_str):
        """
        Parse the attributes and values.
        """
        attrs = GxfAttrs()
        for attr_str in _split_attr_col_re.split(attrs_str):
            if len(attr_str) > 0:
                self._parse_attr_val(attr_str, attrs)
        return attrs
