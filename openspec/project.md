# Project Context

## Purpose

Build a local, explainable **Opportunity Identifier & Evaluator** for multifamily assets that aligns with Aker’s thesis (“urban convenience + outdoor lifestyles”) and investment process.

The tool surfaces high-fit places and sites, converts measurable public data into deal-ready features, and produces a defensible valuation (NOI/DCF, scores, and risk flags).
It is designed for a two-person team, runs on a laptop, and outputs IC-ready one-pagers with full source traceability.

---

## Tech Stack

- **Language**: Python 3.12
- **Data**: pandas, pyarrow, (optional) geopandas + shapely 2 + pyproj, pandera (validation)
- **I/O**: requests/httpx (sync), sqlite3, Parquet/GeoParquet, fsspec
- **GUI**: Streamlit (simple local app; alternative: Textual TUI for terminal)
- **Mapping/Isochrones**: folium/pydeck for display; OSRM/OpenRouteService for travel times
- **Testing**: pytest, hypothesis (property tests), coverage
- **Tooling**: black, ruff, isort, mypy, pre-commit, direnv
- **Docs**: Markdown in `openspec/`, data dictionary auto-generated from the source registry

---

## Project Conventions

### Code Style

- **Formatting**: black; 88-col line length
- **Linting**: ruff with sensible rules; isort for imports
- **Typing**: mypy (strict on `src/`, permissive on connectors initially)
- **Docstrings**: Google style on public functions; brief one-liners OK for internal helpers
- **Errors**: fail fast with clear messages; use custom exceptions in `core/` for common failure modes
- **DataFrames**: validate on function boundaries with Pandera; never return “untyped” frames

### Architecture Patterns

- Registry-driven connectors (repository pattern with read-through cache)
- Feature pipelines as pure functions (deterministic: inputs → features, no I/O)
- Small scoring/valuation engines (explicit, monotonic rules; no ML)
- Three domain entities only: **Place, Property, Scenario**
- UI orchestrates the above; exports capture inputs + data vintages for reproducibility
- `snake_case` package, single responsibility per module, short files (<300 lines where possible)

### Testing Strategy

- **Unit**: feature builders, scoring, valuation math (100% deterministic)
- **Integration**: connectors using fixtures (no live API in CI)
- **Golden**: one or two scenario end-to-end outputs compared to checked-in “golden” CSV/JSON
- **Performance**: smoke test building features for small batch (<50 sites) under time budget (e.g., <10s on dev machine)
- **Quality Gates**: pre-commit must pass locally; CI blocks merges on lint/type/test

### Git Workflow

- Trunk-based with short-lived feature branches: `feat/*`, `fix/*`, `chore/*`
- Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`)
- PR checks: lint + type + tests + screenshot of any UI change
- Release: tag `vX.Y.Z` with summary from `openspec/changes`; attach small artifact (zip with Streamlit runner + sample caches)

---

## Domain Context

- **Aker focus**: Residential communities blending urban convenience (walkability, transit, daily needs) with outdoor lifestyles (access to trails, parks, public lands)
- **Geography priority**: Colorado, Utah, Idaho (Front Range, Wasatch Front, Treasure Valley), extensible to other states
- **Value creation**: better resident experience & retention, targeted value-add capex, community/brand programs
- **Evaluation approach**: measurable place & site features → Aker Fit score; hazard & operating context → insurance/OpEx adjustments; market fundamentals → rents and growth; clear NOI/DCF outputs

---

## Important Constraints

- Small team, local use (no managed infra)
- Explainability over complexity (lender/IC-friendly)
- Measured data only (no news scraping; laws captured as binary flags/parameters when authoritative & stable)
- Licenses must be honored (avoid proprietary ratings unless licensed)
- Performance: interactive on a laptop; keep heavy geo work minimal
- Reproducibility: every output includes sources + vintages and any manual overrides

---

## External Dependencies

*(from sources registry, distilled into major classes)*

- **Market & Population**: BLS CES/LAUS; Census ACS; Census Building Permits Survey
- **Rents**: Zillow Research (ZORI); (optional) Apartment List, Redfin
- **Hazards/Climate**: FEMA NFHL (flood), USGS seismic (PGA screen), USFS Wildfire Risk to Communities, NOAA Climate Normals & Storm Events
- **Access & Mobility**: OpenStreetMap (POIs via Overpass); OSRM/OpenRouteService (isochrones)
- **Outdoor Assets**: Protected Areas Database (PAD-US), USFS trails, NPS, RIDB
- **Ops Context**: EIA rates, OpenEI URDB (tariffs), FCC BDC (broadband)
- **Policy (optional/flagged)**: National Zoning Atlas; municipal GIS (ArcGIS/Socrata); state water resources (CO/UT/ID) for context notes
- **UI/Export**: Streamlit; reportlab/WeasyPrint (or similar) for PDF; pyarrow for Parquet
