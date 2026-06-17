"""Allocate SGIS tract statistics to Pangyo and Cheongna PNU-based boundaries.

Edit the path constants below when new SGIS boundary files are added, then rerun:

    python scripts/04_preprocess_sgis_by_pnu_boundary.py
"""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import geopandas as gpd
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_CRS = "EPSG:5179"
OUTPUT_CRS = "EPSG:4326"

# Existing verified boundaries are reused. They were already built from PROM/PNU inputs.
PANGYO_BOUNDARY_INPUT = (
    PROJECT_ROOT / "data_processed/boundaries/pangyo_validation/pangyo_main_boundary.geojson"
)
CHEONGNA_BOUNDARY_INPUT = (
    PROJECT_ROOT / "data_raw/boundary/cheongna/cheongna_ibd_boundary.geojson"
)
PANGYO_PNU_INPUT = (
    PROJECT_ROOT / "data_processed/boundaries/pangyo_validation/pangyo_main_pnu_verified.csv"
)
CHEONGNA_PNU_INPUT = (
    PROJECT_ROOT / "data_raw/boundary/cheongna/prom_cheongna_ibd_pnu_2026-06-12.xlsx"
)
PANGYO_PROM_ROOT = (
    PROJECT_ROOT / "data_raw/boundary/pangyo/prom_pangyo_spatial_2026-06-12"
)
CHEONGNA_PROM_ZIP = (
    PROJECT_ROOT / "data_raw/boundary/cheongna/prom_cheongna_ibd_spatial_2026-06-12.zip"
)

SGIS_ROOT = PROJECT_ROOT / "data_raw/sgis/request_1781257203152"

PANGYO_SGIS_BOUNDARY = (
    PROJECT_ROOT / "data_raw/sgis/boundaries/bnd_oa_31_2025_2Q/bnd_oa_31_2025_2Q.shp"
)
CHEONGNA_SGIS_BOUNDARY = (
    PROJECT_ROOT / "data_raw/sgis/boundaries/bnd_oa_23_2025_2Q/bnd_oa_23_2025_2Q.shp"
)

BOUNDARY_OUTPUT_DIR = PROJECT_ROOT / "data_processed/boundaries"
PARCEL_OUTPUT_DIR = PROJECT_ROOT / "data_processed/parcels"
SGIS_OUTPUT_DIR = PROJECT_ROOT / "data_processed/sgis"
SUMMARY_OUTPUT_DIR = PROJECT_ROOT / "data_processed/summary"

REGIONS = {
    "pangyo": {
        "name": "제1판교테크노밸리",
        "reference_area_sqm": 674923.28,
        "sgis_code": "31023",
        "sgis_file_prefix": "31_",
        "sgis_stats_dir": SGIS_ROOT,
        "boundary_input": PANGYO_BOUNDARY_INPUT,
        "boundary_output": BOUNDARY_OUTPUT_DIR / "pangyo_main_boundary.geojson",
        "parcel_output": PARCEL_OUTPUT_DIR / "pangyo_parcels_filtered.geojson",
        "intersection_output": SGIS_OUTPUT_DIR / "pangyo_sgis_intersection.geojson",
        "sgis_boundary": PANGYO_SGIS_BOUNDARY,
    },
    "cheongna": {
        "name": "청라국제업무단지",
        "reference_area_sqm": 359301.46,
        "sgis_code": "23080",
        "sgis_file_prefix": "23_",
        "sgis_stats_dir": SGIS_ROOT,
        "boundary_input": CHEONGNA_BOUNDARY_INPUT,
        "boundary_output": BOUNDARY_OUTPUT_DIR / "cheongna_main_boundary.geojson",
        "parcel_output": PARCEL_OUTPUT_DIR / "cheongna_parcels_filtered.geojson",
        "intersection_output": SGIS_OUTPUT_DIR / "cheongna_sgis_intersection.geojson",
        "sgis_boundary": CHEONGNA_SGIS_BOUNDARY,
    },
}

SGIS_CODE_FIELDS = (
    "TOT_OA_CD",
    "tot_oa_cd",
    "OA_CD",
    "oa_cd",
    "oa_code",
    "tract_id",
    "집계구코드",
)


def log(lines: list[str], message: str) -> None:
    print(message)
    lines.append(message)


def read_simple_xlsx(path: Path) -> pd.DataFrame:
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [
                "".join(node.text or "" for node in item.iterfind(".//m:t", namespace))
                for item in root.findall("m:si", namespace)
            ]
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.findall(".//m:sheetData/m:row", namespace):
            values = []
            for cell in row.findall("m:c", namespace):
                value_node = cell.find("m:v", namespace)
                value = "" if value_node is None else value_node.text
                if cell.attrib.get("t") == "s" and value:
                    value = shared[int(value)]
                values.append(value)
            rows.append(values)
    return pd.DataFrame(rows[1:], columns=rows[0])


def find_parcel_layer(root: Path) -> Path:
    for path in root.rglob("*.shp"):
        if "jimok" in gpd.read_file(path, encoding="cp949", rows=1).columns:
            return path
    raise FileNotFoundError(f"No PROM parcel layer with a jimok field under {root}")


def read_pnus(region: str) -> set[str]:
    if region == "pangyo":
        frame = pd.read_csv(PANGYO_PNU_INPUT, dtype={"pnu": str})
    else:
        frame = read_simple_xlsx(CHEONGNA_PNU_INPUT)
    return set(frame["pnu"].astype(str).str.strip())


def build_filtered_parcels(
    region: str, boundary_5179: gpd.GeoDataFrame, temporary_root: Path
) -> gpd.GeoDataFrame:
    if region == "pangyo":
        parcel_path = find_parcel_layer(PANGYO_PROM_ROOT)
    else:
        extract_root = temporary_root / "cheongna_prom"
        with ZipFile(CHEONGNA_PROM_ZIP) as archive:
            archive.extractall(extract_root)
        parcel_path = find_parcel_layer(extract_root)

    parcels = gpd.read_file(parcel_path, encoding="cp949").to_crs(TARGET_CRS)
    parcels["pnu"] = parcels["pnu"].astype(str).str.strip()
    requested_pnus = read_pnus(region)
    filtered = parcels[parcels["pnu"].isin(requested_pnus)].copy()
    if filtered.empty:
        raise ValueError(f"{region}: no parcel polygons matched the PNU list")
    missing_pnus = requested_pnus - set(filtered["pnu"])
    if missing_pnus:
        raise ValueError(
            f"{region}: {len(missing_pnus)} PNU values did not match parcel polygons: "
            f"{sorted(missing_pnus)[:10]}"
        )

    # Clip long road/park parcels to the already verified district boundary.
    district = boundary_5179.geometry.union_all()
    filtered["original_parcel_area_sqm"] = filtered.geometry.area
    filtered.geometry = filtered.geometry.intersection(district)
    filtered = filtered[~filtered.geometry.is_empty].copy()
    filtered["included_area_sqm"] = filtered.geometry.area
    filtered["included_share"] = (
        filtered["included_area_sqm"] / filtered["original_parcel_area_sqm"]
    )
    return filtered


def read_sgis_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        header=None,
        names=["year", "tract_id", "metric", "value"],
        dtype=str,
        encoding="cp949",
    )
    frame["tract_id"] = frame["tract_id"].str.strip()
    frame["value_raw"] = frame["value"]
    frame["value"] = pd.to_numeric(frame["value"].replace("N/A", pd.NA), errors="coerce")
    return frame


def find_stat_file(
    directory: Path,
    includes: tuple[str, ...],
    excludes: tuple[str, ...] = (),
    filename_prefix: str = "",
) -> Path:
    matches = [
        path
        for path in directory.glob("*.csv")
        if path.name.startswith(filename_prefix)
        if all(part in path.name for part in includes)
        and not any(part in path.name for part in excludes)
    ]
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected one SGIS CSV containing {includes} under {directory}; found {matches}"
        )
    return matches[0]


def standardize_sgis_stats(
    directory: Path, filename_prefix: str, region_code: str, lines: list[str]
) -> pd.DataFrame:
    population_file = find_stat_file(
        directory, ("인구총괄",), filename_prefix=filename_prefix
    )
    workers_file = find_stat_file(
        directory, ("대분류", "종사자수"), filename_prefix=filename_prefix
    )
    businesses_file = find_stat_file(
        directory, ("대분류", "사업체수"), ("총괄",), filename_prefix
    )
    total_businesses_file = find_stat_file(
        directory, ("대분류", "총괄사업체수"), filename_prefix=filename_prefix
    )

    population_raw = read_sgis_csv(population_file)
    workers_raw = read_sgis_csv(workers_file)
    businesses_raw = read_sgis_csv(businesses_file)
    total_businesses_raw = read_sgis_csv(total_businesses_file)

    for frame in (population_raw, workers_raw, businesses_raw, total_businesses_raw):
        frame.drop(
            frame[~frame["tract_id"].str.startswith(region_code)].index,
            inplace=True,
        )

    population = population_raw[population_raw["metric"] == "to_in_001"].copy()
    total_businesses = total_businesses_raw[
        total_businesses_raw["metric"] == "to_fa_010"
    ].copy()

    # Industry-category values are summed because the statewide request has no
    # separate total-workers file. Protected/missing category values become zero.
    worker_missing = int(workers_raw["value"].isna().sum())
    workers_raw["value"] = workers_raw["value"].fillna(0)
    workers = workers_raw.groupby("tract_id", as_index=False)["value"].sum()
    business_missing = int(businesses_raw["value"].isna().sum())
    businesses_raw["value"] = businesses_raw["value"].fillna(0)
    businesses = businesses_raw.groupby("tract_id", as_index=False)["value"].sum()

    standardized = (
        population[["tract_id", "value"]]
        .rename(columns={"value": "population"})
        .merge(
            workers.rename(columns={"value": "workers"}),
            on="tract_id",
            how="outer",
        )
        .merge(
            businesses.rename(columns={"value": "businesses"}),
            on="tract_id",
            how="outer",
        )
        .merge(
            total_businesses[["tract_id", "value"]].rename(
                columns={"value": "total_businesses"}
            ),
            on="tract_id",
            how="outer",
        )
    )

    value_fields = ["population", "workers", "businesses", "total_businesses"]
    missing_counts = standardized[value_fields].isna().sum().to_dict()
    standardized[value_fields] = standardized[value_fields].fillna(0)
    standardized["population_year"] = population_raw["year"].iloc[0]
    standardized["employment_business_year"] = workers_raw["year"].iloc[0]
    standardized["region_code"] = region_code

    log(lines, f"  SGIS standardized tracts: {len(standardized)}")
    log(lines, f"  SGIS industry workers summed; protected/missing -> 0: {worker_missing}")
    log(lines, f"  SGIS protected N/A in industry businesses -> 0: {business_missing}")
    log(lines, f"  SGIS missing after outer join -> 0: {missing_counts}")
    return standardized


def auto_find_sgis_boundary(region_code: str) -> Path | None:
    candidates = []
    for extension in ("*.shp", "*.geojson", "*.gpkg"):
        candidates.extend(PROJECT_ROOT.glob(f"data_raw/sgis/**/*{region_code}*{extension[1:]}"))
    return candidates[0] if candidates else None


def detect_tract_code_field(frame: gpd.GeoDataFrame, region_code: str) -> str:
    for field in SGIS_CODE_FIELDS:
        if field in frame.columns:
            return field
    for field in frame.columns.drop("geometry", errors="ignore"):
        values = frame[field].astype(str)
        if values.str.fullmatch(r"\d{14}").mean() > 0.9 and values.str.startswith(region_code).mean() > 0.9:
            return field
    raise ValueError(f"Could not detect a 14-digit SGIS tract code field: {frame.columns.tolist()}")


def intersect_and_allocate(
    region: str,
    boundary: gpd.GeoDataFrame,
    stats: pd.DataFrame,
    sgis_boundary_path: Path,
    lines: list[str],
) -> tuple[gpd.GeoDataFrame, dict[str, float], pd.DataFrame]:
    sgis = gpd.read_file(sgis_boundary_path)
    if sgis.crs is None:
        raise ValueError(f"{sgis_boundary_path}: missing CRS")
    sgis = sgis.to_crs(TARGET_CRS)
    code_field = detect_tract_code_field(sgis, REGIONS[region]["sgis_code"])
    sgis["tract_id"] = sgis[code_field].astype(str).str.strip()
    sgis = sgis[sgis["tract_id"].str.startswith(REGIONS[region]["sgis_code"])].copy()
    invalid_before = int((~sgis.geometry.is_valid).sum())
    if invalid_before:
        sgis.geometry = sgis.geometry.make_valid()
    sgis["original_sgis_area_sqm"] = sgis.geometry.area
    sgis = sgis.merge(stats, on="tract_id", how="left")

    fields = ["population", "workers", "businesses", "total_businesses"]
    missing_before_fill = sgis[fields].isna().sum().to_dict()
    sgis[fields] = sgis[fields].fillna(0)

    intersection = gpd.overlay(
        sgis,
        boundary[["geometry"]],
        how="intersection",
        keep_geom_type=True,
    )
    intersection["intersection_area_sqm"] = intersection.geometry.area
    intersection["area_weight"] = (
        intersection["intersection_area_sqm"] / intersection["original_sgis_area_sqm"]
    )
    intersection = intersection[intersection["area_weight"] > 0].copy()
    for field in fields:
        intersection[f"allocated_{field}"] = intersection[field] * intersection["area_weight"]

    invalid_weights = intersection[intersection["area_weight"] > 1.000001]
    if not invalid_weights.empty:
        log(lines, f"  WARNING area_weight > 1 rows: {len(invalid_weights)}")

    area_sqm = float(boundary.geometry.area.sum())
    totals = {f"allocated_{field}": float(intersection[f"allocated_{field}"].sum()) for field in fields}
    area_km2 = area_sqm / 1_000_000
    summary = {
        "region": region,
        "region_name": REGIONS[region]["name"],
        "area_km2": area_km2,
        **totals,
        "population_density_per_km2": totals["allocated_population"] / area_km2,
        "worker_density_per_km2": totals["allocated_workers"] / area_km2,
        "business_density_per_km2": totals["allocated_businesses"] / area_km2,
        "total_business_density_per_km2": totals["allocated_total_businesses"] / area_km2,
        "workers_per_population": (
            totals["allocated_workers"] / totals["allocated_population"]
            if totals["allocated_population"] > 0
            else pd.NA
        ),
        "intersected_tract_count": int(intersection["tract_id"].nunique()),
        "area_weight_over_1_count": len(invalid_weights),
    }
    check = intersection.drop(columns="geometry").copy()
    check.insert(0, "region", region)
    log(lines, f"  SGIS boundary features: {len(sgis)}")
    log(lines, f"  SGIS invalid boundary geometries repaired: {invalid_before}")
    log(lines, f"  SGIS boundary stats missing -> 0: {missing_before_fill}")
    log(lines, f"  Intersected tracts: {summary['intersected_tract_count']}")
    return intersection, summary, check


def main() -> None:
    for directory in (
        BOUNDARY_OUTPUT_DIR,
        PARCEL_OUTPUT_DIR,
        SGIS_OUTPUT_DIR,
        SUMMARY_OUTPUT_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    for config in REGIONS.values():
        config["intersection_output"].unlink(missing_ok=True)
    for stale_summary in (
        SUMMARY_OUTPUT_DIR / "sgis_region_summary.csv",
        SUMMARY_OUTPUT_DIR / "sgis_area_weight_check.csv",
    ):
        stale_summary.unlink(missing_ok=True)

    lines = [
        f"SGIS preprocessing run: {datetime.now().isoformat(timespec='seconds')}",
        f"Target CRS: {TARGET_CRS}",
        "Allocation method: intersection area / original SGIS tract area",
        "N/A and missing SGIS values are converted to zero and logged.",
    ]
    summaries = []
    checks = []

    with tempfile.TemporaryDirectory(prefix="sgis_by_pnu_") as temp:
        temporary_root = Path(temp)
        for region, config in REGIONS.items():
            log(lines, f"\n[{region}] {config['name']}")
            boundary = gpd.read_file(config["boundary_input"])
            if boundary.crs is None or boundary.empty:
                raise ValueError(f"{region}: invalid boundary input")
            boundary = boundary.to_crs(TARGET_CRS)
            boundary = gpd.GeoDataFrame(
                [{"region": region, "name": config["name"], "geometry": boundary.geometry.union_all()}],
                crs=TARGET_CRS,
            )
            boundary.to_crs(OUTPUT_CRS).to_file(config["boundary_output"], driver="GeoJSON")

            parcels = build_filtered_parcels(region, boundary, temporary_root)
            parcels.to_crs(OUTPUT_CRS).to_file(config["parcel_output"], driver="GeoJSON")
            boundary_area = float(boundary.geometry.area.sum())
            reference_area = float(config["reference_area_sqm"])
            reference_difference_pct = (boundary_area - reference_area) / reference_area * 100
            log(lines, f"  Boundary area sqm ({TARGET_CRS}): {boundary_area:.2f}")
            log(
                lines,
                f"  Difference from prior validation area ({reference_area:.2f} sqm): "
                f"{reference_difference_pct:.4f}%",
            )
            log(lines, f"  Filtered PNU parcels: {len(parcels)}")

            stats = standardize_sgis_stats(
                config["sgis_stats_dir"],
                config["sgis_file_prefix"],
                config["sgis_code"],
                lines,
            )
            stats.to_csv(
                SGIS_OUTPUT_DIR / f"{region}_sgis_stats_standardized.csv",
                index=False,
                encoding="utf-8-sig",
            )

            sgis_boundary = config["sgis_boundary"] or auto_find_sgis_boundary(config["sgis_code"])
            if not sgis_boundary:
                log(
                    lines,
                    "  BLOCKED: matching SGIS tract boundary SHP/GeoJSON not found; "
                    "intersection and allocation outputs were not generated.",
                )
                continue

            intersection, summary, check = intersect_and_allocate(
                region, boundary, stats, sgis_boundary, lines
            )
            intersection.to_crs(OUTPUT_CRS).to_file(
                config["intersection_output"], driver="GeoJSON"
            )
            summaries.append(summary)
            checks.append(check)

    if summaries:
        pd.DataFrame(summaries).to_csv(
            SUMMARY_OUTPUT_DIR / "sgis_region_summary.csv",
            index=False,
            encoding="utf-8-sig",
        )
    if checks:
        pd.concat(checks, ignore_index=True).to_csv(
            SUMMARY_OUTPUT_DIR / "sgis_area_weight_check.csv",
            index=False,
            encoding="utf-8-sig",
        )

    log_path = SUMMARY_OUTPUT_DIR / "sgis_preprocessing_log.txt"
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    print(f"\nLog written: {log_path}")


if __name__ == "__main__":
    main()
