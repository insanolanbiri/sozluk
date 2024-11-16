from sozluk.turkishlowercasedstring import TurkishLowercasedString


class AuthorName(TurkishLowercasedString):
    def __new__(cls, o: object = ""):
        instance = super().__new__(cls, o)
        if " " in instance:
            raise ValueError("Author name cannot contain spaces")

        length = len(instance)

        if length > 40:
            raise ValueError("Author name is too long")
        if length < 1:
            raise ValueError("Author name cannot be empty")

        if not instance.isalnum():
            raise ValueError("Author name is not alphanumeric")

        return instance
