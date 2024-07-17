# datasourcecursor.py
# Copyright 2019 Roger Marsh
# Licence: See LICENCE (BSD licence)

# Build this module like dptdatasource.py
# See use of CreateRecordList and DestroyRecordSet methods, whose analogues
# will be sibling methods of 'self.dbhome.get_table_connection(...)'
"""This module provides a cursor on a datasource's recordset."""

from .dataclient import DataSource


class DataSourceCursor(DataSource):
    """Provide bsddb3 style cursor access to recordset of arbitrary records."""

    def __init__(self, *a, **k):
        """Delegate then set the recordset attribute to None.

        Initially the datasource is not associated with a recordset.

        """
        super().__init__(*a, **k)

        self.recordset = None
        # Not sure if equivalent of this (from dptdatasource) is needed
        # self.dbhome.table[self.dbset]._sources[self] = None
        # which would imply that the close() method be transplanted as well.

    # This method originally present only in ..dpt.datasourcecursor module.
    # Implication is clients of this module must call the close() method
    # if .datasourcecursor and ..dpt.datasourcecursor can be merged.
    def close(self):
        """Do database engine specific close actions on self.recordset."""
        self.dbhome.close_datasourcecursor_recordset(self)

    def get_cursor(self):
        """Create and return cursor on this datasource's recordset."""
        return self.dbhome.get_datasourcecursor_recordset_cursor(self)

    def set_recordset(self, recordset):
        """Set recordset as this datasource's recordset."""
        self.dbhome.set_datasourcecursor_recordset(self, recordset)
