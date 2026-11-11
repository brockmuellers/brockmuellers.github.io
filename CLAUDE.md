# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Philosophy

This is a low-traffic personal website. Prioritize code simplicity and developer ergonomics over performance, scalability, or abstraction. Suggest simplifications whenever you see an opportunity.

## Commands

```bash
# Local development server (localhost:4000)
bundle exec jekyll serve --trace --drafts
# With local config overrides (e.g. local API endpoints); _config.local.yml is gitignored
bundle exec jekyll serve --trace --drafts --config _config.yml,_config.local.yml

# Generate resume PDF from _data/resume.yml
./build_resumes.sh [DATE_FOR_BACKUP]

# Import plant data from CSV
./import_plants.sh [CSV_FILE]
```

## Architecture

**Jekyll static site** hosted on GitHub Pages. Uses the minima 2.5.1 theme with SCSS overrides in `assets/main.scss`. No Node.js/npm — pure Ruby/Jekyll.

**Content sources:**
- Markdown pages in root (`travels.md`, `plants.md`, `about.md`, `resume.md`, etc.)
- Blog posts in `_posts/`, articles in `_more/` (a Jekyll collection outputting to `/more/:path`)
- YAML data files in `_data/`: `travels.yml`, `resume.yml`, `image_source.yml`
- Plant database: `_data/plants.csv`

**Interactive features** use inline JavaScript within Markdown pages:
- `travels.md` — MapLibre GL 3.6.2 interactive map with trip tracks (GeoJSON in `assets/gpx/`, derived from GPX), iNaturalist and eBird GeoJSON observations (`assets/observations/`), waypoints and search via the travel-log API (`travel_log_api` and `travel_log_site_token` in `_config.yml`), and multi-tab trip filtering configured in `_data/travels.yml`
- `plants.md` — DataTables 1.10.20 for sortable/filterable plant database
- `birds.md`, `_more/birdnet-station.md`, `_more/birdnet-weather.md` — BirdNET-Pi detections, station health, and weather, fetched as JSON from `birdnet-data.brockmuellers.com`. Shared SVG chart helpers live in `_includes/chart.html`. The weather page's normals come from `assets/weather/climatology.json`, built once by `./build_climatology.py`

**Resume** is data-driven: `_data/resume.yml` → JSON conversion → LaTeX compilation via LuaLaTeX → PDF in `assets/resume/`.

**Image attribution** is tracked in `_data/image_source.yml` and rendered via `_includes/sourced_image.html`.
