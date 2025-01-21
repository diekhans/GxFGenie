"""
Shared code for GFF3 and GTF parsing.
"""
# Copyright 2025-2025 Mark Diekhans
import re
from abc import ABC, abstractmethod
from gxfgenie.errors import GxfGenieParseError
from gxfgenie.gxf_rec import GxfMeta
from gxfgenie import fileops

_ignored_line_re = re.compile(r"(^[ ]*$)|(^[ ]*#.*$)")  # spaces or comment line


class GxfParser(ABC):
    """
    Common code shared between GTF and GFF3 parser.  This just does basic
    parsing, most validation must be done once file is parsed. Derived class
    implements parse_attrs() to handle different attribute formats.

    This object is used as an iterator to parse a file.
    """

    def __init__(self, gxf_file=None, gxf_fh=None):
        self.gxf_file = gxf_file if gxf_file is not None else "<unknown>"
        self.opened_file = (gxf_fh is None)
        self.fh = fileops.opengz(gxf_file) if gxf_fh is None else gxf_fh
        self.current_line = None
        self.line_number = 0

    def _advance_line(self):
        """Advance to the next line. Sets object state and returns None or line"""
        self.current_line = self.fh.readline()
        if len(self.current_line) == 0:
            return None
        else:
            self.line_number += 1
            return self.current_line.rstrip("\n")

    def close(self):
        if (self.fh is not None) and self.opened_file:
            self.fh.close()
        self.fh = None

    def _ignored(self, line):
        """Check if a line should be ignored (empty or comment)."""
        return _ignored_line_re.search(line) is not None

    def _parse_meta(self, line):
        value = line[2:].strip()   # by pass '##'
        if len(value) > 0:
            return GxfMeta(value, line_number=self.line_number)
        else:
            return None

    @abstractmethod
    def parse_rec(self, row):
        """parse on record line of the GxF"""
        pass

    def _parse_line(self, line):
        gxf_num_cols = 9
        row = line.split("\t")
        if len(row) != gxf_num_cols:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"Wrong number of columns, expected {gxf_num_cols}, got {len(row)}: `{line}'")
        try:
            return self.parse_rec(row)  # derived type returned
        except Exception as ex:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"error parsing GxF record: `{line}'") from ex

    def _process_line(self, line):
        "None is return if line is not used"
        if line.startswith("##"):
            return self._parse_meta(line)
        elif self._ignored(line):
            return None
        else:
            return self._parse_line(line)

    def _next_rec(self):
        line = self._advance_line()
        if line is not None:
            return self._process_line(line)
        return None

    def __iter__(self):
        return self

    def __next__(self):
        rec = self._next_rec()
        if rec is None:
            self.close()
            raise StopIteration
        else:
            return rec
