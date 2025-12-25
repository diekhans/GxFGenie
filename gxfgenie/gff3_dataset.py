"""
Base class to store contents of a GxF file as collection of feature trees.
"""
from gxfgenie.defs import ATTR_ID
from gxfgenie.gxf_dataset import GxfDataSet, GxfRecListDict
from gxfgenie.errors import GxfGenieError, GxfGenieParseError

class GffDataSet(GxfDataSet):
    """Container for contents of a GFF3 file.
    """

    def __init__(self):
        super(self).__init__(self)
        # must be a list for ids due to discontinuous features
        self._records_by_id = GxfRecListDict()

    def add_record(self, rec):
        rec_id = rec.attrs.find_attr_value1(ATTR_ID)
        if rec_id is not None:
            self._records_by_id.append(rec_id, rec)
        super(self).add_record(rec)
