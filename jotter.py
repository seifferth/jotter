#!/usr/bin/env python3

import re, os, sys
from fnmatch import fnmatchcase

def fd():
    for d, _, fs in os.walk('.'):
        if '/.' in d: continue      # Ignore files in hidden directories
        for f in fs:
            if f.startswith('.'): continue      # Ignore hidden files
            if not f.endswith('.md'): continue
            yield os.path.join(d, f)
def pages(filename):
    with open(filename) as f:
        p = []; yaml = 0
        for line in f:
            l = line.strip()
            if not p and not l: continue
            if yaml == 0 and l == '---':
                p.append(line); yaml = 1
            elif yaml == 1 and l in ('---', '...'):
                p.append(line); yaml = 2
            elif l == '---' and yaml == 2:
                yield ''.join(p)
                p = [line]; yaml = 1
            elif re.match(r'^#.*\{#', l):
                yield ''.join(p)
                p = [line]; yaml = 2
            else:
                p.append(line)
        page = ''.join(p)
        if ids(page): yield page
def ids(page) -> set:
    ids = set(); yaml = 0; bibtex = 0
    for line in page.splitlines():
        l = line.strip()
        if yaml == 0 and l == '---':
            yaml = 1; continue
        elif yaml == 1 and l in ('---', '...'):
            yaml = 0; continue
        elif yaml == 1:
            if bibtex == 1 and l and not line.startswith('    '):
                if not re.match(r'^bibtex: +|', line): bibtex = 1
                continue
            elif bibtex == 0 and re.match(r'^bibtex: +|', line):
                bibtex = 1; continue
            elif bibtex == 1:
                m = re.match(r'^@[a-zA-Z]+\{(.+),$', l)
                if m: ids.add(m.groups()[0]); continue
        else:
            m = re.match(r'^#.*\{#([^ \}]+)', line)
            if m: ids.add(m.groups()[0]); continue
    return ids
def cites(page) -> set:
    keys = set(); yaml = 0; bibtex = 0
    for line in page.splitlines():
        l = line.strip()
        if yaml == 0 and l == '---':
            yaml = 1; continue
        elif yaml == 1 and l in ('---', '...'):
            yaml = 0; continue
        elif yaml == 1:
            continue
        m = re.findall(r'@[\w_][\w\d_:-]*[\w\d_]', l)
        for k in m: keys.add(k[1:])
    return keys.difference(ids(page))

def _getrootflag(argv: list):
    """
    Extract the root flag from argv and return either
    the specified root directory as string or None. Note
    that this function will modify argv by removing the
    '--root' flag and the corresponding value if they are
    found. Also note that this function will throw an
    IndexError if the '--root' flag is specified but
    the value is missing.
    """
    rootdir = None
    i = 0
    while i < len(argv):
        if argv[i] == '--root':
            rootdir = argv[i+1]
            argv.pop(i); argv.pop(i)
        elif argv[i].startswith('--root='):
            rootdir = argv[i][7:]
            argv.pop(i)
        i += 1
    return rootdir
def _findrootdir():
    """
    Locate the jotter root directory by checking all
    parent directories. Returns either the jotter root
    directory as string or None.
    """
    ds = os.getcwd().split('/')
    while ds:
        if os.path.isdir('/'.join(ds + ['.jotter'])):
            return '/'.join(ds)
        ds.pop()
def cd_to_root(root: str=0):
    """
    Change the directory to the jotter root directory,
    respecting the --root option if it is specified in
    argv. Note that this function modifies sys.argv by
    removing the root option if it is found and processed.
    Also note that this function calls exit(1) if the root
    directory is not found.

    The optional keyword argument 'root' can be used to
    pass a value obtained from previous argument parsing.
    If this argument is set to any string or to None, this
    function will not mess with sys.argv. If 'root' is set
    to the integer 0 (the default value), this function will
    try to extract the '--root' flag from sys.argv itself,
    removing the flag and its argument from sys.argv if it
    is found.
    """
    if root == 0:
        try:
            root = _getrootflag(sys.argv)
        except IndexError:
            print('The --root option is missing its value', file=sys.stderr)
            exit(1)
    if root == None: root = _findrootdir()
    if root == None:
        print('Unable to locate jotter root dir', file=sys.stderr)
        exit(1)
    os.chdir(root)
