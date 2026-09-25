# auxlabs.co

Static site for Aux Labs LLC. Design system: Neu Brutalism (archival cyber-brutalism), by Samantha Byrd. Copy per AuxLabs-CORE-COPY-v4 + Build Context Pack v1.0 (2026-08-25).

## Pages

- `index.html` — Home
- `commercial.html` — 01_COMMERCIAL
- `research.html` — 02_RESEARCH (working-paper index; papers in `papers/`, plain-text editions in `plain/`)
- `why-us.html` — 03_WHY_US (replaced `cultural.html`; `/cultural` redirects here)
- `terms.html` — The Terms: how we price and make deals
- `field.html` — The Field: the lexicon
- `firewall.html` — The Firewall: conflicts governance
- `record.html` — The Record: every checkable claim
- `provenance.html` — AI Disclosure (also served at `/ai-disclosure`)

## Rules that live in the code

- **The invention rule**: no invented statistics, clients, credentials, dates or case studies. Unverified numbers are labeled as such (see Michelin card — "last verified 2017").
- **Client names as text, never logos.** Legally load-bearing.
- **Dark toggle** is a real token swap (`--paper-rgb / --ink-rgb / --surface-rgb / --panel-rgb` in each page's `<style>`), light-first by ruling.
- **Stylesheet**: `assets/tailwind.css` is compiled, and a fresh build from `src/input.css` does not reproduce it byte-for-byte. Use utilities that already exist in the compiled file; put anything new in a page-local `<style>` block (see `terms.html`).
- **Photo slots**: AI-generated imagery was removed. Search `PHOTO SLOT` comments for where owned photography drops in (use class `archival-duotone` treatment where noted).

## Deploy

Netlify, from this repo, publish directory `.` (see `netlify.toml`). Domain: auxlabs.co via Squarespace DNS — A `@` → 75.2.60.5, CNAME `www` → the Netlify site. **Never change nameservers** (Google Workspace mail lives on Squarespace DNS).

## Pending swaps

- Booking link: live (Google Calendar) on Home, Commercial, Why Us and Terms CTAs.
- Michelin current figures: update the two "last verified 2017" blocks when GCFP responds.
- Role detail for the brand-strip clients: Imran to supply one line each.
- Before merge: pick homepage hero 1/2/3 (preview with `?hero=1|2|3`), then remove the PREVIEW ONLY script at the bottom of `index.html`.

## Future (not in the current merge)

- **Video testimonials**: short clips from former colleagues and collaborators, recorded as an interview series with a third-party host.
- **Guestbook / public feedback**: moderated (Netlify Forms), with selected entries published; likely home is the foot of The Record.
