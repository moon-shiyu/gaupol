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

"""
Names and codes for locales and conversions between them.

Locale codes are of form ``aa[_BB][@Cccc]``, where ``aa`` is a language code,
``BB`` a country code and ``Cccc`` a script. See :mod:`aeidon.languages`,
:mod:`aeidon.countries` and :mod:`aeidon.scripts` for details.
"""

import aeidon
import os

from aeidon.i18n import _


def code_to_country(code):
    """Convert locale `code` to localized country name or ``None``."""
    if len(code) < 5: return None
    return aeidon.countries.code_to_name(code[-2:])

def code_to_language(code):
    """Convert locale `code` to localized language name."""
    if len(code) < 2: return None
    return aeidon.languages.code_to_name(code[:2])

def code_to_name(code):
    """Convert locale `code` to localized name."""
    if len(code) < 5:
        return code_to_language(code)
    return (_("{language} ({country})")
            .format(language=code_to_language(code),
                    country=code_to_country(code)))

@aeidon.deco.once
def get_system_code():
    """Return the locale code preferred by system or ``None``."""
    import locale
    return locale.getlocale()[0]

def prioritize_languages(items, system_code=None, current_code=None, recent_codes=None):
    """
    Reorder language items with priority languages first.

    `items` should be a list of ``(code, name)`` tuples. Returns
    ``(priority_items, remaining_items)`` where priority items appear in order:
    system language, current language, then recently used languages. Remaining
    items are sorted alphabetically by name. Duplicates across priority
    categories are removed (highest priority wins).
    """
    if recent_codes is None:
        recent_codes = []
    # Build ordered list of priority codes (highest priority first).
    priority_codes = []
    for code in [system_code, current_code] + list(recent_codes):
        if code and code not in priority_codes:
            priority_codes.append(code)
    # Build a lookup from item code to (code, name).
    code_map = {code: (code, name) for code, name in items}
    # Match each priority code: try exact match, then 2-letter prefix match.
    priority_items = []
    seen = set()
    for pcode in priority_codes:
        if pcode in code_map and pcode not in seen:
            priority_items.append(code_map[pcode])
            seen.add(pcode)
        elif len(pcode) >= 2:
            prefix = pcode[:2]
            for icode, name in items:
                if icode[:2] == prefix and icode not in seen:
                    priority_items.append((icode, name))
                    seen.add(icode)
                    break
    # Remaining items sorted alphabetically by name.
    remaining_items = sorted(
        [(c, n) for c, n in items if c not in seen],
        key=lambda x: x[1])
    return priority_items, remaining_items

@aeidon.deco.once
def get_system_modifier():
    """Return the system default script modifier or ``None``."""
    for name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(name, None)
        if value and value.count("@") == 1:
            i = value.index("@")
            return value[i+1:i+5]
    # No script modifier found implies the language default script.
    return None
