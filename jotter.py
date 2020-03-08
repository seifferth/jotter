#!/usr/bin/env python3

import sys
import os
import yaml
import re


def find_jotter_root(rel_filename: bool=False):
    """
    The return type of this function varies.

    If rel_filename == False (default): Return absolute path to jotter
    root (str)

    If rel_filename == True: Return a tuple (path, rel_filename), where
    path is the absolute path to jotter root and rel_filename is an
    anonymous function (str -> str) that can be used to convert filenames
    that are relative to jotter root into ones that are relative to the
    current working directory.

    Usage example for the rel_filename function
    ===========================================

    Suppose we have a jotter that looks something like this:

        in_root.md
        dir/
        dir/in_dir.md
        dir/subdir/
        dir/subdir/in_subdir.md

    If "dir/subdir" is the current working directory in the jotter,
    `rel_filename` will produce the following filename conversions:

        > print("dir/subdir/in_subdir.md")
        dir/subdir/in_subdir.md
        > print(rel_filename("dir/subdir/in_subdir.md"))
        in_subdir.md

        > print("dir/in_dir.md")
        dir/in_dir.md
        > print(rel_filename("dir/in_dir.md"))
        ../in_dir.md

        > print("in_root.md")
        in_root.md
        > print(rel_filename("in_root.md"))
        ../../in_root.md
    """
    ### Start confusing code ###
    #
    # This is the code that produces the rel_filename function
    # described in the docstring. If this looks like black magic
    # to you, just skip over this part and continue reading after
    # "End confusing code".
    #
    def def_rel_filename(subdirs):
        def rel_filename(path: str) -> str:
            depth = len(subdirs)
            for lead in subdirs:
                lead = lead+os.sep
                if path.startswith(lead):
                    path = path[len(lead):]
                    depth -= 1
                else:
                    break
            return depth*"../"+path
        return rel_filename
    ### End confusing code ###

    path = os.getcwd()
    subdirs = list()
    while path != "/":
        if os.path.isdir(os.path.join(path, ".jotter")):
            if rel_filename:
                return (path, def_rel_filename(subdirs))
            else:
                return path
        else:
            path, tmp = os.path.split(path)
            subdirs.insert(0, tmp)
    raise Exception(
        "No jotter root found. Run jotter-init to create a new jotter."
    )

def warn(msg, files):
    """
    msg:    Message to be displayed on stdout (string)
    files:  Files affected (either string or list of strings)
    """
    print(msg, file=sys.stderr)
    if type(files) == str:
        files = [files]
    for filename in files:
        print("    " + filename, file=sys.stderr)

def survey(jotter_root: str, full_content: bool=True):
    """
    Find the markdown files in this jotter and obtain some information
    about them.

    Parameters:
      - jotter_root:    The root directory of the jotter to process
      - full_content:   Whether to include a "_content" field in the
                        dict representing the document to store the
                        full content of the file. (default: True)

    Return value: (filename_map, citekey_map, keyword_map)

    All of these return values are dicts, exposing the same document
    specific metadata. The only difference is how these metadata are
    accessed. filename_map uses shortened filenames as keys, citekey_map
    uses citekeys as keys and keyword_map contains a list with entries
    for each keyword. Note that the underlying dicts are mutable data
    structures, so all three maps actually point to the same objects
    in memory.

    Usage example: Suppose we have a file located at "myfolder/myfile.md"
    in the jotter, which contains the bibtex citekeys "key1" and "key2"
    and is associated with the keywords "markdown" and "html". The
    following lookups will lead directly to the dict representing
    this file:

        filename_map["myfolder/myfile.md"]
        citekey_map["key1"]
        citekey_map["key2"]

    Furthermore, looking up either

        keyword_map["markdown"]

    or

        keyword_map["html"]

    will produce lists that also contain the same dict --- possibly
    among other dicts associated with those keywods.

    The full input and output filenames are saved inside the dict
    representing the file. To get this information, you could use
    something like this:

        infile = filename_map["myfolder/myfile.md"]["_full_filename"]
        outfile = filename_map["myfolder/myfile.md"]["_html_filename"]

    Note that both citekey_map and keyword_map may contain multiple keys
    leading to the same file. If you want to iterate over all files in
    the jotter, the best approach is to use either filename_map.values()
    or filename_map.items().
    """
    def get_files(path):
        for d, _, fs in os.walk(path):
            if d.endswith(".jotter"):
                continue
            for f in fs:
                if f.endswith(".md") or f.endswith(".bib"):
                    yield os.path.join(d, f)

    def extract_yaml(content: str) -> dict:
        regex = r'\n\n---+\n' + \
                r'([ \t]*(\S(.|\n)*?\S|\S)[ \t]*\n)' + \
                r'(---+|\.\.\.+)\n\n'
        parts = map(
            lambda x: x[0],
            re.findall(regex, "\n\n"+content+"\n\n")
        )
        return yaml.safe_load("\n\n".join(parts)) or dict()

    def enrich_metadata(doc: dict) -> None:
        """
        Note that the document dict is updated in-place.
        """
        if "bibtex" in doc.keys():
            if doc.get("type") != "bibtex":
                doc["type"] = "excerpt"
            entries = re.findall(
                r'@(.*?)\{(.*?),',
                doc["bibtex"]
            )
            doc["_citekeys"] = list(map(lambda x: x[1], entries))
            if len(doc["_citekeys"]) == 1: doc["_this"] = doc["_citekeys"][0]
            if "id" in doc.keys():
                ids = doc["id"]
                if type(ids) != list:
                    ids = [ids]
                doc["_citekeys"].extend(ids)
        else:
            if "type" not in doc.keys():
                doc["type"] = "note"
            if "id" in doc.keys():
                ids = doc["id"]
            else:
                ids = "{}:{}".format(
                    doc["type"],
                    doc["_short_filename"][:-3]
                )
            if type(ids) != list:
                ids = [ids]
            doc["_citekeys"] = ids
        if "title" not in doc.keys():
            if "_this" in doc.keys():
                doc["title"] = doc["_this"]
            else:
                doc["title"] = doc["_short_filename"]

    def parse_doc(filename, jotter_root="", full_content=True) -> dict:
        with open(filename) as f:
            content = f.read()
        if filename.endswith(".md"):
            doc = extract_yaml(content)
            if full_content == True:
                doc["_content"] = content
        elif filename.endswith(".bib"):
            doc = {
                "type": "bibtex",
                "bibtex": content,
            }
            if full_content == True:
                doc["_content"] = ""
        doc["_filename"] = re.sub(
            r'^{}{}?'.format(jotter_root, os.sep), '', filename
        )
        doc["_short_filename"] = os.path.split(filename)[1]
        doc["_full_filename"] = filename
        doc["_html_filename"] = doc["_filename"].replace(os.sep, ".")+".html"
        enrich_metadata(doc)
        return doc

    files = list(get_files(jotter_root))
    filename_map = dict()
    citekey_map = dict()
    keyword_map = dict()
    for filename in files:
        doc = parse_doc(
            filename,
            jotter_root=jotter_root,
            full_content=full_content
        )
        filename_map[doc["_filename"]] = doc
        if "_citekeys" in doc.keys():
            for key in doc["_citekeys"]:
                if key in citekey_map.keys():
                    warn(
                        "Duplicate citekey \"{}\"".format(key),
                        [citekey_map[key]["_filename"], doc["_filename"]]
                    )
                citekey_map[key] = doc
        if "keywords" in doc.keys():
            try:
                for keyword in doc["keywords"]:
                    if keyword not in keyword_map.keys():
                        keyword_map[keyword] = list()
                    keyword_map[keyword].append(doc)
            except:
                warn("Could not process keywords in file:", meta["_filename"])
    return (filename_map, citekey_map, keyword_map)
