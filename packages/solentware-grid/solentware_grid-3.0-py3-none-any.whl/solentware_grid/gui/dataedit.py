# dataedit.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide base classes for record editing dialogues."""

import tkinter

from solentware_bind.gui.bindings import Bindings

from ..core.dataclient import DataClient

# minimum_width and minimum_height arguments for wm_minsize() calls
# maybe candidate arguments for DataControl.edit_dialog() calls elsewhere
MINIMUM_WIDTH = 800
MINIMUM_HEIGHT = 300


class RecordEdit(DataClient):
    """Edit or insert a database record."""

    def __init__(self, newobject, oldobject):
        """Delegate to superclas then set number of rows to 1.

        newobject - the record to be inserted or the replacement record
        oldobject - the record being replaced or None if insertion

        blockchange is set False to indicate update is allowed unless an
        update notification changes the situation.

        """
        super().__init__()
        self.rows = 1
        self.newobject = newobject
        self.oldobject = oldobject
        self.newobject.newrecord = False
        self.blockchange = False

    def edit(self, commit=True):
        """Edit the record and refresh widgets.

        commit - update within, and commit, transaction if True.  A transaction
                is started if one is not already started.
                If not True a transaction is not started and an existing
                transaction, if there is one, is not committed.

        The datasource must be set by a call to set_data_source (inherited
        from DataClient) to allow edit to happen.  That call should also
        specify on_data_change as the update notification callback to prevent
        edit proceeding if the record is changed elsewhere first.

        """
        if commit:
            self.datasource.dbhome.start_transaction()
        self.oldobject.edit_record(
            self.datasource.dbhome,
            self.datasource.dbset,
            self.datasource.dbname,
            self.newobject,
        )
        if commit:
            self.datasource.dbhome.commit()
        self.datasource.refresh_widgets(self.oldobject)

    def on_data_change(self, instance):
        """Block record edit if instance is record being edited.

        instance - the updated record, which cannot be deleted by self

        Implication is that record has been modified separately and it is
        not correct to edit based on the record as held in self.

        """
        try:
            if instance == self.oldobject:
                self.blockchange = True
        except AttributeError:
            pass

    def put(self, commit=True):
        """Insert the record and refresh widgets.

        commit - update within, and commit, transaction if True.  A transaction
                is started if one is not already started.
                If not True a transaction is not started and an existing
                transaction, if there is one, is not committed.

        The datasource must be set by a call to set_data_source (inherited
        from DataClient) to allow update to happen.  That call should also
        specify on_data_change as the update notification callback to prevent
        edit proceeding if the record is changed elsewhere first.

        """
        if commit:
            self.datasource.dbhome.start_transaction()
        self.newobject.put_record(
            self.datasource.dbhome, self.datasource.dbset
        )
        if commit:
            self.datasource.dbhome.commit()
        self.datasource.refresh_widgets(self.newobject)


class DataEdit(RecordEdit, Bindings):
    """An edit and insert record dialogue."""

    def __init__(
        self,
        newobject=None,
        parent=None,
        oldobject=None,
        newview=None,
        title=None,
        oldview=None,
    ):
        """Delegate to superclass then create the dialogue.

        newobject - passed to superclass as newobject argument
        parent - parent widget for dialog
        oldobject - passed to superclass as oldobject argument
        newview - widget displaying record with updates applied
        title - title for dialogue
        oldview - widget displaying record before edit or None if inserted
        """
        super().__init__(newobject, oldobject)
        self.parent = parent
        self.newview = newview
        self.oldview = oldview
        self.bind(parent, "<Destroy>", function=self.on_destroy)
        parent.wm_title(title)
        parent.wm_minsize(width=MINIMUM_WIDTH, height=MINIMUM_HEIGHT)
        if oldview:
            oldview.get_top_widget().pack(
                fill=tkinter.BOTH, expand=tkinter.TRUE
            )
            oldview.get_top_widget().pack_propagate(False)
            oldview.takefocus_widget.configure(takefocus=tkinter.TRUE)
        newview.get_top_widget().pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
        newview.get_top_widget().pack_propagate(False)
        newview.takefocus_widget.configure(takefocus=tkinter.TRUE)
        newview.takefocus_widget.focus_set()
        self.status = tkinter.Label(parent)
        self.status.pack(side=tkinter.BOTTOM)
        self.buttons = tkinter.Frame(parent)
        self.buttons.pack(
            fill=tkinter.X, expand=tkinter.FALSE, side=tkinter.TOP
        )
        self.ok = tkinter.Button(
            master=self.buttons,
            text="Ok",
            command=self.try_command(self.dialog_on_ok, self.buttons),
        )
        self.ok.pack(expand=tkinter.TRUE, side=tkinter.LEFT)
        self.cancel = tkinter.Button(
            master=self.buttons,
            text="Cancel",
            command=self.try_command(self.dialog_on_cancel, self.buttons),
        )
        self.cancel.pack(expand=tkinter.TRUE, side=tkinter.LEFT)

    def dialog_clear_error_markers(self):
        """Set status report to ''."""
        self.status.configure(text="")

    def dialog_on_cancel(self):
        """Destroy dialogue on Cancel response in dialogue."""
        self.parent.destroy()
        self.set_data_source()

    def dialog_status(self):
        """Return widget used to display status reports and error messages."""
        return self.status

    def on_data_change(self, instance):
        """Delegate to superclass then destroy dialogue if deleted."""
        super().on_data_change(instance)
        if self.blockchange:
            if self.ok:
                self.ok.destroy()
                self.ok = None

    def dialog_on_ok(self):
        """Update record and destroy dialogue on Ok response.

        Update is not allowed if the record has been changed since start
        of update action or the database has been closed since then.

        """
        self.dialog_clear_error_markers()
        if self.blockchange:
            self.status.configure(
                text=" ".join(
                    (
                        "Cannot delete because the record has",
                        "been changed since this dialogue opened.",
                    )
                )
            )
            self.ok.destroy()
            self.ok = None
            return
        dok = self.dialog_ok()
        if dok:
            self.parent.destroy()
            self.set_data_source()
        elif dok is False:
            pass
        elif self.oldobject is None:
            self.status.configure(
                text=" ".join(
                    (
                        "Record inserted.  Start another dialogue to continue",
                        "editing the record.",
                    )
                )
            )
        else:
            self.status.configure(
                text=" ".join(
                    (
                        "Edit applied.  Start another dialogue to continue",
                        "editing the record.",
                    )
                )
            )

    # Method added to allow subclasses direct use of action.
    def destroy_dialog_on_ok_and_blockchange(self):
        """Destroy dialogue and inhibit future attempts to change."""
        if self.ok:
            self.ok.destroy()
            self.ok = None
        self.blockchange = True

    def dialog_ok(self):
        """Update record and return update action response (True for updated).

        Check that database is open and is same one as update action was
        started.

        """
        if (
            self.datasource.dbhome.get_table_connection(self.datasource.dbset)
            is None
        ):
            self.status.configure(
                text="Cannot update because original database was closed"
            )
            self.destroy_dialog_on_ok_and_blockchange()
            return False
        if self.oldobject is not None:
            if self.newobject == self.oldobject:
                self.status.configure(text="No changes to record")
                return False
            self.edit()
            return True
        self.newobject.set_database(self.datasource.dbhome)
        self.newobject.key.recno = None
        self.put()
        return True

    def ok_by_keypress_binding(self, event=None):
        """Delegate to dialog_on_ok after accepting event argument."""
        self.dialog_on_ok()

    def cancel_by_keypress_binding(self, event=None):
        """Delegate to dialog_on_ok after accepting event argument."""
        self.dialog_on_cancel()

    def bind_buttons_to_widget(self, widget):
        """Bind button commands to underlined character for widget."""
        for button, underline, method in (
            (self.ok, 0, self.ok_by_keypress_binding),
            (self.cancel, 0, self.cancel_by_keypress_binding),
        ):
            button.configure(underline=underline)
            self.bind(
                widget,
                button.configure("text")[-1][underline]
                .lower()
                .join(("<Alt-", ">")),
                function=method,
            )

    def on_destroy(self, event=None):
        """Tidy up after destruction of dialogue widget and all children."""
        if event.widget == self.parent:
            self.tidy_on_destroy()

    def tidy_on_destroy(self):
        """Do nothing. Override as required."""
