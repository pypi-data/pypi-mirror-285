# eventspec.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Map Datagrid event names to tk(inter) event detail values."""


class EventSpec:
    """Event detail values for DataGrid keyboard and pointer actions."""

    give_focus_to_datagridbase = "<Button-1>"
    select_row_in_datagridbase = "<Button-3>"
    insert_row_in_datagrid = "<Button-3>"

    grid_or_row_popup_at_top_left = (
        "<Shift-KeyPress-F10>",
        "Popup Menu at Top Left",
        "Shift F10",
    )
    grid_or_row_popup_at_pointer = (
        "<Ctrl-KeyPress-F10>",
        "Popup Menu at Pointer",
        "Ctrl F10",
    )
    up_one_page = "<KeyPress-Prior>", "Page Up", "Page Up"
    down_one_page = "<KeyPress-Next>", "Page Down", "Page Down"
    down_all = "<Shift-KeyPress-End>", "End", "Shift End"
    up_all = "<Shift-KeyPress-Home>", "Start", "Shift Home"
    up_one_line = "<KeyPress-Up>", "Line Up", "Up"
    up_one_line_in_selection = (
        "<Control-KeyPress-Up>",
        "Cycle Up Selection",
        "Ctrl Up",
    )
    down_one_line = "<KeyPress-Down>", "Line Down", "Down"
    down_one_line_in_selection = (
        "<Control-KeyPress-Down>",
        "Cycle Down Selection",
        "Ctrl Down",
    )
    move_visible_select_up_one_line = (
        "<KeyPress-Left>",
        "Select Line Up",
        "Left",
    )
    up_one_bookmarked_line_move_select = (
        "<Alt-KeyPress-Left>",
        "Cycle Up Bookmarks",
        "Alt Left",
    )
    up_one_line_move_select = (
        "<Control-KeyPress-Left>",
        "Move Select Line Up",
        "Ctrl Left",
    )
    move_select_up_one_line_after_align = (
        "<Shift-KeyPress-Left>",
        "Align Select Line Up",
        "Shift Left",
    )
    move_visible_select_down_one_line = (
        "<KeyPress-Right>",
        "Select Line Down",
        "Right",
    )
    down_one_bookmarked_line_move_select = (
        "<Alt-KeyPress-Right>",
        "Cycle Down Bookmarks",
        "Alt Right",
    )
    down_one_line_move_select = (
        "<Control-KeyPress-Right>",
        "Move Select Line Down",
        "Ctrl Right",
    )
    move_select_down_one_line_after_align = (
        "<Shift-KeyPress-Right>",
        "Align Select Line Down",
        "Shift Right",
    )
    bookmark_selected_line = (
        "<Alt-KeyPress-Insert>",
        "Bookmark Selection",
        "Alt Insert",
    )
    remove_selected_line_from_bookmark = (
        "<Alt-KeyPress-Delete>",
        "Remove Bookmark",
        "Alt Delete",
    )
    remove_selected_line_from_selection = (
        "<Control-KeyPress-Delete>",
        "Remove Select",
        "Ctrl Delete",
    )

    launch_show_dialog = "<KeyPress-Return>", "Show", "Enter"
    launch_edit_dialog = "<Shift-KeyPress-Insert>", "Edit", "Shift Insert"
    launch_delete_dialog = "<KeyPress-Delete>", "Delete", "Delete"
    launch_insert_dialog = "<KeyPress-Insert>", "Insert", "Insert"
    launch_edit_and_show_dialog = (
        "<Control-KeyPress-Insert>",
        "Edit and show",
        "Ctrl Insert",
    )
