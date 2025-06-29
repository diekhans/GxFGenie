"""
GFF3 parser
"""
# Copyright 2025-2025 Mark Diekhans

import re
from urllib.parse import quote, unquote
from gxfgenie.errors import GxfGenieParseError, GxfGenieFormatError
from gxfgenie.gxf_record import GxfAttrs, GxfRecord, gxf_attr_add, str_or_dot
from gxfgenie.gxf_parser import GxfParser

# split attributes field
_split_attr_col_re = re.compile(r"; *")

# Parses `attr=val`
_split_attr_re = re.compile(r"^([^=]+)=(.+)$")

# splits multi-value attributes
_split_multi_var_re = re.compile(",")

# seqname characters that do not need to be escaped and safe for encoding
_seqname_valid_re = re.compile(r'^[a-zA-Z0-9.:^*$@!+_?\-\|]+$')
_seqname_safe = ':^*$@!+?|'

# other column that must be escaped, and safe for encoding
#  tab, newline, carriage return, percent, and control characters
_other_quote_re = re.compile(r'[\t\n\r\x00-\x1F\x7F%]|%(?:0[0-9A-F]|1[0-9A-F]|7F|25)')
_other_safe = ':?#[]@!$&\'()*+,;=/'

# column-9 ones that must be escaped
#  adds semicolon, equals, ampersand, and comma
_col9_quote_re = re.compile(r'[;=&,]|' + _other_quote_re.pattern)
_col9_safe = ':?#[]@!$\'()*+,/'

def _quote_seqname(seqname):
    if not _seqname_valid_re.fullmatch(seqname):
        return quote(seqname, safe=_seqname_safe)
    else:
        return seqname

def _quote_other(value):
    if _other_quote_re.search(value):
        return quote(value, safe=_other_safe)
    else:
        return value

def _quote_col9(value):
    if _col9_quote_re.search(value):
        return quote(value, safe=_col9_safe)
    else:
        return value

class Gff3Attrs(GxfAttrs):
    """ GFF3 attributes of a record"""

    def __str__(self):
        return gff3_format_attrs(self)

class Gff3Record(GxfRecord):
    "A GFF3 record"

    def __str__(self):
        """convert to tab-separate line"""

        return '\t'.join([_quote_seqname(self.seqname),
                          _quote_other(self.source),
                          _quote_other(self.feature),
                          str(self.start),
                          str(self.end),
                          str_or_dot(self.score),
                          str_or_dot(self.strand),
                          str_or_dot(self.phase),
                          str(self.attrs)])

class Gff3Parser(GxfParser):
    """
    Parse a GTF file
    """

    def _split_multi_val_attr(self, val_str):
        return tuple([unquote(value)
                      for value in _split_multi_var_re.split(val_str)])

    def _parse_attr_val(self, attr_str, attrs):
        match = _split_attr_re.match(attr_str)
        if match is None:
            raise GxfGenieFormatError(f"Can't parse attribute=value: `{attr_str}'")
        name = match.group(1)
        value = match.group(2)
        if ',' in value:
            value = self._split_multi_val_attr(value)
        else:
            value = unquote(value)
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
        return Gff3Record(unquote(seqname), unquote(source), unquote(feature),
                          start, end, score, strand, phase, attrs, line_number=line_number)

def _format_attr(attr):
    name = _quote_col9(attr.name)
    values = attr.value
    if isinstance(values, str):
        values = [values]
    values = [_quote_col9(v) for v in values]
    return f"{name}=" + ",".join(values)

def gff3_format_attrs(attrs):
    """
    Format a GtfAttrs object into a valid GTF attributes string.
    """
    attrs_strs = []
    for attr in attrs.values():
        attrs_strs.append(_format_attr(attr))
    return ";".join(attrs_strs)
