"""Verify Pangyo candidate PNUs against parcel polygons and plan-block labels."""

from __future__ import annotations

import argparse
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from pathlib import Path

import geopandas as gpd
import pandas as pd


REFERENCE_AREA_SQM = 663_575.0
PNU_PATTERN = re.compile(r"^\d{19}$")
PNU_FIELDS = ("pnu", "PNU", "PNU_CODE", "필지고유번호")
BLOCK_FIELDS = ("plan_block", "block", "BLOCK", "용지번호", "획지번호", "도면구분")


def first_field(columns: pd.Index, candidates: tuple[str, ...]) -> str | None:
    return next((field for field in candidates if field in columns), None)


def normalize_block(value: object) -> str:
    return re.sub(r"\s+", "", str(value)).replace("~", "-")


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


def read_candidates(path: Path) -> pd.DataFrame:
    frame = read_simple_xlsx(path)
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    if "pnu" not in frame.columns:
        raise ValueError("Candidate XLSX must contain a pnu column.")
    frame["pnu"] = frame["pnu"].fillna("").str.strip()
    frame["address"] = frame.get("주소", frame.get("address", "")).fillna("").str.strip()
    frame["pnu_format_valid"] = frame["pnu"].map(lambda value: bool(PNU_PATTERN.fullmatch(value)))
    frame["legal_dong"] = frame["address"].str.extract(r"(\S+동)\s", expand=False).fillna("")
    return (
        frame[["pnu", "address", "pnu_format_valid", "legal_dong"]]
        .drop_duplicates("pnu")
        .sort_values("pnu")
        .reset_index(drop=True)
    )


def empty_csv(path: Path, columns: list[str]) -> None:
    pd.DataFrame(columns=columns).to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--parcels", type=Path)
    parser.add_argument("--target-blocks", required=True, type=Path)
    parser.add_argument("--crosswalk", type=Path, help="Optional CSV with pnu,plan_block.")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    candidates = read_candidates(args.candidates)
    targets = pd.read_csv(args.target_blocks, dtype=str)
    targets["plan_block"] = targets["plan_block"].map(normalize_block)
    target_blocks = set(targets["plan_block"])

    if not args.parcels:
        candidates.to_csv(
            args.output_dir / "pangyo_candidate_pnu_audit.csv", index=False, encoding="utf-8-sig"
        )
        empty_csv(args.output_dir / "pangyo_main_pnu_verified.csv", ["pnu", "address", "plan_block"])
        empty_csv(
            args.output_dir / "pangyo_missing_pnu.csv",
            ["pnu", "missing_plan_block", "reason"],
        )
        empty_csv(
            args.output_dir / "pangyo_extra_pnu.csv",
            ["pnu", "address", "plan_block", "reason"],
        )
        summary = {
            "status": "blocked_missing_parcel_polygons_and_plan_block_mapping",
            "input_pnu_count": len(candidates),
            "verified_pnu_count": 0,
            "suspected_missing_count": "not_determinable",
            "suspected_extra_count": "not_determinable",
            "boundary_area_sqm": "not_determinable",
            "reference_area_sqm": REFERENCE_AREA_SQM,
            "area_error_rate_pct": "not_determinable",
            "area_by_land_category": "not_determinable",
            "note": "Provide parcel polygons with PNU and plan_block, or a PNU-plan_block crosswalk.",
        }
        pd.DataFrame([summary]).to_csv(
            args.output_dir / "pangyo_boundary_check_summary.csv", index=False, encoding="utf-8-sig"
        )
        return

    parcels = gpd.read_file(args.parcels)
    pnu_field = first_field(parcels.columns, PNU_FIELDS)
    if not pnu_field:
        raise ValueError(f"Parcel file needs one of these PNU fields: {PNU_FIELDS}")
    parcels["pnu"] = parcels[pnu_field].astype(str).str.strip()
    parcels = parcels.drop_duplicates("pnu").copy()

    block_field = first_field(parcels.columns, BLOCK_FIELDS)
    if block_field:
        parcels["plan_block"] = parcels[block_field].map(normalize_block)
    elif args.crosswalk:
        crosswalk = pd.read_csv(args.crosswalk, dtype=str)
        crosswalk["plan_block"] = crosswalk["plan_block"].map(normalize_block)
        parcels = parcels.merge(crosswalk[["pnu", "plan_block"]], on="pnu", how="left")
    else:
        raise ValueError(
            "A plan-block field or --crosswalk is required. PNU/polygon matching alone "
            "cannot verify the district-plan designation."
        )

    projected = parcels if parcels.crs and parcels.crs.is_projected else parcels.to_crs(5179)
    parcels["parcel_area_sqm"] = projected.geometry.area
    joined = parcels.merge(candidates[["pnu", "address", "legal_dong"]], on="pnu", how="outer", indicator=True)
    joined["is_target_block"] = joined["plan_block"].isin(target_blocks)

    verified = joined[(joined["_merge"] == "both") & joined["is_target_block"]].copy()
    extra = joined[(joined["_merge"].isin(["both", "right_only"])) & ~joined["is_target_block"]].copy()
    present_blocks = set(verified["plan_block"].dropna())
    missing_blocks = targets[~targets["plan_block"].isin(present_blocks)].copy()

    category = targets[["plan_block", "land_category"]]
    verified = verified.merge(category, on="plan_block", how="left")
    verified.drop(columns=["geometry", "_merge"], errors="ignore").to_csv(
        args.output_dir / "pangyo_main_pnu_verified.csv", index=False, encoding="utf-8-sig"
    )
    extra.drop(columns=["geometry", "_merge"], errors="ignore").to_csv(
        args.output_dir / "pangyo_extra_pnu.csv", index=False, encoding="utf-8-sig"
    )
    missing_blocks.rename(columns={"plan_block": "missing_plan_block"}).to_csv(
        args.output_dir / "pangyo_missing_pnu.csv", index=False, encoding="utf-8-sig"
    )

    boundary_area = 0.0
    if not verified.empty:
        verified_geo = gpd.GeoDataFrame(verified, geometry="geometry", crs=parcels.crs)
        boundary = verified_geo.geometry.union_all()
        boundary_area = float(
            gpd.GeoSeries([boundary], crs=parcels.crs).to_crs(projected.crs).area.iloc[0]
        )
        gpd.GeoDataFrame(
            [{"name": "제1판교테크노밸리", "area_sqm": boundary_area, "geometry": boundary}],
            crs=parcels.crs,
        ).to_crs(4326).to_file(args.output_dir / "pangyo_main_boundary.geojson", driver="GeoJSON")

    category_areas = (
        verified.groupby("land_category")["parcel_area_sqm"].sum().round(2).to_dict()
        if not verified.empty
        else {}
    )
    summary = {
        "status": "verified" if not missing_blocks.shape[0] else "review_required",
        "input_pnu_count": len(candidates),
        "verified_pnu_count": len(verified),
        "suspected_missing_count": len(missing_blocks),
        "suspected_extra_count": len(extra),
        "boundary_area_sqm": round(boundary_area, 2),
        "reference_area_sqm": REFERENCE_AREA_SQM,
        "area_error_rate_pct": round(abs(boundary_area - REFERENCE_AREA_SQM) / REFERENCE_AREA_SQM * 100, 4),
        "area_by_land_category": str(category_areas),
    }
    pd.DataFrame([summary]).to_csv(
        args.output_dir / "pangyo_boundary_check_summary.csv", index=False, encoding="utf-8-sig"
    )


if __name__ == "__main__":
    main()
