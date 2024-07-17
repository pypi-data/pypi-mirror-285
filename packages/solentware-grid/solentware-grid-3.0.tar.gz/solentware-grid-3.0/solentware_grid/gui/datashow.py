# datashow.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide base classes for record display dialogues."""

import tkinter

from solentware_bind.gui.bindings import Bindings

from ..core.dataclient import DataClient

# minimum_width and minimum_height arguments for wm_minsize() calls
# maybe candidate arguments for DataControl.edit_dialog() calls elsewhere
MINIMUM_WIDTH = 600
MINIMUM_HEIGHT = 200


class RecordShow(DataClient):
    """Show a database record."""

    def __init__(self, instance=None):
        """Delegate to superclass then set number of rows to 1.

        instance - the record to be displayed

        instance.newrecord is set None to indicate a record display.

        blockchange is set False to indicate deletion is allowed unless an
        update notification changes the situation.

        """
        super().__init__()
        self.rows = 1
        self.object = instance
        self.object.newrecord = None
        self.blockchange = False

    def on_data_change(self, instance):
        """Block record deletion if instance is record being deleted.

        instance - the updated record, which cannot be deleted by self

        Implication is that record has been modified separately and it is
        not correct to update based on the record as held in self.

        """
        if instance == self.object:
            self.blockchange = True


class DataShow(RecordShow, Bindings):
    """A show record dialogue."""

    def __init__(self, instance=None, parent=None, oldview=None, title=None):
        """Delegate to superclass then create the dialogue.

        instance - passed to superclass as instance argument
        parent - parent widget for dialog
        oldview - widget displaying the record
        title - title for dialogue
        """
        super().__init__(instance)
        self.parent = parent
        self.oldview = oldview
        self.bind(parent, "<Destroy>", function=self.on_destroy)
        oldview.get_top_widget().pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
        oldview.get_top_widget().pack_propagate(False)
        oldview.takefocus_widget.configure(takefocus=tkinter.TRUE)
        oldview.takefocus_widget.focus_set()
        parent.wm_title(title)
        parent.wm_minsize(width=MINIMUM_WIDTH, height=MINIMUM_HEIGHT)
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

    def dialog_clear_error_markers(self):
        """Set status report to ''."""
        self.status.configure(text="")

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

    # Method added to allow subclasses direct use of action.
    def destroy_dialog_on_ok_and_blockchange(self):
        """Destroy dialogue and inhibit future attempts to change."""
        if self.ok:
            self.ok.destroy()
            self.ok = None
        self.blockchange = True

    def dialog_ok(self):
        """Delete record and return show action response."""
        if self.datasource is not None:
            if self.datasource.dbhome.get_table_connection(
                self.datasource.dbset
            ):
                return True
            self.destroy_dialog_on_ok_and_blockchange()
            return False
        return None

    def dialog_on_ok(self):
        """Destroy dialogue."""
        self.dialog_clear_error_markers()
        if self.blockchange:
            self.ok.destroy()
            self.ok = None
            return
        self.dialog_ok()
        self.parent.destroy()
        self.set_data_source()

    def ok_by_keypress_binding(self, event=None):
        """Delegate to dialog_on_ok after accepting event argument."""
        self.dialog_on_ok()

    def bind_buttons_to_widget(self, widget):
        """Bind button commands to underlined character for widget."""
        for button, underline, method in (
            (self.ok, 0, self.ok_by_keypress_binding),
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
