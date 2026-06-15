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


class TestReplaceAllStats(aeidon.TestCase):

    def test___init___defaults(self):
        stats = aeidon.ReplaceAllStats()
        assert stats.matches == 0
        assert stats.replacements == 0
        assert stats.rows == set()

    def test___init___values(self):
        stats = aeidon.ReplaceAllStats(
            matches=5, replacements=3, rows={0, 2, 4})
        assert stats.matches == 5
        assert stats.replacements == 3
        assert stats.rows == {0, 2, 4}

    def test___int__(self):
        stats = aeidon.ReplaceAllStats(matches=5, replacements=3)
        assert int(stats) == 3

    def test___bool___true(self):
        stats = aeidon.ReplaceAllStats(replacements=1)
        assert bool(stats) is True

    def test___bool___false(self):
        stats = aeidon.ReplaceAllStats(replacements=0)
        assert bool(stats) is False

    def test___eq___int(self):
        stats = aeidon.ReplaceAllStats(replacements=7)
        assert stats == 7
        assert not (stats == 6)

    def test___eq___stats(self):
        a = aeidon.ReplaceAllStats(matches=3, replacements=2, rows={1})
        b = aeidon.ReplaceAllStats(matches=3, replacements=2, rows={1})
        assert a == b

    def test___eq___stats_differ(self):
        a = aeidon.ReplaceAllStats(matches=3, replacements=2, rows={1})
        b = aeidon.ReplaceAllStats(matches=3, replacements=1, rows={1})
        assert not (a == b)

    def test___iadd__(self):
        a = aeidon.ReplaceAllStats(matches=2, replacements=1, rows={0})
        b = aeidon.ReplaceAllStats(matches=3, replacements=2, rows={1, 2})
        a += b
        assert a.matches == 5
        assert a.replacements == 3
        assert a.rows == {0, 1, 2}

    def test___repr__(self):
        stats = aeidon.ReplaceAllStats(
            matches=4, replacements=3, rows={0, 5})
        text = repr(stats)
        assert "matches=4" in text
        assert "replacements=3" in text
        assert "rows=2" in text

    def test_row_range__empty(self):
        stats = aeidon.ReplaceAllStats()
        assert stats.row_range is None

    def test_row_range__single(self):
        stats = aeidon.ReplaceAllStats(rows={3})
        assert stats.row_range == (3, 3)

    def test_row_range__multiple(self):
        stats = aeidon.ReplaceAllStats(rows={1, 5, 10})
        assert stats.row_range == (1, 10)


class TestFinder(aeidon.TestCase):

    ####### 00000000001111111111222222 222233333333334444444444555555
    ####### 01234567890123456789012345 678901234567890123456789012345
    text = "One only risks it, because\none's survival depends on it."

    def find_indices(self, next):
        advance = self.finder.next if next else self.finder.previous
        pos = []
        while True:
            try:
                advance()
            except StopIteration:
                break
            pos.append(self.finder.pos)
        return pos

    def setup_method(self, method):
        self.finder = aeidon.Finder()
        self.finder.set_text(self.text)

    def test_next__regex(self):
        self.finder.set_regex(r"^")
        pos = self.find_indices(next=True)
        assert pos == [0, 27]

    def test_next__regex_ignore_case(self):
        self.finder.ignore_case = True
        self.finder.set_regex(r"O")
        pos = self.find_indices(next=True)
        assert pos == [1, 5, 28, 51]

    def test_next__string(self):
        self.finder.pattern = "it"
        pos = self.find_indices(next=True)
        assert pos == [17, 55]

    def test_next__string_ignore_case(self):
        self.finder.ignore_case = True
        self.finder.pattern = "o"
        pos = self.find_indices(next=True)
        assert pos == [1, 5, 28, 51]

    def test_previous__regex(self):
        self.finder.set_regex(r"\s")
        pos = self.find_indices(next=False)
        assert pos == [52, 49, 41, 32, 26, 18, 14, 8, 3]

    def test_previous__regex_ignore_case(self):
        self.finder.ignore_case = True
        self.finder.set_regex(r"O")
        pos = self.find_indices(next=False)
        assert pos == [50, 27, 4, 0]

    def test_previous__string(self):
        self.finder.pattern = "it"
        pos = self.find_indices(next=False)
        assert pos == [53, 15]

    def test_previous__string_ignore_case(self):
        self.finder.ignore_case = True
        self.finder.pattern = "o"
        pos = self.find_indices(next=False)
        assert pos == [50, 27, 4, 0]

    def test_replace__equal_length_next(self):
        self.finder.pattern = "ne"
        self.finder.replacement = "--"
        self.finder.next()
        self.finder.replace()
        assert self.finder.text == (
            "O-- only risks it, because\n"
            "one's survival depends on it.")
        assert self.finder.pos == 3
        self.finder.next()
        self.finder.replace()
        assert self.finder.text == (
            "O-- only risks it, because\n"
            "o--'s survival depends on it.")
        assert self.finder.pos == 30
        self.assert_raises(StopIteration, self.finder.next)

    def test_replace__equal_length_previous(self):
        self.finder.pattern = "ne"
        self.finder.replacement = "--"
        self.finder.previous()
        self.finder.replace(next=False)
        assert self.finder.text == (
            "One only risks it, because\n"
            "o--'s survival depends on it.")
        assert self.finder.pos == 28
        self.finder.previous()
        self.finder.replace(next=False)
        assert self.finder.text == (
            "O-- only risks it, because\n"
            "o--'s survival depends on it.")
        assert self.finder.pos == 1
        self.assert_raises(StopIteration, self.finder.previous)

    def test_replace__lengthen_next(self):
        self.finder.set_regex(r"$")
        self.finder.replacement = "--"
        self.finder.next()
        self.finder.replace()
        assert self.finder.text == (
            "One only risks it, because--\n"
            "one's survival depends on it.")
        assert self.finder.pos == 28
        self.finder.next()
        self.finder.replace()
        assert self.finder.text == (
            "One only risks it, because--\n"
            "one's survival depends on it.--")
        assert self.finder.pos == 60
        self.assert_raises(StopIteration, self.finder.next)

    def test_replace__lengthen_previous(self):
        self.finder.set_regex(r"$")
        self.finder.replacement = "--"
        self.finder.previous()
        self.finder.replace(next=False)
        assert self.finder.text == (
            "One only risks it, because\n"
            "one's survival depends on it.--")
        assert self.finder.pos == 56
        self.finder.previous()
        self.finder.replace(next=False)
        assert self.finder.text == (
            "One only risks it, because--\n"
            "one's survival depends on it.--")
        assert self.finder.pos == 26
        self.assert_raises(StopIteration, self.finder.previous)

    def test_replace__shorten_next(self):
        self.finder.set_regex(r"[.,]")
        self.finder.replacement = ""
        self.finder.next()
        self.finder.replace()
        assert self.finder.text == (
            "One only risks it because\n"
            "one's survival depends on it.")
        assert self.finder.pos == 17
        self.finder.next()
        self.finder.replace()
        assert self.finder.text == (
            "One only risks it because\n"
            "one's survival depends on it")
        assert self.finder.pos == 54
        self.assert_raises(StopIteration, self.finder.next)

    def test_replace__shorten_previous(self):
        self.finder.set_regex(r"[.,]")
        self.finder.replacement = ""
        self.finder.previous()
        self.finder.replace(next=False)
        assert self.finder.text == (
            "One only risks it, because\n"
            "one's survival depends on it")
        assert self.finder.pos == 55
        self.finder.previous()
        self.finder.replace(next=False)
        assert self.finder.text == (
            "One only risks it because\n"
            "one's survival depends on it")
        assert self.finder.pos == 17
        self.assert_raises(StopIteration, self.finder.previous)

    def test_replace_all__regex(self):
        self.finder.set_regex(r"\s")
        self.finder.replacement = ""
        stats = self.finder.replace_all()
        assert stats.matches == 9
        assert stats.replacements == 9
        assert stats.rows == set()
        assert stats == 9
        assert self.finder.text == (
            "Oneonlyrisksit,because"
            "one'ssurvivaldependsonit.")

    def test_replace_all__string(self):
        self.finder.pattern = "i"
        self.finder.replacement = "-"
        stats = self.finder.replace_all()
        assert stats.matches == 4
        assert stats.replacements == 4
        assert stats.rows == set()
        assert stats == 4
        assert self.finder.text == (
            "One only r-sks -t, because\n"
            "one's surv-val depends on -t.")

    def test_replace_all__no_actual_change(self):
        self.finder.pattern = "it"
        self.finder.replacement = "it"
        stats = self.finder.replace_all()
        assert stats.matches == 2
        assert stats.replacements == 0
        assert stats == 0
        assert not stats
