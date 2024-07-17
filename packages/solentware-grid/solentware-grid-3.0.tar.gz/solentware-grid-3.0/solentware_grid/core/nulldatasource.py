# nulldatasource.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide bsddb style access to a null source of data."""

from solentware_base.core.cursor import Cursor

from .dataclient import DataSource


class NullDataSource(DataSource):
    """Define an interface between a database and GUI controls.

    This class provides a zero cursor in an otherwise normal datasource.
    Intended use is where dataclient asks for something that the database
    cannot provide.

    """

    def get_cursor(self):
        """Return cursor on the record set associated with datasource."""
        return CursorNull()

    def set_recordset(self, records):
        """Do nothing.  Null datasource."""
        return


class CursorNull(Cursor):
    """A null cursor - methods do nothing then return None, 0, or False."""

    def __init__(self):
        """Define a cursor to access a null database."""
        super().__init__(None)

    def close(self):
        """Do nothing and return None."""
        return None

    def count_records(self):
        """Do nothing and return 0."""
        return 0

    def database_cursor_exists(self):
        """Do nothing and return False."""
        return False

    def first(self):
        """Do nothing and return None."""
        return None

    def get_position_of_record(self):
        """Do nothing and return 0."""
        return 0

    def get_record_at_position(self):
        """Do nothing and return None."""
        return None

    def last(self):
        """Do nothing and return None."""
        return None

    def set_partial_key(self, partial):
        """Do nothing and return None."""
        return None

    def nearest(self, key):
        """Do nothing and return None."""
        return None

    def next(self):
        """Do nothing and return None."""
        return None

    def prev(self):
        """Do nothing and return None."""
        return None

    def refresh_recordset(self):
        """Do nothing and return None."""
        return None

    def setat(self, record):
        """Do nothing and return None."""
        return None
