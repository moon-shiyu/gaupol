# -*- coding: utf-8 -*-

# Copyright (C) 2011 Osmo Salomaa
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
import re


class TestLiner(aeidon.TestCase):

    def setup_method(self, method):
        self.liner = aeidon.Liner(re.compile(r"<.+?>"))
        self.liner.set_penalties((
            dict(pattern=r"( )- ",
                 flags=re.DOTALL|re.MULTILINE,
                 group=1,
                 value=-1000),

            dict(pattern=r"[,.;:!?]( )",
                 flags=re.DOTALL|re.MULTILINE,
                 group=1,
                 value=-100),

            dict(pattern=r"\b(by|the|into|a)( )",
                 flags=re.DOTALL|re.MULTILINE,
                 group=2,
                 value=1000)))

    def test_break_lines__1(self):
        text = "Hello."
        self.liner.set_text(text)
        assert self.liner.break_lines() == "Hello."

    def test_break_lines__2(self):
        text = ("- Isn't he off on Saturdays? "
                "- Didn't he tell you?")

        self.liner.set_text(text)
        assert self.liner.break_lines() == (
            "- Isn't he off on Saturdays?\n"
            "- Didn't he tell you?")

    def test_break_lines__3(self):
        text = ("Close by the king's castle "
                "lay a great dark forest.")

        self.liner.set_text(text)
        assert self.liner.break_lines() == (
            "Close by the king's castle\n"
            "lay a great dark forest.")

    def test_break_lines__4(self):
        text = ("The king's child went out "
                "into the forest and sat down "
                "by the side of the cool fountain.")

        self.liner.set_text(text)
        assert self.liner.break_lines() == (
            "The king's child went out\n"
            "into the forest and sat down\n"
            "by the side of the cool fountain.")

    def test_break_lines__5(self):
        text = ("The king's child went out "
                "into the forest and sat down by the side "
                "of the cool fountain; and when "
                "she was bored she took a golden ball, "
                "and threw it up high and caught it; "
                "and this ball was her favorite plaything.")

        self.liner.set_text(text)
        assert self.liner.break_lines() == (
            "The king's child went out\n"
            "into the forest and sat down by the side\n"
            "of the cool fountain; and when she\n"
            "was bored she took a golden ball,\n"
            "and threw it up high and caught it; and\n"
            "this ball was her favorite plaything.")

    def test_calc_text_stats__single_line(self):
        stats = self.liner.calc_text_stats("Hello, world!")
        assert stats["max_line_length"] == 13
        assert stats["line_count"] == 1

    def test_calc_text_stats__multiline(self):
        text = "Short line.\nA somewhat longer line.\nTiny."
        stats = self.liner.calc_text_stats(text)
        assert stats["max_line_length"] == 27
        assert stats["line_count"] == 3

    def test_calc_text_stats__empty(self):
        stats = self.liner.calc_text_stats("")
        assert stats["max_line_length"] == 0
        assert stats["line_count"] == 0

    def test_calc_text_stats__custom_length_func(self):
        self.liner.length_func = lambda x: len(x) * 2
        stats = self.liner.calc_text_stats("Hello\nWorld!")
        assert stats["max_line_length"] == 12  # len("Hello") * 2 = 10, len("World!") * 2 = 12
        assert stats["line_count"] == 2

    def test_calc_text_stats__before_after_break(self):
        text = ("Close by the king's castle "
                "lay a great dark forest.")
        orig_stats = self.liner.calc_text_stats(text)
        assert orig_stats["max_line_length"] == len(text)
        assert orig_stats["line_count"] == 1
        self.liner.set_text(text)
        new_text = self.liner.break_lines()
        new_stats = self.liner.calc_text_stats(new_text)
        assert new_stats["max_line_length"] <= orig_stats["max_line_length"]
        assert new_stats["line_count"] == 2
