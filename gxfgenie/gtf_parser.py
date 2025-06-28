"""
GTF parser
"""
# Copyright 2025-2025 Mark Diekhans
import re
from gxfgenie.errors import GxfGenieFormatError
from gxfgenie.gxf_record import GxfAttrs, GxfRecord, gxf_attr_add
from gxfgenie.gxf_parser import GxfParser

# split attributes field
# Will not currently work if attr has quoted space or ;
_split_attr_col_re = re.compile(r"; *")

# Parses `attr "strval"' or `attr numval'.
_split_attr_re = re.compile(r"^([a-zA-Z_]+) +((\"(.+)\")|([0-9]+))$")


class GtfAttrs(GxfAttrs):
    """GTF attributes of a record"""

    def __str__(self):
        return gtf_format_attrs(self)

class GtfRecord(GxfRecord):
    "A GTF record"
    pass

class GtfParser(GxfParser):
    """
    Parse a GTF file.
    """
    def _parse_attr_val(self, attr_str, attrs):
        match = _split_attr_re.match(attr_str)
        if match is None:
            raise GxfGenieFormatError(f"Can't parse attribute/value: `{attr_str}'")
        name = match.group(1)
        value = match.group(5) if match.group(5) is not None else match.group(4)
        gxf_attr_add(attrs, self.attrs_cached, name, value)

    def parse_attrs(self, attrs_str):
        """
        Parse the attributes and values.
        """
        attrs = GtfAttrs()
        for attr_str in _split_attr_col_re.split(attrs_str):
            if len(attr_str) > 0:
                self._parse_attr_val(attr_str, attrs)
        return attrs

    def create_record(self, seqname, source, feature, start, end, score, strand, phase, attrs, *, line_number=None):
        "create a GtfRecord object"
        return GtfRecord(seqname, source, feature, start, end, score, strand, phase, attrs, line_number=line_number)


def _format_attr(attr, value):
    # quote if not a number and add ;
    if value.isdigit():
        return f'{attr.name} {value};'
    else:
        return f'{attr.name} "{value}";'

def gtf_format_attrs(attrs):
    """
    Format a GtfAttrs object into a valid GTF attributes string.
    """
    attrs_strs = []
    for attr in attrs.values():
        for ival in range(0, len(attr)):
            attrs_strs.append(_format_attr(attr, attr[ival]))
    return " ".join(attrs_strs)
