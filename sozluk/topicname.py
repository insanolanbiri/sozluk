from sozluk.turkishlowercasedstring import TurkishLowercasedString


class TopicName(TurkishLowercasedString):
    def __new__(cls, o: object = ""):
        instance = super().__new__(cls, o)
        length = len(instance)

        if length > 50:
            raise ValueError("Topic name is too long")
        if length < 1:
            raise ValueError("Topic name cannot be empty")

        if any(
            (
                instance.endswith(" "),
                instance.startswith(" "),
                "  " in instance,
            )
        ):
            raise ValueError("Topic name has got weird spaces")

        if not instance.replace(" ", "").isalnum():
            raise ValueError("Topic name is not alphanumeric")
        return instance
