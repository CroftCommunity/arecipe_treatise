# RUN-01 Summary — arecipe.croft.ing (the treatise site)

One-page site in the croft.ing family. Built TDD-first: the acceptance harness
was written and run **before** any page existed, its failure recorded, then the
page was built to green.

## Pre-step check

The repository was empty at start (no commits, no files beyond `.git`), which
satisfies the guardrail (nothing beyond a LICENSE and/or README.md). Proceeded.

Branch note: this run was executed on `claude/arecipe-treatise-run-01-jxzta8`
per the standing branch requirement for this environment (which forbids pushing
to any other branch), rather than the `run-01-treatise` name suggested in the
task text.

## Phase 1 (RED) — harness first

`checks/check_site.py` (Python 3 stdlib only) was written and run before any
page, favicon, CNAME, or font existed. Recorded failing output:

```
$ python3 checks/check_site.py
FAIL: 4 check(s) failed
  - index.html is missing
  - CNAME is missing
  - cannot check copy order: index.html missing
  - assets/fonts/ is missing
EXIT: 1
```

The harness asserts: `index.html` exists and `CNAME` contains exactly
`arecipe.croft.ing`; no `<script>` tag in any HTML; every `http(s)` URL in
HTML/CSS is on the outbound-link allowlist (arecipe.app, croft.ing,
arecipe.croft.ing, github.com/CroftCommunity, recipe.exchange,
developer.mozilla.org) or is the SVG namespace inside a CSS data URI, and
nothing is a loaded external resource; the six act headings and the kicker
appear in order; `assets/fonts/` holds the four woff2 files and both OFL
license texts; and every internal href / asset reference resolves to a file.

## Phase 2–3 — build to green

Created the page, stylesheet, CNAME, favicon, and self-hosted fonts. The
treatise copy from the task brief was placed verbatim. Final run:

```
$ python3 checks/check_site.py
OK: all checks passed
EXIT: 0
```

Red-to-green order is thus evidenced: 4 failing checks with no site → 0
failures once the site was built.

### Rendering verification

Rendered headless (Chromium via Playwright) at 360px and 900px viewports:

- External requests observed: **0** (only `file:` and `data:` URIs loaded).
- No horizontal overflow at 360px or desktop. (Long literal URLs in the gate
  list were made to wrap with `overflow-wrap`.)

## Files created

```
index.html                              the treatise (copy verbatim)
styles.css                              single stylesheet, tectonic palette
CNAME                                   arecipe.croft.ing
assets/favicon.svg                      drystone cairn, 3 stroked rects, 275 B
assets/fonts/lora-latin-500-normal.woff2
assets/fonts/lora-latin-600-normal.woff2
assets/fonts/inter-latin-400-normal.woff2
assets/fonts/inter-latin-600-normal.woff2
assets/fonts/OFL-Lora.txt
assets/fonts/OFL-Inter.txt
checks/check_site.py                    acceptance harness (stdlib only)
README.md
RUN-01-SUMMARY.md
```

## Font sourcing outcome

Fetch **succeeded**. Latin-subset woff2 files were pulled from the fontsource
npm artifacts on jsDelivr, and the SIL Open Font License 1.1 texts from the
same packages:

- `@fontsource/lora@5` → lora-latin-500-normal.woff2 (21,900 B),
  lora-latin-600-normal.woff2 (21,916 B), LICENSE → `OFL-Lora.txt`
- `@fontsource/inter@5` → inter-latin-400-normal.woff2 (23,664 B),
  inter-latin-600-normal.woff2 (24,452 B), LICENSE → `OFL-Inter.txt`

All four files verified as valid WOFF2 (TrueType flavour); both license files
verified as genuine "SIL Open Font License, Version 1.1" texts. `@font-face`
declarations use `font-display: swap` with fallback stacks
`Lora, Georgia, 'Times New Roman', serif` and
`Inter, system-ui, -apple-system, 'Segoe UI', sans-serif`. The fallback stacks
are in place regardless, so the page degrades gracefully if a woff2 ever fails
to load.

## Manual follow-ups (maintainer)

Not automatable from this run — do these after review/merge:

1. **GitHub Pages**: Settings → Pages → Build and deployment → *Deploy from a
   branch*, branch `main`, folder `/ (root)`.
2. **Custom domain**: set `arecipe.croft.ing` in the Pages settings (the
   `CNAME` file already carries it).
3. **DNS**: add a `CNAME` record `arecipe` → `croftcommunity.github.io` at the
   registrar for `croft.ing`.
4. **HTTPS**: once the certificate issues, enable *Enforce HTTPS* in Pages
   settings.

## Acceptance

- `python3 checks/check_site.py` exits 0.
- Zero `<script>` tags; zero loaded external resources (verified in a browser).
- Copy placed verbatim; readable at 360px and desktop.
