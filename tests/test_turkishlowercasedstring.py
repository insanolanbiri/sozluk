import pytest

from sozluk.turkishlowercasedstring import TurkishLowercasedString


class TestTurkishLowercasedString:
    @pytest.mark.parametrize(
        "given,expected",
        [
            ("a", "a"),
            ("A", "a"),
            ("!", "!"),
            (" ", " "),
            ("", ""),
            ("i", "i"),
            ("ı", "ı"),
            ("İ", "i"),
            ("I", "ı"),
            ("Ö", "ö"),
            ("Ü", "ü"),
            ("Ğ", "ğ"),
            ("Ş", "ş"),
            ("Ç", "ç"),
            ("ö", "ö"),
            ("ü", "ü"),
            ("ş", "ş"),
            ("ç", "ç"),
            ("ğ", "ğ"),
        ],
    )
    def test_character_capitalizaton(self, given, expected):
        s = TurkishLowercasedString(given)

        assert s == expected
