#!/usr/bin/env python3
"""Usage: jotter-keyword [OPTIONS] [KEYWORD]

Show all files associated with a specific keyword

Options:
    -c  --count     Show keyword counts (implies --list)
    -l  --list      List all keywords used in this jotter
    -h  --help      Print this help message and exit
"""

import sys
from jotter import find_jotter_root, survey

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__, file=sys.stderr); exit(1)
    elif sys.argv[1] in ["-h","--help"]:
        print(__doc__); exit(0)
    else:
        _, _, keyword_map = survey(find_jotter_root(), full_content=False)
        if sys.argv[1] in ["-l","--list","-c","--count"]:
            keywords = list(keyword_map.keys())
            keywords.sort()
            for k in keywords:
                if "-c" in sys.argv or "--count" in sys.argv:
                    pad = int(max(map(len, keyword_map.values()))/10)
                    frame = '  {:>'+str(pad)+'}  '
                    print(frame.format(len(keyword_map[k])), end="")
                print(k)
        else:
            k = " ".join(sys.argv[1:])
            if k not in keyword_map.keys():
                print(
                    "No such keyword: \"{}\"".format(k),
                    file=sys.stderr
                )
                exit(1)
            else:
                files = list(map(
                    lambda doc: doc["_filename"],
                    keyword_map[k]
                ))
                files.sort()
                print("\n".join(files))
