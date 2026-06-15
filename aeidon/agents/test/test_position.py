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

import aeidon


class TestPositionAgent(aeidon.TestCase):

    def setup_method(self, method):
        self.project = self.new_project()

    def test_adjust_durations__gap(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:01.000"
        subtitles[0].end   = "00:00:02.000"
        subtitles[1].start = "00:00:02.000"
        subtitles[1].end   = "00:00:03.000"
        subtitles[2].start = "00:00:04.000"
        self.project.adjust_durations(None,
                                      gap=0.3)

        assert subtitles[0].start == "00:00:01.000"
        assert subtitles[0].end   == "00:00:01.700"
        assert subtitles[1].start == "00:00:02.000"
        assert subtitles[1].end   == "00:00:03.000"
        assert subtitles[2].start == "00:00:04.000"

    def test_adjust_durations__lengthen(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:01.000"
        subtitles[0].end   = "00:00:01.100"
        subtitles[1].start = "00:00:02.000"
        subtitles[1].end   = "00:00:02.100"
        subtitles[0].main_text = "1234567890"
        subtitles[1].main_text = "12345678901234567890"
        self.project.adjust_durations(None,
                                      speed=20,
                                      lengthen=True)

        assert subtitles[0].start == "00:00:01.000"
        assert subtitles[0].end   == "00:00:01.500"
        assert subtitles[1].start == "00:00:02.000"
        assert subtitles[1].end   == "00:00:03.000"

    def test_adjust_durations__maximum(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:01.000"
        subtitles[0].end   = "00:00:01.100"
        subtitles[1].start = "00:00:02.000"
        subtitles[1].end   = "00:00:02.100"
        self.project.adjust_durations(None,
                                      speed=10,
                                      lengthen=True,
                                      maximum=0.5)

        assert subtitles[0].start == "00:00:01.000"
        assert subtitles[0].end   == "00:00:01.500"
        assert subtitles[1].start == "00:00:02.000"
        assert subtitles[1].end   == "00:00:02.500"

    def test_adjust_durations__minimum(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:01.000"
        subtitles[0].end   = "00:00:01.900"
        subtitles[1].start = "00:00:02.000"
        subtitles[1].end   = "00:00:02.900"
        self.project.adjust_durations(None,
                                      speed=1000,
                                      shorten=True,
                                      minimum=0.5)

        assert subtitles[0].start == "00:00:01.000"
        assert subtitles[0].end   == "00:00:01.500"
        assert subtitles[1].start == "00:00:02.000"
        assert subtitles[1].end   == "00:00:02.500"

    def test_adjust_durations__shorten(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:01.000"
        subtitles[0].end   = "00:00:01.900"
        subtitles[1].start = "00:00:02.000"
        subtitles[1].end   = "00:00:02.900"
        subtitles[0].main_text = "1234567890"
        subtitles[1].main_text = "12345678901234567890"
        self.project.adjust_durations(None,
                                      speed=100,
                                      shorten=True)

        assert subtitles[0].start == "00:00:01.000"
        assert subtitles[0].end   == "00:00:01.100"
        assert subtitles[1].start == "00:00:02.000"
        assert subtitles[1].end   == "00:00:02.200"

    def test_convert_framerate(self):
        self.project.open_main(self.new_microdvd_file(), "ascii")
        self.project.subtitles[0].start = 100
        self.project.subtitles[1].start = 200
        ifps = aeidon.framerates.FPS_23_976
        ofps = aeidon.framerates.FPS_25_000
        self.project.convert_framerate(None, ifps, ofps)
        assert self.project.framerate == ofps
        for subtitle in self.project.subtitles:
            assert subtitle.framerate == ofps
        assert self.project.subtitles[0].start == 104
        assert self.project.subtitles[1].start == 209

    def test_set_framerate(self):
        framerate = aeidon.framerates.FPS_25_000
        self.project.set_framerate(framerate)
        assert self.project.framerate == framerate
        for subtitle in self.project.subtitles:
            assert subtitle.framerate == framerate

    @aeidon.deco.reversion_test
    def test_shift_positions(self):
        orig_subtitles = [x.copy() for x in self.project.subtitles]
        indices = self.project.get_all_indices()
        self.project.shift_positions(indices, -10)
        for i, subtitle in enumerate(self.project.subtitles):
            start = orig_subtitles[i].start_frame - 10
            end = orig_subtitles[i].end_frame - 10
            assert subtitle.start_frame == start
            assert subtitle.end_frame == end

    @aeidon.deco.reversion_test
    def test_transform_positions(self):
        a, b = "00:00:01.000", "00:00:45.000"
        self.project.transform_positions(None, (2, a), (6, b))
        assert self.project.subtitles[2].start_time == a
        for subtitle in self.project.subtitles[3:6]:
            assert a < subtitle.start_time < b
        assert self.project.subtitles[6].start_time == b

    def test_preview_shift_positions__time_positive(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:01.000"
        subtitles[0].end   = "00:00:02.000"
        subtitles[-1].start = "00:01:00.000"
        subtitles[-1].end   = "00:01:05.000"
        indices = self.project.get_all_indices()
        preview = self.project.preview_shift_positions(
            indices, aeidon.as_seconds(3.5))
        assert preview is not None
        assert preview["first"]["index"] == indices[0]
        assert preview["first"]["start"] == "00:00:01.000"
        assert preview["first"]["new_start"] == "00:00:04.500"
        assert preview["first"]["end"] == "00:00:02.000"
        assert preview["first"]["new_end"] == "00:00:05.500"
        assert preview["last"]["index"] == indices[-1]
        assert preview["last"]["start"] == "00:01:00.000"
        assert preview["last"]["new_start"] == "00:01:03.500"
        assert preview["last"]["end"] == "00:01:05.000"
        assert preview["last"]["new_end"] == "00:01:08.500"

    def test_preview_shift_positions__time_negative(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:10.000"
        subtitles[0].end   = "00:00:12.000"
        subtitles[-1].start = "00:01:00.000"
        subtitles[-1].end   = "00:01:05.000"
        indices = self.project.get_all_indices()
        preview = self.project.preview_shift_positions(
            indices, aeidon.as_seconds(-5.0))
        assert preview["first"]["new_start"] == "00:00:05.000"
        assert preview["first"]["new_end"] == "00:00:07.000"
        assert preview["last"]["new_start"] == "00:00:55.000"
        assert preview["last"]["new_end"] == "00:01:00.000"

    def test_preview_shift_positions__frame(self):
        self.project.open_main(self.new_microdvd_file(), "ascii")
        subtitles = self.project.subtitles
        subtitles[0].start = 100
        subtitles[0].end   = 200
        subtitles[-1].start = 1000
        subtitles[-1].end   = 1200
        indices = self.project.get_all_indices()
        orig_first_start = subtitles[0].start_time
        orig_last_start = subtitles[-1].start_time
        preview = self.project.preview_shift_positions(
            indices, aeidon.as_frame(50))
        # Preview always returns time strings.
        assert preview["first"]["start"] == orig_first_start
        assert preview["first"]["new_start"] != orig_first_start
        assert preview["last"]["start"] == orig_last_start
        assert preview["last"]["new_start"] != orig_last_start
        # Positive shift => new times should be later.
        calc = self.project.calc
        assert calc.is_later(preview["first"]["new_start"],
                             preview["first"]["start"])
        assert calc.is_later(preview["last"]["new_start"],
                             preview["last"]["start"])

    def test_preview_shift_positions__partial_indices(self):
        subtitles = self.project.subtitles
        subtitles[2].start = "00:00:10.000"
        subtitles[2].end   = "00:00:12.000"
        subtitles[5].start = "00:00:30.000"
        subtitles[5].end   = "00:00:35.000"
        indices = [2, 3, 4, 5]
        preview = self.project.preview_shift_positions(
            indices, aeidon.as_seconds(2.0))
        assert preview["first"]["index"] == 2
        assert preview["first"]["new_start"] == "00:00:12.000"
        assert preview["last"]["index"] == 5
        assert preview["last"]["new_start"] == "00:00:32.000"

    def test_preview_shift_positions__single_subtitle(self):
        subtitles = self.project.subtitles
        subtitles[3].start = "00:00:20.000"
        subtitles[3].end   = "00:00:25.000"
        indices = [3]
        preview = self.project.preview_shift_positions(
            indices, aeidon.as_seconds(1.0))
        assert preview["first"]["index"] == preview["last"]["index"] == 3
        assert preview["first"]["new_start"] == "00:00:21.000"
        assert preview["last"]["new_start"] == "00:00:21.000"

    def test_preview_shift_positions__does_not_modify(self):
        subtitles = self.project.subtitles
        subtitles[0].start = "00:00:01.000"
        subtitles[0].end   = "00:00:02.000"
        orig_start = subtitles[0].start
        orig_end = subtitles[0].end
        indices = self.project.get_all_indices()
        self.project.preview_shift_positions(
            indices, aeidon.as_seconds(10.0))
        assert subtitles[0].start == orig_start
        assert subtitles[0].end == orig_end

    def test_preview_shift_positions__empty_indices(self):
        preview = self.project.preview_shift_positions(
            [], aeidon.as_seconds(1.0))
        assert preview is None
