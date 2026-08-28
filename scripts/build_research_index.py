#!/usr/bin/env python3
"""Aux Labs research index builder.

Renders the 02_RESEARCH gallery from papers.json straight into research.html,
between the AXL markers. The point is that every number on that page is
DERIVED, never typed: the index can no longer claim eight papers filed while
listing seven. Titles, statuses and counts have exactly one source of truth.

The gallery ships as static HTML so it stays crawlable and readable with
JavaScript off; assets/axl.js only layers filtering, expansion and reveal
on top of markup that already works.

Usage:  python3 scripts/build_research_index.py
"""
import json
import pathlib
import re
import sys
from html import escape

REPO = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = REPO / "papers.json"
PAGE = REPO / "research.html"

STATUS_LABEL = {
    "in_preparation": "In Preparation",
    "next": "Next To Publish",
    "in_review": "In Review",
    "published": "Published",
}

# Green pill for the states that mean movement; muted pill for the rest.
STATUS_PILL = {
    "in_preparation": "bg-archival-ink/10 text-archival-ink",
    "next": "bg-brand-green text-black font-bold",
    "in_review": "bg-archival-ink/10 text-archival-ink",
    "published": "bg-panel text-white font-bold",
}

FILTER_BTN = (
    'border border-archival-ink px-4 py-2 font-mono text-[10px] uppercase '
    'tracking-widest hover:bg-brand-green hover:text-black transition-all axl-filter'
)


def marker_sub(text: str, name: str, payload: str) -> str:
    """Replace everything between <!-- AXL:NAME:START --> and :END --> markers."""
    pattern = re.compile(
        r"(<!-- AXL:%s:START -->).*?(<!-- AXL:%s:END -->)" % (name, name), re.S
    )
    if not pattern.search(text):
        sys.exit(f"ERROR: markers AXL:{name}:START / :END not found in research.html")
    return pattern.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(2), text)


def build_cards(papers, field_labels):
    out = []
    for p in papers:
        series = escape(p["series"])
        slug = series.lower()
        status = p.get("status", "in_preparation")
        label = STATUS_LABEL.get(status, status)
        pill = STATUS_PILL.get(status, STATUS_PILL["in_preparation"])
        domains = " ".join(p.get("domains") or [])
        short = p["title"].split(":")[0]

        tags = [
            f'<span class="font-mono text-[9px] {pill} px-2 py-0.5 uppercase">{escape(label)}</span>'
        ]
        if p.get("flagship"):
            tags.append(
                '<span class="font-mono text-[9px] bg-brand-green text-black px-2 py-0.5 '
                'uppercase font-bold">Flagship</span>'
            )
        for d in p.get("domains") or []:
            tags.append(
                '<span class="font-mono text-[9px] border border-archival-ink/40 '
                f'text-archival-ink/70 px-2 py-0.5 uppercase">{escape(field_labels.get(d, d))}</span>'
            )

        # THE INVENTION RULE, ENFORCED IN CODE: no abstract in the manifest means
        # an honest withheld state renders. Never a placeholder, never filler.
        if p.get("abstract"):
            body = (
                '<p class="text-sm leading-relaxed text-archival-ink/80">'
                f'{escape(p["abstract"])}</p>'
            )
        else:
            body = (
                '<p class="text-sm leading-relaxed text-archival-ink/70">'
                "<span class=\"font-mono text-[9px] uppercase tracking-widest "
                'text-archival-ink/50 block mb-2">[ ABSTRACT_WITHHELD ]</span>'
                "This paper is named before it is linked. The abstract publishes when the "
                "paper clears its sourcing pass, one at a time, in order.</p>"
            )

        if p.get("url"):
            action = (
                f'<a href="{escape(p["url"])}" class="inline-block bg-panel text-white px-6 py-3 '
                'font-mono text-[10px] tracking-widest uppercase hover:bg-brand-green '
                f'hover:text-black transition-all">[ READ_{series} -&gt; ]</a>'
            )
        else:
            action = (
                f'<a href="mailto:imran@auxlabs.co?subject=Advance%20copy%3A%20{series}" '
                'class="inline-block border border-archival-ink px-6 py-3 font-mono text-[10px] '
                'tracking-widest uppercase hover:bg-brand-green hover:text-black hover:border-brand-green '
                'transition-all">[ REQUEST_ADVANCE_COPY ]</a>'
            )

        out.append(f"""                    <article class="axl-paper" data-status="{escape(status)}" data-flagship="{'true' if p.get('flagship') else 'false'}" data-domains="{escape(domains)}">
                        <h4 class="m-0">
                            <button type="button" class="axl-paper-toggle paper-card w-full text-left p-8 lg:p-10 flex flex-col md:flex-row gap-6 md:gap-8 transition-colors hover:bg-surface/40" aria-expanded="false" aria-controls="axl-body-{slug}">
                                <span class="flex items-center justify-between md:contents">
                                    <span class="md:order-1 shrink-0 font-mono text-xs font-bold bg-panel text-white w-20 h-20 flex items-center justify-center paper-id transition-colors">{series}</span>
                                    <span class="axl-chev md:order-3 md:self-center shrink-0 font-mono text-brand-green text-lg" aria-hidden="true">&#9656;</span>
                                </span>
                                <span class="md:order-2 flex-grow">
                                    <span class="flex flex-wrap items-center gap-3 mb-4">{''.join(tags)}</span>
                                    <span class="block text-xl lg:text-2xl font-black uppercase tracking-tight">{escape(p["title"])}</span>
                                </span>
                            </button>
                        </h4>
                        <div class="axl-paper-body" id="axl-body-{slug}" role="region" aria-label="{series} detail">
                            <div class="axl-paper-body-inner">
                                <div class="px-8 lg:px-10 pb-8 lg:pb-10 md:pl-[8.5rem] space-y-6 max-w-3xl">
                                    {body}
                                    <p class="font-mono text-[9px] uppercase tracking-widest text-archival-ink/50 leading-relaxed">CITE AS: HAFIZ, I. (FORTHCOMING). {escape(short).upper()}. AUX LABS WORKING PAPER {series}. AUXLABS.CO</p>
                                    {action}
                                </div>
                            </div>
                        </div>
                    </article>""")
    return "\n".join(out)


def build_filters(papers, fields, field_labels):
    seen_status = []
    for p in papers:
        s = p.get("status", "in_preparation")
        if s not in seen_status:
            seen_status.append(s)
    order = ["next", "in_review", "published", "in_preparation"]
    seen_status.sort(key=lambda s: order.index(s) if s in order else 99)

    btns = [
        f'<button type="button" class="{FILTER_BTN}" data-filter="all" aria-pressed="true">All [{len(papers)}]</button>'
    ]
    for s in seen_status:
        n = sum(1 for p in papers if p.get("status") == s)
        btns.append(
            f'<button type="button" class="{FILTER_BTN}" data-filter="status" '
            f'data-value="{escape(s)}" aria-pressed="false">{escape(STATUS_LABEL.get(s, s))} [{n}]</button>'
        )
    if any(p.get("flagship") for p in papers):
        n = sum(1 for p in papers if p.get("flagship"))
        btns.append(
            f'<button type="button" class="{FILTER_BTN}" data-filter="flagship" '
            f'aria-pressed="false">Flagship [{n}]</button>'
        )
    # Domain filters materialise only once papers actually carry tags.
    for f in fields:
        n = sum(1 for p in papers if f["slug"] in (p.get("domains") or []))
        if n:
            btns.append(
                f'<button type="button" class="{FILTER_BTN}" data-filter="domain" '
                f'data-value="{escape(f["slug"])}" aria-pressed="false">{escape(f["label"])} [{n}]</button>'
            )

    return (
        '                <div class="flex flex-wrap gap-3">\n'
        + "\n".join("                    " + b for b in btns)
        + "\n                </div>\n"
        '                <p id="axl-filter-status" class="sr-only" role="status" aria-live="polite"></p>'
    )


def build_counts(papers):
    filed = len(papers)
    published = sum(1 for p in papers if p.get("status") == "published")
    nxt = next((p["series"] for p in papers if p.get("status") == "next"), "—")
    row = (
        '                        <li class="flex justify-between border-b border-white/10 pb-2 %s">'
        "<span>%s</span><span%s>%s</span></li>"
    )
    return "\n".join([
        row % ("text-white", "Papers Filed", "", f"[{filed:02d}]"),
        row % ("", "Published", "", f"[{published:02d}]"),
        row % ("", "Next To Publish", ' class="text-brand-green"', escape(nxt)),
    ])


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    papers = data["papers"]
    fields = data.get("fields", [])
    field_labels = {f["slug"]: f["label"] for f in fields}

    page = PAGE.read_text(encoding="utf-8")
    page = marker_sub(page, "COUNTS", build_counts(papers))
    page = marker_sub(page, "FILTERS", build_filters(papers, fields, field_labels))
    page = marker_sub(page, "PAPERS", build_cards(papers, field_labels))
    PAGE.write_text(page, encoding="utf-8")

    tagged = sum(1 for p in papers if p.get("domains"))
    print(f"research.html rebuilt — {len(papers)} papers, "
          f"{sum(1 for p in papers if p.get('status') == 'published')} published.")
    if not tagged:
        print("NOTE: no paper carries a domain tag, so the domain filter row is "
              "suppressed. Assign 'domains' in papers.json to switch it on.")
    if data.get("_open_question"):
        print("OPEN: " + data["_open_question"])


if __name__ == "__main__":
    main()
