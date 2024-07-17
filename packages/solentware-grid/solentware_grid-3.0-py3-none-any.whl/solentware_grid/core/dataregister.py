# dataregister.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provides a way to link widgets to database updates of interest.

This module designed to work with the dataclient module.

"""


class DataRegister:
    """Register the interest of a DataSource instance in updates to an index.

    Maintain a dictionary of callback methods:
    self._datasources[(db, file, index)][control] = callback
    Notify updates by refresh_after_update(updated index, updated instance).
    The instance may contain data for several indexes that have been updated
    with the update being driven from a control using one of these. This
    dictionary allows the indexes to be cross referenced so that all controls
    that may be displaying the updated instance get a chance to refresh.

    """

    def __init__(self, **kargs):
        """Create an empty register of datasources."""
        super().__init__(**kargs)
        self.datasources = dict()

    def refresh_at_start_of_file(self):
        """Refresh all registered data clients and position at start of file.

        Clear all selections on all dataclients in the register of datasources
        and position datagrid for client at start of file.

        """
        sources = self.datasources
        clients = set()
        for key in sources:
            for client in sources[key]:
                clients.add(client)
        for client in clients:
            client.load_new_index()

    def refresh_after_update(self, dskey, instance):
        """Call registered callbacks for updates to dskey index by instance.

        instance can be None which the callback will likely interpret as
        refresh as close as possible to existing display.

        """
        if dskey in self.datasources:
            for client in self.datasources[dskey]:
                self.datasources[dskey][client](instance)

    def register_in(self, client, callback):
        """Register callback for updates to current DataSource of client."""
        source = client.datasource
        key = (source.dbhome, source.dbset, source.dbname)
        if key not in self.datasources:
            self.datasources[key] = dict()
        self.datasources[key][client] = callback

    def register_out(self, client):
        """Remove callbacks for current DataSource of client from register.

        Clear the register if client is None.

        """
        if client is None:
            self.datasources.clear()
            return
        source = client.datasource
        key = (source.dbhome, source.dbset, source.dbname)
        if key in self.datasources:
            if client in self.datasources[key]:
                del self.datasources[key][client]
                if not self.datasources[key]:
                    del self.datasources[key]
