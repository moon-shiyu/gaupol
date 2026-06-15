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

from aeidon.i18n import d_


class TestModule(aeidon.TestCase):

    def test_code_to_name(self):
        name = d_("iso_639", "Nauru")
        assert aeidon.languages.code_to_name("na") == name
        name = d_("iso_639", "Sindhi")
        assert aeidon.languages.code_to_name("sd") == name

    def test_is_valid(self):
        assert aeidon.languages.is_valid("sv")
        assert not aeidon.languages.is_valid("xx")


class TestSortLanguages(aeidon.TestCase):

    """Tests for aeidon.languages.sort_languages (pure logic, no GTK needed)."""

    # A representative set of codes for testing.
    CODES = ["en", "en_US", "fi", "fr", "de", "sv", "zh"]

    def test_no_priorities_alphabetical(self):
        """Without any priorities, all codes go to 'other' sorted by name."""
        priority, other = aeidon.languages.sort_languages(self.CODES)
        assert priority == []
        assert len(other) == len(self.CODES)
        # other should be sorted by localized name (code_to_name).
        names = [aeidon.languages.code_to_name(c) for c in other]
        assert names == sorted(names)

    def test_system_language_first(self):
        """System language should appear as the first priority item."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES, system_code="fi")
        assert priority[0] == "fi"
        assert "fi" not in other

    def test_system_locale_with_country(self):
        """System locale like fi_FI should match language prefix 'fi'."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES, system_code="fi_FI")
        # fi should be in priority (matched by language prefix).
        assert "fi" in priority
        assert "fi" not in other

    def test_project_language_priority(self):
        """Project language should come after system language in priority."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES, system_code="fi", project_code="de")
        assert priority[0] == "fi"
        assert "de" in priority
        assert "de" not in other

    def test_project_language_without_system(self):
        """Project language should be first priority if no system code."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES, project_code="fr")
        assert priority[0] == "fr"
        assert "fr" not in other

    def test_recent_languages_order(self):
        """Recent languages should appear in priority after system/project."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES,
            system_code="fi",
            project_code="de",
            recent_codes=["sv", "fr"])
        assert priority[0] == "fi"
        assert "de" in priority
        assert "sv" in priority
        assert "fr" in priority
        # sv should come before fr (recent order preserved).
        assert priority.index("sv") < priority.index("fr")
        assert "sv" not in other
        assert "fr" not in other

    def test_recent_without_system_or_project(self):
        """Recent languages alone should be prioritized."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES, recent_codes=["zh", "en"])
        assert priority == ["zh", "en"]

    def test_deduplication(self):
        """Same code appearing in multiple priority sources is not duplicated."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES,
            system_code="fi",
            project_code="fi",
            recent_codes=["fi"])
        assert priority.count("fi") == 1

    def test_priority_codes_not_in_other(self):
        """No priority code should appear in the 'other' list."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES,
            system_code="en_US",
            project_code="de",
            recent_codes=["fr"])
        priority_set = set(priority)
        other_set = set(other)
        assert priority_set.isdisjoint(other_set)
        assert priority_set | other_set == set(self.CODES)

    def test_recent_codes_not_in_list_ignored(self):
        """Recent codes not in the available codes list are ignored."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES, recent_codes=["xx", "zz"])
        assert priority == []
        assert len(other) == len(self.CODES)

    def test_empty_codes(self):
        """Empty codes list returns empty results."""
        priority, other = aeidon.languages.sort_languages(
            [], system_code="fi", project_code="en")
        assert priority == []
        assert other == []

    def test_none_optional_params(self):
        """All optional parameters default to None/empty correctly."""
        priority, other = aeidon.languages.sort_languages(
            self.CODES,
            system_code=None,
            project_code=None,
            recent_codes=None)
        assert priority == []
        assert len(other) == len(self.CODES)

    def test_system_and_project_same_language_prefix(self):
        """System en_US and project en both match 'en' prefix, no duplication."""
        codes = ["en", "en_US", "en_GB", "fi", "fr"]
        priority, other = aeidon.languages.sort_languages(
            codes, system_code="en_US", project_code="en")
        # en_US (system exact) first, then en (system prefix match),
        # then en_GB (system prefix match), project "en" is already seen.
        assert "en_US" in priority
        assert "en" in priority
        assert "en_GB" in priority
        assert len(set(priority)) == len(priority)  # No duplicates.
        assert "fi" in other
        assert "fr" in other

    def test_return_types(self):
        """sort_languages returns a tuple of two lists."""
        result = aeidon.languages.sort_languages(self.CODES)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], list)
        assert isinstance(result[1], list)
