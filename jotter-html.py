#!/usr/bin/env python3
"""Usage jotter-html [options]

Generate or update a static website in `.jotter/static`

Options:
    -c  --clean     Remove old html files and start conversion
                    from scratch. The default behaviour is to
                    only update files that have been changed
                    since the last conversion.
    -h  --help      Print this help message and exit.
"""

import sys
import os
import shutil
import re
import pypandoc
import warnings
import bs4
from jotter import find_jotter_root, survey


def clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)

def create_index(filename_map, citekey_map, keyword_map):
    """
    Return:     A string containing markdown content that is
                ready to be converted to html by pandoc.
    """
    index = list()
    note_types = list(set(map(lambda doc: doc["type"], filename_map.values())))
    note_types.sort()
    for t in note_types:
        if t in ["excerpt", "bibtex"]:
            continue
        index.append("\n\n\n# {}\n\n\n".format(t.capitalize()))
        l = list()
        for doc in filter(lambda doc: doc["type"] == t, filename_map.values()):
            l.append("- [{}]({})\n".format(doc["title"], doc["_html_filename"]))
        l.sort(key=lambda x: x.lower())
        index.extend(l)
    excerpt = list(); bibtex = list()
    for citekey, doc in citekey_map.items():
        if doc["type"] == "excerpt":
            excerpt.append("- [{}]({})\n".format(
                                    citekey, doc["_html_filename"]))
        elif doc["type"] == "bibtex":
            bibtex.append("- [{}]({})\n".format(
                                    citekey, doc["_html_filename"]))
    excerpt.sort(key=lambda x: x.lower())
    index.append("\n\n\n# Excerpt\n\n\n")
    index.extend(excerpt)
    index.append("\n\n\n# Bibtex\n\n\n")
    index.extend(bibtex)
    index.append("\n\n\n# Files\n\n\n")
    l = list()
    for doc in filename_map.values():
        l.append("- [{}]({})\n".format(
            doc["_filename"],
            doc["_html_filename"],
        ))
    l.sort(key=lambda x: x.lower())
    index.extend(l)
    index.append("\n\n\n# Keywords\n\n\n")
    keywords = list(keyword_map.keys())
    keywords.sort(key=lambda x: x.lower())
    for k in keywords:
        index.append("- {}\n".format(k))
        keyword_map[k].sort(key=lambda doc: doc["title"].lower())
        index.extend(map(
            lambda doc: "    - [{}]({})\n".format(
                doc["title"],
                doc["_html_filename"]
            ),
            keyword_map[k]
        ))
    return "".join(index)

def produce_html(doc, html_root, citekey_map=None, internal_links=False):
    pandoc_args = ["-s"]

    # Override certain keys that may be autogenerated by jotter-html
    # if not explicitly specified
    override_keys = [
        "title",
    ]
    for key in override_keys:
        if key in doc.keys():
            pandoc_args.append("--metadata={}:{}".format(key, doc[key]))

    outputfile = os.path.join(html_root, doc["_html_filename"])
    if "_content" in doc.keys():
        content = doc["_content"]
    else:
        with open(doc["_full_filename"]) as f:
            content = f.read()

    html = pypandoc.convert_text(
        source=doc["_content"],
        format="markdown",
        to="html",
        extra_args=pandoc_args,
    )
    # Make all links _blank before jotter_citeproc adds internal links
    if not internal_links:
        html = html.replace('<a href=', '<a target="_blank" href=')
    # Link citekeys to corresponding documents
    if citekey_map != None:
        html = jotter_citeproc(html, doc=doc, citekey_map=citekey_map)

    with open(outputfile, "w") as f:
        f.write(html)

def jotter_citeproc(html: str, doc: dict, citekey_map: dict) -> str:
    label_regex = r'(sec|fig|tbl|lst|eq):[\w:-]+'
    unk = set()
    def report_unk():
        if unk:
            print(
                "Unknown citekeys in {}".format(doc["_filename"]),
                file=sys.stderr
            )
            for key in unk:
                print("  - {}".format(key), file=sys.stderr)

    def link_key(key, target):
        return r'<a href="{}">{}</a>'.format(target, key)

    def link_postfix(postfix, target):
        return re.sub(
            "({})".format(label_regex),
            r'<a href="{}#\1">\1</a>'.format(target),
            postfix,
        )

    def link(key, postfix):
            if not key:
                return postfix
            elif re.match('^'+label_regex, key):
                key = link_key(key, "#"+key)
            elif key == "this" or citekey_map.get(key) == doc:
                postfix = link_postfix(postfix, "")
            elif key == "unknown":
                pass
            elif key in citekey_map.keys():
                target = citekey_map[key]["_html_filename"]
                key = link_key(key, target)
                postfix = link_postfix(postfix, target)
            else:
                unk.add(key)
            return key+postfix

    def parse(html):
        with warnings.catch_warnings():
            warnings.filterwarnings(category=UserWarning, action='ignore')
            return bs4.BeautifulSoup(html)

    html = parse(html)
    for citation in html.find_all(attrs={"class": "citation"}):
        text = citation.get_text()
        content = list()
        oldkey = ""
        for key in citation.get("data-cites").split():
            prefix, text = text.split(key, 1)
            content.append(link(oldkey, prefix))
            oldkey = key
        content.append(link(oldkey, text))

        content = "".join(content).replace("--", "–")
        content = re.sub(r'@(<a href=.*?>)', r'\1@', content)
        citation.replace_with(parse(content))

    for sec in html.find_all(attrs={"id": re.compile(label_regex)}):
        sec.append(" {#"+sec.get("id")+"}")

    report_unk()
    return str(html)


if __name__ == "__main__":
    jotter_root = find_jotter_root()
    html_root = os.path.join(jotter_root, ".jotter", "static")
    if len(sys.argv) > 1:
        if "-h" in sys.argv or "--help" in sys.argv:
            print(__doc__); exit(0)
        elif "-c" in sys.argv or "--clean" in sys.argv:
            clean_dir(html_root)

    filename_map, citekey_map, keyword_map = survey(jotter_root)

    print("\rCreating index ...\r", end="")
    index = {
        "_content": create_index(filename_map, citekey_map, keyword_map),
        "_html_filename": "index.html",
        "title": "Jotter Index",
    }
    produce_html(index, html_root, internal_links=True)

    def needs_update(doc, html_root=html_root):
        html_filename = os.path.join(html_root, doc["_html_filename"])
        if not os.path.isfile(html_filename):
            return True
        md_time = os.path.getmtime(doc["_full_filename"])
        html_time = os.path.getmtime(html_filename)
        if md_time > html_time:
            return True
        return False

    for filename, doc in filename_map.items():
        shorthand = filename
        if len(shorthand) > 43:
            shorthand = shorthand[:6] + ".." + shorthand[-35:]
        fill = (43-len(shorthand)) * " "
        print(
            "\rConverting {} ...{}\r".format(shorthand, fill),
            end=""
        )
        if needs_update(doc, html_root=html_root):
            produce_html(doc, html_root, citekey_map=citekey_map)

    print("\rSuccessfully created static version in {}".format(html_root))
