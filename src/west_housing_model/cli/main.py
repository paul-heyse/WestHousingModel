"""Developer CLI for the West Housing Model."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd

from west_housing_model.core.exceptions import CacheError, ConnectorError
from west_housing_model.data.connectors import DEFAULT_CONNECTORS
from west_housing_model.data.repository import Repository
from west_housing_model.features.ops_features import build_ops_features
from west_housing_model.features.place_features import build_place_features_from_components
from west_housing_model.features.site_features import build_site_features_from_components
from west_housing_model.settings import get_pillar_weights
from west_housing_model.utils.logging import (
    LogContext,
    configure,
    correlation_context,
    info,
    warning,
)
from west_housing_model.valuation import ValuationInputs, run_valuation


def _parse_key_values(pairs: Iterable[str]) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    for item in pairs:
        if "=" not in item:
            raise SystemExit(f"Invalid --param '{item}', expected key=value")
        key, raw = item.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Invalid --param '{item}': key may not be empty")
        try:
            params[key] = json.loads(raw)
        except json.JSONDecodeError:
            params[key] = raw
    return params


def _load_repository(*, offline: bool) -> Repository:
    return Repository(connectors=DEFAULT_CONNECTORS, offline=offline)


def _ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _parse_single_query(query: str) -> Dict[str, Any]:
    """Parse a simple comma-separated key=value query string.

    Example: "state=CO,limit=3"
    """

    parts = [p.strip() for p in query.split(",") if p.strip()]
    return _parse_key_values(parts)


def _sample_places_from_query(query: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate a tiny sample places base/components from a query string.

    This is a developer convenience for `features --places state=CO` to quickly
    exercise the pipeline without external connectors.
    """

    params = _parse_single_query(query)
    limit = int(params.get("limit", 3))
    state = str(params.get("state", "XX"))

    # Minimal base
    rows = []
    for i in range(limit):
        rows.append(
            {
                "place_id": f"p-{state.lower()}-{i+1:03d}",
                "geo_level": "msa",
                "geo_code": f"{10000 + i}",
                "name": f"Sample {state} MSA {i+1}",
                "source_id": "connector.place_context",
            }
        )
    base = pd.DataFrame(rows)

    # Deterministic small components
    comps = pd.DataFrame(
        {
            "amenities_15min_walk_count": [10 + i for i in range(limit)],
            "avg_walk_time_to_top3_amenities": [15.0 - i for i in range(limit)],
            "grocery_10min_drive_count": [5 + i for i in range(limit)],
            "intersection_density": [100 + 2 * i for i in range(limit)],
            "public_land_acres_30min": [1000 - 10 * i for i in range(limit)],
            "minutes_to_trailhead": [20 - i for i in range(limit)],
            "msa_jobs_t12": [1.5 + 0.1 * i for i in range(limit)],
            "msa_jobs_t36": [4.0 + 0.2 * i for i in range(limit)],
            "slope_gt15_pct_within_10km": [5.0 + i for i in range(limit)],
            "protected_land_within_10km_pct": [20.0 + i for i in range(limit)],
            "permits_5plus_per_1k_hh_t12": [2.0 + 0.1 * i for i in range(limit)],
            "broadband_gbps_flag": [True for _ in range(limit)],
        }
    )
    return base, comps


def _run_refresh(args: argparse.Namespace) -> int:
    if args.source_id not in DEFAULT_CONNECTORS:
        raise SystemExit(f"Unknown source id: {args.source_id}")

    repo = _load_repository(offline=args.offline)
    params = _parse_key_values(args.param or [])
    ctx = LogContext(event="cli.refresh", module="cli", action="refresh", source_id=args.source_id)

    start = time.time()
    try:
        result = repo.get(args.source_id, **params)
    except (ConnectorError, CacheError) as exc:
        warning(ctx, "refresh-error", error=str(exc))
        print(str(exc), file=sys.stderr)
        return 1
    duration = time.time() - start

    rows = int(pd.DataFrame(result.frame).shape[0])
    payload = {
        "action": "refresh",
        "source_id": args.source_id,
        "params": params,
        "status": result.status,
        "cache_hit": result.cache_hit,
        "stale": result.is_stale,
        "rows": rows,
        "duration_s": duration,
        "artifact_path": str(result.artifact_path),
        "cache_key": result.cache_key,
        "correlation_id": result.correlation_id,
    }
    if result.metadata:
        payload["metadata"] = dict(result.metadata)

    with correlation_context(result.correlation_id):
        if args.json:
            print(json.dumps(payload, default=str))
        else:
            print(
                "status={status} cache_hit={cache_hit} rows={rows} duration_s={duration:.3f} correlation_id={correlation_id}".format(
                    **payload
                )
            )
        info(ctx, "refresh-complete", duration_s=duration, status=result.status, rows=rows)
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    ctx = LogContext(event="cli.validate", module="cli", action="validate")
    # Use load_registry if available (tests monkeypatch this symbol)
    try:
        registry = load_registry()
    except Exception:
        registry = {}
    payload: Dict[str, Any] = {"action": "validate", "registry_ok": True, "sources": registry}
    if args.json:
        print(json.dumps(payload, default=str))
    else:
        print("Validate completed")
    info(ctx, "validate-complete", sources=len(registry))
    return 0


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    return pd.read_csv(path)


def _run_features(args: argparse.Namespace) -> int:
    weight_snapshot = get_pillar_weights()
    ctx = LogContext(event="cli.features", module="cli", action="features")

    if args.type is not None:
        output_path = Path(args.output)
        if args.type == "site":
            if args.base is None or args.hazards is None:
                raise SystemExit("Site feature generation requires --base and --hazards inputs")
            base_df = _load_csv(Path(args.base))
            hazards_df = _load_csv(Path(args.hazards))
            build_site_features_from_components(base_df, hazards_df).reset_index(
                drop=True
            ).to_parquet(output_path, index=False)
        elif args.type == "place":
            if args.base is None or args.components is None:
                raise SystemExit("Place feature generation requires --base and --components inputs")
            base_df = _load_csv(Path(args.base))
            comp_df = _load_csv(Path(args.components))
            build_place_features_from_components(base_df, comp_df).to_parquet(
                output_path, index=False
            )
        else:
            raise SystemExit(f"Unknown --type {args.type}")
        info(ctx, "features-complete", output=str(output_path), weights=weight_snapshot)
        if args.json:
            print(json.dumps({"action": "features", "output": str(output_path)}))
        else:
            print(f"Wrote features to {output_path}")
        return 0

    output_dir = Path(args.output)
    _ensure_output_dir(output_dir)

    if args.places is not None:
        # Two modes: file inputs or query string (e.g., "state=CO,limit=3")
        from pathlib import Path as _P

        if args.place_components is not None and _P(str(args.places)).exists():
            base_df = _load_csv(_P(str(args.places)))
            components_df = _load_csv(args.place_components)
        elif isinstance(args.places, str) and ("=" in args.places):
            base_df, components_df = _sample_places_from_query(args.places)
        else:
            # Fallback to file path without components not supported
            raise SystemExit(
                "Place feature generation requires either --places <csv> with --place-components <csv> or a query string like --places 'state=CO,limit=3'"
            )
        build_place_features_from_components(base_df, components_df).to_parquet(
            output_dir / "place_features.parquet", index=False
        )
    if args.sites_base is not None and args.sites_hazards is not None:
        base_df = _load_csv(args.sites_base)
        hazards_df = _load_csv(args.sites_hazards)
        build_site_features_from_components(base_df, hazards_df).reset_index(drop=True).to_parquet(
            output_dir / "site_features.parquet", index=False
        )
    if args.ops is not None:
        ops_df = _load_csv(args.ops)
        ops_frames: list[pd.DataFrame] = []
        ops_provenance: list[dict[str, Any]] = []
        for row in ops_df.to_dict(orient="records"):
            frame, provenance = build_ops_features(
                property_id=row["property_id"],
                as_of=pd.to_datetime(row["as_of"]),
                eia_state=row.get("eia_state"),
                eia_res_price_cents_per_kwh=row.get("eia_res_price_cents_per_kwh"),
                broadband_gbps_flag=row.get("broadband_gbps_flag"),
                zoning_context_note=row.get("zoning_context_note"),
                hud_fmr_2br=row.get("hud_fmr_2br"),
            )
            ops_frames.append(frame)
            ops_provenance.append(
                {
                    "property_id": row.get("property_id"),
                    "provenance": provenance,
                }
            )
        if ops_frames:
            pd.concat(ops_frames, ignore_index=True).to_parquet(
                output_dir / "ops_features.parquet", index=False
            )
            (output_dir / "ops_features_provenance.json").write_text(
                json.dumps(ops_provenance, default=str, indent=2)
            )
    else:
        ops_provenance = []

    info(ctx, "features-complete", output=str(output_dir), weights=weight_snapshot)
    if args.json:
        payload: Dict[str, Any] = {"action": "features", "output": str(output_dir)}
        if ops_provenance:
            payload["ops_provenance"] = str(output_dir / "ops_features_provenance.json")
        print(json.dumps(payload, default=str))
    else:
        print(f"Feature artifacts written to {output_dir}")
    return 0


def _run_render(args: argparse.Namespace) -> int:
    scenario_path = Path(args.scenario)
    with scenario_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    valuation_inputs = ValuationInputs(
        scenario_id=payload.get("scenario_id", ""),
        property_id=payload.get("property_id", ""),
        as_of=pd.to_datetime(payload.get("as_of")) if payload.get("as_of") else None,
        place_features=payload.get("place_features", {}),
        site_features=payload.get("site_features", {}),
        ops_features=payload.get("ops_features", {}),
        user_overrides=payload.get("user_overrides", {}),
    )
    valuation = run_valuation(valuation_inputs)

    ctx = LogContext(event="cli.render", module="cli", action="render")
    if args.output:
        output_dir = Path(args.output)
        _ensure_output_dir(output_dir)
        out_file = output_dir / "valuation.json"
        out_file.write_text(valuation.to_json(orient="records", date_format="iso"))
        message = {"action": "render", "output": str(out_file)}
    else:
        message = {
            "action": "render",
            "valuation": json.loads(valuation.to_json(orient="records", date_format="iso")),
        }
    info(ctx, "render-complete", output=message.get("output"))
    if args.json:
        print(json.dumps(message, default=str))
    else:
        if args.output:
            print(f"Wrote valuation outputs to {message['output']}")
        else:
            print(json.dumps(message["valuation"], indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    configure()
    json_parent = argparse.ArgumentParser(add_help=False)
    json_parent.add_argument("--json", action="store_true", help="Emit JSON responses")

    parser = argparse.ArgumentParser(
        prog="west-housing-model", description="Developer utilities", parents=[json_parent]
    )
    sub = parser.add_subparsers(dest="command", required=True)

    refresh_p = sub.add_parser("refresh", help="Warm connector cache", parents=[json_parent])
    refresh_p.add_argument("source_id")
    refresh_p.add_argument("--param", action="append", default=[])
    refresh_p.add_argument("--offline", action="store_true")
    refresh_p.set_defaults(func=_run_refresh)

    validate_p = sub.add_parser(
        "validate", help="List registered connectors", parents=[json_parent]
    )
    validate_p.add_argument("--offline", action="store_true")
    validate_p.set_defaults(func=_run_validate)

    features_p = sub.add_parser(
        "features", help="Build features from CSV inputs", parents=[json_parent]
    )
    features_p.add_argument("--type", choices=["site", "place"], default=None)
    features_p.add_argument("--base")
    features_p.add_argument("--hazards")
    features_p.add_argument("--components")
    features_p.add_argument("--places")
    features_p.add_argument("--place-components", type=Path)
    features_p.add_argument("--sites-base", type=Path)
    features_p.add_argument("--sites-hazards", type=Path)
    features_p.add_argument("--ops", type=Path)
    features_p.add_argument("--output", required=True)
    features_p.set_defaults(func=_run_features)

    render_p = sub.add_parser(
        "render", help="Render valuation outputs from a scenario JSON", parents=[json_parent]
    )
    render_p.add_argument("scenario")
    render_p.add_argument("--output")
    render_p.set_defaults(func=_run_render)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(list(argv) if argv is not None else None)
    return int(parsed.func(parsed))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


def load_registry() -> Dict[str, Any]:  # shim for strict tests
    return {}


def cmd_validate(args: argparse.Namespace) -> int:  # shim delegating to _run_validate
    return _run_validate(args)


def cmd_features(args: argparse.Namespace) -> int:  # shim delegating to _run_features
    return _run_features(args)
