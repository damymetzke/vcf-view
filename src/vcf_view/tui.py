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

import argparse
import curses
import os

from vcf_view.read_vcf import read_vcf
from vcf_view.vcard import VCard

def render_list(position: int, offset: int, height: int, cards: list[VCard], list_win):
    list_win.clear()
    list_win.border()
    for i_screen, (i_card, item) in enumerate(list(enumerate(cards))[offset:]):
        if i_screen >= height - 5:
            break
        if i_card == position:
            list_win.addstr(i_screen + 1, 2, f"> {item}")
        else:
            list_win.addstr(i_screen + 1, 2, f"  {item}")

    list_win.refresh()

def render_card(card: VCard, height: int, card_win):
    card_win.clear()
    card_win.border()

    card_win.addstr(1, 1, f"Contact information for: '{card}'")

    offset = 2

    for section in card.sections():
        offset += 1
        if offset >= height - 5:
            break
        card_win.addstr(offset, 1, f"=== {section.title} ===")
        offset += 1
        for label, value in section.content:
            if offset >= height - 10:
                break

            if len(value) > 100:
                value = value[:100]
            card_win.addstr(offset, 1, f"{label}:")
            card_win.addstr(offset, section.label_max_width + 3, value)
            offset += 1


    card_win.refresh()


def run():
    parser = argparse.ArgumentParser(description="Straightforward viewer for .vcf files")
    parser.add_argument("filepath", metavar="FILEPATH", type=str, help=".vcf file to read")

    args = parser.parse_args()

    try:
        stdscr = curses.initscr()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        stdscr.clear()

        height, width = stdscr.getmaxyx()

        header_height = 3
        list_width = 50
        header_win = curses.newwin(header_height, list_width, 0, 0)
        list_win = curses.newwin(height - header_height, list_width, header_height, 0)
        card_win = curses.newwin(height, width - list_width, 0, list_width)

        header_win.border()
        card_win.border()
        header_win.addstr(1, 1, f"File: {os.path.basename(args.filepath)}")

        with open(args.filepath) as file:
            cards = list(read_vcf(file))

        max_offset = max(
            0,
            len(cards) - height + 5
        )

        stdscr.refresh()
        header_win.refresh()
        card_win.refresh()

        position = 0

        def offset():
            return min(max_offset, max(0, position - (height - header_height) // 2))

        render_list(position, offset(), height, cards, list_win)
        render_card(cards[position], height, card_win)

        while True:
            char = stdscr.getch()
            if char == ord("q"):
                break
            elif char == ord("j"):
                position = min(len(cards) - 1, position + 1)
                render_list(position, offset(), height, cards, list_win)
                render_card(cards[position], height, card_win)
            elif char == ord("k"):
                position = max(0, position - 1)
                render_list(position, offset(), height, cards, list_win)
                render_card(cards[position], height, card_win)
            elif char == ord("g"):
                position = 0
                render_list(position, offset(), height, cards, list_win)
                render_card(cards[position], height, card_win)
            elif char == ord("G"):
                position = len(cards) - 1
                render_list(position, offset(), height, cards, list_win)
                render_card(cards[position], height, card_win)

    finally:
        curses.endwin()

