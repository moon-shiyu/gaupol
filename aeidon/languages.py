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

"""Names and ISO 639 codes for languages and conversions between them."""

import aeidon
import json
import os

from aeidon.i18n import d_

_languages = {}


def _init_languages():
    """Initialize the dictionary mapping codes to names."""
    # Prefer globally installed, fall back on possibly bundled.
    path = "/usr/share/iso-codes/json/iso_639-2.json"
    if os.path.isfile(path):
        return _init_languages_json(path)
    path = os.path.join(aeidon.DATA_DIR, "iso-codes", "iso_639-2.json")
    if os.path.isfile(path):
        return _init_languages_json(path)

def _init_languages_json(path):
    """Initialize the dictionary mapping codes to names."""
    with open(path, "r", encoding="utf_8") as f:
        iso = json.load(f)
    for language in iso["639-2"]:
        code = language.get("alpha_2", None)
        name = language.get("name", None)
        if not code or not name: continue
        _languages[code] = name

def code_to_name(code):
    """Convert ISO 639 `code` to localized language name."""
    if not _languages:
        _init_languages()
    with aeidon.util.silent(LookupError):
        return d_("iso_639", _languages[code])
    return code

def is_valid(code):
    """Return ``True`` if `code` is a valid ISO 639 language code."""
    if not _languages:
        _init_languages()
    return code in _languages

def sort_languages(codes, system_code=None, project_code=None, recent_codes=None):
    """
    Sort language `codes` with priority ordering.

    Priority order:
    1. System language (if in the list)
    2. Project/subtitle language (if in the list)
    3. Recently used languages (in most-recent-first order, if in the list)
    4. Remaining languages sorted alphabetically by localized name

    `codes` is a list of locale codes (e.g. ``["en_US", "fi", "fr"]``).
    `system_code` is the system locale code (e.g. ``"fi_FI"`` or ``"fi"``).
    `project_code` is the current project/spell-check language code.
    `recent_codes` is a list of recently used locale codes, most recent first.

    Returns a tuple ``(priority_codes, other_codes)`` where `priority_codes`
    are the prioritized languages in order and `other_codes` are the remaining
    languages sorted alphabetically by localized display name.
    """
    recent_codes = recent_codes or []
    codes_set = set(codes)
    # Build priority list in order, deduplicating as we go.
    priority = []
    seen = set()
    # 1. System language (match by language prefix for locale codes like fi_FI).
    if system_code:
        system_lang = system_code[:2] if len(system_code) >= 2 else system_code
        # Prefer exact match first, then language-prefix match.
        for candidate in [system_code]:
            if candidate in codes_set and candidate not in seen:
                priority.append(candidate)
                seen.add(candidate)
        # Also include codes that share the language prefix.
        for code in codes:
            if code[:2] == system_lang and code not in seen:
                priority.append(code)
                seen.add(code)
    # 2. Project/subtitle language.
    if project_code:
        project_lang = project_code[:2] if len(project_code) >= 2 else project_code
        for candidate in [project_code]:
            if candidate in codes_set and candidate not in seen:
                priority.append(candidate)
                seen.add(candidate)
        for code in codes:
            if code[:2] == project_lang and code not in seen:
                priority.append(code)
                seen.add(code)
    # 3. Recently used languages (preserve order, most recent first).
    for code in recent_codes:
        if code in codes_set and code not in seen:
            priority.append(code)
            seen.add(code)
    # 4. Remaining languages sorted alphabetically by localized name.
    other = [c for c in codes if c not in seen]
    other.sort(key=lambda c: code_to_name(c))
    return (priority, other)
