import pytest

from sozluk.topicname import TopicName


class TestTopicName:
    def test_init_normal(self):
        topic = TopicName("my awesome topic")
        assert topic == "my awesome topic"

    def test_init_long_name(self):
        assert TopicName("l" * 40) == "l" * 40
        assert TopicName("c" * 45) == "c" * 45
        assert TopicName("l" * 50) == "l" * 50
        with pytest.raises(ValueError):
            TopicName("m" * 51)

    def test_init_empty_name(self):
        with pytest.raises(ValueError):
            TopicName()
        with pytest.raises(ValueError):
            TopicName("")

    @pytest.mark.parametrize(
        "string",
        [
            " hello world",
            "many  spaces",
            "spaces end ",
        ],
    )
    def test_init_weird_spaces(self, string):
        with pytest.raises(ValueError):
            TopicName(string)

    @pytest.mark.parametrize(
        "string",
        [
            "nonalphanum!",
            "slash/.,!",
        ],
    )
    def test_alphanumeric_check(self, string):
        with pytest.raises(ValueError):
            TopicName(string)
