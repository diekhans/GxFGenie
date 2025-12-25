"""
Range index of gxf_record objects
"""
from collections import defaultdict
from intervaltree import IntervalTree

class RangeIndex:
    """Ranges index by chromosome and 0-based, 1/2 open coordinates"""
    def __init__(self):
        self._by_chrom = defaultdict(IntervalTree)

    def add_record(self, rec):
        self._by_chrom[rec.seqname].add(rec.start0, rec.end, rec)

    def iter_overlapping(self, seqname, start, end, *, strand=None):
        """Generator of of overlapping records, optionally filtering for strand"""
        for it in self._by_chrom[seqname].overlap(start - 1, end):
            if (strand is None) or (it.data.strand == strand):
                yield it.data
