#!/usr/bin/env python3
"""Usage: jotter-bib [-h|--help]

Extract all bibtex fields from markdown files
"""

import sys
from jotter import find_jotter_root, survey

if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__); exit(0)
    else:
        filename_map, _, _ = survey(find_jotter_root(), full_content=False)
        bibtex = map(
            lambda doc: doc["bibtex"],
            filter(
                lambda doc: "bibtex" in doc.keys(),
                filename_map.values()
            )
        )
        for entry in bibtex:
            print(entry)
            print() # Just to make sure
