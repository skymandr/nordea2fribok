#! /usr/bin/env python3
"""
    csv2fribok.py
    - a python script for converting Nordea files in CSV
    (comma separted values) format CSV for import in FriBok.

    (C) 2022 Andreas Skyman (skymandr@fripost.org)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see [0].

------
[0]:  http://www.gnu.org/licenses/gpl-3.0.html

"""

import logging
from os import linesep, path
from typing import List, Optional

LICENSE = """csv2fribok.py  Copyright (C) 2022  Andreas Skyman

This program comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it
under certain conditions.

See the file LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
for details!
"""
WARNING = "** WARNING! **"


CSV_ROW = List[str]
CSV = List[CSV_ROW]

FRIBOK_HEADER: CSV_ROW = [
    "Nummer",
    "Beskrivning",
    "Datum",
    "Konto",
    "Debet",
    "Kredit",
    "Projekt",
    "Resultatenhet",
]


# Function definitions:
def print_license() -> None:
    """Function for printing the the license information."""
    print(LICENSE)


def print_warning(warning: str) -> None:
    """Function for printing warnings"""
    print(f"{WARNING} {warning}\n")


def print_error(
    error: Exception,
    debug: bool = False,
) -> None:
    """Function for handling error reporting."""
    if debug:
        logging.exception(error)
    print(error)


def print_csv(csv: CSV, separator: str) -> None:
    """Function for printing CSV with given separator"""
    for row in csv:
        print(args.separator.join(row))


def parse_csv(
    filename: str,
    separator: str,
) -> CSV:
    """Function for parsing input CSV to list of cell rows."""
    parsed = []
    try:
        with open(filename, 'r') as fp:
            lines = fp.readlines()
        for line in lines:
            parsed.append(line.strip().split(separator))
    except Exception:
        raise ValueError(f"Could not parse '{filename}'. Does it exist?")
    return parsed


def save_csv(csv: CSV, outfile: str, separator: str, force: bool) -> None:
    """Function for writing CSV to file"""
    if path.isfile(outfile) and not force:
        raise ValueError(
            f"File '{outfile}' exists. Use '--force' to replace."
        )
    with open(outfile, 'w') as fp:
        for row in csv:
            line = separator.join(row) + linesep
            fp.write(line)


def row_to_fribok(row: CSV_ROW, accounts: List[str]) -> CSV:
    """Function for converting a CSV row to a FriBok CSV entry"""
    try:
        if row[3].startswith("-"):
            debit = row[3][1:]
            credit = ""
        else:
            debit = ""
            credit = row[3]

        fribok = [
            [row[0], row[1], row[2], "", "", "", "", ""],
            ["", "", "", accounts[0], debit, credit, "", ""],
            ["", "", "", accounts[1], credit, debit, "", ""],
        ]
    except Exception:
        raise ValueError(f"Could not parse row '{row}'.")
    return fribok


def parsed_to_fribok(csv: CSV, accounts: List[str]) -> CSV:
    """Function for converting a CSV to a FriBok CSV"""
    fribok = [FRIBOK_HEADER, []]
    for row in csv:
        [fribok.append(r) for r in row_to_fribok(row, accounts)]
    return fribok


def get_outfile(filename: str) -> str:
    """Function for getting default output file from input"""
    return f"{path.splitext(filename)[0]}_fribok.csv"


## Main loop:
if __name__ == "__main__":
    # Setup argument parser:
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog="csv2fribok.py",
        description="Script for converting Nordea CSV to FriBok CSV."
    )
    parser.add_argument(
        "-o", "--out", dest="outfile",
        type=str, default=None,
        metavar="PATH",
        help="specify output file (default: <input>_fribok.csv)",
    )
    parser.add_argument(
        "-s", "--sep", dest="separator",
        type=str, default=";",
        help="specify separator (default: ';')",
    )
    parser.add_argument(
        "-a", "--accounts", dest="accounts",
        type=str, nargs=2, default=["3000", "1200"],
        metavar="ACCOUNT",
        help="specify accounts (default: 3000 and 1200)",
    )
    parser.add_argument(
        "-f", "--force", dest="force",
        action="store_true",
        help="write to output even if it exists",
    )
    parser.add_argument(
        "-p", "--print", dest="print",
        action="store_true",
        help="print output to standard out (use -o to save to file too)",
    )
    parser.add_argument(
        "-v", "--verbose", dest="verbose",
        action="store_true",
        help="enable verbose output",
    )
    parser.add_argument(
        "-d", "--debug", dest="debug",
        action="store_true",
        help="enable debug output",
    )
    parser.add_argument(
        "inputfile",
        type=str,
        metavar="FILE",
        help="file to process",
    )

    # Parse arguments:
    args = parser.parse_args()

    # Process arguments:
    outfile: Optional[str] = args.outfile
    if outfile is None and not args.print:
        outfile = get_outfile(args.inputfile)

    if args.verbose:
        print_license()
        if args.print:
            print_warning(
                "Using 'verbose' with 'print' may cause trouble "
                "with e.g. piping!"
            )

    # Parse file:
    try:
        parsed = parse_csv(args.inputfile, args.separator)
        if args.verbose:
            print(f"Read {len(parsed)} lines from '{args.inputfile}'")
        fribok = parsed_to_fribok(parsed, args.accounts)

        if args.print:
            print_csv(fribok, args.separator)

        if outfile is not None:
            save_csv(fribok, outfile, args.separator, args.force)
            
            if args.verbose:
                print(f"Wrote {len(fribok)} lines to '{outfile}'")

    except Exception as err:
        print_error(err)
