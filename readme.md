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
