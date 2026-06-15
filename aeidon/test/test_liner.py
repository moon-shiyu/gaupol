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


class TestComputeLineStats(aeidon.TestCase):

    def test_single_line(self):
        stats = aeidon.liner.compute_line_stats("Hello world")
        assert stats["line_count"] == 1
        assert stats["max_length"] == 11
        assert stats["lengths"] == [11]

    def test_multi_line(self):
        stats = aeidon.liner.compute_line_stats("Hello\nworld")
        assert stats["line_count"] == 2
        assert stats["max_length"] == 5
        assert stats["lengths"] == [5, 5]

    def test_empty_text(self):
        stats = aeidon.liner.compute_line_stats("")
        assert stats["line_count"] == 1
        assert stats["max_length"] == 0
        assert stats["lengths"] == [0]

    def test_uneven_lines(self):
        stats = aeidon.liner.compute_line_stats("Hello world\nHi")
        assert stats["line_count"] == 2
        assert stats["max_length"] == 11
        assert stats["lengths"] == [11, 2]

    def test_custom_length_func(self):
        func = lambda t: len(t) * 2
        stats = aeidon.liner.compute_line_stats("abc\ndef", func)
        assert stats["max_length"] == 6
        assert stats["lengths"] == [6, 6]


class TestFormatLineBreakDiff(aeidon.TestCase):

    def test_within_limits(self):
        diff = aeidon.liner.format_line_break_diff(
            "Hello world, this is a long subtitle",
            "Hello world,\nthis is a long subtitle",
            length_func=len, max_length=40, max_lines=2)
        assert "1>" in diff
        assert "2" in diff
        assert "[OK]" in diff

    def test_exceeds_max_length(self):
        diff = aeidon.liner.format_line_break_diff(
            "Hello world, this is a very long subtitle text here",
            "Hello world, this is\na very long subtitle text here",
            length_func=len, max_length=20, max_lines=2)
        assert "[!]" in diff

    def test_exceeds_max_lines(self):
        diff = aeidon.liner.format_line_break_diff(
            "a b c d e f",
            "a b\nc d\ne f",
            length_func=len, max_length=40, max_lines=2)
        assert "[!]" in diff

    def test_no_limits(self):
        diff = aeidon.liner.format_line_break_diff(
            "Hello world",
            "Hello\nworld",
            length_func=len)
        assert "[OK]" in diff
        assert "L:" in diff
        assert "W:" in diff


class TestBreakLinesStatsIntegration(aeidon.TestCase):

    def setup_method(self, method):
        self.liner = aeidon.Liner(re.compile(r"<.+?>"))
        self.liner.set_penalties((
            dict(pattern=r"[,.;:!?]( )",
                 flags=re.DOTALL|re.MULTILINE,
                 group=1,
                 value=-100),))

    def test_stats_consistent_with_break(self):
        text = "Hello world, this is a test of the line breaking algorithm."
        self.liner.max_length = 30
        self.liner.set_text(text)
        result = self.liner.break_lines()
        before = aeidon.liner.compute_line_stats(text)
        after = aeidon.liner.compute_line_stats(result)
        assert after["max_length"] <= 30
        assert after["line_count"] >= before["line_count"]

    def test_diff_format_after_break(self):
        text = "Hello world, this is a test of the line breaking algorithm."
        self.liner.max_length = 30
        self.liner.set_text(text)
        result = self.liner.break_lines()
        diff = aeidon.liner.format_line_break_diff(
            text, result, length_func=len,
            max_length=30, max_lines=3)
        assert "[OK]" in diff

    def test_module_exports(self):
        assert hasattr(aeidon.liner, "compute_line_stats")
        assert hasattr(aeidon.liner, "format_line_break_diff")
