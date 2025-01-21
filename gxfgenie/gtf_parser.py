"""
GTF parser
"""
# Copyright 2025-2025 Mark Diekhans
import re
from gxfgenie.errors import GxfGenieParseError
from gxfgenie.gxf_rec import GxfAttrs, GxfRecord
from gxfgenie.gxf_parser import GxfParser

# split attributes field
# Will not currently work if attr has quoted space or ;
_split_attr_col_re = re.compile(r"; *")

# Parses `attr "strval"' or `attr numval'.
_split_attr_re = re.compile(r"^([a-zA-Z_]+) +((\"(.+)\")|([0-9]+))$")


class GtfRecord(GxfRecord):
    "A GTF record"

    def __str__(self):
        pass


class GtfParser(GxfParser):
    """
    Parse a GTF file.
    """

    def _parse_attr_val(self, attr_str, attrs):
        match = _split_attr_re.match(attr_str)
        if match is None:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"Can't parse attribute/value: `{attr_str}'")
        attr = match.group(1)
        val = match.group(5) if match.group(5) is not None else match.group(4)
        setattr(attrs, attr, val)

    def _parse_attrs(self, attrs_str):
        """
        Parse the attributes and values.
        """
        attrs = GxfAttrs()
        for attr_str in _split_attr_col_re.split(attrs_str):
            if len(attr_str) > 0:
                self._parse_attr_val(attr_str, attrs)
        return attrs

    def parse_rec(self, row):
        """parse on record line of the GTF"""
        return GtfRecord(row[0], row[1], row[2],
                         int(row[3]), int(row[4]),
                         row[5], row[6], row[7],
                         self._parse_attrs(row[8]),
                         line_number=self.line_number)
