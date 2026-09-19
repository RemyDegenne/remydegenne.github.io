# Updating the site

The publication list (index.html) and the news lists (index.html and
older_news.html) are generated from the JSON files in `data/`:

| file | holds |
| --- | --- |
| `data/publications.json` | the papers, newest first |
| `data/news.json`         | news entries: `recent` (index.html) and `older` (older_news.html) |
| `data/people.json`       | each coauthor's homepage, written once and reused everywhere |

After editing any of them, run:

    python3 build_site.py

This rewrites the blocks between the `<!-- PUBLICATIONS:START -->`,
`<!-- NEWS:START -->` and `<!-- OLDER_NEWS:START -->` marker comments.
Everything outside those markers is hand-written HTML and is left alone.
`python3 build_site.py --check` reports whether the pages are out of date
without changing anything.

## Adding a paper

```json
{
  "title": "...",
  "url": "https://arxiv.org/abs/...",
  "venue": "NeurIPS 2027",
  "authors": ["RD", "Some Coauthor"]
}
```

A name in `authors` becomes a link if it appears in `people.json`, and plain
text otherwise — so a coauthor's URL is only ever written in one place.
Optionally add `"links": [{"label": "[HTML Version]", "url": "..."}]` for extra
links shown after the venue.

## Adding a news entry

```json
{ "date": "March 2027", "text": "I am doing a thing with {{Some Person}}." }
```

In `text`: `{{Name}}` links to that person's homepage from `people.json`,
`[label](url)` is an ordinary link, and `**text**` is bold. To archive an entry,
move it from `recent` to `older`.
