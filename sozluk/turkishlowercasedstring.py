class TurkishLowercasedString(str):
    def __new__(cls, o: object = ""):
        s = super().__new__(cls, str(o).replace("İ", "i").replace("I", "ı").lower())
        return s
