"""
GxfRecord parsed from either GTF or GFF3 file.
"""
# Copyright 2025-2025 Mark Diekhans
from abc import ABC, abstractmethod

class GxfAttrs:
    """
    Attributes for GTF/GFF3 records.  Attribute names are fields of
    the object.  If an attribute has multiple values, it can be stored as a list.
    Conversion to lists is specified by the user of the library.
    """
    pass

class GxfRecord(ABC):
    """
    One record of a GTF or GFF3 file. Extended to get an implementation of __str__
    that returns a record in the correct format.
    """
    __slots__ = ("seqname", "source", "feature", "start", "end", "score",
                 "strand", "phase", "attrs", "line_number")

    def __init__(self, seqname, source, feature, start, end, score, strand, phase, attrs, *, line_number=None):
        self.seqname = seqname
        self.source = source
        self.feature = feature
        self.start = start
        self.end = end
        self.score = score
        self.strand = strand
        self.phase = phase
        self.attrs = attrs
        self.line_number = line_number

    @abstractmethod
    def __str__(self):
        """format-specific record conversion"""
        pass


class GxfMeta:
    """
    Metadata value (after ##)
    """
    __slots__ = ("value", "line_number")

    def __init__(self, value, *, line_number=None):
        self.value = value
        self.line_number = line_number
