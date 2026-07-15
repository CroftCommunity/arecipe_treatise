#!/usr/bin/env python3
"""Acceptance checks for the arecipe treatise site (arecipe.croft.ing).

Python 3 standard library only. Exits nonzero on any failure.

This harness is written BEFORE the site exists (TDD red-to-green). It is the
regression net: it must keep passing as the site evolves.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Outbound-link allowlist: bare hosts / path-prefixes that clickable links may
# point at. Nothing else is permitted, and nothing may be a loaded resource.
ALLOWLIST = (
    "arecipe.app",
    "croft.ing",
    "arecipe.croft.ing",
    "github.com/CroftCommunity",
    "recipe.exchange",
    "developer.mozilla.org",
)

# The SVG namespace is the single permitted http(s) URL that is not an
# outbound link: it appears as xmlns inside CSS data-URI artwork.
SVG_NS = "http://www.w3.org/2000/svg"

# The six act headings, in order.
ACT_HEADINGS = (
    "Act I. A short story you already know",
    "Act II. The four preconditions",
    "Act III. The shape: a PWA with no back half",
    "Act IV. Security, honestly",
    "Act V. What you actually get",
    "Act VI. What this does not claim",
)

KICKER = "A CROFT FIELD REPORT"

FONT_FILES = (
    "lora-latin-500-normal.woff2",
    "lora-latin-600-normal.woff2",
    "inter-latin-400-normal.woff2",
    "inter-latin-600-normal.woff2",
)
OFL_FILES = ("OFL-Lora.txt", "OFL-Inter.txt")

errors = []


def fail(msg):
    errors.append(msg)


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def html_files():
    out = []
    for dirpath, _dirs, files in os.walk(ROOT):
        if os.sep + ".git" in dirpath:
            continue
        for name in files:
            if name.endswith(".html"):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def css_files():
    out = []
    for dirpath, _dirs, files in os.walk(ROOT):
        if os.sep + ".git" in dirpath:
            continue
        for name in files:
            if name.endswith(".css"):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def strip_html_text(html):
    """Collapse markup to a plain-text stream for in-order phrase checks."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text


# --- Check 1: index.html and CNAME ---------------------------------------

def check_core_files():
    index = os.path.join(ROOT, "index.html")
    if not os.path.isfile(index):
        fail("index.html is missing")

    cname = os.path.join(ROOT, "CNAME")
    if not os.path.isfile(cname):
        fail("CNAME is missing")
    else:
        content = read(cname).strip()
        if content != "arecipe.croft.ing":
            fail("CNAME must contain exactly 'arecipe.croft.ing', got %r" % content)


# --- Check 2: no <script> tags in any HTML file --------------------------

def check_no_script():
    for path in html_files():
        html = read(path)
        if re.search(r"<\s*script", html, re.IGNORECASE):
            fail("<script> tag found in %s" % os.path.relpath(path, ROOT))


# --- Check 3: URL allowlist + no loaded external resources ---------------

def check_urls():
    url_re = re.compile(r"https?://[^\s\"'<>()]+")
    for path in html_files() + css_files():
        text = read(path)
        rel = os.path.relpath(path, ROOT)
        for match in url_re.finditer(text):
            url = match.group(0).rstrip(".,);")
            if url == SVG_NS:
                continue
            stripped = re.sub(r"^https?://", "", url)
            if any(stripped == host or stripped.startswith(host + "/") or
                   stripped.startswith(host + "?") or stripped.startswith(host + "#")
                   for host in ALLOWLIST):
                continue
            fail("Disallowed URL in %s: %s" % (rel, url))

    # No external URL may be a loaded resource.
    for path in html_files():
        html = read(path)
        rel = os.path.relpath(path, ROOT)
        if re.search(r"<\s*script[^>]*\bsrc\s*=", html, re.IGNORECASE):
            fail("External script src in %s" % rel)
        if re.search(r"\bsrc\s*=\s*[\"']https?://", html, re.IGNORECASE):
            fail("Loaded resource via src=http in %s" % rel)
        # <link ...> that loads (stylesheet/preload/icon) from an http(s) URL.
        for link in re.findall(r"<link\b[^>]*>", html, re.IGNORECASE):
            if re.search(r"\bhref\s*=\s*[\"']https?://", link, re.IGNORECASE):
                fail("Loaded external <link> in %s: %s" % (rel, link.strip()))

    for path in css_files():
        css = read(path)
        rel = os.path.relpath(path, ROOT)
        # url(http...) as a loaded resource (data URIs use url(data:...)).
        if re.search(r"url\(\s*[\"']?\s*https?://", css, re.IGNORECASE):
            fail("Loaded external url() in %s" % rel)
        if re.search(r"@import\s+[\"']?\s*https?://", css, re.IGNORECASE):
            fail("External @import in %s" % rel)


# --- Check 4: act headings + kicker in order -----------------------------

def check_copy_order():
    index = os.path.join(ROOT, "index.html")
    if not os.path.isfile(index):
        fail("cannot check copy order: index.html missing")
        return
    text = strip_html_text(read(index))

    kicker_pos = text.find(KICKER)
    if kicker_pos < 0:
        fail("kicker text %r not found" % KICKER)

    positions = []
    prev = 0
    ok = True
    for heading in ACT_HEADINGS:
        pos = text.find(heading, prev)
        if pos < 0:
            fail("act heading not found (or out of order): %r" % heading)
            ok = False
            break
        positions.append(pos)
        prev = pos + len(heading)
    if ok and kicker_pos >= 0 and positions and kicker_pos > positions[0]:
        fail("kicker text must appear before the act headings")


# --- Check 5: fonts + OFL licenses ---------------------------------------

def check_fonts():
    fonts_dir = os.path.join(ROOT, "assets", "fonts")
    if not os.path.isdir(fonts_dir):
        fail("assets/fonts/ is missing")
        return
    for name in FONT_FILES:
        p = os.path.join(fonts_dir, name)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            fail("font file missing or empty: assets/fonts/%s" % name)
    for name in OFL_FILES:
        p = os.path.join(fonts_dir, name)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            fail("OFL license missing or empty: assets/fonts/%s" % name)


# --- Check 6: internal hrefs / asset refs resolve ------------------------

def check_internal_refs():
    ref_re = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
    css_url_re = re.compile(r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)")

    def resolve(base_dir, ref):
        ref = ref.split("#", 1)[0].split("?", 1)[0]
        if not ref:
            return True  # pure fragment / query
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", ref):
            return True  # has a scheme (http:, mailto:, data:, etc.)
        if ref.startswith("//"):
            return True  # protocol-relative (not used, but not an internal file)
        target = os.path.normpath(os.path.join(base_dir, ref.lstrip("/") if ref.startswith("/") else ref))
        return os.path.exists(target)

    for path in html_files():
        base = os.path.dirname(path)
        html = read(path)
        rel = os.path.relpath(path, ROOT)
        for ref in ref_re.findall(html):
            if not resolve(base, ref):
                fail("unresolved internal ref in %s: %s" % (rel, ref))

    for path in css_files():
        base = os.path.dirname(path)
        css = read(path)
        rel = os.path.relpath(path, ROOT)
        for ref in css_url_re.findall(css):
            if ref.startswith("data:"):
                continue
            if not resolve(base, ref):
                fail("unresolved url() ref in %s: %s" % (rel, ref))


def main():
    check_core_files()
    check_no_script()
    check_urls()
    check_copy_order()
    check_fonts()
    check_internal_refs()

    if errors:
        print("FAIL: %d check(s) failed" % len(errors))
        for e in errors:
            print("  - " + e)
        return 1
    print("OK: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
