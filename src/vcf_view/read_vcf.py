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

from collections.abc import Iterator
from typing import TextIO

from vcf_view.properties import Parser
from vcf_view.vcard import VCard

             

def parse_vcard(input: Iterator[str]):
    card = VCard()
    parser = Parser(card)
    for line in input:
        line = line.rstrip("\n")

        if line == "END:VCARD":
            parser.flush()
            return card

        if line.strip() != "":
            parser.push(line)

    raise Exception("Reached end without closing vcard")



def read_vcf(input: TextIO):

    input_iter = iter(input)

    for line in input_iter:
        line = line.rstrip("\n")
        if line == "BEGIN:VCARD":
            yield parse_vcard(input_iter)


