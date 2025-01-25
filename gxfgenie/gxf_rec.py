"""
GxfRecord parsed from either GTF or GFF3 file.
"""
# Copyright 2025-2025 Mark Diekhans
from abc import ABC, abstractmethod
from gxfgenie.objdict import ObjDict

class GxfAttrs:
    """Attributes for GTF/GFF3 records.

    This functions both as dictionary and the attributes can also be accessed
    via the avs (attribute-value) field, were the attributes are field names.

    If an attribute has multiple values, it can be stored as a list.
    Conversion to lists is either implicit, based on added or specified by the
    user of the library.

    """
    def __init__(self):
        self.avs = ObjDict()

    def add(self, name, value):
        """add an attribute and value, if this is the second addition,
        the value is convert to a list"""
        current = self.avs.get(name)
        if current is None:
            self.avs[name] = value
        elif isinstance(current, list):
            current.append(value)
        else:
            # convert to list
            self.avs[name] = [convert, value]

    def num_values(self, name):
        """get the number of """



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

    def __str__(self):
        return f"##{self.value}"
