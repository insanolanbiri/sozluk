from dataclasses import dataclass

from sozluk.authorname import AuthorName


@dataclass
class Human:
    identifier: int
    real_name: str
    primary_authorname: AuthorName
