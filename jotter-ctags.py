#!/usr/bin/env python3
"""Usage: jotter-ctags [-h|--help]

Create or update a tags file in the jotter's root directory.
Unlike some other ctags-like programs, this one doesn't support
any command line arguments other than --help.
"""

import sys
import os
from jotter import find_jotter_root, survey

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print(__doc__)
            exit(0)
        else:
            # It may be a good idea to explicitly tell people that the
            # option they're trying to use doesn't work as in other
            # ctags-like programs.
            print(
                "Unknown command line argument: \"{}\"".format(sys.argv[1]),
                "Run \"jotter-ctags --help\" for usage information.",
                sep="\n", file=sys.stderr,
            )
            exit(1)

    jotter_root = find_jotter_root()
    tags_file = os.path.join(jotter_root, "tags")
    _, citekey_map, _ = survey(jotter_root, full_content=False)
    tags = list()
    for key, doc in citekey_map.items():
        tags.append((key, doc["_filename"], "/"+key))
    tags.sort()
    with open(tags_file, "w") as f:
        for t in tags:
            f.write("{}\t{}\t{}\n".format(*t))
