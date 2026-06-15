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

"""Comprehensive tests for shift preview calculation logic."""

import aeidon


class TestShiftPreviewCalculation(aeidon.TestCase):

    """Tests for get_shift_preview with controlled subtitle data."""

    def setup_method(self, method):
        self.project = self.new_project()
        self.calc = self.project.calc
        # Set up known, controlled positions for deterministic testing
        self.project.subtitles[0].start = "00:01:00.000"
        self.project.subtitles[0].end   = "00:01:03.000"
        self.project.subtitles[1].start = "00:02:00.000"
        self.project.subtitles[1].end   = "00:02:04.000"
        n = len(self.project.subtitles) - 1
        self.project.subtitles[n].start = "00:45:00.000"
        self.project.subtitles[n].end   = "00:45:05.000"

    # --- Basic positive shift (time-mode) ---

    def test_positive_seconds_shift(self):
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(indices, 2.0)
        assert preview["first"]["start"]     == "00:01:00.000"
        assert preview["first"]["new_start"] == "00:01:02.000"
        assert preview["first"]["end"]       == "00:01:03.000"
        assert preview["first"]["new_end"]   == "00:01:05.000"
        n = len(self.project.subtitles) - 1
        assert preview["last"]["start"]     == "00:45:00.000"
        assert preview["last"]["new_start"] == "00:45:02.000"
        assert preview["last"]["end"]       == "00:45:05.000"
        assert preview["last"]["new_end"]   == "00:45:07.000"

    # --- Negative shift (subtitles appear earlier) ---

    def test_negative_seconds_shift(self):
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(indices, -5.0)
        assert preview["first"]["new_start"] == "00:00:55.000"
        assert preview["first"]["new_end"]   == "00:00:58.000"
        assert preview["last"]["new_start"]  == "00:44:55.000"
        assert preview["last"]["new_end"]    == "00:45:00.000"

    # --- Zero shift ---

    def test_zero_shift(self):
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(indices, 0.0)
        assert preview["first"]["start"]     == preview["first"]["new_start"]
        assert preview["first"]["end"]       == preview["first"]["new_end"]
        assert preview["last"]["start"]      == preview["last"]["new_start"]
        assert preview["last"]["end"]        == preview["last"]["new_end"]

    # --- Frame-based shift ---

    def test_frame_shift(self):
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(
            indices, aeidon.as_frame(50))
        # Preview returns time strings; verify they are shifted
        first_orig_secs = self.calc.time_to_seconds(preview["first"]["start"])
        first_new_secs = self.calc.time_to_seconds(preview["first"]["new_start"])
        frame_secs = self.calc.frame_to_seconds(50)
        assert abs(first_new_secs - first_orig_secs - frame_secs) < 0.01

    def test_negative_frame_shift(self):
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(
            indices, aeidon.as_frame(-24))
        first_orig_secs = self.calc.time_to_seconds(preview["first"]["start"])
        first_new_secs = self.calc.time_to_seconds(preview["first"]["new_start"])
        frame_secs = self.calc.frame_to_seconds(-24)
        assert abs(first_new_secs - first_orig_secs - frame_secs) < 0.01

    # --- Subset of indices ---

    def test_subset_indices(self):
        preview = self.project.get_shift_preview([1, 2], 3.0)
        assert preview["first"]["index"] == 1
        assert preview["last"]["index"] == 2
        # First in subset should be subtitle index 1
        assert preview["first"]["start"] == "00:02:00.000"
        assert preview["first"]["new_start"] == "00:02:03.000"

    def test_single_index(self):
        preview = self.project.get_shift_preview([0], 1.5)
        assert preview["first"]["index"] == 0
        assert preview["last"]["index"] == 0
        assert preview["first"]["start"] == preview["last"]["start"]
        assert preview["first"]["new_start"] == preview["last"]["new_start"]
        assert preview["first"]["new_start"] == "00:01:01.500"

    # --- Empty / None indices ---

    def test_empty_indices(self):
        preview = self.project.get_shift_preview([], 1.0)
        assert preview is None

    def test_none_indices_means_all(self):
        preview_all = self.project.get_shift_preview(None, 2.0)
        indices = self.project.get_all_indices()
        preview_explicit = self.project.get_shift_preview(indices, 2.0)
        assert preview_all["first"]["new_start"] == preview_explicit["first"]["new_start"]
        assert preview_all["last"]["new_start"] == preview_explicit["last"]["new_start"]

    # --- Non-destructive: preview does not modify data ---

    def test_non_destructive(self):
        orig = [(s.start_time, s.end_time) for s in self.project.subtitles]
        indices = self.project.get_all_indices()
        self.project.get_shift_preview(indices, 100.0)
        self.project.get_shift_preview(indices, -100.0)
        for i, subtitle in enumerate(self.project.subtitles):
            assert subtitle.start_time == orig[i][0]
            assert subtitle.end_time == orig[i][1]

    # --- Consistency: preview matches actual shift result ---

    def test_preview_matches_actual_shift__seconds(self):
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(indices, 3.5)
        self.project.shift_positions(indices, 3.5)
        first = self.project.subtitles[indices[0]]
        last = self.project.subtitles[indices[-1]]
        assert first.start_time == preview["first"]["new_start"]
        assert first.end_time == preview["first"]["new_end"]
        assert last.start_time == preview["last"]["new_start"]
        assert last.end_time == preview["last"]["new_end"]

    def test_preview_matches_actual_shift__frames(self):
        indices = self.project.get_all_indices()
        value = aeidon.as_frame(100)
        preview = self.project.get_shift_preview(indices, value)
        self.project.shift_positions(indices, value)
        first = self.project.subtitles[indices[0]]
        last = self.project.subtitles[indices[-1]]
        assert first.start_time == preview["first"]["new_start"]
        assert last.start_time == preview["last"]["new_start"]

    # --- Shift resulting in negative time ---

    def test_shift_to_negative_time(self):
        self.project.subtitles[0].start = "00:00:02.000"
        self.project.subtitles[0].end   = "00:00:04.000"
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(indices, -5.0)
        # Result should be a negative time string
        new_start = preview["first"]["new_start"]
        assert new_start.startswith("-")

    # --- Large shift value ---

    def test_large_positive_shift(self):
        indices = self.project.get_all_indices()
        preview = self.project.get_shift_preview(indices, 3600.0)
        # First subtitle: 00:01:00 + 3600s = 01:01:00
        assert preview["first"]["new_start"] == "01:01:00.000"

    # --- Fractional seconds precision ---

    def test_fractional_precision(self):
        indices = [0]
        preview = self.project.get_shift_preview(indices, 0.123)
        assert preview["first"]["new_start"] == "00:01:00.123"

    def test_fractional_negative_precision(self):
        indices = [0]
        preview = self.project.get_shift_preview(indices, -0.500)
        assert preview["first"]["new_start"] == "00:00:59.500"


class TestCalculatorAddForPreview(aeidon.TestCase):

    """Direct tests on Calculator.add to verify the arithmetic used by preview."""

    def setup_method(self, method):
        self.calc = aeidon.Calculator(aeidon.framerates.FPS_23_976)

    def test_add_time_positive(self):
        result = self.calc.add("00:01:00.000", 2.0)
        assert result == "00:01:02.000"

    def test_add_time_negative(self):
        result = self.calc.add("00:01:00.000", -2.0)
        assert result == "00:00:58.000"

    def test_add_time_zero(self):
        result = self.calc.add("00:05:30.000", 0.0)
        assert result == "00:05:30.000"

    def test_add_time_cross_minute_boundary(self):
        result = self.calc.add("00:00:59.500", 1.0)
        assert result == "00:01:00.500"

    def test_add_time_cross_hour_boundary(self):
        result = self.calc.add("00:59:59.000", 2.0)
        assert result == "01:00:01.000"

    def test_add_time_to_negative(self):
        result = self.calc.add("00:00:01.000", -3.0)
        assert result.startswith("-")

    def test_add_seconds_positive(self):
        result = self.calc.add(60.0, 2.5)
        assert result == 62.5

    def test_add_seconds_negative(self):
        result = self.calc.add(60.0, -10.0)
        assert result == 50.0

    def test_add_frames_positive(self):
        result = self.calc.add(100, 50)
        assert result == 150

    def test_add_frames_negative(self):
        result = self.calc.add(100, -30)
        assert result == 70

    def test_add_time_with_frame_value(self):
        # Adding frame value to a time string — calc converts frame to seconds
        result = self.calc.add("00:01:00.000", aeidon.as_frame(24))
        result_secs = self.calc.time_to_seconds(result)
        expected_secs = 60.0 + self.calc.frame_to_seconds(24)
        assert abs(result_secs - expected_secs) < 0.01
