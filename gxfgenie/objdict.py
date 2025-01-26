# Copyright 2006-2025 Mark Diekhans
# Copyright of original unknown (https://goodcode.io/articles/python-dict-object/)
# This code is copied from git@github.com:diekhans/pycbio.git

def _attributeError(name):
    raise AttributeError(f"No such attribute: `{name}'")

class ObjDict(dict):
    """Dict object where keys are field names.
    This is useful for JSON by doing:
       json.load(fh, object_pairs_hook=ObjDict)

    When inserting a dict, it must be explicitly converted to an ObjDict if
    desired.
    """
    __slots__ = ()

    def __getattr__(self, name):
        if name not in self:
            _attributeError(name)
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name not in self:
            _attributeError(name)
        del self[name]
