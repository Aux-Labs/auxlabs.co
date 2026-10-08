"""Paper figures in the house style (see AXL-WP-08 FIG. 01).

Each figure is drawn in code so it matches its paper exactly and can be fixed
when a number changes. Run `python3 scripts/figures.py` to regenerate every SVG
into papers/assets/. Figures are placed in the text by a
`**[Figure N near here.** caption]` marker in the paper's canon markdown.
"""
import pathlib
from html import escape

OUT = pathlib.Path(__file__).resolve().parent.parent / "papers" / "assets"
PAPER, INK, WHITE, GREEN, MUTED = "#F2F1ED", "#1A1A1A", "#FFFFFF", "#00FF41", "#6B6B66"
STYLE = ('<style>.l{font:700 15px "JetBrains Mono",Courier,monospace;letter-spacing:2px}'
         '.s{font:700 13px "JetBrains Mono",Courier,monospace;letter-spacing:1.5px}'
         '.n{font:700 22px Inter,Arial,sans-serif}.b{font:900 26px Inter,Arial,sans-serif;letter-spacing:-.5px}'
         '.t{font:400 18px Inter,Arial,sans-serif}.k{font:900 40px Inter,Arial,sans-serif;letter-spacing:-1px}</style>')


def wrap(text, width):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + ([cur] if cur else [])


class Fig:
    def __init__(self, w, h, label, aria):
        self.w, self.h, self.o = w, h, []
        self.o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(aria)}">')
        self.o.append(f'<rect width="100%" height="100%" fill="{PAPER}"/>{STYLE}')
        self.o.append(f'<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                      f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>'
                      f'<marker id="g" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                      f'<path d="M0 0L10 5L0 10z" fill="#0B6B2E"/></marker></defs>')
        self.text(50, 56, label, "l")

    def text(self, x, y, s, cls="t", anchor="start", fill=INK, lh=None, width=None):
        lines = wrap(s, width) if width else [s]
        lh = lh or {"t": 25, "n": 27, "s": 18, "l": 20, "b": 30, "k": 44}[cls]
        for i, line in enumerate(lines):
            self.o.append(f'<text x="{x}" y="{y + i * lh}" class="{cls}" text-anchor="{anchor}" fill="{fill}">{escape(line)}</text>')
        return y + len(lines) * lh

    def box(self, x, y, w, h, title=None, body=None, fill=WHITE, tag=None, cls="n", wrap_at=None, dashed=False):
        if not dashed:
            self.o.append(f'<rect x="{x+6}" y="{y+6}" width="{w}" height="{h}" fill="{INK}"/>')
        dash = ' stroke-dasharray="7 6"' if dashed else ""
        self.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{INK}" stroke-width="3"{dash}/>')
        ty = y + 34
        if tag:
            self.o.append(f'<text x="{x+18}" y="{y+28}" class="s" fill="{INK}">{escape(tag)}</text>'); ty = y + 60
        if title:
            ty = self.text(x + 18, ty, title, cls, width=wrap_at or max(8, int((w - 36) / 12.5)))
        if body:
            self.text(x + 18, ty + 4, body, "t", width=max(10, int((w - 36) / 9.2)))

    def arrow(self, pts, green=False, dashed=False):
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        col, m = ("#0B6B2E", "g") if green else (INK, "a")
        dash = ' stroke-dasharray="8 6"' if dashed else ""
        self.o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3"{dash} marker-end="url(#{m})"/>')

    def line(self, x1, y1, x2, y2, w=2, col=INK, dashed=False):
        dash = ' stroke-dasharray="4 6"' if dashed else ""
        self.o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}"{dash}/>')

    def raw(self, s): self.o.append(s)

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / name).write_text("\n".join(self.o + ["</svg>"]), encoding="utf-8")
        return name


def loop(f, cx, cy, r, nodes, bw=300, bh=96, green_idx=None):
    """Nodes placed clockwise on a circle, joined by arrows: a self-reinforcing loop."""
    import math
    n = len(nodes); pos = []
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(n):
        (x1, y1), (x2, y2) = pos[i], pos[(i + 1) % n]
        # trim the arrow to the box edges
        dx, dy = x2 - x1, y2 - y1; L = (dx * dx + dy * dy) ** .5
        tx = min(abs((bw / 2 + 14) / (dx / L)) if dx else 1e9, abs((bh / 2 + 14) / (dy / L)) if dy else 1e9)
        f.arrow([(x1 + dx / L * tx, y1 + dy / L * tx), (x2 - dx / L * tx, y2 - dy / L * tx)])
    for i, ((x, y), (title, body)) in enumerate(zip(pos, nodes)):
        f.box(x - bw / 2, y - bh / 2, bw, bh, title, body, fill=GREEN if i == green_idx else WHITE)


# ── WP-01 ────────────────────────────────────────────────────────────────
def wp01():
    f = Fig(1200, 720, "FIG. 02 // OSTROM'S EIGHT PRINCIPLES, APPLIED TO VICE",
            "Ostrom's eight design principles for long-enduring commons. The paper documents violations of principles 1 to 4 at VICE; principles 5 to 8 are not assessed.")
    rows = [("1 · Clearly defined boundaries", "Freelancers and interns did commons work with none of its protections"),
            ("2 · Rules fit local conditions", "Zine-era rules never updated for ~3,000 staff and a $5.7B valuation"),
            ("3 · Collective-choice arrangements", "One founder made the rules; unions arrived in the capture phase"),
            ("4 · Monitors accountable to the community", "No internal monitor; a New York Times investigation surfaced it")]
    y = 100
    for t, b in rows:
        f.box(50, y, 700, 116, t, b, tag="VIOLATED · DOCUMENTED"); y += 134
    f.box(800, 100, 350, 518, None, None, fill=PAPER, dashed=True)
    f.text(825, 140, "NOT ASSESSED IN THIS PAPER", "s")
    for i, t in enumerate(["5 · Graduated sanctions", "6 · Conflict resolution", "7 · Right to organise", "8 · Nested enterprises"]):
        f.text(825, 210 + i * 100, t, "n", fill=MUTED)
    f.text(50, 670, "Four of eight principles fail on the public record, and each maps onto a failure mode in §IV.", "t")
    return f.save("axl-wp-01-figure2.svg")


def wp01_timeline():
    f = Fig(1200, 520, "FIG. 01 // RISE, CAPTURE, COLLAPSE",
            "VICE timeline. Rise 1994 to 2014; capture 2014 to 2018 as TCV invested 250 million dollars in 2014, Disney 400 million from 2015 at a 4 billion valuation, and TPG 450 million in 2017 at the 5.7 billion peak; collapse 2018 to 2023, ending in a May 2023 bankruptcy sale for 225 million dollars, about 96 percent below peak.")
    x0, x1 = 80, 1120; yr = lambda y: x0 + (y - 1994) / (2023 - 1994) * (x1 - x0)
    for a, b, name, fill in [(1994, 2014, "RISE", WHITE), (2014, 2018, "CAPTURE", GREEN), (2018, 2023, "COLLAPSE", INK)]:
        f.raw(f'<rect x="{yr(a)}" y="110" width="{yr(b)-yr(a)}" height="54" fill="{fill}" stroke="{INK}" stroke-width="3"/>')
        f.text((yr(a) + yr(b)) / 2, 145, name, "s", "middle", fill=PAPER if fill == INK else INK)
        f.text(yr(a), 192, str(a), "s", "start" if a == 1994 else "middle")
    f.text(yr(2023), 192, "2023", "s", "end")
    events = [(2013, "2013 · $1.4B valuation", 250), (2014, "2014 · TCV invests $250M", 300), (2015, "2015 · Disney $400M, at a $4B valuation", 350),
              (2017, "2017 · TPG $450M at the $5.7B peak", 400), (2023, "May 2023 · bankruptcy sale, $225M: ~96% below peak", 450)]
    for y, label, ty in events:
        f.line(yr(y), 210, yr(y), ty + 6, dashed=True)
        f.raw(f'<circle cx="{yr(y)}" cy="{ty-7}" r="6" fill="{INK}"/>')
        f.text(yr(y) - 16, ty, label, "n", "end")
    return f.save("axl-wp-01-figure1.svg")


# ── WP-02 ────────────────────────────────────────────────────────────────
def wp02_loop():
    f = Fig(1200, 900, "FIG. 01 // THE ASSURANCE TRAP",
            "A self-fulfilling loop. Drivers privately prefer the zipper merge but believe others see late merging as cheating, so they merge early. A minority block the open lane, which makes late merging genuinely unsafe, which looks like evidence for the original belief.")
    loop(f, 600, 480, 330, [
        ("Private preference", "Most drivers would rather zipper. It is faster for them."),
        ("Perceived norm", "They believe others see late merging as cheating."),
        ("Early merge", "So they merge early, and a minority block the open lane."),
        ("Manufactured hazard", "Blocking makes late merging genuinely unsafe."),
        ("Belief confirmed", "The hazard reads as proof the norm was right."),
    ], bw=320, bh=140, green_idx=1)
    f.text(600, 480, "AN INFORMATION", "s", "middle"); f.text(600, 502, "CAMPAIGN CAN'T", "s", "middle"); f.text(600, 524, "BREAK THIS LOOP", "s", "middle")
    return f.save("axl-wp-02-figure1.svg")


def wp02_chain():
    f = Fig(1200, 490, "FIG. 02 // ONE MISSING TERM",
            "Recoverable burden equals A times B times C. Term A, lane-closure exposure, and Term C, the cost of each unit of throughput loss, are computable today. Term B, throughput loss per unit of non-compliance, does not exist; measuring it costs about 40,000 dollars and unlocks 1.2 to 8.3 billion dollars a year in recoverable loss.")
    xs = [50, 440, 830]
    specs = [("A", "Lane-closure exposure", "Computable today: lane-closure permits plus probe data", WHITE, "ALREADY BUILT"),
             ("B", "Throughput loss per unit of non-compliance", "Does not exist. Needs an observed compliance distribution", GREEN, "MISSING · ~$40,000"),
             ("C", "Cost per unit of throughput loss", "Computable today: EPA MOVES; TTI $24.01/person-hr", WHITE, "ALREADY BUILT")]
    for x, (k, t, b, fill, tag) in zip(xs, specs):
        f.box(x, 110, 320, 210, t, b, fill=fill, tag=f"TERM {k} · {tag}")
    for x in (382, 772):
        f.text(x + 24, 228, "×", "k", "middle")
    f.text(600, 400, "A × B × C  =  $1.2B – $8.3B a year in recoverable loss, US", "b", "middle")
    f.text(600, 440, "Measure B once and it plugs into every simulation model already in the literature.", "t", "middle")
    return f.save("axl-wp-02-figure2.svg")


# ── WP-03 ────────────────────────────────────────────────────────────────
STAGES = ["Listening", "Legitimacy", "Trust", "Sources", "Truth", "Art", "Gravity", "Funding", "Institutions", "Policy"]


def wp03_firewall():
    f = Fig(1200, 560, "FIG. 03 // THE SPONSOR FIREWALL",
            "The ten cascade stages in order. Foundation capital enters upstream, funding Listening, Legitimacy and Trust and the ideation at Art. Brand and sponsor capital enters only at Funding, after Art has been independently ideated.")
    w, g, x0, y = 98, 8, 50, 250
    for i, s in enumerate(STAGES):
        x = x0 + i * (w + g)
        fill = GREEN if s in ("Listening", "Legitimacy", "Trust", "Art") else WHITE
        f.raw(f'<rect x="{x}" y="{y}" width="{w}" height="86" fill="{fill}" stroke="{INK}" stroke-width="3"/>')
        f.text(x + w / 2, y + 30, str(i + 1), "s", "middle")
        f.text(x + w / 2, y + 62, s.upper() if len(s) < 11 else "INSTITU-", "s", "middle")
        if len(s) >= 11: f.text(x + w / 2, y + 78, "TIONS", "s", "middle")
    cx = lambda i: x0 + i * (w + g) + w / 2
    f.box(50, 96, 520, 86, "Foundation capital", "Upstream: Steps 1–3 and the ideation at Step 6")
    for i in (0, 1, 2, 5):
        f.arrow([(cx(i), 188), (cx(i), y - 12)], green=True)
    f.box(630, 430, 520, 86, "Brand and sponsor capital", "Enters only at Step 8, after Art is set")
    f.arrow([(cx(7), 424), (cx(7), y + 98)])
    f.line(x0 + 7 * (w + g) - g / 2, 214, x0 + 7 * (w + g) - g / 2, 372, w=4, dashed=True)
    f.text(x0 + 7 * (w + g) - g / 2, 206, "FIREWALL", "s", "middle")
    f.text(50, 420, "Crossing the regimes produces each kind", "t"); f.text(50, 446, "of capital's characteristic failure (§6.4).", "t")
    return f.save("axl-wp-03-figure3.svg")


def wp03_hsri():
    f = Fig(1200, 520, "FIG. 02 // THE HAFIZ SOCIETAL REPAIR INDEX",
            "The composite index adds three dimensions, preference honesty, integration velocity and coalition breadth, and subtracts a fourth, the capture index. Weights are proprietary.")
    specs = [("+", "Preference honesty", "Gap between private and public preference"),
             ("+", "Integration velocity", "Lag from art and journalism to clinic and institution"),
             ("+", "Coalition breadth", "How widely the vocabulary has spread"),
             ("−", "Capture index", "Sponsor identity predicting topic")]
    for i, (sgn, t, b) in enumerate(specs):
        x = 50 + i * 280
        f.box(x, 110, 250, 210, t, b, fill=GREEN if sgn == "−" else WHITE, tag=f"{sgn} DIMENSION {i+1}")
    f.text(600, 400, "HSRI = w₁·PH + w₂·IV + w₃·CB − w₄·CI", "b", "middle")
    f.text(600, 444, "Capture subtracts from repair. The weights are proprietary; the structure is public (§5.8).", "t", "middle")
    return f.save("axl-wp-03-figure2.svg")


def wp03_dce():
    f = Fig(1200, 560, "FIG. 01 // DOWNSTREAM CLINICAL EFFICIENCY, STEP BY STEP",
            "One million viewers times 10 percent conversion times 1,200 dollars of avoided clinical cost gives 120 million dollars. Against 0.5 to 2 million dollars of production cost the raw ratio is 60 to 1 through 240 to 1. Discounted by 90 percent, the defensible floor is 6 to 1 through 24 to 1.")
    steps = [("1,000,000", "viewers"), ("× 10%", "conversion"), ("× $1,200", "avoided clinical cost each"), ("= $120M", "avoided clinical load")]
    for i, (k, t) in enumerate(steps):
        x = 50 + i * 280
        f.box(x, 100, 250, 140, None, None, fill=GREEN if i == 3 else WHITE)
        f.text(x + 125, 165, k, "k", "middle"); f.text(x + 125, 205, t, "t", "middle", width=24)
    f.box(50, 300, 520, 150, None, None)
    f.text(70, 340, "AGAINST $0.5M – $2M PRODUCTION COST", "s"); f.text(70, 400, "60:1 – 240:1 raw", "k")
    f.arrow([(580, 375), (620, 375)])
    f.box(630, 300, 520, 150, None, None, fill=GREEN)
    f.text(650, 340, "AFTER A 90% DISCOUNT", "s"); f.text(650, 400, "6:1 – 24:1 floor", "k")
    f.text(50, 510, "The discount covers attribution, decay, partial uptake and the chance an artifact never reaches a million viewers (§4.3).", "t")
    return f.save("axl-wp-03-figure1.svg")


# ── WP-04 ────────────────────────────────────────────────────────────────
def wp04_pipeline():
    f = Fig(1200, 380, "FIG. 01 // THE PERMISSION PIPELINE",
            "Cultural object, then permission structure, then identity formation, then political mobilization.")
    specs = [("Cultural object", "A song, film, magazine, meme or gathering"),
             ("Permission", "Leave to feel or become what people already wanted"),
             ("Identity", "“This is who I am now”"),
             ("Mobilization", "“This is what people like me do”")]
    for i, (t, b) in enumerate(specs):
        x = 50 + i * 285
        f.box(x, 110, 245, 160, t, b, fill=GREEN if i == 0 else WHITE)
        if i < 3:
            f.arrow([(x + 251, 190), (x + 279, 190)])
    f.text(50, 330, "The far right already proved the pipeline works, without ethics or accountability (Layer 2).", "t")
    return f.save("axl-wp-04-figure1.svg")


def wp04_arab_spring():
    f = Fig(1200, 640, "FIG. 02 // THE ARAB SPRING, FROM TUNISIA OUTWARD",
            "Timeline. Before 2010 Arabic hip-hop builds a language of dissent. 7 November 2010, El Général releases Rais Lebled. 17 December 2010, Bouazizi's self-immolation sparks protests. 6 January 2011, secret police arrest El Général. 14 January 2011, Ben Ali flees. January to February 2011, the song is chanted in Tahrir Square.")
    ev = [("Before 2010", "Arabic hip-hop builds a language of dissent underground"),
          ("7 Nov 2010", "El Général releases “Rais Lebled”: the cultural object"),
          ("17 Dec 2010", "Bouazizi's self-immolation: protests without a narrative vehicle"),
          ("6 Jan 2011", "Police arrest El Général. The regime treats the song as a threat"),
          ("14 Jan 2011", "Ben Ali flees"),
          ("Jan–Feb 2011", "Tahrir Square chants “Rais Lebled”: the song crosses borders")]
    f.line(110, 110, 110, 590, w=4)
    for i, (d, t) in enumerate(ev):
        y = 120 + i * 80
        fill = GREEN if i in (1, 3) else WHITE
        f.raw(f'<rect x="98" y="{y}" width="24" height="24" fill="{fill}" stroke="{INK}" stroke-width="3"/>')
        f.text(150, y + 19, d.upper(), "s"); f.text(330, y + 19, t, "t")
    f.text(150, 618, "Twitter distributed the energy. The culture made it (Layer 6).", "t")
    return f.save("axl-wp-04-figure2.svg")


# ── WP-05 ────────────────────────────────────────────────────────────────
def wp05_timeline():
    f = Fig(1200, 480, "FIG. 01 // HOW THE OPERATING SYSTEM WAS INSTALLED",
            "Esalen opens at Big Sur in 1962. Branden's self-esteem theory follows in 1969. California's self-esteem task force is created in 1986 and in 1989 declares a link to social problems definitively confirmed, a claim the researchers knew was false. The Human Potential Movement then feeds Silicon Valley's founding mythology, and the attention economy optimizes for self-regard; AI is the newest amplifier.")
    ev = [("1962", "Esalen opens at Big Sur"), ("1969", "Branden's self-esteem theory"),
          ("1986", "California creates a self-esteem task force"), ("1989", "Report: link “definitively confirmed.” It wasn't"),
          ("Then", "Human potential becomes Silicon Valley founder myth"), ("Now", "AI: the most powerful validation engine yet")]
    for i, (y, t) in enumerate(ev):
        x = 50 + i * 186
        f.box(x, 120, 164, 220, y, t, fill=GREEN if y == "1989" else WHITE, cls="b")
        if i < 5:
            f.arrow([(x + 166, 230), (x + 184, 230)])
    f.text(50, 410, "1989 is where the Pretend Era begins: private knowledge and public claim part ways, and nobody corrects the record (§1.3).", "t", width=110)
    return f.save("axl-wp-05-figure1.svg")


def wp05_trap():
    f = Fig(1200, 860, "FIG. 02 // THE VALIDATION TRAP",
            "A clinical feedback loop. A patient who cannot tolerate reality meets a therapist trained to put the patient's subjective experience first. Empathic attunement confirms the self-concept instead of introducing reality-testing, and the dysfunction is reinforced.")
    loop(f, 600, 440, 250, [
        ("Patient", "Cannot yet tolerate an unwelcome reality"),
        ("Therapist", "Trained to put subjective experience first"),
        ("Attunement", "Confirms the self-concept"),
        ("Reinforcement", "Reality-testing never arrives"),
    ], bw=320, bh=118, green_idx=2)
    f.text(600, 820, "The way out is calibration: validation delivered with enough safety that reality can be taken in (§5.3).", "t", "middle")
    return f.save("axl-wp-05-figure2.svg")


# ── WP-06 ────────────────────────────────────────────────────────────────
def wp06_eurostar():
    f = Fig(1200, 440, "FIG. 01 // TWO WAYS TO IMPROVE A TRAIN",
            "Sutherland's Eurostar example. An engineering fix costing 6 billion pounds shortens London to Paris by forty minutes. A psychological fix costing a fraction of that, better wifi and free champagne, would produce more passenger satisfaction.")
    f.box(50, 110, 520, 170, "The engineering fix", "Spend £6 billion to cut forty minutes from London–Paris. It solves the objective problem.", tag="OBJECTIVE")
    f.box(630, 110, 520, 170, "The psychological fix", "Spend a fraction of that on better WiFi and free champagne. It solves the problem people experience.", fill=GREEN, tag="EXPERIENCED")
    f.text(600, 350, "Same journey. More satisfaction from the cheaper fix.", "b", "middle")
    f.text(600, 390, "Humans live in experience, not in engineering specifications (§I).", "t", "middle")
    return f.save("axl-wp-06-figure1.svg")


def wp06_scaling():
    f = Fig(1200, 520, "FIG. 02 // REPLICATION AND CULTIVATION",
            "Tangible infrastructure scales by replication: one blueprint, a thousand identical bridges. Intangible infrastructure scales by cultivation: shared method and measurement, with each local instance growing its own cultural specifics.")
    f.box(50, 100, 520, 110, "Tangible: replicate", "One blueprint, a thousand identical bridges")
    for i in range(5):
        f.raw(f'<rect x="{70 + i*98}" y="260" width="80" height="80" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>')
        f.text(110 + i * 98, 308, "■", "n", "middle")
    f.box(630, 100, 520, 110, "Intangible: cultivate", "Shared method and measurement, local growth", fill=GREEN)
    import random; random.seed(6)
    for i in range(5):
        h = [60, 92, 74, 104, 68][i]
        f.raw(f'<rect x="{650 + i*98}" y="{340-h}" width="80" height="{h}" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>')
    f.line(640, 360, 1140, 360, w=4)
    f.text(890, 392, "SHARED METHOD AND MEASUREMENT", "s", "middle")
    f.text(50, 470, "VICE tried to scale authenticity by replication and lost the emergence that made it valuable (§5.2).", "t", width=110)
    return f.save("axl-wp-06-figure2.svg")


# ── WP-07 ────────────────────────────────────────────────────────────────
def wp07_scoreboards():
    f = Fig(1200, 570, "FIG. 02 // ONE DOCKET, TWO SCOREBOARDS",
            "Illustrative. On a high-volume debt docket, more than seventy percent of cases end in default judgment without any look at the merits. Clearance counts every one of them as a case resolved. The merits-reached rate counts none of them.")
    f.text(50, 110, "ILLUSTRATIVE: 100 DISPOSED CASES ON A HIGH-VOLUME DEBT DOCKET", "s")
    for i in range(100):
        x = 50 + (i % 25) * 44; y = 130 + (i // 25) * 44
        f.raw(f'<rect x="{x}" y="{y}" width="34" height="34" fill="{INK if i < 70 else WHITE}" stroke="{INK}" stroke-width="2"/>')
    f.box(50, 330, 520, 150, "Clearance rate", "Every disposal counts. The 70+ defaults look like a fast, healthy court.", tag="COUNTS ALL 100")
    f.box(630, 330, 520, 150, "Merits-Reached Rate", "Counts only cases decided on their merits. The defaults score zero.", fill=GREEN, tag="DEFAULTS COUNT AS NOT REACHED")
    f.text(50, 530, "■ default judgment, no examination of the merits (Pew Charitable Trusts 2020)   □ other dispositions", "s")
    return f.save("axl-wp-07-figure2.svg")


# ── WP-09 ────────────────────────────────────────────────────────────────
def wp09_crucible():
    f = Fig(1200, 630, "FIG. 01 // THE CRUCIBLE: THREE ROOMS",
            "A funder publishes a question and underwrites one round. Anyone may submit a proposal or attack one. The Room evaluates: a random expert panel answers what it thinks and what it expects the panel to say, and payment follows the surprisingly popular answer. The Board prices each surviving proposal with a bounded-loss market maker that resolves against a fresh panel and an audit. The Draw allocates by weighted lottery among proposals above the threshold, with probabilities published in advance.")
    f.box(50, 100, 1100, 90, "A funder publishes a question and underwrites one round", "Anyone may submit a proposal. Anyone may attack one. Nobody bets.", fill=GREEN)
    specs = [("THE ROOM · EVALUATION", "Random expert panel", "Two questions: what you think, and what you expect the panel to say. Paid for the surprisingly popular answer."),
             ("THE BOARD · PRICING", "Bounded-loss market", "One price per surviving proposal: will a fresh panel, with an audit, judge it sound? Funder exposure fixed: b·ln(n)."),
             ("THE DRAW · ALLOCATION", "Weighted lottery", "Among everything above the threshold, with probabilities published in advance.")]
    for i, (tag, t, b) in enumerate(specs):
        x = 50 + i * 380
        f.box(x, 250, 340, 230, t, b, tag=tag)
        f.arrow([(x + 170, 196), (x + 170, 238)]) if i == 0 else f.arrow([(x - 34, 365), (x - 10, 365)])
    f.text(50, 550, "Because the Draw randomises among proposals review can't separate, it is also an experiment.", "t")
    f.text(50, 578, "Funded and unfunded proposals can be compared, so the process can measure its own accuracy (§5).", "t")
    return f.save("axl-wp-09-figure1.svg")


ALL = [wp01, wp01_timeline, wp02_loop, wp02_chain, wp03_firewall, wp03_hsri, wp03_dce, wp04_pipeline, wp04_arab_spring,
       wp05_timeline, wp05_trap, wp06_eurostar, wp06_scaling, wp07_scoreboards, wp09_crucible]

if __name__ == "__main__":
    for fn in ALL:
        print(fn())
