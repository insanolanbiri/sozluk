import pytest

from sozluk.authorname import AuthorName


class TestAuthorName:
    def test_init_normal(self):
        assert AuthorName("hello") == "hello"
        assert AuthorName("Hello") == "hello"

    def test_init_spaces(self):
        with pytest.raises(ValueError):
            AuthorName("i love space")

    def test_init_long_name(self):
        assert AuthorName("a" * 40) == "a" * 40
        with pytest.raises(ValueError):
            AuthorName("a" * 41)

    def test_init_empty(self):
        with pytest.raises(ValueError):
            AuthorName()
        with pytest.raises(ValueError):
            AuthorName("")

    def test_init_nonalphanumeric(self):
        with pytest.raises(ValueError):
            AuthorName("nonalpha:/")
