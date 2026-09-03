#!/usr/bin/env python3
"""Aux Labs paper publisher.

Renders canon working papers (markdown + YAML frontmatter) into Neu Brutalist
HTML pages under /papers/. THE GATE: a paper renders ONLY when its frontmatter
says `publish: true`. Flip the flag in the vault, re-run, commit, push.

Usage:  python3 scripts/build_papers.py <canon_dir> [--force-preview SERIES]
        --force-preview renders one paper regardless of its flag, into
        /tmp/paper-preview/ (never into the repo). For operator review only.
"""
import sys, re, pathlib, html

import yaml, markdown

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "papers"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{series} | {short_title} — AUX LABS</title>
    <meta name="description" content="{meta_abstract}">
    <link rel="canonical" href="https://auxlabs.co/papers/{slug}.html">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Aux Labs">
    <meta property="og:url" content="https://auxlabs.co/papers/{slug}.html">
    <meta property="og:title" content="{series} | {short_title}">
    <meta property="og:description" content="{meta_abstract}">
    <meta property="og:image" content="https://auxlabs.co/assets/og.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{series} | {short_title}">
    <meta name="twitter:description" content="{meta_abstract}">
    <meta name="twitter:image" content="https://auxlabs.co/assets/og.png">
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%231A1A1A'/%3E%3Ctext x='16' y='22' font-family='monospace' font-size='13' font-weight='bold' fill='%2300FF41' text-anchor='middle'%3EAX%3C/text%3E%3C/svg%3E">
    <script>(function(){{try{{if(localStorage.getItem('axl-theme')==='dark'){{document.documentElement.setAttribute('data-theme','dark');}}}}catch(e){{}}}})();</script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=JetBrains+Mono:wght@300;400;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/tailwind.css">
    <link rel="stylesheet" href="../assets/paper.css">
</head>
<body class="antialiased overflow-x-hidden selection:bg-brand-green selection:text-black">
    <a href="#main" class="skip-link">Skip to content</a>
    <div class="fixed inset-0 pointer-events-none border-[12px] border-archival-ink/5 z-[100]"></div>

    <nav class="sticky top-0 z-[90] bg-archival-paper/80 backdrop-blur-md border-b border-archival-ink flex flex-wrap items-stretch uppercase font-mono text-[10px] tracking-[0.15em] lg:tracking-[0.25em]">
        <a href="../index.html" class="flex items-center px-4 lg:px-8 py-4 border-r border-archival-ink font-black text-base lg:text-lg tracking-tighter">AUX LABS LLC</a>
        <div class="flex-grow flex flex-wrap">
            <a href="../research.html" class="flex items-center px-4 lg:px-10 py-4 border-r border-archival-ink hover:bg-brand-green hover:text-black transition-all">&lt;- 02_RESEARCH</a>
            <span class="hidden md:flex items-center px-4 lg:px-10 py-4 border-r border-archival-ink text-archival-ink/60">{series}</span>
        </div>
        <button onclick="axlToggleTheme()" aria-label="Toggle light/dark" class="flex items-center px-4 lg:px-6 border-l border-archival-ink hover:bg-brand-green hover:text-black transition-all font-bold">[ ◐ ]</button>
    </nav>

    <main id="main" class="relative">
        <div class="px-4 lg:px-8 py-3 bg-panel text-brand-green font-mono text-[9px] tracking-widest flex justify-between uppercase">
            <span>{series} · {version}</span>
            <span class="hidden sm:inline">STATUS: WORKING_PAPER</span>
            <span>AUX LABS RESEARCH</span>
        </div>
        <div class="axl-stripe axl-stripe--thin" aria-hidden="true"></div>

        <header class="p-8 lg:p-16 border-b border-archival-ink bg-surface/20 relative overflow-hidden">
            <span class="axl-wm" style="font-size:clamp(5rem,13vw,10rem); right:-1rem; top:-1.5rem;" aria-hidden="true">RESEARCH</span>
            <div class="max-w-4xl mx-auto relative">
                <div class="flex flex-wrap items-center gap-3 mb-8 font-mono text-[10px] uppercase tracking-widest">
                    <span class="bg-panel text-white px-3 py-1.5 font-bold">{series}</span>
                    <span class="border border-archival-ink px-3 py-1.5">WORKING PAPER · {version}</span>
                    <span class="border border-archival-ink px-3 py-1.5">AUX LABS LLC</span>
                    <a href="../plain/{slug}.html" class="border border-archival-ink px-3 py-1.5 font-bold hover:bg-brand-green hover:text-black hover:border-brand-green transition-all">"PLAIN ENGLISH" VERSION -&gt;</a>
                </div>
                <h1 class="text-3xl lg:text-[2.75rem] font-black leading-[1.02] tracking-tighter uppercase mb-8">{title}</h1>
                <div class="border-l-4 border-brand-green pl-6 lg:pl-8 py-2 mb-8">
                    <div class="font-mono text-[9px] uppercase tracking-widest text-archival-ink/60 mb-3">ABSTRACT</div>
                    <p class="text-sm lg:text-base leading-relaxed text-archival-ink/80">{abstract}</p>
                </div>
                <div class="font-mono text-[9px] uppercase tracking-widest text-archival-ink/60 space-y-1">
                    <p>KEYWORDS: {keywords}</p>
                    <p>CITE AS: HAFIZ, I. ({year}). {short_title}. AUX LABS WORKING PAPER {series}. AUXLABS.CO</p>
                    <p>CONTACT: <a class="underline text-archival-ink hover:text-brand-green" href="mailto:{contact}">{contact}</a></p>
                </div>
            </div>
        </header>

        <article class="paper-prose px-6 lg:px-8 py-12 lg:py-16">
            <div class="max-w-3xl mx-auto">
{body}
            </div>
        </article>

        <div class="axl-stripe" aria-hidden="true"></div>
    <footer class="p-8 flex flex-col lg:flex-row justify-between items-start lg:items-end gap-8 bg-archival-paper">
            <div class="font-mono text-[9px] uppercase tracking-widest text-archival-ink/60">
                <p>© {year} AUX LABS LLC // AUSTIN, TX // ALL RIGHTS RESERVED</p>
                <p>CONTACT: <a href="mailto:imran@auxlabs.co" class="text-archival-ink hover:text-brand-green underline transition-colors">imran@auxlabs.co</a></p>
                <p class="axl-co">c/o AUX LABS LLC · "AUSTIN, TEXAS" · 30.2672° N, 97.7431° W</p>
                <p>auxlabs.co // Signal @nawab.12</p>
            </div>
            <div class="text-left lg:text-right">
                <h2 class="text-3xl font-black tracking-tighter uppercase leading-none mb-2">End of <br> Paper.</h2>
                <p class="font-mono text-[9px] text-brand-green bg-black px-2 py-0.5 inline-block uppercase">{series}_FIN</p>
            </div>
        </footer>
    </main>

    <script>
        function axlToggleTheme(){{
            var h = document.documentElement;
            var toDark = h.getAttribute('data-theme') !== 'dark';
            if (toDark) {{ h.setAttribute('data-theme','dark'); }} else {{ h.removeAttribute('data-theme'); }}
            try {{ localStorage.setItem('axl-theme', toDark ? 'dark' : 'light'); }} catch(e) {{}}
        }}
    </script>
</body>
</html>
"""

BLOCK_PREFIXES = ("#", "-", "*", "+", ">", "|", "```", "~~~", "    ", "\t")

# ── Plaintext normalization (pandoc-exported papers) ─────────────────────────
# Several canon files are plaintext exports: ASCII mastheads, centered title
# blocks, ALL-CAPS section lines, and indentation that markdown reads as code.
# This pass turns that furniture into real structure. Content is never edited.

_MASTHEAD_KV = re.compile(r"^\s*(DOCUMENT|AUTHOR|DATE|CLASSIFICATION|WORD COUNT|STATUS|PROJECT)\s*:", re.I)
_BAR_LINE = re.compile(r"^\s*[█▓▒░=─━┄\-_*]{6,}\s*$")
_ROMAN_HEAD = re.compile(r"^\s*([IVXL]+)\.\s+(.{3,90})$")
_NUM_SUBHEAD = re.compile(r"^\s*(\d+\.\d+(?:\.\d+)?)\.?\s+([A-Z].{2,90})$")
_BOLD_LINE = re.compile(r"^\s*\*\*([^*]{3,90})\*\*\s*$")

def _is_caps_head(s):
    t = s.strip()
    if not (3 <= len(t) <= 90) or t.endswith((".", ",")) and not t.endswith("..."):
        return False
    letters = [c for c in t if c.isalpha()]
    return len(letters) >= 3 and all(c.isupper() for c in letters) and "|" not in t

def _title_words(fm):
    words = set()
    for k in ("title", "series"):
        for w in re.findall(r"[A-Za-z]{3,}", str(fm.get(k, ""))):
            words.add(w.lower())
    return words

_SECTION_WORDS = re.compile(r"^[\s*_]*((EXECUTIVE SUMMARY|ABSTRACT|PLAIN-LANGUAGE SUMMARY|FOR THE READER IN A HURRY|INTRODUCTION|KEY TERMS)[\s*_:]*)$", re.I)
_TABLE_ROW = re.compile(r"\S(   +)\S")


_HEADING_REPAIRS = {
    "WHATISALREADYKNOWNANDWHATISNOT": "WHAT IS ALREADY KNOWN, AND WHAT IS NOT",
    "WHATTHISSTUDYPRODUCES": "WHAT THIS STUDY PRODUCES",
    "WHATFULLCOMPLIANCEISWORTHANNUALLY": "WHAT FULL COMPLIANCE IS WORTH, ANNUALLY",
    "WHYTHISPROBLEMISUNUSUALLYTRACTABLE": "WHY THIS PROBLEM IS UNUSUALLY TRACTABLE",
    "WHOCARRIESTHELOSSTODAY": "WHO CARRIES THE LOSS TODAY",
}

def _repair_heading(s):
    key = re.sub(r"[^A-Za-z]", "", s).upper()
    return _HEADING_REPAIRS.get(key, s)

def _despace_heading(s, vocab):
    """Repair PDF-extraction letter-spacing ('W H AT I S' -> 'WHAT IS') by
    segmenting the collapsed string against the document's own vocabulary."""
    toks = s.split()
    if not toks or sum(1 for t in toks if len(t) <= 2) / len(toks) < 0.5:
        return s
    joined = "".join(toks)
    words, cur = [], joined
    # DP segmentation: prefer fewest chunks whose lowercase forms are in vocab
    n = len(joined)
    best = [None] * (n + 1); best[0] = (0, 0, [])
    for i in range(n):
        if best[i] is None: continue
        for j in range(i + 1, min(n, i + 22) + 1):
            piece = joined[i:j]
            alpha = re.sub(r"[^A-Za-z]", "", piece)
            known = bool(alpha) and alpha.lower() in vocab
            cost = (0 if known else 1, best[i][1] + 1)
            cand = (best[i][0] + cost[0], cost[1], best[i][2] + [piece])
            if best[j] is None or (cand[0], cand[1]) < (best[j][0], best[j][1]):
                best[j] = cand
    if best[n] is None or best[n][0] > max(1, len(joined) // 18):
        return s
    return " ".join(best[n][2])

def normalize_plaintext(md, fm):
    lines = md.split("\n")
    # Only fire on plaintext exports: few real markdown headings up top.
    if sum(1 for l in lines[:80] if l.lstrip().startswith("#")) >= 2:
        return md
    vocab = {w.lower() for w in re.findall(r"[A-Za-z]+", md)} | {
        "a","i","is","of","to","in","and","the","what","why","who","how","worth","loss"}
    twords = _title_words(fm)
    out, seen_content = [], False
    _byline = re.compile(r"^\s*(\*{0,2}Imran Hafiz|Founder,|imran@|Draft\b|Prepared for|AUX LABS LLC\b|Aux Labs LLC\s*$)", re.I)
    i, n = 0, len(lines)
    in_table = False

    def _promote_section(word):
        lvl = "###" if word.upper() == "FOR THE READER IN A HURRY" else "##"
        out.extend(["", f"{lvl} {word.title()}", ""])

    def _looks_tabular(idx):
        return idx < n and bool(_TABLE_ROW.search(lines[idx]))

    while i < n:
        raw = lines[i]; i += 1
        line = raw.rstrip()
        if _BAR_LINE.match(line) or _MASTHEAD_KV.match(line):
            continue
        s = line.strip()
        # Leading zone: drop title echoes, bylines, and subtitle blocks; keep
        # epigraph quotes; content starts at a section word, a numbered caps
        # heading, or a block that reads as prose (ends with sentence punctuation).
        if not seen_content:
            if not s:
                out.append("")
                continue
            sw = _SECTION_WORDS.match(s)
            if sw:
                seen_content = True
                _promote_section(sw.group(2))
                continue
            if _ROMAN_HEAD.match(s) and s.upper() == s:
                seen_content = True
                out.extend(["", f"## {_repair_heading(_despace_heading(s, vocab))}", ""])
                continue
            if s.startswith(('*"', '"', "*“", "“", '*\\"')):
                quote = [s]
                while i < n and lines[i].strip():
                    quote.append(lines[i].strip()); i += 1
                out.extend(["", "> " + " ".join(quote).strip("*"), ""])
                continue
            block = [s]
            while i < n and lines[i].strip():
                nxt = lines[i].strip()
                if _SECTION_WORDS.match(nxt) or _is_caps_head(lines[i]) or (_ROMAN_HEAD.match(nxt) and nxt.upper() == nxt):
                    break
                block.append(nxt); i += 1
            tail = block[-1]
            is_prose = tail.endswith((".", "?", "!", '."', ".”", '?"', "]", ")"))
            wl = [w.lower() for w in re.findall(r"[A-Za-z]{3,}", " ".join(block))]
            title_echo = wl and sum(1 for w in wl if w in twords) / len(wl) > 0.55
            allcaps = all(b.isupper() for b in block)
            if is_prose and not title_echo and not allcaps and not _byline.match(s):
                w0 = [w.lower() for w in re.findall(r"[A-Za-z]{3,}", block[0])]
                if w0 and sum(1 for w in w0 if w in twords) / len(w0) > 0.55 and not block[0].rstrip().endswith((".", "?", "!")):
                    block = block[1:]
                seen_content = True
                out.extend([""] + block)
            continue
        # Structure promotion (standalone lines only).
        m = _NUM_SUBHEAD.match(line)
        if m and not line.lstrip().startswith(("#", "-", "*", ">")):
            out.extend(["", f"### {m.group(1)} {m.group(2).strip()}", ""])
            continue
        sw = _SECTION_WORDS.match(s)
        if sw:
            _promote_section(sw.group(2))
            continue
        # ASCII table region: keep as indented monospace so alignment survives.
        if _TABLE_ROW.search(line):
            in_table = True
            out.append("    " + s.replace("**", ""))
            continue
        if in_table:
            if not s:
                # table continues across a blank only if a tabular row follows
                nxt_real = next((lines[k] for k in range(i, min(i + 2, n)) if lines[k].strip()), "")
                if _TABLE_ROW.search(nxt_real):
                    out.append("")
                    continue
                in_table = False
                out.append("")
                continue
            if len(s) <= 70:
                out.append("    " + s.replace("**", ""))
                continue
            in_table = False
        rm = _ROMAN_HEAD.match(line)
        caps_head = _is_caps_head(line) and len(s) >= 8 and not _TABLE_ROW.search(s)
        if (rm and rm.group(2).strip() == rm.group(2).strip().upper()) or caps_head:
            head = s
            while i < n and _is_caps_head(lines[i]) and not _ROMAN_HEAD.match(lines[i]) and lines[i].strip() and not _TABLE_ROW.search(lines[i]):
                head += " " + lines[i].strip(); i += 1
            out.extend(["", f"## {_repair_heading(_despace_heading(head, vocab))}", ""])
            continue
        bm = _BOLD_LINE.match(line)
        if bm:
            inner = bm.group(1).strip()
            if re.match(r"^\d+\.\d", inner):
                out.extend(["", f"### {inner}", ""])
                continue
            if re.match(r"^\d+\.\s", inner) or inner.isupper():
                out.extend(["", f"## {inner}", ""])
                continue
        if s.startswith(("•", "◦", "▪")):
            out.append("- " + s.lstrip("•◦▪ "))
            continue
        # De-indent so markdown never reads prose as a code block.
        out.append(s if line.startswith((" ", "\t")) else line)
    return "\n".join(out)

# ── Pull quotes (verbatim sentences from each paper, presentation only) ──────
PULLQUOTES = {
    "AXL-WP-01": ["The Ostrom analysis is therefore diagnostic, not descriptive: it reveals what VICE needed and lacked.",
                   "If every company is a \"captured commons,\" the concept loses analytical power and the framework becomes unfalsifiable."],
    "AXL-WP-02": ["Almost nobody does it, and the reason is not ignorance.",
                   "The protocol is published in advance."],
    "AXL-WP-03": ["The equilibrium is stable because it is rational.",
                   "The relationship is additive, not competitive."],
    "AXL-WP-04": ["This is where I learned that the attention economy is not a market failure."],
    "AXL-WP-05": ["The Pretend Era was not caused by stupidity.",
                   "The most dangerous clinical presentation in the Pretend Era is not the patient who feels bad about themselves."],
    "AXL-WP-06": ["The psychological revolution is not coming.",
                   "Art is not decoration applied to truth."],
    "AXL-WP-07": ["The burden is degraded signal, not only length.",
                   "When a case is resolved against a party without reaching its merits, and the resolution is wrong, the error does not stop at the courthouse."],
    "AXL-WP-08": ["Policy without trust is dead on arrival.",
                   "What is complicated is getting institutions built for technical problems to recognize that their hardest problem is not technical."],
}

def _norm_txt(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

def inject_pullquotes(body_html, series):
    quotes = PULLQUOTES.get(series, [])
    if not quotes:
        return body_html
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return body_html
    soup = BeautifulSoup(body_html, "html.parser")
    for q in quotes:
        key = _norm_txt(q)
        for p in soup.find_all("p"):
            if key in _norm_txt(p.get_text()):
                aside = soup.new_tag("aside")
                aside["class"] = "axl-pull"
                aside["aria-hidden"] = "true"
                aside.string = q.strip().rstrip(".")+"."
                p.insert_before(aside)
                break
    return str(soup)

def _is_block_line(line):
    ls = line.lstrip()
    if not ls:
        return True
    if line.startswith(BLOCK_PREFIXES) or ls.startswith(("#", "-", "*", "+", ">", "|", "```", "~~~")):
        return True
    import re as _re
    if _re.match(r"^\s*\d+[.)]\s", line):
        return True
    return False

def unwrap_paragraphs(md):
    """Join hard-wrapped lines inside plain paragraphs (conversion artifact) so
    inline emphasis that was split across lines renders. Leaves headings, lists,
    quotes, tables, and code fences untouched."""
    out, in_code = [], False
    for line in md.split("\n"):
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            out.append(line); continue
        if in_code or _is_block_line(line) or not out:
            out.append(line); continue
        prev = out[-1]
        if prev and not _is_block_line(prev) and prev.strip() and not prev.rstrip().endswith(("  ", "\\")):
            out[-1] = prev.rstrip() + " " + line.strip()
        else:
            out.append(line)
    return "\n".join(out)

def parse_fm_tolerant(block):
    """Line-wise fallback for frontmatter that isn't strict YAML
    (unquoted colons in values, pandoc habits). Handles `key: value`
    and `key: >` folded blocks; values stay strings."""
    fm, key, folding = {}, None, False
    for line in block.splitlines():
        if folding:
            if line.startswith((" ", "\t")):
                fm[key] = (fm[key] + " " + line.strip()).strip()
                continue
            folding = False
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).split("#")[0].strip()
            if val == ">":
                fm[key], folding = "", True
            else:
                fm[key] = val
    if isinstance(fm.get("keywords"), str):
        fm["keywords"] = [k.strip() for k in fm["keywords"].strip("[]").split(",")]
    if isinstance(fm.get("publish"), str):
        fm["publish"] = fm["publish"].lower().startswith("true")
    return fm

def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = parse_fm_tolerant(m.group(1))
    return fm, text[m.end():]

def render(path, outdir):
    raw = path.read_text(encoding="utf-8")
    fm, body_md = split_frontmatter(raw)
    body_md = re.sub(r"<!--.*?-->", "", body_md, flags=re.S)          # strip editorial comments
    body_md = re.sub(r"^ (?=\S)", "", body_md, flags=re.M)            # pandoc single-space indent
    body_md = normalize_plaintext(body_md, fm)                        # mastheads out, structure in
    body_md = unwrap_paragraphs(body_md)
    # figure placement markers: **[Figure N near here.** caption...] -> real <figure> if asset exists
    def _fig(m):
        n, cap = m.group(1), m.group(2).strip()
        slug = fm.get("series", path.stem).lower()
        asset = REPO / "papers" / "assets" / f"{slug}-figure{n}.png"
        if asset.exists():
            import html as _h
            return (f'<figure class="axl-figure"><img src="assets/{slug}-figure{n}.png" '
                    f'alt="Figure {n}. {_h.escape(cap[:200])}" loading="lazy">'
                    f'<figcaption><span class="fig-label">FIG. {n:0>2}</span> {_h.escape(cap)}</figcaption></figure>')
        return f"*Figure {n}. {cap}*"
    body_md = re.sub(r"\*\*\[Figure (\d+) near here\.\*\*(.*?)\]", _fig, body_md, flags=re.S)
    body_md = re.sub(r"\\([$%&#_])", r"\1", body_md)  # pandoc-escaped symbols
    body_md = re.sub(r"(\w)- (?=[a-z])", r"\1-", body_md)  # rejoin words hyphen-split at line wraps
    # (unwrap above rejoins hard-wrapped lines so **emphasis** renders)
    md = markdown.Markdown(extensions=["tables", "footnotes", "sane_lists", "smarty"])
    body_html = md.convert(body_md)
    body_html = inject_pullquotes(body_html, fm.get("series", ""))
    title = str(fm.get("title", path.stem))
    short = title.split(":")[0]
    abstract = " ".join(str(fm.get("abstract", "")).split())
    page = TEMPLATE.format(
        slug=fm.get("series", path.stem).lower(),
        series=fm.get("series", "AXL-WP"),
        version=fm.get("version", "v1.0"),
        title=html.escape(title),
        short_title=html.escape(short),
        abstract=html.escape(abstract),
        meta_abstract=html.escape(abstract[:300]),
        keywords=html.escape(", ".join(fm.get("keywords", [])) if isinstance(fm.get("keywords"), list) else str(fm.get("keywords", ""))).upper(),
        contact=fm.get("contact", "imran@auxlabs.co"),
        year="2026",
        body=body_html,
    )
    slug = fm.get("series", path.stem).lower()
    out = outdir / f"{slug}.html"
    out.write_text(page, encoding="utf-8")
    return fm, out

def main():
    canon = pathlib.Path(sys.argv[1])
    force = sys.argv[sys.argv.index("--force-preview") + 1] if "--force-preview" in sys.argv else None
    built, skipped = [], []
    for f in sorted(canon.glob("AXL-WP-*.md")):
        fm, _ = split_frontmatter(f.read_text(encoding="utf-8"))
        series = fm.get("series", f.stem)
        if fm.get("publish") is True:
            _, out = render(f, OUT)
            built.append((series, str(out)))
        elif force and force in series:
            prev = pathlib.Path("/tmp/paper-preview"); prev.mkdir(exist_ok=True)
            _, out = render(f, prev)
            print(f"PREVIEW ONLY (publish:false): {series} -> {out}")
        else:
            skipped.append(series)
    print("BUILT (publish:true):", built or "none")
    print("GATED (publish:false):", skipped)

if __name__ == "__main__":
    main()
