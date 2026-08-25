# auxlabs.co

Static site for Aux Labs LLC. Design system: Neu Brutalism (archival cyber-brutalism), by Samantha Byrd. Copy per AuxLabs-CORE-COPY-v4 + Build Context Pack v1.0 (2026-08-25).

## Pages

- `index.html` — Home
- `commercial.html` — 01_COMMERCIAL
- `research.html` — 02_RESEARCH (papers named, not linked — rolling publication)
- `cultural.html` — 03_CULTURAL

## Rules that live in the code

- **The invention rule**: no invented statistics, clients, credentials, dates or case studies. Unverified numbers are labeled as such (see Michelin card — "last verified 2017").
- **Client names as text, never logos.** Legally load-bearing.
- **Dark toggle** is a real token swap (`--paper-rgb / --ink-rgb / --surface-rgb / --panel-rgb` in each page's `<style>`), light-first by ruling.
- **Photo slots**: AI-generated imagery was removed. Search `PHOTO SLOT` comments for where owned photography drops in (use class `archival-duotone` treatment where noted).

## Deploy

Netlify, from this repo, publish directory `.` (see `netlify.toml`). Domain: auxlabs.co via Squarespace DNS — A `@` → 75.2.60.5, CNAME `www` → the Netlify site. **Never change nameservers** (Google Workspace mail lives on Squarespace DNS).

## Pending swaps

- Booking link: CTAs use `mailto:imran@auxlabs.co` until the booking link exists.
- Michelin current figures: update the two "last verified 2017" blocks when GCFP responds.
- Role detail for the five brand-strip clients: Imran to supply one line each.
- Behavioral-infrastructure field page: ruled binding 8/24, not yet built.
