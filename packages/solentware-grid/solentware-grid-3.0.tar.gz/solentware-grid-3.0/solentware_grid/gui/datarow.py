# datarow.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Base classes to display a database record in a row of a datagrid."""

from solentware_bind.gui.bindings import Bindings

NULL_COLOUR = "#d9d9d9"  # system backgound.
SELECTION_COLOUR = "#76d9d9"  # a light blue.
BOOKMARK_COLOUR = "#86d929"  # a light green.
SELECTION_CYCLE_COLOUR = "#eb3010"  # a dark orange.
SELECTION_AND_BOOKMARK_COLOUR = "#e0f113"  # a pale yellow.
ROW_UNDER_POINTER_COLOUR = "yellow"

# keys for header and row specification dictionaries.
GRID_COLUMNCONFIGURE = 1
GRID_CONFIGURE = 2
WIDGET_CONFIGURE = 3
WIDGET = 4
ROW = 5

_widget_configure = {"background", "font"}


class DataRowError(Exception):
    """Exception for DataRow class."""


class DataHeader(Bindings):
    """Provide methods to create a new header and configure its widgets."""

    def __init__(self):
        """Delegate to superclass then define an empty header row."""
        super().__init__()
        self.header_specification = ()

    # Not necessarily best but minimum change to get this out of DataRow.
    # Now we are there: is this method needed at all?
    def grid_header_row(self, specification):
        """Note specification and return self.make_header_widgets method.

        specification - the definition of the header row

        The master widget for the header row widget is not known when header
        is created so return the method to create the header row widget.

        """
        self.header_specification = specification
        return self.make_header_widgets

    def make_header_widgets(self, widgetpool, parent):
        """Return row of populated widgets with grid configuration arguments.

        widgetpool - function that returns an existing available widget or None
        parent - master for header row widget

        The widget pool manager returns a widget from the widget pool, or makes
        a new one if none are available, to display an item of data in the
        header row.

        The widget pool manager exists to work around a problem encountered
        when moving from Windows 2000 to XP.  Details in comments at top of
        solentware_grid.datagrid module.

        """
        # Maybe return dictionary of widgets with (row, col) as keys?
        # If spec per instance set spec[TEXT] in grid_row() call?
        row = []
        for spec in self.header_specification:
            wconf = spec[WIDGET_CONFIGURE].copy()
            widget = widgetpool(spec[WIDGET])
            if widget is None:
                widget = spec[WIDGET](master=parent)
            self.bind(widget, "<Enter>", function="")
            self.bind(widget, "<Leave>", function="")
            widget.configure(background=NULL_COLOUR, **wconf)
            widget.grid_configure(spec[GRID_CONFIGURE])
            parent.grid_columnconfigure(
                spec[GRID_CONFIGURE]["column"], spec[GRID_COLUMNCONFIGURE]
            )
            row.append((widget, spec[GRID_CONFIGURE]))
        return (row,)


class DataRow(Bindings):
    """Provide methods to create a new row and set background colour of a row.

    Set row properties based on selection status.
    Subclass must override methods grid_row.

    Typical use is
    class FooRecord(solentware_base.core.record.Record):
        ...
    class FooRow(FooRecord, solentware_grid.gui.datarow.DataRow):
        ...

    """

    # background argument to be put in kargs throughout.
    # This becomes obvious thing to do with removal of row widget.

    def __init__(self):
        """Delegate to superclass then define an empty data row."""
        super().__init__()
        self._row_widgets = ()
        self._current_row_background = NULL_COLOUR
        self._pointer_popup_active = False

    def set_current_row_background(self, value):
        """Set colour used to set backgound colour for a row to value."""
        self._current_row_background = value

    def set_background(self, widgets, background):
        """Set background colour of widgets.

        widgets - list((widget, specification), ...).
        background - the background colour.

        Each element of widgets will have been created by make_row_widgets()
        or DataHeader.make_header_widgets() and reused by DataGrid instance
        in a data row.

        """
        for widget in widgets:
            widget[0].configure(background=background)

    def set_background_bookmark(self, widgets):
        """Set background colour of widgets to BOOKMARK_COLOUR."""
        self._current_row_background = BOOKMARK_COLOUR
        self.set_background(widgets, self._current_row_background)

    def set_background_bookmarked_selection(self, widgets):
        """Set background colour to SELECTION_AND_BOOKMARK_COLOUR."""
        self._current_row_background = SELECTION_AND_BOOKMARK_COLOUR
        self.set_background(widgets, self._current_row_background)

    def set_background_normal(self, widgets):
        """Set background colour of widgets to NULL_COLOUR."""
        self._current_row_background = NULL_COLOUR
        self.set_background(widgets, self._current_row_background)

    def set_background_row_under_pointer(self, widgets):
        """Set background colour of widgets to ROW_UNDER_POINTER_COLOUR."""
        self.set_background(widgets, ROW_UNDER_POINTER_COLOUR)

    def set_background_selection(self, widgets):
        """Set background colour of widgets to SELECTION_COLOUR."""
        self._current_row_background = SELECTION_COLOUR
        self.set_background(widgets, self._current_row_background)

    def set_background_selection_cycle(self, widgets):
        """Set background colour of widgets to SELECTION_CYCLE_COLOUR."""
        self._current_row_background = SELECTION_CYCLE_COLOUR
        self.set_background(widgets, self._current_row_background)

    def form_row(self, parent, rowsizer):
        """Not implemented."""
        # Arguments unchanged from wxPython revisions.
        raise DataRowError("form_row not implemented")

    def grid_row(self, textitems=(), **kargs):
        """Return (<row maker method>, <data items>, <configuration>).

        textitems - the data items to be displayed in the row
        **kargs - configuration arguments passed to the widgets in the row

        The return value is a tuple containing the instructions to create a
        row for display in a grid.
        """
        configure = dict()
        for attr in kargs:
            if attr in _widget_configure:
                configure[attr] = kargs[attr]
        return (self.make_row_widgets, textitems, configure)

    def grid_row_bookmark(self, **kargs):
        """Return self.grid_row(background=BOOKMARK_COLOUR, **kargs)."""
        self._current_row_background = BOOKMARK_COLOUR
        return self.grid_row(background=BOOKMARK_COLOUR, **kargs)

    def grid_row_bookmarked_selection(self, **kargs):
        """Return grid_row with background SELECTION_AND_BOOKMARK_COLOUR."""
        self._current_row_background = SELECTION_AND_BOOKMARK_COLOUR
        return self.grid_row(background=SELECTION_AND_BOOKMARK_COLOUR, **kargs)

    def grid_row_normal(self, **kargs):
        """Return self.grid_row(background=NULL_COLOUR, **kargs)."""
        self._current_row_background = NULL_COLOUR
        return self.grid_row(background=NULL_COLOUR, **kargs)

    def grid_row_under_pointer(self, **kargs):
        """Return grid_row with background ROW_UNDER_POINTER_COLOUR."""
        return self.grid_row(background=ROW_UNDER_POINTER_COLOUR, **kargs)

    def grid_row_selection(self, **kargs):
        """Return self.grid_row(background=SELECTION_COLOUR, **kargs)."""
        self._current_row_background = SELECTION_COLOUR
        return self.grid_row(background=SELECTION_COLOUR, **kargs)

    def grid_row_selection_cycle(self, **kargs):
        """Return self.grid_row(background=SELECTION_CYCLE_COLOUR, **kargs)."""
        self._current_row_background = SELECTION_CYCLE_COLOUR
        return self.grid_row(background=SELECTION_CYCLE_COLOUR, **kargs)

    def __call__(self):
        """Hack to check that make_row_widgets return self enables pointer."""
        return (self._row_widgets,)

    def make_row_widgets(self, widgetpool, parent, items, **kargs):
        """Return row of populated widgets with grid configuration arguments.

        widgetpool - function that returns an existing available widget or None
        parent - master for row of widgets
        items - tuple of text option values for widget configure command.
        **kargs - widget configure options to override spec for all row widgets

        """
        # Maybe return dictionary of widgets with (row, col) as keys?
        # If spec per instance set spec[TEXT] in grid_row() call?
        row = []
        for item, spec in zip(items, self.row_specification):
            wconf = spec[WIDGET_CONFIGURE].copy()
            for attr in kargs:
                if attr not in wconf:
                    wconf[attr] = kargs[attr]
            widget = widgetpool(spec[WIDGET])
            if widget is None:
                widget = spec[WIDGET](master=parent)
            self.bind(
                widget, "<Enter>", function=self.highlight_row_on_pointer_enter
            )
            self.bind(
                widget, "<Leave>", function=self.highlight_row_on_pointer_leave
            )
            # populate_widget is Tkinter.Label.configure by default
            # Typical subclass override is populate and format the Text widget
            # passed as widget argument from the item passed as text argument.
            self.populate_widget(widget, text=item, **wconf)
            row.append((widget, spec[GRID_CONFIGURE]))
        self._row_widgets = row
        return self

    def populate_widget(self, widget, cnf=None, text=None, **kw):
        """Delegate to widget's configure method."""
        # Replaces the class attribute set by
        # populate_widget = tkinter.Label.configure
        # at Python 2.n version of this module.
        widget.configure(cnf=cnf, text=text, **kw)

    def highlight_row_on_pointer_enter(self, event):
        """Change row background colour when pointer enters row."""
        self.set_background_row_under_pointer(self._row_widgets)

    def highlight_row_on_pointer_leave(self, event):
        """Change row background colour when pointer leaves row."""
        if not self._pointer_popup_active:
            self.set_background(
                self._row_widgets, self._current_row_background
            )

    def set_popup_state(self, state=True):
        """Set flag indicating if popup menu is active.

        state - True means popup menu is active and False means inactive
        """
        self._pointer_popup_active = bool(state)

    def is_row_under_pointer(self, pointerx, pointery):
        """Return True if row is under the pointer.

        pointerx - x-coordinate of pointer position in window
        pointery - y-coordinate of pointer position in window
        """
        for row in self._row_widgets:
            widget = row[0]
            wrx = int(widget.winfo_rootx())
            wry = int(widget.winfo_rooty())
            if pointery < wry:
                pass
            elif pointery > wry + int(widget.winfo_height()):
                pass
            elif pointerx < wrx:
                pass
            elif pointerx > wrx + int(widget.winfo_width()):
                pass
            else:
                return True
        return False
