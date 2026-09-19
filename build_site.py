#!/usr/bin/env python3
"""Generate the publication and news lists from the JSON files in data/.

Usage:
    python3 build_site.py            rewrite the generated blocks in place
    python3 build_site.py --check    report whether anything is out of date
                                     (exit code 1 if it is), change nothing

The generated blocks live between <!-- NAME:START --> and <!-- NAME:END -->
comments in index.html and older_news.html. Everything outside those markers is
left untouched, so the rest of the pages stays ordinary hand-written HTML.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

TAB = "\t"


# --- loading ---------------------------------------------------------------


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        return json.load(f)


class BuildError(Exception):
    """A problem in the data files, reported without a traceback."""


# --- inline markup ---------------------------------------------------------

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PERSON_RE = re.compile(r"\{\{([^}]+)\}\}")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def esc(text):
    """Escape for text content: quotes are fine as-is there."""
    return html.escape(text, quote=False)


def attr(url):
    """Escape for an href. A literal quote would break out of the attribute."""
    if '"' in url:
        raise BuildError("URL contains a quote character: {}".format(url))
    return html.escape(url, quote=False)


def link(url, label):
    return '<a href="{}">{}</a>'.format(url, label)


def person(name, people, used):
    """Render an author/person name, linked if we know their homepage."""
    name = name.strip()
    if name in people:
        used.add(name)
        return link(attr(people[name]), esc(name))
    return esc(name)


def inline(text, people, used, where):
    """Expand {{Name}}, [label](url) and **bold** in a news entry."""
    # Escape first so that any & < > in the prose is safe; the markup below is
    # then inserted as real HTML. URLs written in the source get their & turned
    # into &amp;, which is what an href needs anyway.
    out = esc(text)

    def person_sub(m):
        name = m.group(1).strip()
        if name not in people:
            raise BuildError(
                "{}: {{{{{}}}}} is not in people.json "
                "(add them there, or write the name as plain text)".format(where, name)
            )
        return person(name, people, used)

    out = PERSON_RE.sub(person_sub, out)
    out = LINK_RE.sub(lambda m: link(attr(m.group(2)), m.group(1)), out)
    out = BOLD_RE.sub(lambda m: "<b>{}</b>".format(m.group(1)), out)

    for leftover in ("{{", "}}"):
        if leftover in out:
            raise BuildError("{}: unbalanced '{}' in the text".format(where, leftover))
    return out


# --- rendering -------------------------------------------------------------


def render_publications(publications, people, used, indent):
    lines = []
    for i, pub in enumerate(publications):
        where = "publication {} ({})".format(i + 1, pub.get("title", "untitled"))
        for field in ("title", "url", "venue", "authors"):
            if not pub.get(field):
                raise BuildError("{}: missing '{}'".format(where, field))

        title = link(attr(pub["url"]), esc(pub["title"]))
        head = "<b>{}</b>, {}".format(title, esc(pub["venue"]))

        extra = pub.get("links") or []
        if extra:
            # The venue is followed by a full stop before any extra link.
            head += ". " + " ".join(
                link(attr(l["url"]), esc(l["label"]))
                for l in extra
            )

        authors = ", ".join(person(a, people, used) for a in pub["authors"])

        lines.append("{}<li>{}</br>".format(indent, head))
        lines.append("{}{}{}.</li>".format(indent, TAB, authors))
    return lines


def render_news(entries, people, used, indent, listname):
    lines = []
    for i, entry in enumerate(entries):
        where = "{} news entry {} ([{}])".format(listname, i + 1, entry.get("date", "?"))
        for field in ("date", "text"):
            if not entry.get(field):
                raise BuildError("{}: missing '{}'".format(where, field))

        lines.append("{}<p>".format(indent))
        lines.append(
            '{}{}<span class="news-date">[{}]</span> {}'.format(
                indent, TAB, esc(entry["date"]), inline(entry["text"], people, used, where)
            )
        )
        lines.append("{}</p>".format(indent))
    return lines


def render_collaborators(groups, people, used, indent):
    lines = []
    for i, group in enumerate(groups):
        label = group.get("label")
        members = group.get("members") or []
        if not label:
            raise BuildError("collaborator group {}: missing 'label'".format(i + 1))

        lines.append('{}<p class="group-label">{}</p>'.format(indent, esc(label)))
        lines.append("{}<ul>".format(indent))
        for j, member in enumerate(members):
            where = "{} entry {} ({})".format(label, j + 1, member.get("name", "unnamed"))
            if not member.get("name"):
                raise BuildError("{}: missing 'name'".format(where))

            item = "<b>{}</b>".format(person(member["name"], people, used))
            note = (member.get("note") or "").strip()
            if note:
                note = inline(note, people, used, where)
                # One separator and one full stop for every entry, whatever the
                # note happens to start or end with.
                item += ", " + note + ("" if note.endswith(".") else ".")
            lines.append("{}{}<li>{}</li>".format(indent, TAB, item))
        lines.append("{}</ul>".format(indent))
    return lines


# --- splicing into the pages ----------------------------------------------


def splice(text, name, body_lines, path):
    """Replace the lines between <!-- name:START --> and <!-- name:END -->."""
    start = re.search(r"^([ \t]*)<!-- {}:START[^>]*-->[ \t]*$".format(name), text, re.M)
    end = re.search(r"^([ \t]*)<!-- {}:END -->[ \t]*$".format(name), text, re.M)
    if not start or not end:
        raise BuildError("{}: could not find the {} markers".format(path.name, name))
    if end.start() < start.end():
        raise BuildError("{}: {}:END comes before {}:START".format(path.name, name, name))

    body = "\n".join(body_lines)
    return text[: start.end()] + "\n" + body + "\n" + text[end.start() :]


def indent_of(text, name):
    """The indentation of the START marker, used for the generated lines."""
    m = re.search(r"^([ \t]*)<!-- {}:START".format(name), text, re.M)
    return m.group(1) if m else TAB * 9


# --- main ------------------------------------------------------------------


def build(check_only=False):
    people = {k: v for k, v in load("people.json").items() if not k.startswith("_")}
    pubs_data = load("publications.json")
    news_data = load("news.json")
    collab_data = load("collaborators.json")

    publications = pubs_data["publications"]
    used = set()

    index_path = ROOT / "index.html"
    older_path = ROOT / "older_news.html"

    index = original_index = index_path.read_text(encoding="utf-8")
    older = original_older = older_path.read_text(encoding="utf-8")

    index = splice(
        index,
        "PUBLICATIONS",
        render_publications(publications, people, used, indent_of(index, "PUBLICATIONS")),
        index_path,
    )
    index = splice(
        index,
        "NEWS",
        render_news(news_data["recent"], people, used, indent_of(index, "NEWS"), "recent"),
        index_path,
    )
    index = splice(
        index,
        "COLLABORATORS",
        render_collaborators(
            collab_data["groups"], people, used, indent_of(index, "COLLABORATORS")
        ),
        index_path,
    )
    older = splice(
        older,
        "OLDER_NEWS",
        render_news(news_data["older"], people, used, indent_of(older, "OLDER_NEWS"), "older"),
        older_path,
    )

    # A name that is in people.json but never referenced is usually a typo on
    # one side or the other, so it is worth saying out loud.
    unused = sorted(set(people) - used)
    if unused:
        print("note: in people.json but never used: " + ", ".join(unused))

    changed = []
    for path, before, after in (
        (index_path, original_index, index),
        (older_path, original_older, older),
    ):
        if before != after:
            changed.append(path.name)
            if not check_only:
                path.write_text(after, encoding="utf-8")

    if check_only:
        if changed:
            print("out of date: " + ", ".join(changed) + " (run: python3 build_site.py)")
            return 1
        print("up to date")
        return 0

    print(
        "{} publications, {} news entries, {} collaborators, {} people -> {}".format(
            len(publications),
            len(news_data["recent"]) + len(news_data["older"]),
            sum(len(g.get("members") or []) for g in collab_data["groups"]),
            len(people),
            ", ".join(changed) if changed else "no change",
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(build(check_only="--check" in sys.argv[1:]))
    except BuildError as e:
        sys.exit("error: {}".format(e))
