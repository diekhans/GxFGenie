"""
Exception classes
"""
# Copyright 2006-2022 Mark Diekhans

class GxfGenieError(Exception):
    "GxfGenie base error class"
    pass


class GxfGenieParseError(GxfGenieError):
    """
    Indicates a parser error that is reported but allows checking to continue.
    """
    def __init__(self, gxf_file, line_number, msg):
        super().__init__(f"Error: {gxf_file}:{line_number}: {msg}")
