#!/usr/bin/env python3
"""Usage: jotter-bib [options] [citekeys]..

Extract bibtex fields from markdown files

Positional Arguments:
    citekeys        Only include specific citekeys. If this argument
                    is omitted, the full bibliography will be printed.
Options:
    -C PATH         Change directory before executing command. This
        --cd PATH   is useful for invoking jotter-bib from a directory
                    that is not part of the jotter itself, e. g. when
                    compiling the bibliography for an essay.
    -l  --list      List all bibtex citekeys defined in this jotter.
    -L  --list-all  List all citekeys, including non-bibtex ones.
        --no-deps   Do not include dependencies for "crossref" or
                    "xref" entries.
    -h  --help      Print this help message and exit.
"""

import sys
import os
import re
from jotter import find_jotter_root, survey

def get_bib(citekey_map, citekeys: list, deps=True):
    done = set()
    for key in citekeys:
        if key in done:
            continue
        try:
            bibtex = re.split(r'\n\s*@', "\n"+citekey_map[key]["bibtex"])
            for entry in bibtex:
                if re.match(r'^.*?{'+key+r',', entry):
                    if deps:
                        crossref = re.findall(
                            r'(xref|crossref)\s*=\s*[{"](.*?)[}"]',
                            entry,
                            re.I,
                        )
                        for crossref_type, crossref_key in crossref:
                            if crossref_key in done:
                                continue
                            for dep in get_bib(citekey_map, [crossref_key]):
                                dep_key = re.findall(r'^@.*?{(.*?),', dep)[0]
                                if dep_key not in done:
                                    done.add(dep_key)
                                    yield dep
                    done.add(key)
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

def print_bib(citekeys, deps=True):
    citekey_map = get_citekey_map()
    if not citekeys:
        citekeys = get_citekeys(citekey_map)
    first = True
    for entry in get_bib(citekey_map, citekeys, deps=deps):
        if first:
            first = False
        else:
            print()         # Separate entries by newline
        print(entry)

def print_citekeys(real=True):
    print("\n".join(get_citekeys(get_citekey_map(), real=real)))


if __name__ == "__main__":
    deps = True
    if "--no-deps" in sys.argv:
        deps=False
        sys.argv.remove("--no-deps")
    if "-C" in sys.argv or "--cd" in sys.argv:
        if "-C" in sys.argv:
            cd_opt = "-C"
        elif "--cd" in sys.argv:
            cd_opt = "--cd"
        try:
            opt_i = sys.argv.index(cd_opt)
            new_dir = sys.argv[opt_i+1]
            del sys.argv[opt_i:opt_i+2]
        except IndexError:
            print("{} requires an argument".format(cd_opt), file=sys.stderr)
            exit(1)
        try:
            os.chdir(new_dir)
        except (FileNotFoundError, NotADirectoryError) as e:
            print(re.sub(r'^\[.*\] ', '', str(e)), file=sys.stderr)
            exit(1)
    if len(sys.argv) == 1:
        print_bib(None, deps=deps)
    elif "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__); exit(0)
    elif sys.argv[1] in ["-l", "--list"]:
        print_citekeys(real=True)
    elif sys.argv[1] in ["-L", "--list-all"]:
        print_citekeys(real=False)
    else:
        print_bib(sys.argv[1:], deps=deps)
