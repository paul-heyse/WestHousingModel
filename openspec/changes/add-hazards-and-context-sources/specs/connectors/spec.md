## ADDED Requirements

### Requirement: Hazard & Context Connectors

The system SHALL provide validated connectors for public datasets powering hazards and context features: USFS Wildfire Risk, USGS Seismic Design Maps, NOAA Storm Events, PAD-US, FCC BDC, HUD FMR, EIA v2, USFS Trails, and USGS EPQS.

#### Scenario: Wildfire risk percentiles

- **WHEN** fetching wildfire layers for a tract/block-group
- **THEN** the connector SHALL normalize to a frame including `place/property key`, `wildfire_risk_percentile`, `as_of`, `source_id`.

#### Scenario: Seismic PGA screen

- **WHEN** querying the USGS designmaps endpoint for a point
- **THEN** the connector SHALL return `pga_10in50_g` and `as_of`.

#### Scenario: Winter storm events

- **WHEN** aggregating NCEI storm events at county level
- **THEN** the connector SHALL return a 10-yr count as `winter_storms_10yr_county`.

#### Scenario: PAD-US outdoor access

- **WHEN** computing protected land within 30-min drive
- **THEN** the connector SHALL return `public_land_acres_30min` with units and `as_of` (MVP: vector overlay approximate if isochrones unavailable).

#### Scenario: Broadband flag

- **WHEN** deriving fixed availability from FCC BDC
- **THEN** the connector SHALL compute `broadband_gbps_flag` at tract/place level.

#### Scenario: HUD FMR & EIA utilities context

- **WHEN** fetching HUD FMR and EIA RES series
- **THEN** the connectors SHALL provide normalized frames used by valuation guardrails and ops scalers.
