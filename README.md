# arecipe treatise

The one-page treatise for **arecipe**, published at
[arecipe.croft.ing](https://arecipe.croft.ing). Part of the
[croft.ing](https://croft.ing) family of sites.

It is a field report arguing a single idea: that the slow decay of beloved
software is largely a design outcome, and that a different design makes
software structurally resistant to it. arecipe is the working example.

## Stance

- Plain HTML and one CSS file. No frameworks, no `package.json`, no build
  step, no JavaScript.
- Renders identically from `file://` and from any static server.
- Zero loaded external requests. Fonts are self-hosted; no CDNs, no analytics,
  no external images. Outbound clickable links only.
- AGPL-3.0. No cookies, no scripts, no tracking.

## Files

```
index.html            the treatise
styles.css            the single stylesheet (tectonic palette)
CNAME                 arecipe.croft.ing
assets/favicon.svg    a drystone-cairn mark
assets/fonts/         self-hosted Lora + Inter (latin subset) + OFL licenses
checks/check_site.py  acceptance harness (stdlib only)
```

## Preview

No tooling required. Either:

- Open `index.html` directly in a browser (`file://`), or
- Serve the directory statically, e.g.:

  ```sh
  python3 -m http.server
  # then visit http://localhost:8000/
  ```

## Checks

The acceptance harness verifies the structural guarantees of the site:
that there are no `<script>` tags, that no external resource is loaded,
that every outbound URL is on the allowlist, that the copy and headings
are present in order, and that fonts, licenses, and internal references all
resolve.

```sh
python3 checks/check_site.py
```

It uses only the Python 3 standard library and exits nonzero on any failure.
It is the regression net: keep it green.
