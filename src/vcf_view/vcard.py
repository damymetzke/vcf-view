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
from typing import Optional

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

@dataclass
class CustomProperty:
    property: str
    parameters: dict[str, str]
    values: list[str]


class VCard:
    name: Optional[Name] = None
    custom_properties: list[CustomProperty] = []

    _last_line: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.name}"
