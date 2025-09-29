import pandas as pd

from west_housing_model.features.site_features import (
    build_site_features_from_components,
    extract_provenance,
)


def test_build_site_features_from_components_happy_path():
    base = pd.DataFrame(
        {
            "property_id": ["p1"],
            "place_id": ["pl1"],
            "latitude": [39.74],
            "longitude": [-104.99],
        }
    )

    hazards = pd.DataFrame(
        {
            "property_id": ["p1"] * 9,
            "hazard_type": [
                "in_sfha",
                "wildfire_risk_percentile",
                "pga_10in50_g",
                "hdd_annual",
                "cdd_annual",
                "rail_within_300m_flag",
                "winter_storms_10yr_county",
                "minutes_to_trailhead",
                "broadband_gbps_flag",
            ],
            "value": [None, 87, 0.18, 6200, 900, None, 5, 18.5, None],
            "flag": [True, None, None, None, None, True, None, None, True],
            "as_of": [pd.Timestamp("2025-01-01")] * 9,
            "source_id": [
                "fema_nfhl",
                "usfs_wildfire_risk",
                "usgs_seismic_designmaps",
                "noaa_normals",
                "noaa_normals",
                "pipelines_prox",
                "connector.noaa_storm_events",
                "connector.usfs_trails",
                "connector.fcc_bdc",
            ],
        }
    )

    out = build_site_features_from_components(base, hazards)

    # Required columns exist and validate types
    for col in [
        "property_id",
        "place_id",
        "latitude",
        "longitude",
        "as_of",
        "source_id",
        "in_sfha",
        "wildfire_risk_percentile",
        "pga_10in50_g",
        "hdd_annual",
        "cdd_annual",
        "rail_within_300m_flag",
        "winter_storms_10yr_county",
        "minutes_to_trailhead",
        "broadband_gbps_flag",
    ]:
        assert col in out.columns

    assert out.loc[0, "property_id"] == "p1"
    # Flags and values propagated
    assert out.loc[0, "in_sfha"] is True
    assert out.loc[0, "wildfire_risk_percentile"] == 87
    assert out.loc[0, "pga_10in50_g"] == 0.18
    assert out.loc[0, "hdd_annual"] == 6200
    assert out.loc[0, "cdd_annual"] == 900
    assert out.loc[0, "rail_within_300m_flag"] is True
    assert out.loc[0, "winter_storms_10yr_county"] == 5
    assert out.loc[0, "minutes_to_trailhead"] == 18.5
    assert out.loc[0, "broadband_gbps_flag"] is True


def test_extract_provenance_sidecar_fields():
    hazards = pd.DataFrame(
        {
            "property_id": ["p1", "p1"],
            "hazard_type": ["in_sfha", "pga_10in50_g"],
            "value": [None, 0.2],
            "flag": [False, None],
            "as_of": [pd.Timestamp("2024-12-01"), pd.Timestamp("2024-11-01")],
            "source_id": ["fema_nfhl", "usgs_seismic_designmaps"],
        }
    )
    prov = extract_provenance(hazards)
    assert prov["in_sfha"]["source_id"] == "fema_nfhl"
    assert str(prov["in_sfha"]["as_of"]).startswith("2024-12-01")
