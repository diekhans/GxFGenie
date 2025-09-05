"""
Base class to store contents of a GxF file as collection of feature trees.
"""
from gxfgenie.errors import GxfGenieError

class GxfRecListDict(dict):
    """Dict for a list of values"""
    # Don't use defaultdict, since it creates on read too and
    # want to be able to update

    def append(self, idx, rec):
        if idx not in self:
            self[idx] = []
        self[idx].append(rec)


class GxfDataSet:
    """Container for contents of a GTF or GFF3 file.

    This implements lookup of genes by gene_id and transcripts by
    transcript_id as well as hierarchy traversal.  As gene and transcript
    records are not required to be unique, lists are always returned.  This is
    the case for the PAR with RefSeq and older GENCODE versions.

    """

    def __init__(self):
        self._records = []
        self._roots = []
        self._transcripts_by_id = GxfRecListDict()
        self._genes_by_id = GxfRecListDict()
        # Built in a lazy manner
        self._transcripts_by_range = None
        self._genes_by_range = None

    def add_record(self, rec):
        self._records.append(rec)

    def get_transcripts(self):
        """
        Get an generator over all transcript records.
        """
        return self._transcripts_by_id.values()

    def get_transcripts_by_id(self, transcript_id, default=None):
        """
        Get a list transcripts records for a transcript_id or default if not found.
        """
        return self._transcripts_by_id.get(transcript_id, default)

    def fetch_transcripts_by_id(self, transcript_id):
        """
        Get a list transcripts records for a transcript_id or raise an exception if it doesn't exist.
        """
        transes = self.transcripts_by_id.get(transcript_id)
        if transes is None:
            raise GxfGenieError(f"transcript_id not found: `{transcript_id}'")
        return transes

    def get_overlapping_transcripts(self, chrom, start, end, strand=None):
        """
        Get transcript records overlapping a range, optionally filtering by strand
        """
        if self._transcript_loci_by_range is None:
            self._build_transcript_loci_by_range()
        return self._transcript_loci_by_range.overlapping(chrom, start, end, strand)

    def _build_transcripts_range_index(self):
        assert False

    def get_genes(self):
        """
        Get an generator over all gene records.
        """
        return self.genes_by_id.values()

    def get_genes_by_id(self, gene_id, default=None):
        """
        Get a list genes records for a gene_id or default if not found.
        """
        return self._genes_by_id.get(gene_id, default)

    def fetch_genes_by_id(self, gene_id):
        """
        Get a list genes records for a gene_id or raise an exception if it doesn't exist.
        """
        transes = self._genes_by_id.get(gene_id)
        if transes is None:
            raise GxfGenieError(f"gene_id not found: `{gene_id}'")
        return transes

    def get_overlapping_genes(self, chrom, start, end, strand=None):
        """
        Get gene records overlapping a range, optionally filtering by strand
        """
        if self._gene_loci_by_range is None:
            self._build_gene_loci_by_range()
        return self._gene_loci_by_range.overlapping(chrom, start, end, strand)

    def _build_genes_range_index(self):
        assert False
