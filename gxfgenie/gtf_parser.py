"""
GTF parser
"""
# Copyright 2025-2025 Mark Diekhans
import re
from gxfgenie.errors import GxfGenieParseError
from gxfgenie.gxf_record import GxfAttrs, GxfRecord, gxf_attr_add
from gxfgenie.gxf_parser import GxfParser

# split attributes field
# Will not currently work if attr has quoted space or ;
_split_attr_col_re = re.compile(r"; *")

# Parses `attr "strval"' or `attr numval'.
_split_attr_re = re.compile(r"^([a-zA-Z_]+) +((\"(.+)\")|([0-9]+))$")


class GtfRecord(GxfRecord):
    "A GTF record"

    def __str__(self):
        return gtf_format_rec(self)

class GtfParser(GxfParser):
    """
    Parse a GTF file.
    """
    def _parse_attr_val(self, attr_str, attrs):
        match = _split_attr_re.match(attr_str)
        if match is None:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"Can't parse attribute/value: `{attr_str}'")
        name = match.group(1)
        value = match.group(5) if match.group(5) is not None else match.group(4)
        gxf_attr_add(attrs, self.attrs_cached, name, value)

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

def _format_attr(attr, value):
    # quote if not a number and add ;
    if value.isdigit():
        return f'{attr.name} {value};'
    else:
        return f'{attr.name} "{value}";'

def gtf_format_attrs(attrs):
    """
    Format a GxfAttrs object into a valid GTF attributes string.
    """
    attrs_strs = []
    for attr in attrs.values():
        for ival in range(0, len(attr)):
            attrs_strs.append(_format_attr(attr, attr[ival]))
    return " ".join(attrs_strs)

def gtf_format_rec(rec):
    """format a GTF record"""
    return '\t'.join([rec.seqname,
                      rec.source,
                      rec.feature,
                      str(rec.start),
                      str(rec.end),
                      str(rec.score),
                      rec.strand,
                      rec.phase,
                      gtf_format_attrs(rec.attrs)])
