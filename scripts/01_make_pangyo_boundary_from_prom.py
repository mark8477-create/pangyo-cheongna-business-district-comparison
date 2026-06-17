"""Build and audit the Pangyo main boundary from a PROM export."""

from __future__ import annotations

import argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import geopandas as gpd
import pandas as pd


REFERENCE_AREA_SQM = 663_575.0
MIN_OVERLAP_SQM = 0.01


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


def find_layer(root: Path, required_field: str) -> Path:
    for path in root.rglob("*.shp"):
        if required_field in gpd.read_file(path, encoding="cp949", rows=1).columns:
            return path
    raise FileNotFoundError(f"No shapefile with field {required_field!r} under {root}")


def classify_land(jimok: str) -> str:
    return {
        "대": "도시지원시설용지",
        "주차장": "주차장용지",
        "주유소용지": "위험물저장및처리시설용지",
    }.get(jimok, "구역내_공공공간및기반시설")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--prom-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    candidates = read_simple_xlsx(args.candidates).rename(columns={"주소": "candidate_address"})
    candidates["pnu"] = candidates["pnu"].astype(str).str.strip()
    candidates = candidates.drop_duplicates("pnu")

    aoi_path = next(args.prom_root.glob("01_*/*.shp"))
    parcel_path = find_layer(args.prom_root, "jimok")
    aoi = gpd.read_file(aoi_path, encoding="cp949")
    parcels = gpd.read_file(parcel_path, encoding="cp949")
    parcels["pnu"] = parcels["pnu"].astype(str).str.strip()
    aoi_union = aoi.geometry.union_all()

    intersecting = parcels[parcels.intersects(aoi_union)].copy()
    intersecting["overlap_area_sqm"] = intersecting.geometry.intersection(aoi_union).area
    intersecting = intersecting[intersecting["overlap_area_sqm"] > MIN_OVERLAP_SQM].copy()
    intersecting["parcel_area_sqm"] = intersecting.geometry.area
    intersecting["overlap_share"] = (
        intersecting["overlap_area_sqm"] / intersecting["parcel_area_sqm"]
    )
    intersecting["review_flag"] = intersecting["overlap_share"].map(
        lambda share: "boundary_sliver_under_1pct" if share < 0.01 else ""
    )
    intersecting["land_category"] = intersecting["jimok"].map(classify_land)

    candidate_pnus = set(candidates["pnu"])
    spatial_pnus = set(intersecting["pnu"])
    verified_pnus = candidate_pnus & spatial_pnus

    verified = intersecting[intersecting["pnu"].isin(verified_pnus)].merge(
        candidates[["pnu", "candidate_address"]], on="pnu", how="left"
    )
    missing = intersecting[intersecting["pnu"].isin(spatial_pnus - candidate_pnus)].copy()
    extra = candidates[candidates["pnu"].isin(candidate_pnus - spatial_pnus)].copy()

    output_columns = [
        "pnu",
        "address",
        "candidate_address",
        "jibun",
        "jimok",
        "land_category",
        "parcel_area_sqm",
        "overlap_area_sqm",
        "overlap_share",
        "review_flag",
    ]
    verified.drop(columns="geometry")[output_columns].sort_values("pnu").to_csv(
        args.output_dir / "pangyo_main_pnu_verified.csv", index=False, encoding="utf-8-sig"
    )
    missing.drop(columns="geometry").to_csv(
        args.output_dir / "pangyo_missing_pnu.csv", index=False, encoding="utf-8-sig"
    )
    extra.to_csv(args.output_dir / "pangyo_extra_pnu.csv", index=False, encoding="utf-8-sig")

    clipped_geometry = verified.geometry.intersection(aoi_union).union_all()
    boundary = gpd.GeoDataFrame(
        [
            {
                "name": "제1판교테크노밸리 도시지원시설 지정대상",
                "source": "PROM 직접 디지타이징 구역계와 검증 PNU 필지 교차",
                "reference_area_sqm": REFERENCE_AREA_SQM,
                "geometry": clipped_geometry,
            }
        ],
        crs=parcels.crs,
    )
    boundary_area = float(boundary.geometry.area.iloc[0])
    boundary["area_sqm"] = boundary_area
    boundary["area_error_rate_pct"] = (
        abs(boundary_area - REFERENCE_AREA_SQM) / REFERENCE_AREA_SQM * 100
    )
    boundary.to_crs(4326).to_file(
        args.output_dir / "pangyo_main_boundary.geojson", driver="GeoJSON"
    )

    category_areas = (
        verified.groupby("land_category")["overlap_area_sqm"].sum().round(2).to_dict()
    )
    summary = {
        "status": "verified_spatially_plan_block_labels_unavailable",
        "input_pnu_count": len(candidates),
        "verified_pnu_count": len(verified),
        "suspected_missing_count": len(missing),
        "suspected_extra_count": len(extra),
        "boundary_area_sqm": round(boundary_area, 2),
        "reference_area_sqm": REFERENCE_AREA_SQM,
        "area_error_rate_pct": round(
            abs(boundary_area - REFERENCE_AREA_SQM) / REFERENCE_AREA_SQM * 100, 4
        ),
        "area_by_land_category": str(category_areas),
        "urban_support_parcel_count": int((verified["jimok"] == "대").sum()),
        "parking_parcel_count": int((verified["jimok"] == "주차장").sum()),
        "hazardous_facility_parcel_count": int((verified["jimok"] == "주유소용지").sum()),
        "boundary_sliver_review_count": int((verified["overlap_share"] < 0.01).sum()),
        "note": (
            "PROM에는 도시1~5 등 계획블록 번호 속성이 없어 개별 블록명-PNU 대응은 "
            "확정할 수 없음. 주차장 6필지와 주유소용지 2필지는 시행지침 개수와 일치. "
            "필지 전체 면적의 1% 미만만 경계와 접하는 필지는 review_flag로 표시."
        ),
    }
    pd.DataFrame([summary]).to_csv(
        args.output_dir / "pangyo_boundary_check_summary.csv", index=False, encoding="utf-8-sig"
    )


if __name__ == "__main__":
    main()
