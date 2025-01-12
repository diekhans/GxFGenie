"""
Shared code for GFF3 and GTF parsing.
"""
# Copyright 2025-2025 Mark Diekhans
import re
from abc import ABC, abstractmethod
from gxfgenie.errors import GxfGenieParseError
from gxfgenie.gxf_rec import GxfRecord, GxfMeta
from gxfgenie import fileops

_ignored_line_re = re.compile(r"(^[ ]*$)|(^[ ]*#.*$)")  # spaces or comment line


class GxfParser(ABC):
    """
    Common code shared between GTF and GFF3 parser.  This just does basic
    parsing, most validation must be done once file is parsed. Derived class
    implements parse_attrs() to handle different attribute formats.
    """

    def __init__(self, gxf_file=None, gxf_fh=None):
        self.gxf_file = gxf_file if gxf_file is not None else "<unknown>"
        self.opened_file = (gxf_fh is None)
        self.fh = fileops.opengz(gxf_file) if gxf_fh is None else gxf_fh
        self.current_line = None
        self.line_number = 0

    @abstractmethod
    def parse_attrs(self, attrs_field):
        """Parsed the attributes field into a GxfAttrs object"""
        pass

    def _advance_line(self):
        """Advance to the next line. Sets object state and returns None or line"""
        self.current_line = self.fh.readline()
        if len(self.current_line) == 0:
            return None
        else:
            self.line_number += 1
            return self.currrent_line.rstrip("\n")

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
            return GxfMeta(value, self.line_number)
        else:
            return None

    def parse_row(self, row):
        return GxfRecord(row[0], row[1], row[2],
                         int(row[3]), int(row[4]),
                         row[5], row[6], row[7],
                         self.parse_attrs(row[8]),
                         line_number=self.line_number)

    def _parse_record(self, line):
        gxf_num_cols = 9
        row = line.split("\t")
        if len(row) != gxf_num_cols:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"Wrong number of columns, expected {gxf_num_cols}, got {len(row)}: `{line}'")
        try:
            return self.parse_row(row)  # derived type function
        except Exception as ex:
            raise GxfGenieParseError(self.gxf_file, self.line_number,
                                     f"error parsing GxF record: `{line}'") from ex

    def _parse_line(self, line):
        "None is return if line is not used"
        if line.startswith("##"):
            return self._parse_meta(line)
        elif self._ignored(self.line):
            return None
        else:
            return self._parser_record(line)

    def reader(self):
        """
        Generator over GxfRecord and GxfMeta lines.
        """
        try:
            while (line := self._advance_line()) is not None:
                if (rec := self._parse_line(line)) is not None:
                    yield rec
        finally:
            self.close()
