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
            if bibtex == 1 and not line.startswith('    '):
                bibtex = 0; continue
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
