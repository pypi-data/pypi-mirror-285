# datagrid.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Base classes for scrollable grids of rows from a database."""

import tkinter
from bisect import insort, bisect_left, bisect_right

from solentware_bind.gui.bindings import Bindings

from .gui.constants import SHIFTDOWN, CONTROLDOWN
from .core.dataclient import DataClient
from .gui.datarow import DataHeader
from .gui.eventspec import EventSpec

# DataGridBase.get_spare_row_widget is necessary in XP, but not W2000 or *nix,
# to allow resizing by mouse drag to work. In W2000 and *nix destroying and
# creating windows as needed is fine. get_spare_row_widget is used in all
# environments. XP generates <Configure> events while mouse is being dragged
# but others generate one <Configure> event when mouse released.
# If I figure a way of making mouse drag resizing work while destroying and
# creating windows under XP (or someone tells me how) then get_spare_row_widget
# can be removed.
# However it probably will remain because there is a noticable performance
# advantage in having a pool of ready made widgets for scrolling.
# Known to occur with Tcl/Tk 8.4 support for Tkinter.
# A possibly related problem appeared on upgrade to FreeBSD 8.2 Python 2.7 and
# Tcl/Tk 8.5 where the resize works slowly and with too many widgets causes the
# application to enter an infinite loop judging by CPU usage.  Traced to change
# in default for opaqueresize attribute of PanedWindow from False at Tk 8.4 to
# True at 8.5 - well adding opaqueresize=False at 8.5 fixes problem.
# Certainly a plausible reason for the XP problem, where the resize backed out
# but application never failed, if defaults were different even if Tk versions
# were same.
# A similar problem appeared running under Wine after this upgrade.  It is not
# in the straightforward refresh of the grid after scrolling the grid, but when
# repopulating the grid after a change in another widget which is neither
# ancestor descendant or sibling of the grid.  An infinite loop is entered
# which can be broken by clicking on the menu bar causing the refresh, and
# other expected actions, to complete as expected.
# The Wine problem is fixed by changing DataGridBase.add_widget_to_spare_pool
# to destroy the widget.  But this brings back the problem with drag resizing
# the application on Windows 7 (Vista and XP also I assume).
# The Microsoft Windows problem does not occur at Windows 10 with Python 3.9
# or 3.10 which is fortunate because disabling the spare widget pool by
# destroying the widget in method add_widget_to_spare_pool fixes the problem
# introduced by plugging the memory leak described in the tkinter.Misc.bind
# docstring.  See methods make_header_widgets and make_row_widgets in the
# gui.datarow module.  The problem is highlighting apparently random cells
# in the datagrid when the pointer is over a header row: it is assumed the
# highlighted cells were all in the same row before the application was
# resized.


class GridBaseError(Exception):
    """Exception for DataGridBase class."""


class DataGridBase(DataClient, Bindings):
    """Display records as rows in a scrollable grid.

    The row definition class given to the DataClient via
    a DataSource class must provide a number of methods
    with pre-determined names that create and populate
    the widgets placed in the DataGrid. This in turn is
    used as a component in a parent widget.
    A key selection and bookmark management function is
    provided but use of this is for derived classes
    to define.

    """

    def __init__(self, parent=None, **kwargs):
        """Delegate to superclass then create grid widget.

        parent - passed to top tkinter.Frame in grid widget as master argument.

        Grid contains 3 rows, header data and horizontal scrollbar,
        and 2 columns: first containing the 3 rows and second containing
        vertical scrollbar for the data row.

        """
        super().__init__(**kwargs)

        self.parent = parent
        # _spare_rows use becomes uncertain in presence of gridrows_for_key
        # per class dictionary of unused widgets for constructing rows
        self._spare_rows = dict()
        # gridrows_for_keys added so that the Frame for each key can be
        # removed allowing -uniform attribute for grid geometry manager
        # to arrange data into neat columns.
        # the grid rows used for key item in self.keys (DataClient)
        self.gridrows_for_key = dict()  # {key: set([gridrow, ...,], ...)
        # Count of scrollable records.  Maintained so the slider gives a
        # reasonable idea of the number of records available.
        self.record_count = None

        # Top frame for grid widget.
        self.frame = tkinter.Frame(parent, takefocus=1, highlightthickness=1)
        self.frame.grid_rowconfigure(0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1)

        # Class responsible for creating grid header (DataHeader by default).
        self.dataheader = None

        # Set by self.make_header to invoke DataRow.make_header_widgets().
        self.header_maker = None

        # Canvas for header and data rows.
        self.gcanvas = tkinter.Canvas(self.frame)
        self.gcanvas.grid(column=0, row=0, sticky=tkinter.NSEW, rowspan=2)
        self.__bind_on()

        # Top frame for header and data rows.
        self.data = tkinter.Frame(self.gcanvas)
        self.gcanvas.create_window(0, 0, window=self.data, anchor=tkinter.NW)

        # Vertical scrollbar for data canvas.
        self.vsbar = tkinter.Scrollbar(self.frame, orient=tkinter.VERTICAL)
        self.vsbar.grid(column=1, row=1, sticky=tkinter.NSEW)
        self.vsbar_number = None
        self.bind(self.vsbar, "<ButtonRelease-1>", function=self.move_slider)

        # Horizontal scrollbar for header and data canvases.
        self.hsbar = tkinter.Scrollbar(self.frame, orient=tkinter.HORIZONTAL)
        self.hsbar.grid(column=0, row=2, sticky=tkinter.NSEW)

        self.gcanvas.configure(
            xscrollcommand=self.try_command(self.hsbar.set, self.gcanvas)
        )
        self.gcanvas.configure(
            yscrollcommand=self.try_command(self.vsbar.set, self.gcanvas)
        )
        self.hsbar.configure(
            command=self.try_command(self.set_xview, self.hsbar)
        )
        # Turn off vertical scrolling by scrollbar action if wait_visibility()
        # call turns out to be needed in fill_data_grid method.
        self.vsbar.configure(
            command=self.try_command(self.set_yview, self.vsbar)
        )

        # Current key for top row.
        # Used as a base point for scrolling.
        # Set to cursor position by _fill_down _fill_up _add_record_to_view.
        self.topkey = None

        # Key or keys of object for current selected row.
        self.selection = []

        # Keys marked while current selection (???).
        self.bookmarks = []

        # Current key for bottom row.
        # Used as a base point for scrolling.
        # Set to cursor position by _fill_down _fill_up _add_record_to_view.
        self.bottomkey = None

        # Current key on cursor.
        # Value determines action of _add_record_to_view method. There are
        # usually two versions of action: for up and down directions.
        # False - position cursor at record at top or bottom of display and
        # add record to display.
        # <any other value> - step on one record from cursor position and add
        # record to display.
        # For all values set self.currentkey to cursor position for record
        # added to display. Cursor operations may cause self.currentkey to
        # be set to None.
        self.currentkey = None

        # Current datagrid load direction.
        self.down = True

        # Set by set_fill_parameters for _add_record_to_view use as currentkey.
        self.startkey = None

        # The popup menu for the row under the pointer
        self.menupopup = tkinter.Menu(master=self.data, tearoff=False)
        self.bind(self.menupopup, "<Unmap>", function=self.exit_popup)
        self.bind(self.menupopup, "<Map>", function=self.enter_popup)

        # Click to focus and popup menu bindings for empty areas of grid.
        # Added April 2016 and some subclasses may have to suppress actions.

        # The popup menu for the grid when no row under the pointer
        self.menupopupnorow = tkinter.Menu(master=self.data, tearoff=False)

        for widget in self.gcanvas, self.data:
            self.bind(
                widget,
                EventSpec.give_focus_to_datagridbase,
                function=self.focus_set_frame,
            )
            self.bind(
                widget,
                EventSpec.insert_row_in_datagrid,
                function=self.show_popup_menu_no_row,
            )

        # Selection and pointer location when popup invoked.
        # The popup is mapped before the Leave event for invoking widget.
        # The popup is unmapped before the action, if any, is invoked.
        self.pointer_popup_xy = None
        self.pointer_popup_selection = None

    def add_bookmark(self, key):
        """Add key to bookmarks."""
        if key not in self.bookmarks:
            insort(self.bookmarks, key)
            if key not in self.keys:
                self.fill_view_from_record(key)
            else:
                self.set_properties(key)

    def add_selection_bookmark(self):
        """Add selection to bookmarks."""
        if self.selection:
            selected = self.selection[0]
            self.add_bookmark(selected)

    def _add_record_to_view(self):
        """Add record to grid and return record depending on load direction.

        This method is called repeatedly until any more records would not be
        visible on the grid.  If load direction is down return the record at
        bottom of view otherwise return record at top.

        """
        if self.cursor is not None:
            if self.currentkey is False:
                # start of new sequence of _add_record_to_view calls.
                self.currentkey, self.startkey = self.startkey, None
                if not self.currentkey:
                    if self.down:
                        self.currentkey = self.cursor.first()
                    else:
                        self.currentkey = self.cursor.last()
            elif self.down:
                # continuation of down sequence of _add_record_to_view calls.
                self.currentkey = self.cursor.next()
            else:
                # continuation of up sequence of _add_record_to_view calls.
                self.currentkey = self.cursor.prev()
            if self.currentkey:
                # get the record.
                # Adjusted to catch exception diplaying grid after drop table.
                # ValueError exception added to cope with sqlite rows kept to
                # keep bitmapped record numbers aligned with rowids allowing
                # reuse record number.
                # The test against cursor class name will be the reason sqlite3
                # does not survive as an implementation of bitmapped record
                # numbers: if it proves impossible to do a general test.
                if self.down:
                    while True:
                        try:
                            self.load_object(self.currentkey)
                        except TypeError:
                            return None
                        except ValueError:
                            if self.currentkey[-1] is None:
                                self.currentkey = self.cursor.next()
                                continue
                        self.bottomkey = self.currentkey
                        self.keys.append(self.currentkey)
                        return self.keys[-1]
                else:
                    while True:
                        try:
                            self.load_object(self.currentkey)
                        except TypeError:
                            return None
                        except ValueError:
                            if self.currentkey[-1] is None:
                                self.currentkey = self.cursor.prev()
                                continue
                        self.topkey = self.currentkey
                        self.keys.insert(0, self.currentkey)
                        return self.keys[0]
        return None

    def add_widget_to_spare_pool(self, widget):
        """Return widget to the pool of discarded grid cell widgets.

        This method is a hack to make mouse-drag resizing of the toplevel
        widget of the application work on XP.  See comments at top of
        datagrid.py

        """
        # try:
        #     self._spare_rows[widget.__class__].add(widget)
        # except KeyError:
        #     self._spare_rows[widget.__class__] = {widget}
        widget.destroy()

    def bind_off(self):
        """Disable all bindings."""
        self.bind(self.gcanvas, "<Configure>", function="")

    def bind_on(self):
        """Enable all bindings."""
        self.__bind_on()

    def __bind_on(self):
        """Enable all bindings."""
        self.bind(
            self.gcanvas, "<Configure>", function=self.on_configure_canvas
        )

    def bookmark_down(self):
        """Select first bookmark after current selection."""
        if len(self.keys) == 0:
            return

        bookmarks = self.bookmarks
        if len(bookmarks) == 0:
            return

        if self.selection:
            oldselection = self.selection[0]
        else:
            oldselection = None

        if oldselection in bookmarks:
            if oldselection in self.keys:
                if oldselection == bookmarks[-1]:
                    self.set_selection(bookmarks[0])
                else:
                    self.set_selection(
                        bookmarks[bookmarks.index(oldselection) + 1]
                    )
        elif oldselection is not None:
            i = bisect_right(bookmarks, oldselection)
            if i == len(bookmarks):
                self.set_selection(bookmarks[0])
            else:
                self.set_selection(bookmarks[i])
        else:
            i = bisect_left(bookmarks, self.keys[0])
            j = bisect_right(bookmarks, self.keys[-1])
            if i == j:
                if i == len(bookmarks):
                    self.set_selection(bookmarks[0])
                else:
                    self.set_selection(bookmarks[i])
            else:
                self.set_selection(bookmarks[i])

        if self.selection[0] not in self.keys:
            self.fill_view(currentkey=self.selection[0], exclude=False)
        else:
            self.set_properties(oldselection)
            self.set_properties(self.selection[0])

    def bookmark_up(self):
        """Select first bookmark before current selection."""
        if len(self.keys) == 0:
            return

        bookmarks = self.bookmarks
        if len(bookmarks) == 0:
            return

        if self.selection:
            oldselection = self.selection[0]
        else:
            oldselection = None

        if oldselection in bookmarks:
            if oldselection in self.keys:
                if oldselection == bookmarks[0]:
                    self.set_selection(bookmarks[-1])
                else:
                    self.set_selection(
                        bookmarks[bookmarks.index(oldselection) - 1]
                    )
        elif oldselection is not None:
            i = bisect_left(bookmarks, oldselection)
            if i == len(bookmarks):
                self.set_selection(bookmarks[-1])
            elif i == 0:
                self.set_selection(bookmarks[-1])
            else:
                self.set_selection(bookmarks[i - 1])
        else:
            i = bisect_left(bookmarks, self.keys[0])
            j = bisect_right(bookmarks, self.keys[-1])
            if i == j:
                if i == 0:
                    self.set_selection(bookmarks[-1])
                else:
                    self.set_selection(bookmarks[i - 1])
            else:
                self.set_selection(bookmarks[j - 1])

        if self.selection[0] not in self.keys:
            self.fill_view(
                currentkey=self.selection[0], down=False, exclude=False
            )
        else:
            self.set_properties(oldselection)
            self.set_properties(self.selection[0])

    def cancel_selection_bookmark(self):
        """Cancel selection from bookmarks."""
        if self.selection:
            selected = self.selection[0]
            self.cancel_bookmark(selected)

    def cancel_bookmark(self, key):
        """Cancel key from bookmarks."""
        if key in self.bookmarks:
            self.bookmarks.remove(key)
            if key not in self.keys:
                self.fill_view(currentkey=key, exclude=False)
            else:
                self.set_properties(key)

    def cancel_selection(self):
        """Cancel selection."""
        if self.selection:
            selected = self.selection[0]
            self.cancel_visible_selection(selected)

    def cancel_visible_selection(self, key):
        """Cancel selection highlighting if key is visible."""
        if key in self.keys:
            self.selection = []
            self.set_properties(key)

    def clear_bookmarks(self):
        """Clear bookmarks and remove actual visible indicators."""
        for key in self.bookmarks:
            if key in self.keys:
                self.set_properties(key)
        self.bookmarks = []

    def clear_selections(self):
        """Clear selections and remove actual visible indicators."""
        for key in self.selection:
            if key in self.keys:
                self.set_properties(key)
        self.selection = []

    def clear_client_keys(self):
        """Extend to set background for listed items if re-listed."""
        super().clear_client_keys()

    def clear_grid_description(self):
        """Clear grid description and keys."""
        self.clear_client_keys()
        self.gridrows_for_key = dict()

    def clear_grid_keys(self):
        """Clear grid selections and description and keys."""
        self.selection = []
        self.bookmarks = []
        self.topkey = None
        self.bottomkey = None
        self.currentkey = False
        self.startkey = None
        self.down = True
        self.clear_grid_description()

    def fill_data_grid(self):
        """Put rows in grid until added row is not completely visible.

        The row that is not completely visible is removed.

        """
        # forget widgets currently gridded and put in spare widget pool.
        for widget in self.data.grid_slaves():
            widget.grid_forget()
            self.add_widget_to_spare_pool(widget)
        cheight = 0
        # build widgets for header rows but do not grid them.
        headers = self.header_maker(self.get_spare_row_widget, self.data)
        cheight += self._get_row_reqheight(headers)
        for hrow in headers:
            for wspec in hrow:
                self.focus_set_grid_on_click_child_widget(wspec[0])
        # align vertical scrollbar with data rows.
        self.frame.grid_rowconfigure(0, minsize=cheight)
        # build widgets for data rows but do not grid them.
        rows = []
        if self.partial is False:
            # No keys match so display no records.
            pass
        elif self.is_load_direction_down():
            cheight = self._fill_down(rows, cheight)
            if cheight < self.gcanvas.winfo_height():
                self.reverse_add_record_direction()
                cheight = self._fill_up(rows, cheight)
            for k in self.keys[len(rows) :]:
                del self.objects[k]
                del self.gridrows_for_key[k]
            del self.keys[len(rows) :]
        else:
            cheight = self._fill_up(rows, cheight)
            if cheight < self.gcanvas.winfo_height():
                self.reverse_add_record_direction()
                cheight = self._fill_down(rows, cheight)
            for k in self.keys[: -len(rows)]:
                del self.objects[k]
                del self.gridrows_for_key[k]
            del self.keys[: -len(rows)]
        # assume one grid row per record.
        # assume all configuration done except for row and column.
        # grid the new header widgets.
        baserow = 0
        for row, gridrow in enumerate(headers):
            for column, widget in enumerate(gridrow):
                widget[0].grid_configure(
                    row=row + baserow,
                    column=column,
                    sticky=widget[1]["sticky"],
                )
        # grid the new data widgets.
        baserow += len(headers)
        for key in self.keys:
            for row, gridrow in enumerate(self.gridrows_for_key[key]()):
                for column, widget in enumerate(gridrow):
                    widget[0].grid_configure(
                        row=row + baserow,
                        column=column,
                        sticky=widget[1]["sticky"],
                    )
            baserow += len(self.gridrows_for_key[key]())
        # Ref: Pract. Prog. in Tcl and Tk (4th ed) Canvas widget Window Items.
        # There is a suggestion that a wait_visibility() call on one of the
        # self.data.grid_slaves() widgets is necessary at this point to
        # guarantee correct calculation of scrollregion below.
        # Such a call causes infinite loops when vertical scrollbar action,
        # such as click on scrollbar, is done.
        # It also causes a problem when switching to a grid in another panel
        # after window size is changed since panel last displayed. First time
        # panel is displayed nothing is visible.  But if paned windows are
        # involved there does not seem to be a problem.
        self.gcanvas.configure(
            scrollregion=" ".join(
                (
                    "0",
                    "0",
                    str(self.data.winfo_reqwidth()),
                    str(self.gcanvas.winfo_height()),
                )
            )
        )
        # Schedule the setting of vertical scrollbar to occur after processing
        # triggering event.
        self.frame.after_idle(
            self.try_command(self.set_yscrollbar, self.frame)
        )

    def fill_view(
        self,
        currentkey=None,
        down=True,
        topstart=True,
        exclude=True,
    ):
        """Clear and populate a grid.

        See set_fill_parameters for detail on use of arguments.

        Get a cursor, initialize the fill, clear current value from grid,
        fill the grid, reset the scrollbar, and close cursor.

        """
        self.datasource.dbhome.start_read_only_transaction()
        self.make_client_cursor()
        try:
            self.set_fill_parameters(
                currentkey=currentkey,
                down=down,
                topstart=topstart,
                exclude=exclude,
            )
            self.clear_grid_description()
            self.fill_data_grid()
        finally:
            self.close_client_cursor()
            self.datasource.dbhome.end_read_only_transaction()

    def fill_view_from_bottom(self):
        """Load view starting at self.bottomkey."""
        self.fill_view(currentkey=False, topstart=False)

    def fill_view_from_item_index(self, index):
        """Load view starting at record at item index."""
        self.fill_view(currentkey=self.keys[index])

    def fill_view_from_position(self, position):
        """Load view starting at position."""
        self.datasource.dbhome.start_read_only_transaction()
        self.make_client_cursor()
        try:
            key = self.cursor.get_record_at_position(position)
        finally:
            self.close_client_cursor()
            self.datasource.dbhome.end_read_only_transaction()
        self.fill_view(currentkey=key, exclude=False)

    def fill_view_from_record(self, record):
        """Load view starting at record."""
        self.fill_view(currentkey=record)

    def fill_view_from_top(self):
        """Load view starting at self.topkey."""
        self.fill_view(currentkey=self.topkey)

    def fill_view_with_top(self):
        """Load view starting at, and including, self.topkey."""
        self.fill_view(currentkey=self.topkey, exclude=False)

    def fill_view_to_item_index(self, index):
        """Load view ending at record at item index."""
        self.fill_view(currentkey=self.keys[index], down=False)

    def fill_view_to_position(self, position):
        """Load view ending at position."""
        self.make_client_cursor()
        try:
            key = self.cursor.get_record_at_position(position)
        finally:
            self.close_client_cursor()
        self.fill_view(currentkey=key, down=False)

    def fill_view_to_record(self, record):
        """Load view ending at record."""
        self.fill_view(currentkey=record, down=False)

    def fill_view_to_top(self):
        """Load view ending at self.topkey."""
        self.fill_view(currentkey=False, down=False)

    def focus_set_frame(self, event=None):
        """Give grid the focus."""
        self.frame.focus_set()

    def focus_set_grid_on_click_child_widget(self, widget):
        """Bind button1 to focus_set_frame for widget and all child widgets."""
        self.bind(
            widget,
            EventSpec.give_focus_to_datagridbase,
            function=self.focus_set_frame,
        )
        self.bind(
            widget,
            EventSpec.select_row_in_datagridbase,
            function=self.select_row_by_click,
        )
        for child in widget.winfo_children():
            self.focus_set_grid_on_click_child_widget(child)

    def get_client_item_and_record_counts(self):
        """Return scrollbar slider positioning information."""
        items = self.get_client_item_count()
        self.datasource.dbhome.start_read_only_transaction()
        self.make_client_cursor()
        try:
            if self.record_count is None:
                self.record_count = self.cursor.count_records()
            position = self.cursor.get_position_of_record(record=self.topkey)
            return self.record_count, items, position
        finally:
            self.close_client_cursor()
            self.datasource.dbhome.end_read_only_transaction()

    def get_client_item_count(self):
        """Return grid item count."""
        return len(self.keys)

    def get_row_widgets(self, key):
        """Return widgets for row associated with key."""
        widgets = []
        for row in self.gridrows_for_key[key]():
            for widget in row:
                widgets.append(widget)
        return widgets

    def get_data_canvas(self):
        """Return the data Canvas widget."""
        return self.gcanvas

    def get_data_frame(self):
        """Return the data Frame widget."""
        return self.data

    def get_frame(self):
        """Return the top Frame widget."""
        return self.frame

    def get_horizontal_scrollbar(self):
        """Return the horizontal scrollbar widget."""
        return self.hsbar

    def get_selected_record(self):
        """Return selected record if it is visible."""
        if self.selection:
            if self.selection[0] in self.keys:
                return self.objects[self.selection[0]]
        return None

    def get_spare_row_widget(self, widget_type=tkinter.Label):
        """Return a widget from the pool of discarded grid cell widgets.

        This method is a hack to make mouse-drag resizing of the toplevel
        widget of the application work on XP.  See comments at top of
        datagrid.py

        """
        swt = self._spare_rows.get(widget_type)
        if swt:
            return swt.pop()
        return None

    def get_vertical_scrollbar(self):
        """Return the vertical scrollbar widget."""
        return self.vsbar

    def get_visible_key(self, key):
        """Return key if it is visible."""
        if key in self.keys:
            return key
        return None

    def get_visible_record(self, key):
        """Return selected record if it is visible."""
        if key in self.keys:
            return self.objects[key]
        return None

    def get_visible_selected_key(self):
        """Return selected record if it is visible."""
        if self.selection:
            if self.selection[0] in self.keys:
                return self.selection[0]
        return None

    def is_load_direction_down(self):
        """Return current load direction."""
        return self.down

    def load_data_change(self, oldkeys, newkeys):
        """Replace existing rows in grid and fill it.

        oldkeys - the keys in grid
        newkeys - the keys to put in grid, replacing those already there.
        """
        if self.selection:
            oldselection = self.selection[0]
        else:
            oldselection = None

        if newkeys is None:
            for key in oldkeys:
                if oldselection == key:
                    self.selection = []
                if key in self.bookmarks:
                    self.bookmarks.remove(key)
            if self.keys:
                self.fill_view_from_item_index(0)
            else:
                self.fill_view_from_top()
        elif newkeys is False:
            if len(oldkeys):
                keys = sorted(oldkeys[:])
                self.fill_view_from_record(keys[0])
                self.set_selection(keys[0])
                self.set_properties(oldselection)
                self.set_properties(keys[0])
        else:
            for key in [o for o in oldkeys if o not in newkeys]:
                if key in self.bookmarks:
                    self.bookmarks.remove(key)
            if oldselection in newkeys:
                self.fill_view_from_item_index(0)
                self.set_selection(oldselection)
            else:
                keys = [n for n in newkeys if n not in oldkeys]
                if len(keys):
                    keys.sort()
                    self.fill_view_from_record(keys[0])
                    self.set_selection(keys[0])
                    self.set_properties(oldselection)
                    self.set_properties(keys[0])
                else:
                    self.fill_view_from_top()

    def load_new_index(self):
        """Clear selection and reload grid after changing index."""
        self.record_count = None
        self.datasource.dbhome.start_read_only_transaction()
        self.make_client_cursor()
        try:
            self.clear_grid_keys()
            self.fill_data_grid()
        finally:
            self.close_client_cursor()
            self.datasource.dbhome.end_read_only_transaction()

    def load_new_partial_key(self, key):
        """Clear selection and reload grid after changing partial key."""
        self.record_count = None
        self.set_partial_key(key)
        # Presumably to avoid calling a subclass' load_new_index() method.
        self.datasource.dbhome.start_read_only_transaction()
        self.make_client_cursor()
        try:
            self.clear_grid_keys()
            self.fill_data_grid()
        finally:
            self.close_client_cursor()
            self.datasource.dbhome.end_read_only_transaction()

    def make_header(self, specification):
        """Set header_maker as callback to create, and return, header widget.

        specification - header row definition.

        Assumption is that click gives top frame in grid the focus.

        """
        if self.dataheader is not None:
            dataheader = self.dataheader()
        else:
            dataheader = DataHeader()
        self.header_maker = dataheader.grid_header_row(specification)

    def make_row(self, record):
        """Return callback to create, and return, row of widgets.

        record - a tuple containing, in order, the method to create the row,
                the data to put in the row, and the configuration arguments
                for the widgets in the row.

        Assumption is that click gives top frame in grid the focus.

        """
        row_maker, values, kargs = record
        newrow = row_maker(
            self.get_spare_row_widget, self.data, values, **kargs
        )
        for gridrow in newrow():
            for row in gridrow:
                self.focus_set_grid_on_click_child_widget(row[0])
        return newrow

    def move_slider(self, event=None):
        """Move slider on release of button at end of motion."""
        if self.vsbar_number is None:
            return
        number = float(self.vsbar_number)
        self.vsbar_number = None
        if number < 0:
            number = 0
        elif number > 1:
            number = 1
        if self.record_count is None:
            self.make_client_cursor()
            try:
                self.record_count = self.cursor.count_records()
            finally:
                self.close_client_cursor()
        record_count = self.record_count
        position = int(record_count * number)
        if position < 0:
            position = 0
        elif position >= record_count:
            position = record_count - 1
        if self.partial is not None:
            pass
        elif position > record_count // 2:
            position = position - record_count
        self.fill_view_from_position(position)

    def encode_navigate_grid_key(self, key, encoding="utf8"):
        """Encode string for find nearest in database index.

        This method is used to process text entered by the user.
        It is not used by standard navigation functions (page up and so on).

        Subclasses must override this method if 'utf8' is not the encoding
        used on the database index which populates the grid.

        """
        return self.datasource.dbhome.encode_record_selector(key)

    def navigate_grid_by_key(self, event=None):
        """Navigate grid using partial key in Entry widget.

        The key from event.widget is non-local with respect to the keys
        displayed in the grid.  This is likely true of the event.widget key
        as characters are added and removed (compare keys P Pa and Po for
        example).  However P Pa and Po are found by searching B-tree and
        first record for key is always displayed.

        """
        if not isinstance(event.widget, tkinter.Entry):
            return False
        self.move_to_row_in_grid(event.widget.get())
        return True

    def move_to_row_in_grid(self, key):
        """Navigate grid to nearest row starting with key."""
        self.datasource.dbhome.start_read_only_transaction()
        cursor = self.datasource.get_cursor()
        try:
            cursor.set_partial_key(self.partial)
            row = cursor.nearest(self.encode_navigate_grid_key(key))
        finally:
            cursor.close()
            self.datasource.dbhome.end_read_only_transaction()
        self.fill_view(currentkey=row, exclude=False)

    def on_configure_canvas(self, event=None):
        """Populate grid for a <Configure> event (resize)."""
        self.datasource.dbhome.start_read_only_transaction()
        self.make_client_cursor()
        try:
            self.set_fill_parameters(currentkey=False)
            self.clear_grid_description()
            self.fill_data_grid()
        finally:
            self.close_client_cursor()
            self.datasource.dbhome.end_read_only_transaction()

    def on_data_change(self, instance):
        """Refresh data control after database update for instance.

        If instance is None refresh control.
        If instance.newrecord is False then object was added.
        If instance.newrecord is None or absent then object was deleted.
        Otherwise object.newrecord replaced object.
        Exact behaviour depends on use of set_data_source method.

        """
        self.record_count = None
        self.refresh_cursor(instance)
        if instance is None:
            if len(self.keys) == 0:
                self.fill_view_from_top()
                return
            # does self.fill_view_from_top() do this as well? if so use it!
            self.datasource.dbhome.start_read_only_transaction()
            record = self.make_client_cursor(self.keys[0])
            try:
                if record is None:
                    record = self.cursor.nearest(self.keys[0][0])
                self.set_fill_parameters(currentkey=record, exclude=False)
                self.clear_client_keys()
                self.fill_data_grid()
            finally:
                self.close_client_cursor()
                self.datasource.dbhome.end_read_only_transaction()
            return

        oldkeys = instance.get_keys(self.datasource)
        newobject = instance.__dict__.get("newrecord")
        # Changed to allow removal of 'self.newrecord = None' in edit_record()
        # method of Record in record.py with the beneficial consequence new
        # record data remains available when "on_data_change" methods fire.
        # The 'else' clause below will need changing because grid displays may
        # now move the updated record to top of grid display rather than show
        # the same records.
        if newobject is None:  # == None:
            newkeys = newobject
        elif newobject is False:  # == False:
            newkeys = newobject
        else:
            newkeys = None  # newobject.get_keys(self.datasource)
        self.load_data_change(oldkeys, newkeys)

    def reverse_add_record_direction(self):
        """Add records to opposite end of self.keys in future."""
        if self.down:
            if self.topkey is not None:
                self.currentkey = self.cursor.setat(self.topkey)
            else:
                self.currentkey = False
        else:
            if self.bottomkey is not None:
                self.currentkey = self.cursor.setat(self.bottomkey)
            else:
                self.currentkey = False
        self.down = not self.down

    def scroll_grid_down_one_line(self):
        """Scroll grid retaining displayed versions of existing rows."""
        self.fill_view_from_top()

    def scroll_grid_up_one_line(self):
        """Scroll grid retaining displayed versions of existing rows."""
        self.fill_view(currentkey=self.bottomkey, down=False)

    def select_cycle_down(self):
        """Select row in current selection by next key."""
        if len(self.keys) == 0:
            return
        if len(self.selection) < 2:
            return
        oldselection = self.selection[0]
        self.selection.append(self.selection.pop(0))
        selected = self.selection[0]
        if selected not in self.keys:
            self.fill_view_from_record(selected)
        self.set_properties(oldselection)
        self.set_properties(selected)

    def select_cycle_up(self):
        """Select row in current selection by previous key."""
        if len(self.keys) == 0:
            return
        if len(self.selection) < 2:
            return
        oldselection = self.selection[0]
        self.selection.insert(0, self.selection.pop(-1))
        selected = self.selection[0]
        if selected not in self.keys:
            self.fill_view_to_record(selected)
        self.set_properties(oldselection)
        self.set_properties(selected)

    def select_down(self):
        """Select row after current selection."""
        if len(self.keys) == 0:
            return
        if self.selection:
            oldselection = self.selection[0]
        else:
            oldselection = None
        if oldselection is None:
            self.set_selection(self.keys[0])
        elif oldselection == self.keys[-1]:
            self.scroll_grid_down_one_line()
            self.set_selection(self.keys[-1])
        elif oldselection not in self.keys:
            self.fill_view(currentkey=oldselection, exclude=False)
            return
        else:
            self.set_selection(self.keys[self.keys.index(oldselection) + 1])
        self.set_properties(oldselection)
        self.set_properties(self.selection[0])

    def select_up(self):
        """Select row before current selection."""
        if len(self.keys) == 0:
            return
        if self.selection:
            oldselection = self.selection[0]
        else:
            oldselection = None
        if oldselection is None:
            self.set_selection(self.keys[-1])
        elif oldselection == self.keys[0]:
            self.scroll_grid_up_one_line()
            self.set_selection(self.keys[0])
        elif oldselection not in self.keys:
            self.fill_view(currentkey=oldselection, down=False, exclude=False)
            return
        else:
            self.set_selection(self.keys[self.keys.index(oldselection) - 1])
        self.set_properties(oldselection)
        self.set_properties(self.selection[0])

    def set_data_header(self, header=None):
        """Set current dataheader generator.

        By default datarow.DataHeader class is used to generate a grid header.
        A custom header builder can be supplied using this method.

        """
        self.dataheader = header

    def set_fill_parameters(
        self,
        currentkey=None,
        down=True,
        topstart=True,
        exclude=True,
    ):
        """Set start point and direction for next fill of grid.

        currentkey - start key for next fill of grid
        down == True - direction down
        topstart == True - start at top (if currentkey == None)
        exclude == True - exclude currentkey (if currentkey != None)

        currentkey is likely local with respect to the keys displayed in the
        grid.  first() and last() are exceptions but the destination is easy
        to reach.

        """
        if currentkey:
            self.currentkey = False
            self.startkey = self.cursor.setat(currentkey)
            if self.startkey is None:
                if down:
                    if self.topkey:
                        self.startkey = self.cursor.setat(self.topkey)
                    else:
                        self.startkey = self.cursor.first()
                elif self.bottomkey:
                    self.startkey = self.cursor.setat(self.bottomkey)
                else:
                    self.startkey = self.cursor.last()
            elif exclude:
                if down:
                    self.startkey = self.cursor.next()
                    if self.startkey is None:
                        self.startkey = self.cursor.first()
                else:
                    self.startkey = self.cursor.prev()
                    if self.startkey is None:
                        self.startkey = self.cursor.last()
        else:
            self.currentkey = currentkey
            if topstart:
                if self.topkey:
                    self.startkey = self.cursor.setat(self.topkey)
                else:
                    self.startkey = self.cursor.first()
            elif self.bottomkey:
                self.startkey = self.cursor.setat(self.bottomkey)
            else:
                self.startkey = self.cursor.last()

        self.topkey = None
        self.bottomkey = None
        self.down = down

    def set_grid_properties(self):
        """Set widget properties for all rows in grid.

        This method does not refresh the displayed data from the database.

        """
        for key in self.keys:
            self.set_properties(key)

    def set_properties(self, key, dodefaultaction=True):
        """Set row properties and return True if settings for key are done.

        The return value is always True unless bool(dodefaultaction) is False.

        This method allows caller to take responsibility for setting properties
        where the alternative is the default properties. dodefaultaction=False
        causes this method to return False in cases where it would otherwise
        set the default properties.

        """
        if key not in self.keys:
            return True
        if self.selection:
            selection = self.selection[0]
        else:
            selection = None
        if key == selection:
            if key in self.bookmarks:
                self.objects[key].set_background_bookmarked_selection(
                    self.get_row_widgets(key)
                )
            elif key != self.selection[-1]:
                self.objects[key].set_background_selection_cycle(
                    self.get_row_widgets(key)
                )
            else:
                self.objects[key].set_background_selection(
                    self.get_row_widgets(key)
                )
        elif key in self.bookmarks:
            self.objects[key].set_background_bookmark(
                self.get_row_widgets(key)
            )
        elif dodefaultaction:
            self.objects[key].set_background_normal(self.get_row_widgets(key))
        else:
            return False
        self.set_row_under_pointer_background(key)
        return True

    def set_row_under_pointer_background(self, key):
        """Set row backgound if row for key is under pointer."""
        if self.objects[key].is_row_under_pointer(*self.get_pointerxy()):
            self.objects[key].set_background_row_under_pointer(
                self.get_row_widgets(key)
            )

    def set_row(self, key, dodefaultaction=True, **kargs):
        """Return row widget for key or None.

        **kargs can contain arguments in either of two sets.  One set is widget
        configuration arguments passed to things like Tkinter.Text() calls and
        the other set is used by an extension of the grid_row method in a
        subclass of DataRow.

        """
        if key not in self.keys:
            return None
        if self.selection:
            selection = self.selection[0]
        else:
            selection = None
        if key == selection:
            if key in self.bookmarks:
                return self.objects[key].grid_row_bookmarked_selection(**kargs)
            if len(self.selection) > 1:
                return self.objects[key].grid_row_selection_cycle(**kargs)
            return self.objects[key].grid_row_selection(**kargs)
        if key in self.bookmarks:
            return self.objects[key].grid_row_bookmark(**kargs)
        if dodefaultaction:
            return self.objects[key].grid_row_normal(**kargs)
        return None

    def set_selection(self, key):
        """Set selection to all keys for row referenced by key.

        Often this does, in effect, self.selection = [key]

        """
        if key not in self.objects:
            self.fill_view(currentkey=key, exclude=False)
        selection = sorted(
            self.objects[key].get_keys(self.datasource, self.partial)
        )
        for i in range(len(selection)):
            if key == selection[0]:
                self.selection = selection
                break
            selection.append(selection.pop(0))
        else:
            self.selection = [key]

    def set_yscrollbar(self):
        """Set Y scrollbar to match position of displayed records in file."""
        # It seems necessary to postpone set_yscrollbar till completion of
        # triggering event by <...>.after_idle(self.set_yscrollbar).  Calling
        # set_yscrollbar directly causes slider to fill scrollbar (at time of
        # writing - also not clear if this is correct effect).

        # Changes to close cursors as soon as possible seem to have closed them
        # too early when after_idle is involved in a path which closes a grid.
        # Do nothing because get_client_item_and_record_counts will try to make
        # a cursor for self.datasource.

        # At revision 5213 (appsuites), 5214 (app-lmdb), self.topkey points
        # to record relevant after moving slider in bsddb3, but to record
        # relevant before moving slider in lmdb, at this point when the
        # primary database (Berkeley DB term) is displayed in the grid.
        # Thus the call to self.get_client_item_and_record_counts()
        # calculates the wrong position for slider in lmdb.
        # Secondary databases (Berkeley DB term) are not affected.
        # Other database engine behave like bsddb3, or berkeleydb,
        # whichever is installed, and supported, by the version of Python
        # used (berkeleydb available >= 3.6 and bsddb3 < 10).

        # There is another problem with ordered display by secondary database
        # key first confirmed on lmdb.
        # An erratic number of rows are displayed on the grid, both
        # initally and on scrolling in some way, and an exception occurs
        # sooner or later on repeated scrolling action.
        # (This is a convenient place for noting it's existence.)
        # (No idea if the problem is related to the one tracked to here.)

        # Running solentware_base.samples.compare_secondary_dumps and
        # solentware_base.samples.compare_primary_dumps suggests the problem
        # arises from splicing the final segment of one import with the
        # first segment of the next import whenever an import does not end
        # on a segment boundary.  The problem affects bsddb3 too, but not
        # vedis or sqlite3, so there seems to be a problem in the _dbdu
        # module, and the _dbdu_tkinter and _lmdbdu modules derived from it.
        # The primary database seems to be fine, but all secondary databases
        # are affected.  The problem exists on ancient versions where just
        # bsddb3 was available.

        # There was some cursor confusion in method
        # solentware_base.core._dbdu.Database._sort_and_write_high_or_chunk().

        if self.datasource is None:
            return
        count, items, position = self.get_client_item_and_record_counts()
        # There may be not enough records to fill the widget; and position
        # is counted from 1 while slider position calculation needs a
        # position counted from 0 (zero).
        # Assume items == 0 if count == 0.
        if count <= items:
            self.vsbar.set(0.0, 1.0)
        else:
            self.vsbar.set(
                float(position - 1) / count,
                float(position - 1 + items) / count,
            )

    def set_xview(self, scroll=None, number=None, scrollunit=None):
        """Adjust datagrid on horizontal scrollbar action."""
        self.gcanvas.xview(scroll, number, scrollunit)
        self.frame.after_idle(
            self.try_command(self.set_yscrollbar, self.frame)
        )

    def set_yview(self, scroll=None, number=None, scrollunit=None):
        """Adjust datagrid on vertical scrollbar action.

        moveto disabled in Berkeley DB because it takes too long to
        maintain reliable record counts.

        """
        if self.get_client_item_count():
            if scroll == "scroll":
                if int(number) > 0:
                    if scrollunit == "pages":
                        self.fill_view_from_item_index(
                            max(-2, -self.get_client_item_count())
                        )
                    elif scrollunit == "units":
                        self.fill_view_from_item_index(0)
                else:
                    if scrollunit == "pages":
                        if self.get_client_item_count() > 1:
                            self.fill_view_to_item_index(1)
                        else:
                            self.fill_view_to_item_index(0)
                    elif scrollunit == "units":
                        self.fill_view_to_item_index(-1)
            elif scroll == "moveto":
                self.vsbar_number = number
                # movement done by move_slider() method on button release.

    def select_row_by_click(self, event=None):
        """Select row clicked by button-3 (right)."""
        self.pointer_popup_selection = None
        event_wigdet = event.widget
        for k, row in self.gridrows_for_key.items():
            for item in row():
                for widget, i in item:
                    if widget == event_wigdet:
                        self.pointer_popup_selection = k
                        self.show_popup_menu()
                        return

    def show_popup_menu(self):
        """Show the popup menu for the grid over a row.

        Subclasses may have particular entries to be the default which is
        implemented by overriding this method.

        """
        self.pointer_popup_xy = self.data.winfo_pointerxy()
        self.menupopup.tk_popup(*self.pointer_popup_xy)

    def show_popup_menu_no_row(self, event=None):
        """Show the popup menu for the grid over no row.

        Subclasses may have particular entries to be the default which is
        implemented by overriding this method.

        """
        self.pointer_popup_xy = self.data.winfo_pointerxy()
        self.menupopupnorow.tk_popup(*self.pointer_popup_xy)

    # At present callers must establish the keystroke binding.
    # Intention is to fix on 'Shift F10' implemented in DataGridBase class at
    # some point in future.
    # return 'break' to prevent the menubar, if there is one, being activated.
    def show_grid_or_row_popup_menu_at_top_left_by_keypress(self, event=None):
        """Show the popup menu for the grid or the selected row if visible.

        At some point in future the binding will become 'Shift F10' by default
        but at present callers must establish a suitable keystroke binding.

        """
        self.pointer_popup_xy = event.x_root - event.x, event.y_root - event.y
        if self.selection:
            if self.selection[0] in self.gridrows_for_key:
                self.pointer_popup_selection = self.selection[0]
                self.menupopup.tk_popup(*self.pointer_popup_xy)
                return "break"
        self.menupopupnorow.tk_popup(*self.pointer_popup_xy)
        return "break"

    # At present callers must establish the keystroke binding.
    # Intention is to fix on 'Ctrl F10' implemented in DataGridBase class at
    # some point in future.
    # return 'break' to prevent the menubar, if there is one, being activated.
    def show_grid_or_row_popup_menu_at_pointer_by_keypress(self, event=None):
        """Show the popup menu for the grid or the selected row if visible.

        The pointer may be anywhere: context is provided by the widget having
        focus, not pointer location.

        At some point in future the binding will become 'Ctrl F10' by default
        but at present callers must establish a suitable keystroke binding.

        """
        self.pointer_popup_xy = event.widget.winfo_pointerxy()
        if self.selection:
            if self.selection[0] in self.gridrows_for_key:
                self.pointer_popup_selection = self.selection[0]
                self.menupopup.tk_popup(*self.pointer_popup_xy)
                return "break"
        self.menupopupnorow.tk_popup(*self.pointer_popup_xy)
        return "break"

    def move_selection_to_popup_selection(self):
        """Change selection to active row for popup menu."""
        if self.selection:
            oldselection = self.selection[0]
        else:
            oldselection = None
        self.set_selection(self.pointer_popup_selection)
        self.pointer_popup_selection = None
        self.set_properties(oldselection)
        self.set_properties(self.selection[0])

    def exit_popup(self, event=None):
        """Reset the colour of popup row to the current normal colour."""
        # See enter_popup - this may be affected too.
        try:
            self.objects[self.pointer_popup_selection].set_popup_state(
                state=False
            )
            self.set_properties(self.pointer_popup_selection)
        except KeyError:
            pass

    def enter_popup(self, event=None):
        """Set colour of popup row to the colour when under pointer."""
        # KeyError exception was raised on the first self.objects reference
        # approximately concurrent with a widget refresh when deleting the
        # associated database record.  Unable to repeat but the consequence was
        # very severe as I had to power-off to recover (after attempting to
        # view the error detail from the error dialogue).  May be because the
        # row was the top one in the grid.
        # No problems on database afterwards, and the delete succeeded.
        # Briefly it is not yet clear where to adjust pointer_popup_selection.
        key = self.pointer_popup_selection
        try:
            self.objects[key].set_popup_state(state=True)
            self.objects[key].set_background_row_under_pointer(
                self.get_row_widgets(key)
            )
        except KeyError:
            pass

    def get_pointerxy(self):
        """Return the xy pixel coordinates of the pointer."""
        return self.data.winfo_pointerxy()

    def _fill_down(self, rows, cheight):
        """Put rows in grid until added row is not completely visible."""
        # should setting self.topkey and self.bottomkey be job of caller?
        while True:
            if cheight > self.gcanvas.winfo_height():
                if len(rows) > 1:
                    cheight -= self._get_row_reqheight(rows[-1]())
                    for k in rows.pop()():
                        for j in k:
                            j[0].grid_forget()
                            self.add_widget_to_spare_pool(j[0])
                    try:
                        del self.objects[self.keys[-1]]
                        del self.gridrows_for_key[self.keys[-1]]
                        del self.keys[-1]
                        self.bottomkey = self.keys[-1]
                    except:
                        self.bottomkey = None
                        self.topkey = None
                break
            if len(self.keys) > len(rows):
                key = self.bottomkey = self.keys[len(rows)]
            else:
                key = self._add_record_to_view()
            if key is None:
                break
            rows.append(self.make_row(self.set_row(key)))
            cheight += self._get_row_reqheight(rows[-1]())
            self.gridrows_for_key[key] = rows[-1]

        try:
            self.topkey = self.keys[0]
        except:
            pass
        return cheight

    def _fill_up(self, rows, cheight):
        """Put rows in grid until added row is not completely visible."""
        # should setting self.topkey and self.bottomkey be job of caller?
        while True:
            if cheight > self.gcanvas.winfo_height():
                if len(rows) > 1:
                    cheight -= self._get_row_reqheight(rows[-1]())
                    for k in rows.pop(0)():
                        for j in k:
                            j[0].grid_forget()
                            self.add_widget_to_spare_pool(j[0])
                    try:
                        del self.objects[self.keys[0]]
                        del self.gridrows_for_key[self.keys[0]]
                        del self.keys[0]
                        self.topkey = self.keys[0]
                    except:
                        self.bottomkey = None
                        self.topkey = None
                break
            if len(self.keys) > len(rows):
                key = self.topkey = self.keys[-len(rows) - 1]
            else:
                key = self._add_record_to_view()
            if key is None:
                break
            rows.insert(0, self.make_row(self.set_row(key)))
            cheight += self._get_row_reqheight(rows[-1]())
            self.gridrows_for_key[key] = rows[0]

        try:
            self.bottomkey = self.keys[-1]
        except:
            pass
        return cheight

    def _get_row_reqheight(self, rows):
        """Return sum of maximum reqheight of widgets in each row in rows."""
        return sum([max([w[0].winfo_reqheight() for w in r]) for r in rows])


class DataGridReadOnly(DataGridBase):
    """Data grid defining all read-only navigation."""

    def __init__(self, **kwargs):
        """Delegate to superclass then enable event bindings for this class."""
        super().__init__(**kwargs)
        self.__bind_on()

    def bind_off(self):
        """Disable all bindings."""
        super().bind_off()
        for sequence, function in (
            (EventSpec.up_one_page, ""),
            (EventSpec.down_one_page, ""),
            (EventSpec.down_all, ""),
            (EventSpec.up_all, ""),
            (EventSpec.up_one_line, ""),
            (EventSpec.up_one_line_in_selection, ""),
            (EventSpec.down_one_line, ""),
            (EventSpec.down_one_line_in_selection, ""),
            (EventSpec.move_visible_select_up_one_line, ""),
            (EventSpec.up_one_bookmarked_line_move_select, ""),
            (EventSpec.up_one_line_move_select, ""),
            (EventSpec.move_select_up_one_line_after_align, ""),
            (EventSpec.move_visible_select_down_one_line, ""),
            (EventSpec.down_one_bookmarked_line_move_select, ""),
            (EventSpec.down_one_line_move_select, ""),
            (EventSpec.move_select_down_one_line_after_align, ""),
            (EventSpec.bookmark_selected_line, ""),
            (EventSpec.remove_selected_line_from_bookmark, ""),
            (EventSpec.remove_selected_line_from_selection, ""),
        ):
            self.bind(self.frame, sequence[0], function=function)

    def bind_on(self):
        """Enable all bindings."""
        super().bind_on()
        self.__bind_on()

    def __bind_on(self):
        """Enable all bindings."""
        for sequence, function in (
            (EventSpec.up_one_page, self.up_one_page),
            (EventSpec.down_one_page, self.down_one_page),
            (EventSpec.down_all, self.down_all),
            (EventSpec.up_all, self.up_all),
            (EventSpec.up_one_line, self.up_one_line),
            (EventSpec.up_one_line_in_selection, self.up_one_line_selection),
            (EventSpec.down_one_line, self.down_one_line),
            (
                EventSpec.down_one_line_in_selection,
                self.down_one_line_selection,
            ),
            (
                EventSpec.move_visible_select_up_one_line,
                self.select_up_one_line,
            ),
            (
                EventSpec.up_one_bookmarked_line_move_select,
                self.select_bookmark_up_one_line,
            ),
            (
                EventSpec.up_one_line_move_select,
                self.select_up_one_line_control,
            ),
            (
                EventSpec.move_select_up_one_line_after_align,
                self.select_up_one_line_shift,
            ),
            (
                EventSpec.move_visible_select_down_one_line,
                self.select_down_one_line,
            ),
            (
                EventSpec.down_one_bookmarked_line_move_select,
                self.select_bookmark_down_one_line,
            ),
            (
                EventSpec.down_one_line_move_select,
                self.select_down_one_line_control,
            ),
            (
                EventSpec.move_select_down_one_line_after_align,
                self.select_down_one_line_shift,
            ),
            (EventSpec.bookmark_selected_line, self.add_bookmark_event),
            (
                EventSpec.remove_selected_line_from_bookmark,
                self.cancel_bookmark_event,
            ),
            (
                EventSpec.remove_selected_line_from_selection,
                self.cancel_selection_event,
            ),
        ):
            self.bind(self.frame, sequence[0], function=function)

    def up_one_page(self, event):
        """Scroll grid up one page of rows."""
        self.fill_view_to_top()

    def down_one_page(self, event):
        """Scroll grid down one page of rows."""
        self.fill_view_from_bottom()

    def down_all(self, event=None):  # Hack for menu item.
        """Scroll grid to last row."""
        self.topkey = None
        self.bottomkey = None
        self.fill_view(currentkey=False, down=False, topstart=False)

    def up_all(self, event=None):  # Hack for menu item.
        """Scroll grid to first row."""
        self.topkey = None
        self.bottomkey = None
        self.fill_view(currentkey=False)

    def up_one_line(self, event):
        """Scroll grid up one row."""
        self.scroll_grid_up_one_line()

    def up_one_line_selection(self, event):
        """Scroll grid up one row in selection."""
        self.select_cycle_up()

    def down_one_line(self, event):
        """Scroll grid down one row."""
        self.scroll_grid_down_one_line()

    def down_one_line_selection(self, event):
        """Scroll grid down one row in selection."""
        self.select_cycle_down()

    def select_bookmark_up_one_line(self, event):
        """Make the previous bookmark visible as top row."""
        self.bookmark_up()

    def select_up_one_line_shift(self, event):
        """Move the selection to previous row from current selection."""
        self.select_up()

    def select_up_one_line(self, event=None):  # Hack for menu item.
        """Move the selection to previous row if selection is visible."""
        if self.selection:
            if self.selection[0] in self.keys:
                self.select_up()
        else:
            self.select_up()

    def select_up_one_line_control(self, event=None):  # Hack for menu item.
        """Move selection to previous row or bottom row if not visible."""
        if self.selection:
            if self.selection[0] in self.keys:
                self.select_up()
            else:
                self.selection = []
                self.select_up()
        else:
            self.select_up()

    def select_bookmark_down_one_line(self, event):
        """Make the next bookmark visible as top row."""
        self.bookmark_down()

    def select_down_one_line_shift(self, event):
        """Move the selection to next row from current selection."""
        self.select_down()

    def select_down_one_line(self, event=None):  # Hack for menu item.
        """Move the selection to next row if selection is visible."""
        if self.selection:
            if self.selection[0] in self.keys:
                self.select_down()
        else:
            self.select_down()

    def select_down_one_line_control(self, event=None):  # Hack for menu item.
        """Move selection to next row or top row if not visible."""
        if self.selection:
            if self.selection[0] in self.keys:
                self.select_down()
            else:
                self.selection = []
                self.select_down()
        else:
            self.select_down()

    def add_bookmark_event(self, event):
        """Add selection."""
        self.add_selection_bookmark()

    def cancel_bookmark_event(self, event):
        """Cancel bookmark."""
        self.cancel_selection_bookmark()

    def cancel_selection_event(self, event):
        """Cancel selection."""
        self.cancel_selection()


class DataGrid(DataGridReadOnly):
    """Data grid defining all update navigation."""

    def __init__(self, **kwargs):
        """Delegate to superclass then enable event bindings for this class."""
        super().__init__(**kwargs)
        self.__bind_on()
        for function, accelerator in (
            (self.show_from_popup, EventSpec.launch_show_dialog),
            (self.insert_from_popup, EventSpec.launch_insert_dialog),
            (self.edit_from_popup, EventSpec.launch_edit_dialog),
            (self.edit_show_from_popup, EventSpec.launch_edit_and_show_dialog),
            (self.delete_from_popup, EventSpec.launch_delete_dialog),
        ):
            self.menupopup.add_command(
                label=accelerator[1],
                command=self.try_command(function, self.menupopup),
                accelerator=accelerator[2],
            )
        for function, accelerator in (
            (self.insert_from_popup, EventSpec.launch_insert_dialog),
        ):
            self.menupopupnorow.add_command(
                label=accelerator[1],
                command=self.try_command(function, self.menupopupnorow),
                accelerator=accelerator[2],
            )
        self.menupopup_grid_actions = tkinter.Menu(
            master=self.menupopup, tearoff=False
        )
        self.menupopup.add_cascade(
            label="Grid Actions", menu=self.menupopup_grid_actions
        )
        for function, accelerator in (
            (self.fill_view_to_top, EventSpec.up_one_page),
            (self.fill_view_from_bottom, EventSpec.down_one_page),
            (self.up_all, EventSpec.up_all),
            (self.down_all, EventSpec.down_all),
            (self.scroll_grid_up_one_line, EventSpec.up_one_line),
            (self.scroll_grid_down_one_line, EventSpec.down_one_line),
            (self.select_cycle_up, EventSpec.up_one_line_in_selection),
            (self.select_cycle_down, EventSpec.down_one_line_in_selection),
            (
                self.select_up_one_line,
                EventSpec.move_visible_select_up_one_line,
            ),
            (
                self.select_down_one_line,
                EventSpec.move_visible_select_down_one_line,
            ),
            (
                self.select_up_one_line_control,
                EventSpec.up_one_line_move_select,
            ),
            (
                self.select_down_one_line_control,
                EventSpec.down_one_line_move_select,
            ),
            (self.select_up, EventSpec.move_select_up_one_line_after_align),
            (
                self.select_down,
                EventSpec.move_select_down_one_line_after_align,
            ),
            (self.bookmark_up, EventSpec.up_one_bookmarked_line_move_select),
            (
                self.bookmark_down,
                EventSpec.down_one_bookmarked_line_move_select,
            ),
            (self.add_selection_bookmark, EventSpec.bookmark_selected_line),
            (
                self.cancel_selection_bookmark,
                EventSpec.remove_selected_line_from_bookmark,
            ),
            (
                self.cancel_selection,
                EventSpec.remove_selected_line_from_selection,
            ),
        ):
            self.menupopup_grid_actions.add_command(
                label=accelerator[1],
                command=self.try_command(
                    function, self.menupopup_grid_actions
                ),
                accelerator=accelerator[2],
            )

    def bind_off(self):
        """Disable all bindings."""
        super().bind_off()
        for sequence, function in (
            (EventSpec.launch_show_dialog, ""),
            (EventSpec.launch_insert_dialog, ""),
            (EventSpec.launch_delete_dialog, ""),
        ):
            self.bind(self.frame, sequence[0], function=function)

    def bind_on(self):
        """Enable all bindings."""
        super().bind_on()
        self.__bind_on()

    def __bind_on(self):
        """Enable all bindings."""
        for sequence, function in (
            (EventSpec.launch_show_dialog, self.show_dialog_event),
            (EventSpec.launch_insert_dialog, self.edit_dialog_event),
            (EventSpec.launch_delete_dialog, self.delete_dialog_event),
        ):
            self.bind(self.frame, sequence[0], function=function)

    def create_delete_dialog(
        self, instance, oldobject, modal, title="Delete record"
    ):
        """Create dialogue and display record for deletion.

        Create a toplevel widget and pass it to the record's delete_row
        method for completion before concluding the dialog.

        This method may need to be extended in subclasses, especially if the
        launch_... methods are extended.

        """
        # need to make dialog modal if requested {dialog.grab_set() sequence}.
        dialog = tkinter.Toplevel(master=self.parent)
        dialog.wm_title(title)
        datadelete = instance.delete_row(dialog, oldobject)
        datadelete.set_data_source(self.datasource, datadelete.on_data_change)

    def create_edit_dialog(
        self,
        instance,
        newobject,
        oldobject,
        showinitial,
        modal,
        title="Edit Record",
    ):
        """Create dialog and display for record insetion or amendment.

        Create a toplevel widget and pass it to the record's edit_row
        method for completion before concluding the dialog.

        This method may need to be extended in subclasses, especially if the
        launch_... methods are extended.

        """
        # need to make dialog modal if requested {dialog.grab_set() sequence}.
        dialog = tkinter.Toplevel(master=self.parent)
        dialog.wm_title(title)
        dataedit = instance.edit_row(dialog, newobject, oldobject, showinitial)
        dataedit.set_data_source(self.datasource, dataedit.on_data_change)

    def create_show_dialog(
        self, instance, oldobject, modal, title="Show record"
    ):
        """Create dialogue and display.

        Create a toplevel widget and pass it to the record's delete_row
        method for completion before concluding the dialog.

        This method may need to be extended in subclasses, especially if the
        launch_... methods are extended.

        """
        # need to make dialog modal if requested {dialog.grab_set() sequence}.
        dialog = tkinter.Toplevel(master=self.parent)
        dialog.wm_title(title)
        datashow = instance.show_row(dialog, oldobject)
        datashow.set_data_source(self.datasource, datashow.on_data_change)

    def edit_dialog(self, key, event, modal=True):
        """Display object for editing and optionally a copy of original."""
        if key not in self.keys:
            self.launch_insert_new_record(modal=modal)
        elif event.state & SHIFTDOWN:
            self.launch_edit_record(key, modal=modal)
        elif event.state & CONTROLDOWN:
            self.launch_edit_show_record(key, modal=modal)
        else:
            self.launch_insert_new_record(modal=modal)

    def edit_dialog_event(self, event):
        """Add selection and database record insert and edit functions."""
        if self.selection:
            selected = self.selection[0]
        else:
            selected = None
        self.edit_dialog(selected, event, False)

    def delete_dialog(self, key, event, modal=True):
        """Create and display object to be deleted.

        By default use the datagrid new_row() method.  If the row instance does
        not implement the full behaviour needed to generate the database
        transaction this delete_dialog method must be overridden in the
        DataGrid subclass.

        """
        if key not in self.keys:
            return
        self.launch_delete_record(key)

    def delete_dialog_event(self, event):
        """Cancel selection and database record delete function."""
        if self.selection:
            selected = self.selection[0]
        else:
            selected = None
        self.delete_dialog(selected, event, False)

    def show_dialog(self, key, event, modal=True):
        """Create and display object.

        By default use the datagrid new_row() method.  If the row instance does
        not implement the full behaviour needed to generate the database
        transaction this delete_dialog method must be overridden in the
        DataGrid subclass.

        """
        if key not in self.keys:
            return
        self.launch_show_record(key)

    def show_dialog_event(self, event):
        """Cancel selection and database record show function."""
        if self.selection:
            selected = self.selection[0]
        else:
            selected = None
        self.show_dialog(selected, event, False)

    def delete_from_popup(self):
        """Launch a delete record dialogue."""
        self.launch_delete_record(self.pointer_popup_selection)
        self.move_selection_to_popup_selection()

    def edit_from_popup(self):
        """Launch an edit record dialogue from popup."""
        self.launch_edit_record(self.pointer_popup_selection)
        self.move_selection_to_popup_selection()

    def edit_show_from_popup(self):
        """Launch an edit record dialogue with a reference copy from popup."""
        self.launch_edit_show_record(self.pointer_popup_selection)
        self.move_selection_to_popup_selection()

    def insert_from_popup(self):
        """Launch an insert new record dialogue from popup."""
        self.launch_insert_new_record()

    def show_from_popup(self):
        """Launch a delete record dialogue."""
        self.launch_show_record(self.pointer_popup_selection)
        self.move_selection_to_popup_selection()

    def launch_delete_record(self, key, modal=True):
        """Create delete dialogue.

        By default use the datagrid new_row() method for insert and clones of
        the displayed row for edit.  If the row instance does not implement
        the full behaviour needed to generate the database transaction the
        launch_... methods, and probably the create_edit_dialog method, will
        need to be extended in the DataGrid subclass.

        """
        self.create_delete_dialog(
            self.objects[key], self.objects[key].clone, modal
        )

    def launch_edit_record(self, key, modal=True):
        """Create edit dialogue.

        By default use clones of the displayed row for edit.  If the row
        instance does not implement the full behaviour needed to generate the
        database transaction the launch_... methods, and probably the
        create_edit_dialog method, will need to be extended in the DataGrid
        subclass.

        """
        self.create_edit_dialog(
            self.objects[key],
            self.objects[key].clone,
            self.objects[key].clone,
            False,
            modal,
        )

    def launch_edit_show_record(self, key, modal=True):
        """Create edit dialogue including reference copy of original.

        By default use clones of the displayed row for edit.  If the row
        instance does not implement the full behaviour needed to generate the
        database transaction the launch_... methods, and probably the
        create_edit_dialog method, will need to be extended in the DataGrid
        subclass.

        """
        self.create_edit_dialog(
            self.objects[key],
            self.objects[key].clone,
            self.objects[key].clone,
            True,
            modal,
        )

    def launch_insert_new_record(self, modal=True):
        """Create insert dialogue.

        By default use the datagrid new_row() method for insert.  If the row
        instance does not implement the full behaviour needed to generate the
        database transaction the launch_... methods, and probably the
        create_edit_dialog method, will need to be extended in the DataGrid
        subclass.

        """
        newobject = self.datasource.new_row
        instance = newobject()
        newobject.empty()
        self.create_edit_dialog(
            instance, newobject, None, False, modal, title="New Record"
        )

    def launch_show_record(self, key, modal=True):
        """Create show dialogue.

        By default use the datagrid new_row() method for insert and clones of
        the displayed row for edit.  If the row instance does not implement
        the full behaviour needed to generate the database transaction the
        launch_... methods, and probably the create_edit_dialog method, will
        need to be extended in the DataGrid subclass.

        """
        self.create_show_dialog(
            self.objects[key], self.objects[key].clone, modal
        )
