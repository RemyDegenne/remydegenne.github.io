# The site

Static HTML on GitHub Pages. No build system, no framework: one stylesheet
(`assets/css/site.css`), one small script (`assets/js/site.js`, a scroll-spy for
the nav), and a Python script that renders the publication and news lists from
JSON.

## Content in `data/`

| file | holds |
| --- | --- |
| `data/publications.json`  | the papers, newest first |
| `data/news.json`          | news entries: `recent` (index.html) and `older` (older_news.html) |
| `data/collaborators.json` | the students and post-docs, in groups |
| `data/people.json`        | everyone's homepage, written once and reused everywhere |

After editing any of them, run:

    python3 build_site.py

This rewrites the blocks between the `<!-- PUBLICATIONS:START -->`,
`<!-- NEWS:START -->`, `<!-- COLLABORATORS:START -->` and
`<!-- OLDER_NEWS:START -->` marker comments.
Everything outside those markers is hand-written HTML and is left alone.
`python3 build_site.py --check` reports whether the pages are out of date
without changing anything.

### Adding a paper

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

### Adding a collaborator

```json
{ "name": "Some Student", "note": "co-advised with {{Emilie Kaufmann}}, since October 2027" }
```

Inside the group you want, under `groups`. The name is linked from
`people.json` like an author, and the note takes the same `{{Name}}`,
`[label](url)` and `**bold**` markup as a news entry. The generator adds the
separating comma and the closing full stop, so leave those out.

### Adding a news entry

```json
{ "date": "March 2027", "text": "I am doing a thing with {{Some Person}}." }
```

In `text`: `{{Name}}` links to that person's homepage from `people.json`,
`[label](url)` is an ordinary link, and `**text**` is bold. To archive an entry,
move it from `recent` to `older`.

## The look

Every page shares the same shell: a `.masthead`, a sticky `.topnav`, a
`<main id="content">` and a `.site-footer`. Page content lives in
`<section id="...">` blocks, as before.

Colours, fonts and the page width are CSS custom properties at the top of
`assets/css/site.css`:

```css
--ink      /* body text        */   --accent  /* links, section marks */
--bg       /* page background  */   --muted   /* secondary text       */
--surface  /* code blocks etc. */   --rule    /* hairlines            */
--wrap     /* reading measure  */
```

Change them in the `:root` block and the whole site follows. Dark mode is the
same set of properties redefined under `prefers-color-scheme: dark`, so a new
colour needs setting in both places.

Typefaces are Source Serif 4 (headings) and Inter (body), loaded from Google
Fonts in each page's `<head>`. To drop the external request, delete those two
`<link>` tags and adjust `--serif` / `--sans`.

## Adding a page

Copy the shell of an existing subpage — for example `older_news.html` — change
the `<title>`, the `<h1 class="masthead-name">`, and the content inside
`<main>`. Pages that show mathematics also load MathJax; see
`Lean_projects.html`.
