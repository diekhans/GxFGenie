"""
Objects to store contents of a GxF file
"""
# FIXME: currently incomplete and not working
# flake8: noqa
from gxfgenie.errors import GxfGenieError

class GencodeGenes(object):
    """
    Object to store information and optional genePreds of all Gencode genes.
    """

    def __init__(self):
        self.transcripts_by_id = dict()
        self.genes_by_id = dict()
        # Build in a lazy manner
        self.transcript_loci_by_range = None
        self.gene_loci_by_range = None

    def get_transcript(self, transcript_id):
        """
        Get a transcript object, or None if it doesn't exist.
        """
        return self.transcripts_by_id.get(transcript_id)

    def get_transcript_required(self, transcript_id):
        """
        Get a transcript object, or raise an exception if it doesn't exist.
        """
        trans = self.transcripts_by_id.get(transcript_id)
        if trans is None:
            raise GxfGenieError(f"Transcript not found in attributes: {transcript_id}")
        return trans

    def get_transcripts(self):
        """
        Get an iterator over all transcript objects.
        """
        return self.transcripts_by_id.values()

    def obtain_transcript(self, transcript_id):
        """
        Get or create a transcript object.
        """
        trans = self.get_transcript(transcript_id)
        if trans is None:
            trans = self.transcripts_by_id[transcript_id] = GencodeTranscript(transcript_id)
        return trans

    def get_gene(self, gene_id):
        """
        Get a gene object, or None if it doesn't exist.
        """
        return self.genes_by_id.get(gene_id)

    def get_gene_required(self, gene_id):
        """
        Get a gene object, or raise an exception if it doesn't exist.
        """
        gene = self.genes_by_id.get(gene_id)
        if gene is None:
            raise GencodeGenesException(f"Gene not found in attributes: {gene_id}")
        return gene

    def obtain_gene(self, gene_id):
        """
        Get or create a gene object.
        """
        gene = self.get_gene(gene_id)
        if gene is None:
            gene = self.genes_by_id[gene_id] = GencodeGene(gene_id)
        return gene

    def get_gene_loci(self):
        """
        Generator over all GencodeGeneLocus objects.
        """
        for gene in self.genes_by_id.values():
            for gene_locus in gene.gene_loci:
                yield gene_locus

    def get_overlapping_gene_loci(self, chrom, chrom_start, chrom_end, strand=None):
        """
        Get GeneLoci overlapping a range. Includes the entry range of the gene, including introns.
        """
        if self.gene_loci_by_range is None:
            self._build_gene_loci_by_range()
        return self.gene_loci_by_range.overlapping(chrom, chrom_start, chrom_end, strand)

    def get_transcript_loci(self):
        """
        Generator over all GencodeTranscriptLocus objects.
        """
        for trans in self.transcripts_by_id.values():
            for trans_locus in trans.transcript_loci:
                yield trans_locus

    def get_overlapping_transcript_loci(self, chrom, chrom_start, chrom_end, strand=None):
        """
        Get TranscriptLoci overlapping a range. This only overlaps with exons.
        """
        if self.transcript_loci_by_range is None:
            self._build_transcript_loci_by_range()
        return self.transcript_loci_by_range.overlapping(chrom, chrom_start, chrom_end, strand)

    def get_transcripts_sorted_by_locus(self):
        """
        Get a list of transcript objects sorted to optimize access by location.
        """
        return sorted(self.transcripts_by_id.values(),
                      key=lambda t: (t.transcript_loci[0].gp.chrom,
                                     t.transcript_loci[0].gp.tx_start,
                                     t.transcript_loci[0].gp.tx_end,
                                     t.transcript_loci[0].gp.name))

    def get_transcripts_sorted_by_id(self):
        """
        Get a list of transcript objects sorted by ID.
        """
        return sorted(self.transcripts_by_id.values(), key=lambda t: t.id)

    def get_transcripts_sorted(self):
        """
        Get a list of transcript objects sorted first by gene ID, then transcript ID.
        """
        return sorted(self.transcripts_by_id.values(), key=lambda t: (t.gene.id, t.id))

    def _build_transcript_loci_by_range(self):
        """
        Construct the transcript_loci_by_range index when needed.
        """
        self.transcript_loci_by_range = RangeFinder()
        for trans_locus in self.get_transcript_loci():
            gp = trans_locus.gp
            for exon in gp.exons:
                self.transcript_loci_by_range.add(gp.chrom, exon.start, exon.end, trans_locus, gp.strand)

    def _build_gene_loci_by_range(self):
        """
        Construct the gene_loci_by_range index when needed.
        """
        self.gene_loci_by_range = RangeFinder()
        for gene_locus in self.get_gene_loci():
            self.gene_loci_by_range.add(gene_locus.chrom, gene_locus.chrom_start, gene_locus.chrom_end, gene_locus, strand=gene_locus.strand)
