# Jotter

Jotter is a simple wiki system based on markdown files. It is still
in very early stages of development and, as of now, only consists of a
few shell commands which provide some basic functionality. An upcoming
addition will be a static site generator, which will export the whole
wiki as a static html5/css3 (no javascript) website to be served by the
server of your choice.

## Dependencies

- POSIX-compliant shell scripting environment
- [pandoc](https://pandoc.org)
- [fd-find](https://github.com/sharkdp/fd)
- [pyyaml](https://pyyaml.org) for `jotter-html`
- [pypandoc](https://github.com/bebraw/pypandoc) for `jotter-html`

## Installing

Simply include the scripts in your `PATH` and mark them as executable,
make sure all dependencies are satisfied and you're good to go.

## Usage

A jotter is essentially just a collection of markdown files placed in a
common directory and subdirectories. You can use any text editor to write
these files. Just make sure you specify `.md` as the filename extension,
since jotter ignores any files with different extensions. Since jotter
uses `fd` to locate files, it will also respect any `.gitignore`,
`.ignore` and `.fdignore` files that might be present in the directory
structure.

For markdown syntax, pandoc-markdown is used. This dialect allows to
include blocks of yaml-metadata in markdown files as such:

```
---
author: John Doe
title: My first jotter entry
---

What follows after the metadata block is basically *simple markdown*.
```

These metadata blocks are the basis for jotter's functionality. Currently,
jotter handles two variables which can be specified in such yaml-blocks:
`keywords` and `bibtex`.

### Keywords

You can specify lists of keywords to describe the content of markdown
files. The syntax is as follows:

```
---
keywords:
  - free software
  - commandline
  - personal wiki
---
```

These keywords can be searched or listed using the `jotter-keyword`
command described below.

### Bibtex

You can also specify bibliographic information associated with an
entry. This is mainly useful for academic note-taking. If you use a
single file for taking notes on some paper, you can specify the bibtex
entry right inside the yaml-block rather than relying on separate bibtex
files. Bibtex entries from the whole jotter can be extracted and combined
at any time using the `jotter-bib` command. The syntax is as follows:

```
---
bibtex: |
    @article{sustainable-authorship,
        author="Dennis Tenen and Grant Wythoff",
        title="Sustainable Authorship in Plain Text using Pandoc and Markdown",
        journal="The Programming Historian",
        volume="3",
        year="2014",
    }
---
```

Additionally, you can also include plain bibtex files in your jotter,
using `.bib` as the filename extension. `jotter-bib` will combine all
entries found in these plain bibtex files with the ones specified in
metadata blocks.

This functionality can come in handy when including bibliographic
information that is not directly associated with any note. If you use
both *collection* and *incollection* entries, for instance, you may wish
to take notes for the individual *incollection* entries while there
might not no need write any notes on the entire collection. If this
is the case, you could simply specify the bibliographic information of
the *collection* using a plain bibtex file, which would be considered
whenever jotter extracts bibliographic information, but which would not
show up in your notes.

## Commands

jotter
: This is just a wrapper around the other scripts, which allows to run
`jotter-something` as `jotter something`, inspired by jupyter and git.

jotter-init
: Create a new jotter. Running this command is required before using any
other commands. It is perfectly ok, however, to start writing markdown
files before running `jotter-init`.

jotter-bib
: Extract bibtex entries from all markdown files in the jotter and combine
them in a single file.

jotter-keyword
: Interact with keywords specified throughout the wiki.
See `jotter-keyword -h` for further information.

jotter-html
: Produce a static website of this jotter in the `.jotter` directory.


## Limitations

- All content files must contain an `.md`-Extension. Files with different
  extensions will be ignored.
- Keys in yaml-blocks must not start with an underscore (`_`).
  Keywords starting with an underscore are reserved for internal use
  by `jotter-html` and their use may therefore produce unpredictable
  results.
- `jotter-html` currently produces a flat directory structure in
  `.jotter/static/`. This makes linking files together way easier.
  It also means that filenames have to be changed so they don't include
  directory separators. This is accomplished in a way similar to the one
  used in python libraries, by using `.` as a separator substitute. As a
  consequence, the files `a/b` and `a.b` look the same to `jotter-html`.
  As of now, it is the user's responsibility to avoid such naming
  conflicts.
- Some filenames are furthermore reserved for use by `jotter-html`:
    - index
- The following citekeys have special meanings for jotter:
    - `@this`: Refers to the reference specified in the `bibtex` metadata
      entry in the same file. `@this` must not be used if the `bibtex`
      entry contains more than one reference. (You can still use the
      citekey of a specific entry you want to refer to in this case.)
      One exception to this rule are `bibtex` entries containing both
      a `collection` and one `incollection` entry, for which `@this`
      is interpreted to refer to the `incollection` entry.
    - `@unknown`: Refers to a reference that has not been added to the
      jotter yet, but will be added in the future. This citekey is
      currently mostly reserved for future use and thus simply ignored
      at the moment.
