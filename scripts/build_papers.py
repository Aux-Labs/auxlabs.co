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

        <header class="p-8 lg:p-16 border-b border-archival-ink bg-surface/20">
            <div class="max-w-4xl mx-auto">
                <div class="flex flex-wrap items-center gap-3 mb-8 font-mono text-[10px] uppercase tracking-widest">
                    <span class="bg-panel text-white px-3 py-1.5 font-bold">{series}</span>
                    <span class="border border-archival-ink px-3 py-1.5">WORKING PAPER · {version}</span>
                    <span class="border border-archival-ink px-3 py-1.5">AUX LABS LLC</span>
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

        <footer class="p-8 border-t border-archival-ink flex flex-col lg:flex-row justify-between items-start lg:items-end gap-8 bg-archival-paper">
            <div class="font-mono text-[9px] uppercase tracking-widest text-archival-ink/60">
                <p>© {year} AUX LABS LLC // AUSTIN, TX // ALL RIGHTS RESERVED</p>
                <p>CONTACT: <a href="mailto:imran@auxlabs.co" class="text-archival-ink hover:text-brand-green underline transition-colors">imran@auxlabs.co</a></p>
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
    # (unwrap above rejoins hard-wrapped lines so **emphasis** renders)
    md = markdown.Markdown(extensions=["tables", "footnotes", "sane_lists", "smarty"])
    body_html = md.convert(body_md)
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
