# Jotter

Jotter is a simple wiki system based on markdown files. It provides both
a static site generator that can render the content of these markdown
files as interlinked html pages and a few command line tools which
facilitate working with keywords and bibliographic information. As this
project is still in very early stages of development, the specifications
outlined below may be subject to change. Since I am already using these
scripts on a personal project, however, such changes are likely to be
backward-compatible at least to some degree.

A jotter is essentially just a collection of markdown files placed in a
common directory and subdirectories. You can use any text editor to write
these files. Just make sure you specify `.md` as the filename extension,
since jotter ignores any files with different extensions. Additionally,
a jotter may also contain plain bibtex files --- using `.bib` as the
filename extension ---, which contain bibliographic information (see
further explanation below).

## Dependencies

- POSIX-compliant shell scripting environment
- Python 3
- [pandoc](https://pandoc.org)
- [fd-find](https://github.com/sharkdp/fd)
- [pyyaml](https://pyyaml.org)
- [pypandoc](https://github.com/bebraw/pypandoc) for `jotter-html`
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
  for `jotter-html`

## Installing

As of now, the functionality is split across both shell and python
scripts. For installing the shell scripts, it is enough to include them in
your `PATH` and to mark them as executable. The python scripts, however,
share some functionality provided by `jotter.py`.  That library needs
to be available under that name in the same directory the scripts are
located in. The suggested way of installing the python parts is to simply
link to them from a directory included in `PATH`, ideally removing the
`.py`-extension from the link's name:

```bash
ln -s /path/to/jotter/jotter-keyword.py /path/to/bin/jotter-keyword
ln -s /path/to/jotter/jotter-html.py /path/to/bin/jotter-html
```

Also make sure that all the dependencies are satisfied to avoid runtime
errors.

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

- type
- title
- keywords
- bibtex

### Type

`type` can be used to specify the type of note a certain markdown file
represents. For files that also contain a `bibtex` field, the type will
always be set to `excerpt`, ignoring any value specified by the user. For
any other files, `type` may be an arbitrary user-defined string. If it
isn't explicitly set, it will default to `note`.

This variable can be used to group notes together into categories. I
personally use an `author` type, for instance, to distinguish notes about
authors form notes about topics. The type of a note is important for
creating links between notes (see below). I may also decide to handle
notes of a certain type in some special way in the future, although I
don't have any concrete plans for this yet.

### Title

This one should be rather self-explanatory. It may be worth noting,
however, that `jotter-html` will try to infer the title if it isn't set,
falling back either on the file's citekey or on its filename.

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
metadata blocks. This functionality can come in handy when including
bibliographic information that is not directly associated with any
note. If you use both *collection* and *incollection* entries, for
instance, you may wish to take notes on the individual *incollection*
entries while there might not be any need to write a note on the
entire collection. If this is the case, you could simply specify the
bibliographic information of the *collection* using a plain bibtex
file, which would be considered whenever jotter extracts bibliographic
information, but which would not show up in your notes.

## Usage: Linking notes together

Besides converting markdown documents to html, the main feature of
`jotter-html` is that it will take care of creating links between the
resulting html pages. These links can then be used to navigate the
html-version of the jotter.

In addition to the usual way of creating links by pointing either to
online resources or to filenames --- which is already well supported by
most markdown processors and static site generators ---, jotter relies
on the notion of *citekeys*, known from academic markup languages such
as LaTeX and Pandoc Markdown. Citekeys are commonly used as shorthands
for bibliographic references that would be expanded when producing the
final version of some document. (The citekey of the bibtex example given
above, for instance, is `sustainable-authorship`.) Using these citekeys
as the basis for interlinking the individual files in a jotter takes the
process of writing a personal wiki closer to that of writing a college
report or a research paper and may thus feel more natural to some people
(including myself). It also allows the user to completely reorganise the
directory structure of the jotter without breaking the links between
pages --- a feature that I have found surprisingly valuable in my own
experiences with using these tools so far.

### Citekey assignment

In case of `excerpt`-type notes (i. e. notes containing a `bibtex`
field), jotter will automatically extract all citekeys found in that
note's `bibtex` field and use these as citekeys. For other notes, jotter
will use the note's `type`, a colon and the note's filename (stripping
off any leading directories as well as the `.md` extension) to generate
a citekey. A note with the filename `notes/authors/wythoff.md` and the
type `author`, for example, would have the citekey `author:wythoff`
assigned to it. A note with the filename `notes/tools/wiki-systems.md`
and no user-specified type would have the citekey `note:wiki-systems`.

### Using citekeys

Citekeys are used in exactly the same way as they are in Pandoc Markdown
(by prefacing them with `@`). Here's an example reusing some of the
citekeys from the examples above:

```
There are many tools one could use for academic writing. One of them is
a plain old text editor combined with a powerful markdown processor such
as pandoc. Indeed, it has been suggested by Dennis Tenen [@author:tenen]
and Grant Wythoff [@author:wythoff] that this is probably the most
sustainable way of doing one's academic writing [@sustainable-authorship].

There are also quite a lot of wiki systems out there, as described in
@note:wiki-systems. [Jotter](https://github.com/seifferth/jotter) is
but one of them.
```

As seen in the last paragraph above, the use of citekey-style links
and common hyperlinks can of course be combined. `jotter-html` will
even take care of adding `target="_blank"` to these common hyperlinks,
so that common hyperlinks are opened in a new tab while citekey-style
links are opened inside the same one.

Note: The difference between jotter's citation handling and tools such
as pandoc-citeproc is that `jotter-html` will add hyperlinks around
citekeys, rather than expanding them into references. While it would
be easily possible to also replace the citekeys themselves with some
expanded bibliographic information, I decided against it. Since I am
likely to copy these citekeys into other documents when I need to refer
to other works, I actually find it quite useful to see the shorthand
rather than the full-blown citation.

### Referring to specific sections

It is also possible to use citekey-style linking to refer to specific
sections within a note. This functionality reuses and slightly extends
the syntax proposed by [pandoc-crossref]. To refer to a section, figure,
table, equation or code listing within a note, the special citekey
prefixes `@sec:`, `@fig:`, `@tbl:`, `@eq:` and `@lst:` can be used. To
refer to a section labelled `#sec:further-reading` within the same file,
for instance, one would write something like this:

```
Also note the references referred to in @sec:further-reading.
```

[pandoc-crossref]: http://lierdakil.github.io/pandoc-crossref/

To refer to that section from a different file, the section label
can be added the same way one would add a page number for use with
pandoc-citeproc:

```
Also see the information on this point outlined in @note:wiki-systems
[sec:introduction, sec:further-reading].
```

As seen in the example above, it is also possible to use a single
citation to refer to multiple sections of a given note. In this example,
`jotter-html` would create a hyperlink to the specific note around
`@note:wiki-systems`, as well as different hyperlinks to subsections
around each of the sections mentioned.

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

jotter-ctags
: Create a `tags` file in the jotter's root directory. This file is meant
to allow users to easily follow internal links between files using their
text editors. Text editors still need to handle this file correctly,
of course.

jotter-status
: Show some general information about this jotter, such as the number of
files, words, etc. This command can also be used to check whether there
is a jotter in some parent directory (using `jotter-status -q`), similar
to how one might run `git status` to check if there is a repo somewhere.


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
    - `@unknown`: Refers to a reference that has not been added to the
      jotter yet, but will be added in the future. This citekey is
      currently mostly reserved for future use and thus simply ignored
      at the moment.

## Known bugs

- `jotter-bib` still uses some slightly flawed heuristics for locating
  metadata blocks in markdown files. Although I didn't test it, I
  would expect `jotter-bib` to produce faulty results (including broken
  bibtex syntax) if the string `\n\n---\n\n` is used as a horizontal
  rule anywhere in a markdown file. This bug should be automatically
  fixed once `jotter-bib` is rewritten in python.
- The metedata extraction function (`survey`) from `jotter.py` doesn't
  account for code blocks or html comments. Metadata extraction could thus
  be broken by crafting (or inadvertently writing) code blocks or comments
  which contain content that looks like the beginning of a metadata block.
