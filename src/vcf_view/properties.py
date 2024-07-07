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

import quopri

from abc import abstractmethod
from inspect import signature, Parameter
from typing import Any, Literal, Optional, Protocol

from vcf_view.vcard import CustomProperty, EmailAddress, Name, PhoneNumber, VCard

class PropertyFunction(Protocol):
    @staticmethod
    @abstractmethod
    def __call__(card: VCard, values: list[str], parameters: dict[str, str]) -> None:
        pass

PROPERTIES: dict[str, PropertyFunction] = {}

def prop(inner_function):
    sig = signature(inner_function)
    num_positional = sum(1 for param in sig.parameters.values() if param.kind == Parameter.POSITIONAL_ONLY) - 1
    allowed_parameters = {key for key, param in sig.parameters.items() if param.kind == Parameter.KEYWORD_ONLY}
    def result(card: VCard, values: list[str], parameters: dict[str, str]):
        if len(values) != num_positional:
            raise Exception(f"Not the right amount of arguments.\nExpected: {num_positional}\nReceived: {len(values)}")
        inner_function(card, *values, **{key: value for key, value in parameters.items() if key in allowed_parameters})
    return result

def reg(name: str, inner_function: PropertyFunction):
    PROPERTIES[name] = inner_function

class Parser:
    def __init__(self, card: VCard):
        self._current: Optional[str] = None
        self._in_x_custom: Literal["not-yet", "currently", "parsed"] = "not-yet"
        self._card = card

    def flush(self):
        current = self._current
        self._current = None
        self._in_x_custom = "not-yet"

        if current is None:
            return


        left, right = current.split(":", 1)
        property, *raw_parameters = left.split(";")
        values = right.split(";")

        parameters = {parameter[0]: parameter[1] if len(parameter) > 1 else "" for parameter in (parameter.split("=", 1) for parameter in raw_parameters)}

        if "ENCODING" in parameters and parameters["ENCODING"] == "QUOTED-PRINTABLE":
            values = [quopri.decodestring(value).decode("utf-8") for value in values]

        if property in PROPERTIES:
            PROPERTIES[property](self._card, values, parameters)
        else:
            self._card.custom_properties.append(CustomProperty(
                property=property,
                parameters=parameters,
                values=values,
            ))

    def push(self, value: str):
        if value.startswith(" ") or self._in_x_custom == "currently":
            if self._in_x_custom == "currently" and ")" in value:
                self._in_x_custom = "parsed"

            if self._in_x_custom == "not-yet":
                _, *right = value.split("X-CUSTOM(", 1)
                if len(right) == 1:
                    self._in_x_custom = "currently"
                    if ")" in right[0]:
                        self._in_x_custom = "parsed"

            if self._current is None:
                raise Exception("Invalid format")
            self._current += value.lstrip(" ")
            return
        if self._current is not None:
            self.flush()

        self._current = value

        _, *right = value.split("X-CUSTOM(", 1)

        if len(right) == 0 or ")" in right[0]:
            self._in_x_custom = "parsed"
        else:
            self._in_x_custom = "currently"

@prop
def version(card: VCard, version: str, /):
    card.version = version
reg("VERSION", version)


@prop
def name(card: VCard, family_names: str, given_names: str, additional_names: str, honorific_prefixes: str, honorific_suffixes: str, /):
    card.name = Name(
        family_names=family_names,
        given_names=given_names,
        additional_names=additional_names,
        honorific_prefixes=honorific_prefixes,
        honorific_suffixes=honorific_suffixes,
    )
reg("N", name)

@prop
def formatted_name(card: VCard, name: str, /):
    card.formatted_name = name
reg("FN", formatted_name)

@prop
def phone_number(card: VCard, number: str, /, *, PREF: Optional[Any] = None, TYPE: Optional[str] = None, CELL: Optional[Any] = None, WORK: Optional[Any] = None, HOME: Optional[Any] = None):
    if TYPE is not None:
        tel_type = TYPE
    else:
        tel_types = set()
        if CELL is not None:
            tel_types.add("cell")
            tel_types.add("voice")
        if WORK is not None:
            tel_types.add("work")
            tel_types.add("voice")
        if HOME is not None:
            tel_types.add("voice")
        if len(tel_types) == 0:
            tel_types.add("voice")

        tel_type = ",".join(sorted(tel_types))


    card.phone_numbers.append(PhoneNumber(
        preferred=PREF is not None,
        tel_type=tel_type,
        number=number,
    ))
reg("TEL", phone_number)

@prop
def email_address(card: VCard, address: str, /, *, PREF: Optional[Any] = None, TYPE: Optional[str] = None, HOME: Optional[Any] = None, WORK: Optional[Any] = None):
    if TYPE is not None:
        email_type = TYPE
    else:
        email_types = set()
        if WORK is not None:
            email_types.add("work")
        if HOME is not None:
            email_types.add("home")

        email_type = ",".join(sorted(email_types))


    card.email_addresses.append(EmailAddress(
        preferred=PREF is not None,
        email_type=email_type,
        address=address,
    ))
reg("EMAIL", email_address)
