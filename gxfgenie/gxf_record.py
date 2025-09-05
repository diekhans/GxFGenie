"""
GxfRecord parsed from either GTF or GFF3 file.
"""
# Copyright 2025-2025 Mark Diekhans
from abc import ABC, abstractmethod
from collections.abc import Iterable, Hashable
from gxfgenie.errors import GxfGenieError

def _is_immutable(value):
    if isinstance(value, tuple):
        # all elements in the tuple must be are hashable
        return all(_is_immutable(v) for v in value)
    return isinstance(value, Hashable)

def _normalize_value(value):
    """convert a scalar or iterable value to tuple if needed"""
    if (not isinstance(value, (bytes, str, tuple))) and isinstance(value, Iterable):
        value = tuple(value)
    return value

def str_or_dot(value):
    "return a period if value is None, otherwise str(value)"
    return '.' if value is None else str(value)

class GxfAttr:
    """An attribute in GxF can have one or more values. The major use case are
    single-value, thus these are stored as scalars, and special-case multiple
    valued attributes as tuple to save memory.  Instance of this class are immutable.

    Attributes:
        name (str): The name of the attribute.
        value (scalar, or iterable): The value of the attribute, which is
            either a single-value immutable scalar, normally a str, or a
            iterable of immutable scalars.  The standard parse only supports
            string values, it is possible to derive a parser that converts
            them to a more specific type, such as floats.  The standard
            formaters will call str() on the value to support more specific
            types.  Iterable values are convert to tuples, or a scalar if they
            have a single value.

    Methods:
        len(): Returns the number of values, returning 1 if single-valued.
        [idx]: Retrieves the value by index, if it is single-value, an index
               of [0] will return the single value.
    """
    __slots__ = ("name", "value")

    def __init__(self, name, value):
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        value = _normalize_value(value)
        if isinstance(value, tuple) and len(value) == 1:
            value = value[0]  # convert to scalar
        if not _is_immutable(value):
            raise TypeError(f"attribute `{name}' must have value that is immutable object or an iterable of immutable objects")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", value)

    def __setattr__(self, key, value):
        raise AttributeError(f"{self.__class__.__name__} is immutable")

    def __delattr__(self, item):
        raise AttributeError(f"{self.__class__.__name__} is immutable")

    def __hash__(self):
        return hash((self.name, self.value))

    def __len__(self):
        return len(self.value) if isinstance(self.value, tuple) else 1

    def __getitem__(self, idx):
        if not isinstance(idx, int):
            raise TypeError(f"index must be an integers not `{type(idx)}'")
        if isinstance(self.value, tuple):
            return self.value[idx]
        elif idx != 0:
            raise IndexError(f"value index '{idx}' out of range, expected `0'")
        else:
            return self.value

class GxfAttrs(dict, ABC):
    """Attributes for GTF/GFF3 records.

    Mutable object of attribute in a GxF, containing GxfAttr objects.
    Each attribute maybe a scalar or tuple value.
    """
    def __setattr__(self, name, value):
        if not isinstance(value, GxfAttr):
            raise TypeError(f"attribute `{name}' must have a value of type `GxfAttr', got `{type(value)}'")
        super().__setitem__(name, value)

    @abstractmethod
    def __str__(self):
        """convert to file format"""
        pass

    def find_attr(self, name, default=None):
        "Get an GxfAttr or default if it does not exist"
        return self.get(name, default)

    def get_attr(self, name):
        "Get an GxfAttr or error if it does not exist"
        attr = self.find_attr(name)
        if name is not None:
            raise GxfGenieError(f"attribute `{name}' not found")
        return attr

    def find_attr_value(self, name, default=None):
        "Get an attribute or default. Returns a list or scalar"
        attr = self.find_attr(name, None)
        if attr is None:
            return default
        return attr.value

    def get_attr_value(self, name):
        "Get an attribute or error. Returns a list or scalar"
        return self.get_attr(name).value

    def _not_single_value_error(self, attr):
        return GxfGenieError(f"requested single value attribute `{attr.name}' has {len(attr)} values")

    def find_attr_value1(self, name, default=None):
        "Get a single value attribute or default"
        attr = self.find_attr(name)
        if attr is None:
            return default
        if len(attr) > 1:
            raise self._not_single_value_error(attr)
        return attr.value

    def get_attr_value1(self, name):
        "Get a single value attribute or error"
        attr = self.get_attr(name)
        if len(attr) > 1:
            raise self._not_single_value_error(attr)
        return attr.value


def _merge_attr_values(old_value, new_value):
    new_value = _normalize_value(new_value)
    if not isinstance(old_value, tuple):
        old_value = (old_value,)
    if not isinstance(new_value, tuple):
        new_value = (new_value,)
    return old_value + new_value

def gxf_attr_add(attrs, attr_cache, name, value):
    """Add an attribute and value, storing it as a GxfAttr.  If an attribute by
    this name already exists, it will be converted into a multi-value attribute.

    Attributes:
        name (str): The name of the attribute.
        value (scalar, or iterable): The value of the attribute, which is
            either a single-value immutable scalar, normally a str, or a
            iterable of immutable scalars.
        attr_cache (dict): If not None, a cache used to reuse GxfAttr objects
            to save memory.
    Returns:
        the GxfAttr object that was stored
    """
    attr = attrs.find_attr(name)
    if attr is None:
        attr = GxfAttr(name, value)
    else:
        attr = GxfAttr(name, _merge_attr_values(attr.value, value))
    if attr_cache is not None:
        cached = attr_cache.get(attr)
        if cached is None:
            attr_cache[attr] = attr
        else:
            attr = cached
    attrs[name] = attr
    return attr


class GxfRecord(ABC):
    """
    One record of a GTF or GFF3 file. Extended to get an implementation of __str__
    that returns a record in the correct format.

    Attributes:
        seqname (str): sequence name
        source (str): source of annotation
        feature (str): feature name
        start (int): start of feature in sequence (one-based, closed)
        end (int):: end of feature in sequence (one-based, closed)
        score (int,float,None): score if present
        strand (str): strand of feature, one of '+', '-', or None if not specfied.
        phase (int,None): phase of CDS exon, 0, 1, 2, or None
        attrs (GxfAttrs): Attributes
        parent (GxfRecord):  Pointer to the parent object, or None if no parent.
        children ([GxfRecord]): list of children of this record
        file_name (str or None): Name of file the record was parsed from, if available
        line_number (int or None): Line number of file the record was parsed from, or None if not available.
    """
    __slots__ = ("seqname", "source", "feature", "start", "end", "score",
                 "strand", "phase", "attrs", "parent", "children",
                 "file_name", "line_number")

    def __init__(self, seqname, source, feature, start, end, score, strand, phase, attrs, *,
                 file_name=None, line_number=None):
        assert seqname is not None
        assert isinstance(attrs, GxfAttrs)
        self.seqname = seqname
        self.source = source
        self.feature = feature
        self.start = start
        self.end = end
        self.score = score
        self.strand = strand
        self.phase = phase
        self.attrs = attrs
        self.parent = None
        self.children = []
        self.file_name = file_name
        self.line_number = line_number

    @abstractmethod
    def __str__(self):
        """convert to tab-separate line"""
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
