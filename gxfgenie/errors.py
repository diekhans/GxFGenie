"""
Exception classes
"""
# Copyright 2006-2022 Mark Diekhans

class GxfGenieError(Exception):
    "GxfGenie base error class"
    pass

class GxfGenieFormatError(GxfGenieError):
    """indicates a format error cause without location information to not
    repeat information added by the top level GxfGenieParseError"""
    pass

class GxfGenieParseError(GxfGenieFormatError):

    """
    Indicates a parser error that is reported but allows checking to continue.
    """
    def __init__(self, gxf_file, line_number, msg):
        super().__init__(f"Error: {gxf_file}:{line_number}: {msg}")
