import os
from gxfgenie.gtf_parser import GtfParser
from gxfgenie.gff3_parser import Gff3Parser
from gxfgenie.errors import GxfGenieError


def _get_filetype_ext(gxf_file):
    """
    Get the primary file extension for the given GXF file, accounting for possible compression.
    """
    from gxfgenie import fileops
    if fileops.is_compressed(gxf_file):
        return os.path.splitext(os.path.splitext(gxf_file)[0])[1]
    else:
        return os.path.splitext(gxf_file)[1]

def gxf_parser_factory(gxf_file):
    """
    Factory function to return the appropriate parser (GtfParser or Gff3Parser)
    based on the file extension.

    Args:
        gxf_file (str): Path to the GXF file (.gtf or .gff3).

    Returns:
        GtfParser or Gff3Parser: The appropriate parser instance.

    Raises:
        GxfGenieError: If the file extension is not .gtf or .gff3.
    """
    ext = _get_filetype_ext(gxf_file)
    if ext == ".gtf":
        return GtfParser(gxf_file)
    elif ext == ".gff3":
        return Gff3Parser(gxf_file)
    else:
        raise GxfGenieError(f"Unsupported file extension in: {gxf_file}. Expected .gtf or .gff3 (with optional compression extension).")
