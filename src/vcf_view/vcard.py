# Straightforward viewer for .vcf files
# Copyright (C) 2024  Damy Metzke
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
from typing import Iterable, Optional

@dataclass
class Name:
    family_names: str
    given_names: str
    additional_names: str
    honorific_prefixes: str
    honorific_suffixes: str

    def __str__(self) -> str:
        return " ".join((value for value in (
            self.honorific_prefixes,
            self.given_names,
            self.additional_names,
            self.family_names,
            self.honorific_suffixes,
        ) if value != ""))

    def to_content(self):
        yield "Prefix", self.honorific_prefixes
        yield "First name", self.given_names
        yield "Middle name", self.additional_names
        yield "Family name", self.family_names
        yield "Suffix", self.honorific_suffixes

    def lable_max_width(self):
        return 11

@dataclass
class CustomProperty:
    property: str
    parameters: dict[str, str]
    values: list[str]

@dataclass
class Section:
    title: str
    content: Iterable[tuple[str, str]]
    label_max_width: int


class VCard:
    def __init__(self):
        self.name: Optional[Name] = None
        self.custom_properties: list[CustomProperty] = []

    _last_line: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.name}"

    def sections(self):
        if self.name is not None:
            yield Section(
                title="Name (parts)",
                content=self.name.to_content(),
                label_max_width=self.name.lable_max_width(),
            ) 

            yield Section(
                title="Custom fields",
                content=(
                    (property.property, ";".join(property.values))
                    for property in self.custom_properties
                ),
                label_max_width=max(len(property.property) for property in self.custom_properties)
            )
