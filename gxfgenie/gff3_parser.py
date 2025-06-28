"""
GFF3 parser
"""
# Copyright 2025-2025 Mark Diekhans

import re
import urllib
from gxfgenie.errors import GxfGenieParseError
from gxfgenie.gxf_record import GxfAttrs, GxfRecord, gxf_attr_add
from gxfgenie.gxf_parser import GxfParser

# split attributes field
_split_attr_col_re = re.compile(r"; *")

# Parses `attr=val`
_split_attr_re = re.compile(r"^([a-zA-Z_]+)=(.+)$")

# splits multi-value attributes
_split_multi_var_re = re.compile(",")


class Gff3Attrs(GxfAttrs):
    """ GFF3 attributes of a record"""

    def __str__(self):
        return gff3_format_attrs(self)

class Gff3Record(GxfRecord):
    "A GFF3 record"
    pass

class Gff3Parser(GxfParser):
    """
    Parse a GTF file
    """

    def _split_multi_val_attr(self, val_str):
        return tuple([urllib.parse.unquote(value)
                      for value in _split_multi_var_re.split(val_str)])

    def _parse_attr_val(self, attr_str, attrs):
        match = _split_attr_re.match(attr_str)
        if match is None:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"Can't parse attribute/value: `{attr_str}'")
        name = match.group(1)
        value = match.group(2)
        if ',' in value:
            value = self._split_multi_val_attr(value)
        else:
            value = urllib.parse.unquote(value)
        gxf_attr_add(attrs, self.attrs_cached, name, value)

    def parse_attrs(self, attrs_str):
        """
        Parse the attributes and values.
        """
        attrs = Gff3Attrs()
        for attr_str in _split_attr_col_re.split(attrs_str.strip()):
            if len(attr_str) > 0:
                self._parse_attr_val(attr_str, attrs)
        return attrs

    def create_record(self, seqname, source, feature, start, end, score, strand, phase, attrs, *, line_number=None):
        "create a Gff3Record object"
        return Gff3Record(seqname, source, feature, start, end, score, strand, phase, attrs, line_number=line_number)

def _format_attr(attr):
    values = attr.value
    if isinstance(values, str):
        values = [values]
    escaped = [urllib.parse.quote(v, safe='') for v in values]
    return f"{attr.name}=" + ",".join(escaped)

def gff3_format_attrs(attrs):
    """
    Format a GtfAttrs object into a valid GTF attributes string.
    """
    attrs_strs = []
    for attr in attrs.values():
        for ival in range(0, len(attr)):
            attrs_strs.append(_format_attr(attr, attr[ival]))
    return " ".join(attrs_strs)
