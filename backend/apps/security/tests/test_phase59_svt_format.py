"""Phase 59 — formatted Secure Voting Token (VB-XXXX-XXXX)."""

from django.test import SimpleTestCase

from core.utils.svt_token_format import (
    generate_formatted_svt,
    is_valid_svt_format,
    normalize_svt_token,
)


class Phase59SvtFormatTests(SimpleTestCase):
    def test_generate_formatted_svt(self):
        code = generate_formatted_svt()
        self.assertTrue(is_valid_svt_format(code))
        self.assertTrue(code.startswith("VB-"))

    def test_normalize_accepts_svt_prefix(self):
        self.assertEqual(normalize_svt_token("SVT-9K4M-X72P"), "VB-9K4M-X72P")

    def test_normalize_strips_noise(self):
        self.assertEqual(normalize_svt_token("vb7f4k92xm"), "VB-7F4K-92XM")

    def test_invalid_length_rejected(self):
        self.assertIsNone(normalize_svt_token("VB-1234"))
        self.assertFalse(is_valid_svt_format("123456"))
