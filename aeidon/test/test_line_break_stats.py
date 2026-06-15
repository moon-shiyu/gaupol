# -*- coding: utf-8 -*-

# Standalone validation for line-break stats enhancement.
# Run with: python -m pytest aeidon/test/test_line_break_stats.py -v
# Or: python aeidon/test/test_line_break_stats.py

"""
Validation tests for the line-break length statistics feature.

These tests exercise the pure aeidon logic (no GTK dependency) to
verify that calc_text_stats and the stats formatting helper work
correctly across a range of subtitle scenarios.
"""

import aeidon
import re


class TestCalcTextStats:
    """Tests for Liner.calc_text_stats."""

    def setup_method(self, method):
        self.liner = aeidon.Liner(re.compile(r"<.+?>"))
        self.liner.set_penalties((
            dict(pattern=r"( )- ",
                 flags=re.DOTALL | re.MULTILINE,
                 group=1,
                 value=-1000),
            dict(pattern=r"[,.;:!?]( )",
                 flags=re.DOTALL | re.MULTILINE,
                 group=1,
                 value=-100),
            dict(pattern=r"\b(by|the|into|a)( )",
                 flags=re.DOTALL | re.MULTILINE,
                 group=2,
                 value=1000)))

    # -- Basic cases ---------------------------------------------------

    def test_empty_text(self):
        stats = self.liner.calc_text_stats("")
        assert stats["max_line_length"] == 0
        assert stats["line_count"] == 0

    def test_single_line(self):
        stats = self.liner.calc_text_stats("Hello, world!")
        assert stats["max_line_length"] == 13
        assert stats["line_count"] == 1

    def test_two_lines(self):
        stats = self.liner.calc_text_stats("Line one.\nLine two.")
        assert stats["max_line_length"] == 9  # "Line two." is longer
        assert stats["line_count"] == 2

    def test_three_lines(self):
        text = "Short.\nA much longer line here.\nMid."
        stats = self.liner.calc_text_stats(text)
        assert stats["max_line_length"] == 26
        assert stats["line_count"] == 3

    # -- Custom length_func -------------------------------------------

    def test_custom_length_func_double(self):
        self.liner.length_func = lambda x: len(x) * 2
        stats = self.liner.calc_text_stats("Hi\nHello!")
        # "Hi" -> 4, "Hello!" -> 12
        assert stats["max_line_length"] == 12
        assert stats["line_count"] == 2

    def test_custom_length_func_constant(self):
        self.liner.length_func = lambda x: 42
        stats = self.liner.calc_text_stats("a\nb\nc")
        assert stats["max_line_length"] == 42
        assert stats["line_count"] == 3

    # -- Markup tags (Liner strips them via Parser) --------------------

    def test_text_with_markup_tags(self):
        # calc_text_stats operates on raw text (no tag stripping),
        # so tags are counted in the length.
        text = "<i>Hello</i>\nWorld"
        stats = self.liner.calc_text_stats(text)
        assert stats["max_line_length"] == len("<i>Hello</i>")
        assert stats["line_count"] == 2

    # -- Integration: before/after break_lines -------------------------

    def test_stats_improve_after_break(self):
        """After breaking, max line length should not increase."""
        text = ("Close by the king's castle "
                "lay a great dark forest.")
        orig_stats = self.liner.calc_text_stats(text)
        assert orig_stats["line_count"] == 1

        self.liner.set_text(text)
        new_text = self.liner.break_lines()
        new_stats = self.liner.calc_text_stats(new_text)

        assert new_stats["max_line_length"] <= orig_stats["max_line_length"]
        assert new_stats["line_count"] >= orig_stats["line_count"]

    def test_stats_multi_break(self):
        """Long text broken into 3+ lines has correct stats."""
        text = ("The king's child went out "
                "into the forest and sat down "
                "by the side of the cool fountain.")
        orig_stats = self.liner.calc_text_stats(text)
        assert orig_stats["line_count"] == 1

        self.liner.set_text(text)
        new_text = self.liner.break_lines()
        new_stats = self.liner.calc_text_stats(new_text)

        assert new_stats["line_count"] == 3
        assert new_stats["max_line_length"] < orig_stats["max_line_length"]

    def test_single_word_no_change(self):
        """Single word text cannot be broken; stats remain the same."""
        text = "Hello."
        orig_stats = self.liner.calc_text_stats(text)
        self.liner.set_text(text)
        new_text = self.liner.break_lines()
        new_stats = self.liner.calc_text_stats(new_text)
        assert orig_stats == new_stats


class TestFormatLineBreakStats:
    """Tests for the stats formatting helper (pure logic, no GTK)."""

    @staticmethod
    def _format_line_break_stats(orig, new, length_func=len):
        """Mirror of TextAssistant._format_line_break_stats."""
        orig_lines = orig.split("\n")
        new_lines = new.split("\n")
        orig_max = max(length_func(l) for l in orig_lines)
        new_max = max(length_func(l) for l in new_lines)
        orig_cnt = len(orig_lines)
        new_cnt = len(new_lines)
        if orig_max == new_max and orig_cnt == new_cnt:
            return ""
        return "{}\u2192{} chr\n{}\u2192{} lines".format(
            orig_max, new_max, orig_cnt, new_cnt)

    def test_no_change_returns_empty(self):
        result = self._format_line_break_stats("Hello", "World")
        assert result == ""

    def test_length_change(self):
        orig = "This is a very long single line of subtitle text."
        new = "This is a very long\nsingle line of subtitle text."
        result = self._format_line_break_stats(orig, new)
        assert "49" in result  # original max
        assert "29" in result  # new max (longer of the two lines)
        assert "1\u21922 lines" in result

    def test_line_count_same_length_different(self):
        orig = "Short\nLonger line"
        new = "Medium\nMed"
        result = self._format_line_break_stats(orig, new)
        # max changed from 11 to 6, count stayed at 2
        assert "11" in result
        assert "6" in result
        assert "2\u21922 lines" in result

    def test_same_max_different_count(self):
        orig = "Twelve chars"
        new = "Twelve chars\nHi"
        result = self._format_line_break_stats(orig, new)
        # max stayed at 12, count changed 1 -> 2
        assert "1\u21922 lines" in result


if __name__ == "__main__":
    import sys
    errors = 0
    for cls in (TestCalcTextStats, TestFormatLineBreakStats):
        inst = cls()
        inst.setup_method(None) if hasattr(inst, "setup_method") else None
        for name in sorted(dir(inst)):
            if not name.startswith("test_"):
                continue
            try:
                if hasattr(inst, "setup_method"):
                    inst.setup_method(None)
                getattr(inst, name)()
                print("  PASS  {}.{}".format(cls.__name__, name))
            except Exception as e:
                errors += 1
                print("  FAIL  {}.{}: {}".format(cls.__name__, name, e))
    sys.exit(1 if errors else 0)
