from typing import NamedTuple

from PySide6.QtCore import QLocale


class LanguageAuthor(NamedTuple):
    name: str
    url: str


class Language(NamedTuple):
    code: str
    completion: int
    authors: list[LanguageAuthor]

    @property
    def author_names(self) -> list:
        return [author.name for author in self.authors]

    @property
    def author_links(self) -> list[str]:
        return ['<a href="{0}">{1}</a>'.format(author.url, author.name) for author in self.authors]

    @property
    def title_native(self) -> str:
        return QLocale(self.code).nativeLanguageName().title()

    @property
    def country_native(self) -> str:
        return QLocale(self.code).nativeCountryName().title()


def get_system_language(languages) -> str:
    system_language_code = QLocale.system().name()

    language_codes = {language.code for language in languages}

    if system_language_code in language_codes:
        return system_language_code

    return "en_US"
