#!/usr/bin/env python3
"""Usage: jotter-bib [options] [citekeys]..

Extract bibtex fields from markdown files

Positional Arguments:
    citekeys        Only include specific citekeys. If this argument
                    is omitted, the full bibliography will be printed.
Options:
    -l  --list      List all bibtex citekeys defined in this jotter
    -L  --list-all  List all citekeys, including non-bibtex ones
    -h  --help      Print this help message and exit
"""

import sys
import re
from jotter import find_jotter_root, survey

def get_bib(citekey_map, citekeys: list):
    for key in citekeys:
        try:
            bibtex = re.split(r'\n\s*@', "\n"+citekey_map[key]["bibtex"])
            for entry in bibtex:
                if re.match(r'^.*?{'+key+r',', entry):
                    yield '@'+re.sub(r'\n+$', '', entry)
                    break
        except KeyError:
            print("No bibtex entry for {}".format(key), file=sys.stderr)

def get_citekeys(citekey_map, real=True):
    if real:
        return filter(
            lambda key: "bibtex" in citekey_map[key],
            citekey_map.keys()
        )
    else:
        return citekey_map.keys()

def get_citekey_map():
    _, citekey_map, _ = survey(find_jotter_root(), full_content=False)
    return citekey_map

def print_bib(citekeys):
    citekey_map = get_citekey_map()
    if not citekeys:
        citekeys = get_citekeys(citekey_map)
    first = True
    for entry in get_bib(citekey_map, citekeys):
        if first:
            first = False
        else:
            print()         # Separate entries by newline
        print(entry)

def print_citekeys(real=True):
    print("\n".join(get_citekeys(get_citekey_map(), real=real)))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_bib(None)
    elif "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__); exit(0)
    elif sys.argv[1] in ["-l", "--list"]:
        print_citekeys(real=True)
    elif sys.argv[1] in ["-L", "--list-all"]:
        print_citekeys(real=False)
    else:
        print_bib(sys.argv[1:])
