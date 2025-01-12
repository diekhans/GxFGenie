"""
Various file-related operations
"""
# Copyright 2025-2025 Mark Diekhans
import shutil
from pathlib import Path
import pipettor
from gxfgenie.errors import GxfGenieError

def is_compressed(path):
    """
    Determine if a file appears to be compressed by extension.
    """
    compressed_extensions = (".gz", ".bz2", ".Z")
    return str(path).endswith(compressed_extensions)


def compress_cmd(path):
    """
    Return the command to compress the file at the given path.
    Defaults to `cat` if not compressed. Raises an error for unsupported formats.
    """
    if str(path).endswith(".Z"):
        raise GxfGenieError("Writing compressed .Z files is not supported")
    elif str(path).endswith(".gz"):
        return ["pigz"] if shutil.which("pigz") else ["gzip"]
    elif str(path).endswith(".bz2"):
        return ["bzip2"]
    else:
        return ["cat"]


def compress_base_name(path):
    """
    If a file is compressed, return the path without the compressed extension.
    """
    path = Path(path)
    if is_compressed(path):
        return path.with_suffix("")
    return str(path)


def decompress_cmd(path):
    """
    Return the command to decompress the file to stdout.
    Defaults to `cat` if the file is not compressed.
    """
    if str(path).endswith(".gz") and shutil.which("unpigz"):
        return ["unpigz", "-c"]
    elif str(path).endswith((".Z", ".gz")):
        return ["zcat"]
    elif str(path).endswith(".bz2"):
        return ["bzcat"]
    else:
        return ["cat"]


def opengz(file_name, mode="r", buffering=-1, encoding=None, errors=None):
    """
    Open a file. If it ends with a compression extension, open with
    a compression/decompression pipe.
    """
    if is_compressed(file_name):
        if mode.startswith("r"):
            cmd = decompress_cmd(file_name)
            return pipettor.Popen(cmd + [file_name], mode=mode, buffering=buffering, encoding=encoding, errors=errors)
        elif mode.startswith("w"):
            cmd = compress_cmd(file_name)
            return pipettor.Popen(cmd, mode=mode, stdout=file_name, buffering=buffering, encoding=encoding, errors=errors)
        else:
            raise GxfGenieError(f"Mode `{mode}' not supported with compression for `{file_name}'")
    else:
        return open(file_name, mode, buffering=buffering, encoding=encoding, errors=errors)
