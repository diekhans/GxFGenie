"""
Shared code for GFF3 and GTF parsing.
"""
# Copyright 2025-2025 Mark Diekhans
import re
from abc import ABC, abstractmethod
from gxfgenie.errors import GxfGenieFormatError, GxfGenieParseError
from gxfgenie.gxf_record import GxfMeta
from gxfgenie import fileops

_ignored_line_re = re.compile(r"(^[ ]*$)|(^[ ]*#.*$)")  # spaces or comment line

class GxfParser(ABC):
    """
    Common code shared between GTF and GFF3 parser.  This just does basic
    parsing, most validation must be done once file is parsed. Derived class
    implements parse_attrs() to handle different attribute formats and
    create_record() to create a record derived from GxfRecord.

    This object is used as an iterator to parse a file.
    """

    def __init__(self, gxf_file=None, gxf_fh=None):
        assert (gxf_file is not None) or (gxf_fh is not None)
        self.gxf_file = gxf_file if gxf_file is not None else "<unknown>"
        self.opened_file = (gxf_fh is None)
        self.fh = fileops.opengz(gxf_file) if gxf_fh is None else gxf_fh
        self.line_number = 0
        self.attrs_cached = {}

    def _advance_line(self):
        """Advance to the next line. Sets object state and returns None or line"""
        line = self.fh.readline()
        if len(line) == 0:
            return None
        else:
            self.line_number += 1
            return line.rstrip("\n")

    def close(self):
        """close GxF file if it was opened by __init__"""
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
    def parse_attrs(self, attrs_str):
        "parse attributes of the derived type"
        pass

    @abstractmethod
    def create_record(self, seqname, source, feature, start, end, score, strand, phase, attrs, *, line_number=None):
        "create a record of the derived type"
        pass

    @staticmethod
    def _parse_no_space_column(col_name, value):
        if (len(value) == 0) or re.search(r'\s', value):
            raise GxfGenieFormatError(f"Invalid `{col_name}', value may not be empty or contain whitespace, got `{value}'")
        return value

    @staticmethod
    def _parse_no_empty_column(col_name, value):
        # yes, refseq put spaces in features
        if len(value.strip()) == 0:
            raise GxfGenieFormatError(f"Invalid `{col_name}', value may not be empty, got `{value}'")
        return value

    @staticmethod
    def _parse_pos_column(col_name, value):
        "parse start or end"
        pos = None
        try:
            pos = int(value)
        except ValueError:
            pass
        if (pos is None) or (pos <= 0):
            raise GxfGenieFormatError(f"Invalid `{col_name}', expected a positive integer, got `{value}'")
        return pos

    @staticmethod
    def _parse_score(value):
        if value == '.':
            return None
        try:
            if value.find('.') >= 0:
                return float(value)
            else:
                return int(value)
        except ValueError:
            raise GxfGenieFormatError(f"Invalid `score', expected a floating point or integer number, or `.', got `{value}'")

    @staticmethod
    def _parse_strand(value):
        if value == '.':
            return None
        if value not in ('+', '-'):
            raise GxfGenieFormatError(f"Invalid `strand', expected `+', `-', or `.', got `{value}'")
        return value

    @staticmethod
    def _parse_phase(value):
        if value == '.':
            return None
        phase = None
        try:
            phase = int(value)
        except ValueError:
            pass
        if (phase is None) or (phase < 0) or (phase > 2):
            raise GxfGenieFormatError(f"Invalid `phase', expected `0', `1', `2', or `.', got `{value}'")
        return phase

    def _parse_record(self, row):
        """parse on record line of the GTF"""
        start = self._parse_pos_column('start', row[3])
        end = self._parse_pos_column('end', row[4])
        if start > end:
            raise GxfGenieFormatError(f"'start' column must be less-than or equal to end, got `{start} > {end}'")

        return self.create_record(self._parse_no_space_column('seqname', row[0]),
                                  self._parse_no_empty_column('source', row[1]),
                                  self._parse_no_empty_column('feature', row[2]),
                                  start, end,
                                  self._parse_score(row[5]),
                                  self._parse_strand(row[6]),
                                  self._parse_phase(row[7]),
                                  self.parse_attrs(row[8]),
                                  line_number=self.line_number)

    def _parse_line(self, line):
        gxf_num_cols = 9
        row = line.split("\t")
        try:
            if len(row) != gxf_num_cols:
                raise GxfGenieFormatError(f"Wrong number of columns, expected {gxf_num_cols}, got {len(row)}: `{line}'")
            return self._parse_record(row)
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

    def parse(self):
        "parse generator of records or metadata"
        try:
            while (line := self._advance_line()) is not None:
                rec = self._process_line(line)
                if rec is not None:
                    yield rec
        finally:
            self.close()
