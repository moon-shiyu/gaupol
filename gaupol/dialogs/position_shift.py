# -*- coding: utf-8 -*-

# Copyright (C) 2005 Osmo Salomaa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Dialogs for shifting positions."""

import aeidon
import gaupol

from aeidon.i18n   import _
from gi.repository import Gtk

__all__ = ("FrameShiftDialog", "TimeShiftDialog")


class PositionShiftDialog(gaupol.BuilderDialog):

    """Base class for dialogs for shifting positions."""

    _widgets = [
        "all_radio",
        "amount_spin",
        "current_radio",
        "preview_button",
        "preview_box",
        "preview_first_label",
        "preview_last_label",
        "selected_radio",
        "to_end_radio",
        "unit_label",
    ]

    def __init__(self, parent, application):
        """Initialize a :class:`PositionShiftDialog` instance."""
        gaupol.BuilderDialog.__init__(self, "position-shift-dialog.ui")
        self.application = application
        self._init_dialog(parent)
        self._init_widgets()
        self._init_values()

    def _get_preview_row(self):
        """Return row to start preview from."""
        page = self.application.get_current_page()
        rows = page.view.get_selected_rows()
        return rows[0] if rows else 0

    def _get_target(self):
        """Return the selected target."""
        if self._selected_radio.get_active():
            return gaupol.targets.SELECTED
        if self._to_end_radio.get_active():
            return gaupol.targets.SELECTED_TO_END
        if self._current_radio.get_active():
            return gaupol.targets.CURRENT
        if self._all_radio.get_active():
            return gaupol.targets.ALL
        raise ValueError("Invalid target radio state")

    def _init_dialog(self, parent):
        """Initialize the dialog."""
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Shift"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)
        self.set_transient_for(parent)
        self.set_modal(True)

    def _init_values(self):
        """Intialize default values for widgets."""
        target = gaupol.conf.position_shift.target
        self._selected_radio.set_active(target == gaupol.targets.SELECTED)
        self._to_end_radio.set_active(target == gaupol.targets.SELECTED_TO_END)
        self._current_radio.set_active(target == gaupol.targets.CURRENT)
        self._all_radio.set_active(target == gaupol.targets.ALL)
        page = self.application.get_current_page()
        rows = page.view.get_selected_rows()
        if not rows and target in (
                gaupol.targets.SELECTED,
                gaupol.targets.SELECTED_TO_END):
            self._current_radio.set_active(True)
        self._selected_radio.set_sensitive(bool(rows))
        self._to_end_radio.set_sensitive(bool(rows))
        if (page.project.video_path is None or
            page.project.main_file is None):
            self._preview_button.set_sensitive(False)
        # Update time preview when target scope changes.
        for radio in (self._selected_radio, self._to_end_radio,
                      self._current_radio, self._all_radio):
            radio.connect("toggled", lambda *a: self._update_time_preview())
        self._amount_spin.emit("value-changed")

    def _init_widgets(self):
        """Initialize widgets."""
        raise NotImplementedError

    def _on_amount_spin_value_changed(self, spin_button):
        """Set response sensitivity and update preview."""
        has_value = (spin_button.get_value() != 0.0)
        self.set_response_sensitive(Gtk.ResponseType.OK, has_value)
        self._update_time_preview()

    def _on_preview_button_clicked(self, *args):
        """Preview shift changes with a video player."""
        page = self.application.get_current_page()
        target = self._get_target()
        rows = self.application.get_target_rows(target)
        self.application.preview_changes(page,
                                         self._get_preview_row(),
                                         aeidon.documents.MAIN,
                                         page.project.shift_positions,
                                         (rows, self._get_amount()))

    def _on_response(self, dialog, response):
        """Save target and shift positions."""
        gaupol.conf.position_shift.target = self._get_target()
        if response == Gtk.ResponseType.OK:
            self._shift_positions()

    def _shift_positions(self):
        """Shift positions in subtitles."""
        gaupol.util.set_cursor_busy(self)
        target = self._get_target()
        amount = self._get_amount()
        for page in self.application.get_target_pages(target):
            self.application.set_current_page(page)
            rows = self.application.get_target_rows(target)
            page.project.shift_positions(rows, amount)
        gaupol.util.set_cursor_normal(self)

    def _update_time_preview(self):
        """Update inline preview labels with first/last subtitle times."""
        page = self.application.get_current_page()
        project = page.project
        if not project.subtitles:
            self._preview_first_label.set_text("")
            self._preview_last_label.set_text("")
            return
        target = self._get_target()
        rows = self.application.get_target_rows(target)
        amount = self._get_amount()
        preview = project.preview_shift_positions(rows, amount)
        if preview is None:
            self._preview_first_label.set_text(_("No subtitles to shift"))
            self._preview_last_label.set_text("")
            return
        first = preview["first"]
        last = preview["last"]
        if first["index"] == last["index"]:
            # Only one subtitle affected -- show it on the first line.
            self._preview_first_label.set_markup(
                "<b>#{}:</b>  {} → {}  /  {} → {}".format(
                    first["index"] + 1,
                    first["start"], first["new_start"],
                    first["end"], first["new_end"]))
            self._preview_last_label.set_text("")
        else:
            self._preview_first_label.set_markup(
                "<b>{}:</b>  #{}: {} → {}  /  {} → {}".format(
                    _("First"), first["index"] + 1,
                    first["start"], first["new_start"],
                    first["end"], first["new_end"]))
            self._preview_last_label.set_markup(
                "<b>{}:</b>  #{}: {} → {}  /  {} → {}".format(
                    _("Last"), last["index"] + 1,
                    last["start"], last["new_start"],
                    last["end"], last["new_end"]))


class FrameShiftDialog(PositionShiftDialog):

    """Dialog for shifting frames."""

    def _get_amount(self):
        """Return the amount of frames to shift."""
        return aeidon.as_frame(self._amount_spin.get_value_as_int())

    def _init_widgets(self):
        """Initialize widgets."""
        self._amount_spin.set_numeric(True)
        self._amount_spin.set_digits(0)
        self._amount_spin.set_increments(1, 10)
        self._amount_spin.set_range(-9999999, 9999999)
        self._amount_spin.set_value(0)
        self._unit_label.set_text(_("frames"))


class TimeShiftDialog(PositionShiftDialog):

    """Dialog for shifting times."""

    def _get_amount(self):
        """Return the amount of seconds to shift."""
        return aeidon.as_seconds(self._amount_spin.get_value())

    def _init_widgets(self):
        """Initialize widgets."""
        self._amount_spin.set_numeric(True)
        self._amount_spin.set_digits(3)
        self._amount_spin.set_increments(0.1, 1)
        self._amount_spin.set_range(-99999, 99999)
        self._amount_spin.set_value(0.000)
        self._unit_label.set_text(_("seconds"))
