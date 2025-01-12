"""
GxfRecord parsed from either GTF or GFF3 file.
"""
# Copyright 2025-2025 Mark Diekhans

class GxfAttrs:
    """
    Attributes for GTF/GFF3 records.  Attribute names are fields of
    the object.  If an attribute has multiple values, it can be stored as a list.
    Conversion to lists is specified by the user of the library.
    """
    pass

class GxfRecord:
    """
    One record of a GTF or GFF3 file.
    """
    __slots__ = ("seqname", "source", "feature", "start", "end", "score",
                 "strand", "phase", "attributes", "line_number")

    def __init__(self, seqname, source, feature, start, end, score, strand, phase, gxf_attrs, *, line_number=None):
        self.seqname = seqname
        self.source = source
        self.feature = feature
        self.start = start
        self.end = end
        self.score = score
        self.strand = strand
        self.phase = phase
        self.attrs = gxf_attrs
        self.line_number = line_number


class GxfMeta:
    """
    Metadata value (after ##)
    """
    __slots__ = ("value", "line_number")

    def __init__(self, value, *, line_number=None):
        self.value = value
        self.line_number = line_number
