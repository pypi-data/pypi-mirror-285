# gridbindings.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide classes which define shared grid event bindings.

Used in applications available on www.solentware.co.uk which have a
class from solentware_grid.datagrid as a superclass.

The gridbindings module provides standard bindings used by applications
available on www.solentware.co.uk.  The gridbindings.GridBindings class
expects to be a superclass alongside the solentware_grid.datagrid.DataGrid
class.

"""

import tkinter

from solentware_bind.gui.bindings import Bindings


class GridBindings(Bindings):
    """This class applies some standard bindings to data grids."""

    def __init__(
        self,
        receivefocuskey=None,
        appsyspanel=None,
        selecthintlabel=None,
        setbinding=None,
        focus_selector=None,
        keypress_grid_to_select=True,
        **kargs
    ):
        """Extend and bind grid row selection commands to popup menus.

        receivefocuskey - the keypress sequence to give focus to grid.
        appsyspanel - the panel containing the grid.
        **kwargs - argument to super().__init__ call.
        The other arguments are extracted from kargs but ignored otherwise.

        """
        super().__init__(**kargs)
        self.receivefocuskey = receivefocuskey
        self.appsyspanel = appsyspanel
        self.make_focus_to_grid()
        for label, function, accelerator in (
            ("Select", self.select_from_popup, "Left/Right Arrow"),
            (
                "Cancel Select",
                self.cancel_select_from_popup,
                "Control + Delete",
            ),
            (
                "Select Visible",
                self.move_selection_to_popup_selection,
                "Control + L/R Arrow",
            ),
            ("Bookmark", self.bookmark_from_popup, "Alt + Ins"),
            (
                "Cancel Bookmark",
                self.cancel_bookmark_from_popup,
                "Alt + Delete",
            ),
        ):
            self.menupopup.add_command(
                label=label,
                command=self.try_command(function, self.menupopup),
                accelerator=accelerator,
            )

    def bindings(self):
        """Apply DataGrid's bindings to it's frame and scrollbar widgets."""
        # Assume, for now, that appsyspanel frame instance bindtag is to
        # be inserted at front of grid instance bindtags
        if self.appsyspanel:
            for widget in (
                self.get_horizontal_scrollbar(),
                self.get_vertical_scrollbar(),
            ):
                widget.configure(highlightthickness=1)
                gridtags = list(widget.bindtags())
                gridtags.insert(
                    0, self.appsyspanel.get_appsys().explicit_focus_tag
                )
                widget.bindtags(tuple(gridtags))
            bindings = self.appsyspanel.get_widget().bindtags()[0]
            for widget in (
                self.get_frame(),
                self.get_horizontal_scrollbar(),
                self.get_vertical_scrollbar(),
            ):
                gridtags = list(widget.bindtags())
                gridtags.insert(0, bindings)
                widget.bindtags(tuple(gridtags))

    def give_and_set_focus(self):
        """Give grid the focus."""
        if self.appsyspanel is not None:
            self.appsyspanel.give_focus(self.get_frame())
        self.focus_set_frame()

    def grid_bindings(self, siblings, *a, **ka):
        """Bind grid switching methods to all exposed widgets taking focus.

        siblings - iterable of widgets which can give focus to self
        *a - ignored
        **ka - ignored

        """
        widgets = (
            self.get_frame(),
            self.get_horizontal_scrollbar(),
            self.get_vertical_scrollbar(),
        )
        self.receive_focus(widgets[1:])
        for sibling in siblings:
            sibling.receive_focus(widgets)

    def make_focus_to_grid(self):
        """Create method to give focus to self and bind to self.focus_to_grid.

        Replaces any existing definition of self.focus_to_grid method.

        """

        def focus(event):
            self.give_and_set_focus()

        self.focus_to_grid = focus

    def receive_focus(self, widgets):
        """Bind take focus method to all exposed widgets taking focus.

        widgets - iterable of widgets which can be given focus from self

        """
        for widget in widgets:
            self.bind(
                widget, self.receivefocuskey, function=self.focus_to_grid
            )

    def select_from_popup(self):
        """Select row under pointer unless current selection not visible."""
        if len(self.selection):
            if self.selection[0] not in self.objects:
                return
        self.move_selection_to_popup_selection()

    def cancel_select_from_popup(self):
        """Cancel selection if selected row is under pointer."""
        if self.pointer_popup_selection in self.selection:
            self.cancel_visible_selection(self.pointer_popup_selection)

    def bookmark_from_popup(self):
        """Bookmark row under pointer."""
        self.add_bookmark(self.pointer_popup_selection)

    def cancel_bookmark_from_popup(self):
        """Cancel bookmark for row under pointer."""
        if self.pointer_popup_selection in self.bookmarks:
            self.cancel_bookmark(self.pointer_popup_selection)


class SelectorGridBindings(GridBindings):
    """Standard bindings for data grids with item selection."""

    def __init__(
        self,
        selecthintlabel=None,
        setbinding=None,
        focus_selector=None,
        keypress_grid_to_select=True,
        **kwargs
    ):
        """Extend and bind grid navigation within page commands to events.

        selecthintlabel
        setbinding
        focus_selector
        keypress_grid_to_select

        """
        super().__init__(**kwargs)
        if setbinding is None:
            self.position_grid_at_record = self.navigate_grid_by_key
        else:
            self.position_grid_at_record = setbinding
        self.selecthintlabel = selecthintlabel
        self.make_focus_to_grid()
        self.make_grid_bindings(
            setfocuskey=focus_selector,
            keypress_grid_to_select=keypress_grid_to_select,
        )

    def bind_return(
        self, setbinding=None, clearbinding=None, siblingargs=(), slavegrids=()
    ):
        """Set bindings for <Return> in selector Entry widgets.

        setbinding must be an iterable of Datagrids or None
        clearbinding must be a selector Entry widget or None or True
        siblingargs
        slavegrids - keystroke sequence to give focus to grid from selector

        """
        if self.appsyspanel is None:
            return
        gridselector = self.appsyspanel.gridselector
        if not setbinding:
            if setbinding is None:
                if clearbinding is True:
                    for widget in gridselector.values():
                        self.bind(widget, "<KeyPress-Return>")
                        self.bind(widget, "<Control-KeyPress-Return>")
                else:
                    widget = gridselector.get(clearbinding)
                    if widget is not None:
                        self.bind(widget, "<KeyPress-Return>")
                        self.bind(widget, "<Control-KeyPress-Return>")
            return
        if setbinding is True:
            setbinding = (self,)
        widget = gridselector.get(self)
        if widget is not None:
            self.bind(
                widget,
                "<KeyPress-Return>",
                function=self.position_grid_at_record,
            )
            slaved = {self}
            for binding, args in zip(setbinding, siblingargs):
                for slave in slavegrids:
                    if slave == args["gridfocuskey"]:
                        slaved.add(binding)

            def position_grids(event=None):
                if not isinstance(event.widget, tkinter.Entry):
                    return False
                for slave in slaved:
                    slave.move_to_row_in_grid(event.widget.get())
                return True

            for binding, args in zip(setbinding, siblingargs):
                for slave in slavegrids:
                    if slave == args["gridfocuskey"]:
                        self.bind(
                            widget,
                            "<Control-KeyPress-Return>",
                            function=position_grids,
                        )

    def bindings(self, function=None):
        """Extend to handle FocusIn event for superclass' frame.

        function - the function to bind to event

        """
        super().bindings()
        self.bind(self.get_frame(), sequence="<FocusIn>", function=function)

    def focus_selector(self, event):
        """Give focus to the Entry for record selection."""
        if self.appsyspanel is None:
            return
        if self.appsyspanel.get_grid_selector(self) is not None:
            self.appsyspanel.give_focus(
                self.appsyspanel.get_grid_selector(self)
            )
            self.appsyspanel.get_grid_selector(self).focus_set()
        return

    def keypress_selector(self, event):
        """Give focus to the Entry for record selection and set text."""
        if event.char.isalnum():
            if self.appsyspanel is None:
                return
            self.focus_selector(event)
            self.appsyspanel.get_grid_selector(self).delete(0, tkinter.END)
            self.appsyspanel.get_grid_selector(self).insert(
                tkinter.END, event.char
            )

    def make_focus_to_grid(self):
        """Create method to give focus to self and bind to self.focus_to_grid.

        Replaces any existing definition of self.focus_to_grid method.

        """

        def focus(event):
            self.set_select_hint_label()
            self.give_and_set_focus()

        self.focus_to_grid = focus

    def make_grid_bindings(
        self, setfocuskey=None, keypress_grid_to_select=True
    ):
        """Create method to set event bindings and bind to self.grid_bindings.

        setfocuskey -
        The keypress_grid_to_select argument should be a boolean value.

        Replaces any existing definition of self.grid_bindings method.

        """
        if self.appsyspanel is None:
            return

        def bindings(siblings, siblingargs, slavegrids=(), **ka):
            widgets = (
                self.get_frame(),
                self.get_horizontal_scrollbar(),
                self.get_vertical_scrollbar(),
                self.appsyspanel.get_grid_selector(self),
            )
            rfk = self.receivefocuskey[1:-1].split("-")
            rfk.insert(0, "Control")
            defaultsetfocuskey = "-".join(rfk).join(("<", ">"))
            self.receive_focus(widgets[1:])
            for sibling in siblings:
                sibling.receive_focus(widgets)
            if widgets[-1] is not None:
                for sibling in siblings:
                    selector = self.appsyspanel.get_grid_selector(sibling)
                    if widgets[-1] is not selector:
                        for widget in (
                            selector,
                            sibling.get_frame(),
                            sibling.get_horizontal_scrollbar(),
                            sibling.get_vertical_scrollbar(),
                        ):
                            self.bind(
                                widget,
                                defaultsetfocuskey,
                                function=self.focus_selector,
                            )
                            if setfocuskey is not None:
                                self.bind(
                                    widget,
                                    setfocuskey,
                                    function=self.focus_selector,
                                )
                for widget in widgets[:-1]:
                    self.bind(
                        widget,
                        defaultsetfocuskey,
                        function=self.focus_selector,
                    )
                    if setfocuskey is not None:
                        self.bind(
                            widget, setfocuskey, function=self.focus_selector
                        )
                    if keypress_grid_to_select is True:
                        self.bind(
                            widget,
                            "<KeyPress>",
                            function=self.keypress_selector,
                        )
                # for shared selector __init__() targets last grid created
                self.bind_return(
                    setbinding=siblings,
                    siblingargs=siblingargs,
                    slavegrids=slavegrids,
                )

        self.grid_bindings = bindings

    def on_focus_in(self, event=None):
        """Clear the record selector Entry."""
        if self.appsyspanel is None:
            return
        self.appsyspanel.get_active_grid_hint(self).configure(
            text=self.selecthintlabel
        )

    def set_select_hint_label(self):
        """Set the selection widget hint (to indicate selection target)."""
        if self.appsyspanel is None:
            return
        try:
            self.appsyspanel.get_active_grid_hint(self).configure(
                text=self.selecthintlabel
            )
        except tkinter.TclError as error:
            # application destroyed while confirm dialogue exists
            if str(error) != "".join(
                (
                    'invalid command name "',
                    str(self.appsyspanel.get_active_grid_hint(self)),
                    '"',
                )
            ):
                raise
