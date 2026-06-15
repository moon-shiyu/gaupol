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
import codecs

from aeidon.i18n   import _
from unittest.mock import patch, MagicMock

# https://docs.python.org/3.10/library/codecs.html#standard-encodings
ENCODINGS = [
    "ascii",
    "big5",
    "big5hkscs",
    "cp037",
    "cp273",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "cp1006",
    "cp1026",
    "cp1125",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "euc_jp",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_kr",
    "gb2312",
    "gbk",
    "gb18030",
    "hz",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "latin_1",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "iso8859_10",
    "iso8859_11",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "johab",
    "koi8_r",
    "koi8_t",
    "koi8_u",
    "kz1048",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
    "utf_32",
    "utf_32_be",
    "utf_32_le",
    "utf_16",
    "utf_16_be",
    "utf_16_le",
    "utf_7",
    "utf_8",
    "utf_8_sig",
]


class TestModule(aeidon.TestCase):

    def test_all_found(self):
        for code in ENCODINGS:
            # Skip if code not included in the Python version
            # that we're currently running.
            if not aeidon.encodings.is_valid_code(code): continue
            code = aeidon.encodings.translate_code(code)
            assert aeidon.encodings.code_to_name(code)
            assert aeidon.encodings.code_to_description(code)

    def test_code_to_description(self):
        code_to_description = aeidon.encodings.code_to_description
        assert code_to_description("cp1006") == _("Urdu")
        assert code_to_description("hz") == _("Chinese simplified")
        assert code_to_description("shift_jis") == _("Japanese")

    def test_code_to_long_name(self):
        code, name, description = ("cp1140", "IBM1140", _("Western"))
        long_name = aeidon.encodings.code_to_long_name(code)
        assert long_name == _("{description} ({name})").format(**locals())

    def test_code_to_name(self):
        code_to_name = aeidon.encodings.code_to_name
        assert code_to_name("big5hkscs") == "Big5-HKSCS"
        assert code_to_name("cp949") == "IBM949"
        assert code_to_name("mac_roman") == "MacRoman"

    def test_detect(self):
        name = aeidon.encodings.detect(self.new_subrip_file())
        assert aeidon.encodings.is_valid_code(name)

    def test_detect_bom__none(self):
        path = self.new_subrip_file()
        encoding = aeidon.encodings.detect_bom(path)
        assert encoding is None

    @patch("aeidon.encodings.is_valid_code", lambda x: True)
    def test_detect_bom__utf_16_be(self):
        path = self.new_subrip_file()
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(codecs.BOM_UTF16_BE + blob)
        encoding = aeidon.encodings.detect_bom(path)
        assert encoding == "utf_16_be"

    @patch("aeidon.encodings.is_valid_code", lambda x: True)
    def test_detect_bom__utf_16_le(self):
        path = self.new_subrip_file()
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(codecs.BOM_UTF16_LE + blob)
        encoding = aeidon.encodings.detect_bom(path)
        assert encoding == "utf_16_le"

    @patch("aeidon.encodings.is_valid_code", lambda x: True)
    def test_detect_bom__utf_32_be(self):
        path = self.new_subrip_file()
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(codecs.BOM_UTF32_BE + blob)
        encoding = aeidon.encodings.detect_bom(path)
        assert encoding == "utf_32_be"

    @patch("aeidon.encodings.is_valid_code", lambda x: True)
    def test_detect_bom__utf_32_le(self):
        path = self.new_subrip_file()
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(codecs.BOM_UTF32_LE + blob)
        encoding = aeidon.encodings.detect_bom(path)
        assert encoding == "utf_32_le"

    @patch("aeidon.encodings.is_valid_code", lambda x: True)
    def test_detect_bom__utf_8_sig(self):
        path = self.new_subrip_file()
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(codecs.BOM_UTF8 + blob)
        encoding = aeidon.encodings.detect_bom(path)
        assert encoding == "utf_8_sig"

    def test_get_locale_code(self):
        code = aeidon.encodings.get_locale_code()
        assert aeidon.encodings.is_valid_code(code)

    def test_get_locale_long_name(self):
        long_name = aeidon.encodings.get_locale_long_name()
        code = aeidon.encodings.get_locale_code()
        name = aeidon.encodings.code_to_name(code)
        assert long_name == _("Current locale ({})").format(name)

    def test_get_valid(self):
        assert aeidon.encodings.get_valid()
        for item in aeidon.encodings.get_valid():
            code, name, description = item
            assert aeidon.encodings.is_valid_code(code)

    def test_is_valid_code(self):
        assert aeidon.encodings.is_valid_code("gbk")
        assert aeidon.encodings.is_valid_code("utf_16_be")
        assert not aeidon.encodings.is_valid_code("xxxxx")

    def test_name_to_code(self):
        name_to_code = aeidon.encodings.name_to_code
        assert name_to_code("IBM037") == "cp037"
        assert name_to_code("GB2312") == "gb2312"
        assert name_to_code("PTCP154") == "ptcp154"

    def test_translate_code(self):
        translate_code = aeidon.encodings.translate_code
        assert translate_code("johab") == "johab"
        assert translate_code("UTF-8") == "utf_8"
        assert translate_code("ISO-8859-1") == "latin_1"

    # --- EncodingCandidate ---

    def test_encoding_candidate(self):
        c = aeidon.encodings.EncodingCandidate("utf_8", 0.95, "English")
        assert c.encoding == "utf_8"
        assert c.confidence == 0.95
        assert c.language == "English"

    def test_encoding_candidate__empty_language(self):
        c = aeidon.encodings.EncodingCandidate("ascii", 0.80, "")
        assert c.language == ""

    # --- DetectionResult ---

    def test_detection_result__defaults(self):
        r = aeidon.encodings.DetectionResult()
        assert r.encoding is None
        assert r.confidence == 0.0
        assert r.candidates == []

    def test_detection_result__with_values(self):
        candidates = [
            aeidon.encodings.EncodingCandidate("utf_8", 0.95, ""),
            aeidon.encodings.EncodingCandidate("ascii", 0.80, ""),
        ]
        r = aeidon.encodings.DetectionResult("utf_8", 0.95, candidates)
        assert r.encoding == "utf_8"
        assert r.confidence == 0.95
        assert len(r.candidates) == 2

    def test_detection_result__is_uncertain__true(self):
        r = aeidon.encodings.DetectionResult("cp1252", 0.50)
        assert r.is_uncertain

    def test_detection_result__is_uncertain__false(self):
        r = aeidon.encodings.DetectionResult("utf_8", 0.95)
        assert not r.is_uncertain

    def test_detection_result__is_uncertain__none_encoding(self):
        r = aeidon.encodings.DetectionResult(None, 0.0)
        assert not r.is_uncertain

    def test_detection_result__repr(self):
        r = aeidon.encodings.DetectionResult("utf_8", 0.95, [
            aeidon.encodings.EncodingCandidate("utf_8", 0.95, ""),
        ])
        text = repr(r)
        assert "utf_8" in text
        assert "0.950" in text
        assert "1" in text

    # --- detect_candidates ---

    @patch("aeidon.encodings.is_valid_code", lambda x: True)
    def test_detect_candidates__bom(self):
        path = self.new_subrip_file()
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(codecs.BOM_UTF8 + blob)
        result = aeidon.encodings.detect_candidates(path)
        assert result.encoding == "utf_8_sig"
        assert result.confidence == 1.0
        assert not result.is_uncertain
        assert len(result.candidates) == 1
        assert result.candidates[0].encoding == "utf_8_sig"

    def _make_mock_match(self, encoding, coherence, language=""):
        match = MagicMock()
        match.encoding = encoding
        match.coherence = coherence
        match.language = language
        return match

    @patch("aeidon.encodings.detect_bom", return_value=None)
    def test_detect_candidates__charset_normalizer(self, mock_bom):
        mock_best = self._make_mock_match("utf_8", 0.95, "English")
        mock_alt = self._make_mock_match("ascii", 0.70, "")
        mock_result_set = MagicMock()
        mock_result_set.best.return_value = mock_best
        mock_result_set.__iter__ = MagicMock(
            return_value=iter([mock_best, mock_alt]))
        with patch("charset_normalizer.from_path",
                   return_value=mock_result_set):
            path = self.new_subrip_file()
            result = aeidon.encodings.detect_candidates(path)
        assert result.encoding == "utf_8"
        assert result.confidence == 0.95
        assert not result.is_uncertain
        assert len(result.candidates) == 2
        assert result.candidates[0].encoding == "utf_8"
        assert result.candidates[1].encoding == "ascii"

    @patch("aeidon.encodings.detect_bom", return_value=None)
    def test_detect_candidates__uncertain(self, mock_bom):
        mock_best = self._make_mock_match("cp1252", 0.40)
        mock_alt = self._make_mock_match("latin_1", 0.38)
        mock_result_set = MagicMock()
        mock_result_set.best.return_value = mock_best
        mock_result_set.__iter__ = MagicMock(
            return_value=iter([mock_best, mock_alt]))
        with patch("charset_normalizer.from_path",
                   return_value=mock_result_set):
            path = self.new_subrip_file()
            result = aeidon.encodings.detect_candidates(path)
        assert result.encoding == "cp1252"
        assert result.is_uncertain
        assert len(result.candidates) == 2

    @patch("aeidon.encodings.detect_bom", return_value=None)
    def test_detect_candidates__no_result(self, mock_bom):
        mock_result_set = MagicMock()
        mock_result_set.best.return_value = None
        with patch("charset_normalizer.from_path",
                   return_value=mock_result_set):
            path = self.new_subrip_file()
            result = aeidon.encodings.detect_candidates(path)
        assert result.encoding is None
        assert result.confidence == 0.0
        assert result.candidates == []
