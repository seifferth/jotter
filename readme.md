# Jotter

Jotter is a simple wiki system based on markdown files. It provides a
few command line tools to facilitate working with research notes written
in plain markdown. It aims to introduce some of the amenities you may be
used to from programming into the process of scholarly writing.

A jotter is essentially just a collection of markdown files placed in a
common directory and subdirectories. You can use any text editor to write
these files. Just make sure you specify `.md` as the filename extension,
since jotter ignores any files with different extensions.

## Dependencies

- POSIX-compliant shell scripting environment
- [fd-find](https://github.com/sharkdp/fd)
- python3 (for jotter-ls and jotter-rev)

## Installing

As of now, the functionality is split across several shell scripts. For
installing the shell scripts, it is enough to include them in your `PATH`
and to mark them as executable.

## Usage: Metadata

For markdown syntax, Pandoc Markdown is used. This dialect allows to
include blocks of yaml-metadata in markdown files as such:

```
---
author: John Doe
title: My first jotter entry
---

What follows after the metadata block is basically *simple markdown*.
```

These metadata blocks are the basis for jotter's functionality. Currently,
jotter handles the following variables which can be specified in such
yaml-blocks:

- keywords
- bibtex

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
command described below. If jotter encounters more than one list of
keywords, it computes the union of all keywords found in any of the
lists.

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

Note that you can use any number of metadata blocks per file, any number
fo "bibtex" fields per metadata block and any number of bibliographic
entries per "bibtex" field. This way, notes from different files can be
concatenated, split and moved around easily.

## Usage: Linking notes together

Jotter supports the notion of *citekeys*, known from academic markup
languages such as LaTeX and Pandoc Markdown. Citekeys are commonly used
as shorthands for bibliographic references that would be expanded when
producing the final version of some document. (The citekey of the bibtex
example given above, for instance, is `sustainable-authorship`.) Jotter
provides a way of generating a ctags-like tags file by running
`jotter-tags`. This file will include an index of all citekeys defined
within bibliographic entries and the files they were defined in. If you
use a ctags-capable text editor, you should be able to use some keyboard
shortcut (e. g. `C-]` in vi-like editors) to jump to that definition.
Note that there might be a mismatch between your text editor's identifier
detection and the symbols you use in citekeys.

Should jotter ever regain the ability to export a bunch of markdown
files in some other format (html or pdf, for instance), support for
linking citekeys is planned.

## Commands

jotter
: This is just a wrapper around the other scripts, which allows to run
`jotter-something` as `jotter something`, inspired by jupyter and git.

jotter-bib
: Extract bibtex entries from all markdown files in the jotter and combine
them in a single file.

jotter-keyword
: Interact with keywords specified throughout the wiki.
See `jotter-keyword -h` for further information.

jotter-tags
: Create a `tags` file in the current working directory. This file is meant
to allow users to easily follow internal links between files using their
text editors. Text editors still need to handle this file correctly,
of course. The `tags` file will include tags for both bibtex entries and
[pandoc-crossref] style section, figure, table and equation labels.

[pandoc-crossref]: http://lierdakil.github.io/pandoc-crossref/

jotter-status
: Show some general information about this jotter, such as the number of
files, words, etc.

jotter-ls
: Print a list of citekeys found in this jotter to stdout. This list can
optionally be filtered by specifying glob expressions.

jotter-rev
: Perform reverse citekey lookups. That is, print a list of all notes
that reference a certain key.

## Limitations

- All content files must contain an `.md`-Extension. Files with different
  extensions will be ignored.

## Known bugs

- Metedata extraction does not account for html comments. Metadata
  extraction could thus be broken by crafting (or inadvertently writing)
  comments which contain content that looks like the beginning of a
  metadata block.

## License

All files in this repository are made available under the terms of the
GNU General Purpose License, version 3 or later. A copy of that license
is included in the repository as `license.txt`.
