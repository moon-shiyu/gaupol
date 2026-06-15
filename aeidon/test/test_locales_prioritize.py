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


class TestPrioritizeLanguages(aeidon.TestCase):

    ITEMS = [
        ("de",    "German"),
        ("en",    "English"),
        ("es",    "Spanish"),
        ("fr",    "French"),
        ("ja",    "Japanese"),
        ("pt_BR", "Portuguese (Brazil)"),
        ("zh_CN", "Chinese (China)"),
    ]

    def test_system_language_first(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="fr")
        assert priority[0] == ("fr", "French")
        assert ("fr", "French") not in remaining

    def test_current_language_second(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="fr", current_code="de")
        assert priority[0] == ("fr", "French")
        assert priority[1] == ("de", "German")

    def test_recent_languages_in_order(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, recent_codes=["ja", "es"])
        assert priority[0] == ("ja", "Japanese")
        assert priority[1] == ("es", "Spanish")

    def test_full_priority_order(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS,
            system_code="zh_CN",
            current_code="en",
            recent_codes=["es", "fr"])
        assert priority[0] == ("zh_CN", "Chinese (China)")
        assert priority[1] == ("en", "English")
        assert priority[2] == ("es", "Spanish")
        assert priority[3] == ("fr", "French")
        assert len(priority) == 4

    def test_dedup_system_equals_current(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="en", current_code="en")
        assert len([x for x in priority if x[0] == "en"]) == 1
        assert priority[0] == ("en", "English")

    def test_dedup_recent_overlaps_system(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="fr", recent_codes=["fr", "de"])
        codes = [c for c, n in priority]
        assert codes.count("fr") == 1
        assert codes == ["fr", "de"]

    def test_remaining_sorted_alphabetically(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="ja")
        names = [n for c, n in remaining]
        assert names == sorted(names)

    def test_prefix_matching(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="en_US")
        assert priority[0] == ("en", "English")

    def test_prefix_matching_locale_item(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="pt")
        assert priority[0] == ("pt_BR", "Portuguese (Brazil)")

    def test_none_system_code(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code=None)
        assert len(priority) == 0
        assert len(remaining) == len(self.ITEMS)

    def test_all_none(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS)
        assert len(priority) == 0
        names = [n for c, n in remaining]
        assert names == sorted(names)

    def test_empty_items(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            [], system_code="en", current_code="fr")
        assert priority == []
        assert remaining == []

    def test_code_not_in_items(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS, system_code="xx", current_code="yy")
        assert len(priority) == 0
        assert len(remaining) == len(self.ITEMS)

    def test_no_items_lost(self):
        priority, remaining = aeidon.locales.prioritize_languages(
            self.ITEMS,
            system_code="en",
            current_code="fr",
            recent_codes=["ja"])
        total = len(priority) + len(remaining)
        assert total == len(self.ITEMS)
