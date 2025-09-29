## MODIFIED Requirements

### Requirement: Place Features (Pillars)

The system SHALL compute pillar components and pillar scores using normalized, provenance-backed inputs.

#### Scenario: Outdoor Access

- **WHEN** PAD-US acres within 30-min drive and nearest trailhead proxy are available
- **THEN** the system SHALL compute pillar components and aggregate to the Outdoor Access pillar.

### Requirement: Site Features (Hazards & Context)

The system SHALL compute site-level hazard and context fields.

#### Scenario: Hazard and climate fields

- **WHEN** wildfire, seismic, and storm events data are available
- **THEN** the system SHALL append `wildfire_risk_percentile`, `pga_10in50_g`, and `winter_storms_10yr_county` to site features with provenance.

#### Scenario: Broadband flag

- **WHEN** FCC BDC fixed availability indicates ≥1 Gbps service
- **THEN** the system SHALL set `broadband_gbps_flag` to True for the site/place.
