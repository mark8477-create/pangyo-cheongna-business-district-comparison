"""Rebuild Pangyo and redefined Cheongna metrics with one calculation method."""

from __future__ import annotations

import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely import make_valid
from shapely.geometry import Point
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[1]
CRS = "EPSG:5179"
OUT = ROOT / "data" / "processed"
PUBLIC = ROOT / "public" / "data"
WEB_DATA = ROOT / "web" / "data"
PROM_C = ROOT / "data_raw/boundary/cheongna_prom_redefined_2026-06-13/prom_spatial"
PROM_P = ROOT / "data_raw/boundary/pangyo/prom_pangyo_spatial_2026-06-12"
PNU_C = ROOT / "data_raw/boundary/cheongna_prom_redefined_2026-06-13/cheongna_redefined_pnu_2026-06-13.xlsx"
PNU_P = ROOT / "data_processed/boundaries/pangyo_validation/pangyo_main_pnu_verified.csv"
BOUNDARY_P = ROOT / "data_processed/boundaries/pangyo_validation/pangyo_main_boundary.geojson"
SGIS_STATS = ROOT / "data_raw/sgis/request_1781257203152"
SGIS_DISTRICT_STATS = ROOT / "data_raw/sgis/request_1781242203667"
CUTOFF = "2023-12-31"
STATISTICS_YEAR = 2023
PROM_REFERENCE_YEAR = 2026
SGIS_BOUNDARY_PERIOD = "2025_Q2"


def xlsx(path: Path) -> pd.DataFrame:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(n.text or "" for n in x.iterfind(".//m:t", ns)) for x in root.findall("m:si", ns)]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.findall(".//m:sheetData/m:row", ns):
            vals = []
            for cell in row.findall("m:c", ns):
                node = cell.find("m:v", ns)
                val = "" if node is None else node.text
                if cell.attrib.get("t") == "s" and val:
                    val = shared[int(val)]
                vals.append(val)
            rows.append(vals)
    return pd.DataFrame(rows[1:], columns=rows[0])


def layer(root: Path, required: str, forbidden: str | None = None) -> Path:
    for path in root.rglob("*.shp"):
        columns = gpd.read_file(path, encoding="cp949", rows=1).columns
        if required in columns and (forbidden is None or forbidden not in columns):
            return path
    raise FileNotFoundError(f"{required} layer not found under {root}")


def read_prom(root: Path) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    parcels = gpd.read_file(layer(root, "pnu", "bd_mng_id"), encoding="cp949").to_crs(CRS)
    buildings = gpd.read_file(layer(root, "bd_mng_id"), encoding="cp949").to_crs(CRS)
    parcels["pnu"] = parcels["pnu"].astype(str).str.strip()
    return parcels, buildings


def read_zoning(root: Path) -> gpd.GeoDataFrame:
    zoning = gpd.read_file(layer(root, "uzone_nm"), encoding="cp949").to_crs(CRS)
    zoning.geometry = zoning.geometry.make_valid()
    return zoning


def category(use: object) -> str:
    text = str(use or "")
    rules = [
        ("office_research", ("업무", "사무", "연구")),
        ("residential", ("주택", "아파트", "공동주택", "기숙사")),
        ("retail_neighborhood", ("판매", "근린생활", "상점")),
        ("education", ("교육", "학교", "학원")),
        ("culture_assembly", ("문화", "집회", "종교")),
        ("lodging", ("숙박", "호텔")),
        ("industrial", ("공장", "창고", "위험물")),
    ]
    for name, keys in rules:
        if any(key in text for key in keys):
            return name
    return "other"


def land_building_metrics(region: str, boundary, parcels, target_pnus, buildings):
    selected_parcels = parcels[parcels["pnu"].isin(target_pnus)].copy()
    selected_parcels.geometry = selected_parcels.geometry.intersection(boundary)
    selected_parcels = selected_parcels[~selected_parcels.geometry.is_empty].copy()
    selected_buildings = buildings[buildings.geometry.intersects(boundary)].copy()
    selected_buildings = selected_buildings.drop_duplicates("bd_mng_id").copy()
    for col in ("tot_fl_ar", "fl_ar_ra_ar", "fl_ar_ratio"):
        selected_buildings[col] = pd.to_numeric(selected_buildings[col], errors="coerce").fillna(0)
    selected_buildings["use_category"] = selected_buildings["mn_use_nm"].map(category)
    built_union = selected_buildings.geometry.union_all() if len(selected_buildings) else None
    if built_union is None:
        unbuilt = selected_parcels.copy()
    else:
        unbuilt = selected_parcels[~selected_parcels.geometry.intersects(built_union)].copy()
    parcel_area = float(selected_parcels.geometry.area.sum())
    unbuilt_area = float(unbuilt.geometry.area.sum())
    area = float(boundary.area)
    floors = selected_buildings.groupby("use_category", as_index=False)["tot_fl_ar"].sum()
    total_floor = float(floors["tot_fl_ar"].sum())
    floors["share"] = floors["tot_fl_ar"] / total_floor if total_floor else pd.NA
    floors.insert(0, "region", region)
    positive = floors.loc[floors["tot_fl_ar"] > 0, "tot_fl_ar"]
    if total_floor and len(positive) > 1:
        lum = float(-(positive / total_floor * (positive / total_floor).map(math.log)).sum() / math.log(len(positive)))
    elif total_floor:
        lum = 0.0
    else:
        lum = pd.NA
    office_floor = float(floors.loc[floors["use_category"] == "office_research", "tot_fl_ar"].sum())
    land = {
        "region": region, "area_sqm": area, "area_km2": area / 1e6,
        "parcel_count": len(selected_parcels), "parcel_area_sqm": parcel_area,
        "unbuilt_parcel_count": len(unbuilt),
        "unbuilt_parcel_count_ratio": len(unbuilt) / len(selected_parcels) if len(selected_parcels) else pd.NA,
        "unbuilt_parcel_area_sqm": unbuilt_area,
        "unbuilt_parcel_area_ratio": unbuilt_area / parcel_area if parcel_area else pd.NA,
    }
    building = {
        "region": region, "building_count": len(selected_buildings), "total_floor_area_sqm": total_floor,
        "office_floor_area_sqm": office_floor,
        "office_floor_area_ratio": office_floor / total_floor if total_floor else pd.NA,
        "average_far_pct": total_floor / parcel_area * 100 if parcel_area else pd.NA, "lum": lum,
    }
    for key, value in building.items():
        if key != "region":
            floors[key] = value
    selected_parcels["is_unbuilt"] = selected_parcels.index.isin(unbuilt.index)
    return land, building, floors, selected_parcels, selected_buildings


def zoning_metrics(region: str, boundary, zoning: gpd.GeoDataFrame):
    selected = zoning[zoning.geometry.intersects(boundary)].copy()
    dissolved = selected.dissolve(by=["uzone_cd", "uzone_nm"], as_index=False)
    dissolved.geometry = dissolved.geometry.intersection(boundary)
    dissolved = dissolved[~dissolved.geometry.is_empty].copy()
    dissolved["area_sqm"] = dissolved.geometry.area
    dissolved["share"] = dissolved["area_sqm"] / boundary.area
    dissolved.insert(0, "region", region)
    metrics = dissolved[["region", "uzone_cd", "uzone_nm", "area_sqm", "share"]].copy()
    return metrics, dissolved


def read_sgis(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, header=None, names=["year", "tract_id", "metric", "value"], dtype=str, encoding="cp949")
    d["value"] = pd.to_numeric(d["value"].replace("N/A", "0"), errors="coerce").fillna(0)
    return d


def stat_file(prefix: str, includes: tuple[str, ...], excludes: tuple[str, ...] = ()) -> Path:
    found = [p for p in SGIS_STATS.glob("*.csv") if p.name.startswith(prefix) and all(x in p.name for x in includes) and not any(x in p.name for x in excludes)]
    if len(found) != 1:
        raise FileNotFoundError((prefix, includes, found))
    return found[0]


def sgis_inputs(prefix: str, use_district_total_workers: bool = True):
    pop = read_sgis(stat_file(prefix, ("인구총괄",)))
    population = pop[pop["metric"] == "to_in_001"][["tract_id", "value"]].rename(columns={"value": "population"})
    households = pop[pop["metric"] == "to_in_007"][["tract_id", "value"]].rename(columns={"value": "households"})
    biz_raw = read_sgis(stat_file(prefix, ("대분류", "사업체수"), ("총괄",)))
    worker_raw = read_sgis(stat_file(prefix, ("대분류", "종사자수")))
    total_biz = read_sgis(stat_file(prefix, ("대분류", "총괄사업체수")))
    total_biz = total_biz[total_biz["metric"] == "to_fa_010"][["tract_id", "value"]].rename(columns={"value": "businesses"})
    district_code = {"23_": "23080", "31_": "31023"}.get(prefix) if use_district_total_workers else None
    if district_code:
        total_worker_path = next(
            SGIS_DISTRICT_STATS.glob(
                f"**/{district_code}_2023년_산업분류별(10차_대분류)_총괄종사자수.csv"
            )
        )
        total_workers = read_sgis(total_worker_path)
        workers = total_workers[total_workers["metric"] == "to_em_020"][
            ["tract_id", "value"]
        ].rename(columns={"value": "workers"})
    else:
        workers = worker_raw.groupby("tract_id", as_index=False)["value"].sum().rename(columns={"value": "workers"})
    base = (
        population.merge(households, on="tract_id", how="outer")
        .merge(total_biz, on="tract_id", how="outer")
        .merge(workers, on="tract_id", how="outer")
        .fillna(0)
    )
    return base, biz_raw, worker_raw


def allocate(boundary, prefix: str, boundary_path: Path):
    base, biz_raw, worker_raw = sgis_inputs(prefix)
    tracts = gpd.read_file(boundary_path).to_crs(CRS).rename(columns={"TOT_OA_CD": "tract_id"})
    tracts["tract_id"] = tracts["tract_id"].astype(str)
    tracts["tract_area"] = tracts.geometry.area
    tracts = tracts.merge(base, on="tract_id", how="left")
    hit = gpd.overlay(tracts, gpd.GeoDataFrame(geometry=[boundary], crs=CRS), how="intersection")
    hit["weight"] = hit.geometry.area / hit["tract_area"]
    total_fields = ("population", "households", "businesses", "workers")
    totals = {x: float((hit[x].fillna(0) * hit["weight"]).sum()) for x in total_fields}
    metrics = {
        **totals,
        "job_housing_ratio_workers_per_resident": totals["workers"] / totals["population"] if totals["population"] else pd.NA,
        "worker_density_per_km2": totals["workers"] / (boundary.area / 1e6),
        "intersected_tract_count": int(hit["tract_id"].nunique()),
        "tract_code_match_rate": float(hit[list(total_fields)].notna().all(axis=1).mean()),
    }
    weights = hit[["tract_id", "weight"]]
    rows = []
    for label, raw in (("businesses", biz_raw), ("workers", worker_raw)):
        d = raw.merge(weights, on="tract_id", how="inner")
        d["allocated_value"] = d["value"] * d["weight"]
        for metric, value in d.groupby("metric")["allocated_value"].sum().items():
            rows.append({"metric": metric, "measure": label, "value": float(value)})
    industry = pd.DataFrame(rows)
    for measure, total in (("businesses", totals["businesses"]), ("workers", totals["workers"])):
        subtotal = float(industry.loc[industry["measure"] == measure, "value"].sum())
        industry.loc[len(industry)] = {"metric": "secret_or_unprovided_gap", "measure": measure, "value": total - subtotal}
    return metrics, industry, hit


def osm_metrics(region: str, boundary):
    graph = ox.load_graphml(ROOT / f"data_raw/osm/{region}_osm_drive_1km.graphml")
    nodes, _ = ox.graph_to_gdfs(graph)
    nodes = nodes.to_crs(CRS)
    nodes = nodes[nodes.geometry.intersects(boundary)].copy()
    nodes["street_count"] = pd.to_numeric(nodes.get("street_count", 0), errors="coerce").fillna(0)
    graph_u = ox.convert.to_undirected(graph)
    _, edges = ox.graph_to_gdfs(graph_u)
    edges = gpd.clip(edges.to_crs(CRS), boundary, keep_geom_type=True)
    road_km = float(edges.geometry.length.sum() / 1000)
    area_km2 = boundary.area / 1e6
    count = int((nodes["street_count"] >= 3).sum())
    return {"road_length_km": road_km, "road_density_km_per_km2": road_km / area_km2, "intersection_count": count, "intersection_density_per_km2": count / area_km2}


def accessibility(region: str):
    nodes = pd.read_csv(ROOT / "data_raw/subway_network/network/nodes.tsv", sep="\t")
    links = pd.read_csv(ROOT / "data_raw/subway_network/network/links.tsv", sep="\t")
    effective = nodes["effective_begin"].fillna(nodes["begin"])
    active = nodes[effective <= CUTOFF].copy()
    ids = set(active["id"])
    links = links[(links["begin"] <= CUTOFF) & links["fromNode"].isin(ids) & links["toNode"].isin(ids)]
    graph = nx.DiGraph()
    for r in links.itertuples():
        graph.add_edge(r.fromNode, r.toNode, weight=float(r.timeFT))
        graph.add_edge(r.toNode, r.fromNode, weight=float(r.timeTF))
    station = "판교" if region == "pangyo" else "청라국제도시"
    starts = active.loc[active["statnm"] == station, "id"].tolist()
    distances = {}
    for start in starts:
        for node, value in nx.single_source_dijkstra_path_length(graph, start, cutoff=3600, weight="weight").items():
            distances[node] = min(value, distances.get(node, float("inf")))
    tract_sets = []
    for code, path in (("11", ROOT / "data_raw/sgis/boundaries/bnd_oa_11_2025_2Q/bnd_oa_11_2025_2Q.shp"), ("23", ROOT / "data_raw/sgis/boundaries/bnd_oa_23_2025_2Q/bnd_oa_23_2025_2Q.shp"), ("31", ROOT / "data_raw/sgis/boundaries/bnd_oa_31_2025_2Q/bnd_oa_31_2025_2Q.shp")):
        tr = gpd.read_file(path).to_crs(CRS).rename(columns={"TOT_OA_CD": "tract_id"})
        tr["tract_id"] = tr["tract_id"].astype(str); tr["tract_area"] = tr.geometry.area
        base, _, _ = sgis_inputs(code + "_", use_district_total_workers=False)
        tract_sets.append(tr.merge(base, on="tract_id", how="left"))
    tracts = pd.concat(tract_sets, ignore_index=True)
    tracts = gpd.GeoDataFrame(tracts, geometry="geometry", crs=CRS)
    rows, geometries = [], []
    for minute in range(0, 61, 5):
        reached = active[active["id"].map(lambda x: distances.get(x, float("inf")) <= minute * 60)]
        geom = unary_union([Point(x, y).buffer(800) for x, y in zip(reached["x_5179"], reached["y_5179"])]) if len(reached) else None
        vals = {"population": 0.0, "households": 0.0, "workers": 0.0}
        if geom is not None:
            hit = gpd.overlay(tracts, gpd.GeoDataFrame(geometry=[geom], crs=CRS), how="intersection")
            weight = hit.geometry.area / hit["tract_area"]
            vals = {x: float((hit[x].fillna(0) * weight).sum()) for x in vals}
        rows.append({"region": region, "minutes": minute, **vals, "reached_station_nodes": len(reached)})
        if geom is not None:
            geometries.append({"region": region, "minutes": minute, **vals, "geometry": geom})
    return pd.DataFrame(rows), gpd.GeoDataFrame(geometries, crs=CRS)


def serializable(record: dict) -> dict:
    return {k: (None if pd.isna(v) else v) for k, v in record.items()}


def valid_wgs84(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = frame.to_crs(4326).copy()
    result.geometry = result.geometry.buffer(0)
    return result


def write_geojson(frame: gpd.GeoDataFrame, filename: str) -> None:
    output = valid_wgs84(frame)
    for directory in (OUT, PUBLIC, WEB_DATA):
        directory.mkdir(parents=True, exist_ok=True)
        output.to_file(directory / filename, driver="GeoJSON")


def write_json_records(frame: pd.DataFrame, filename: str) -> None:
    records = [serializable(record) for record in frame.to_dict("records")]
    text = json.dumps(records, ensure_ascii=False, indent=2)
    for directory in (PUBLIC, WEB_DATA):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / filename).write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True); PUBLIC.mkdir(parents=True, exist_ok=True); WEB_DATA.mkdir(parents=True, exist_ok=True)
    p_parcels, p_buildings = read_prom(PROM_P); c_parcels, c_buildings = read_prom(PROM_C)
    zoning = {"pangyo": read_zoning(PROM_P), "cheongna": read_zoning(PROM_C)}
    p_pnus = set(pd.read_csv(PNU_P, dtype=str)["pnu"].str.strip())
    c_pnus = set(xlsx(PNU_C)["pnu"].astype(str).str.strip())
    target_pnus = {"pangyo": p_pnus, "cheongna": c_pnus}
    boundaries = {
        "pangyo": make_valid(
            gpd.read_file(BOUNDARY_P).to_crs(CRS).geometry.union_all()
        ).buffer(0),
        "cheongna": make_valid(
            c_parcels[c_parcels["pnu"].isin(c_pnus)].geometry.union_all()
        ).buffer(0),
    }
    boundary_gdf = gpd.GeoDataFrame([{"region": k, "geometry": v} for k, v in boundaries.items()], crs=CRS)
    write_geojson(boundary_gdf, "comparison_boundaries.geojson")
    cheongna_boundary = valid_wgs84(boundary_gdf[boundary_gdf["region"] == "cheongna"])
    cheongna_boundary.to_file(OUT / "cheongna_boundary_final.geojson", driver="GeoJSON")
    cheongna_boundary.to_file(PUBLIC / "cheongna_boundary_final.geojson", driver="GeoJSON")
    cheongna_boundary.to_file(
        ROOT / "data_processed/boundaries/cheongna_main_boundary.geojson",
        driver="GeoJSON",
    )
    c_parcels[c_parcels["pnu"].isin(c_pnus)].to_crs(4326).to_file(
        ROOT / "data_processed/parcels/cheongna_parcels_filtered.geojson",
        driver="GeoJSON",
    )
    land_rows, building_rows, floor_rows, zoning_rows, sgis_rows, industry_rows, osm_rows, access, isochrones = [], [], [], [], [], [], [], [], []
    for region, parcels, buildings, prefix, shp in [
        ("pangyo", p_parcels, p_buildings, "31_", ROOT / "data_raw/sgis/boundaries/bnd_oa_31023_2025_2Q/bnd_oa_31023_2025_2Q.shp"),
        ("cheongna", c_parcels, c_buildings, "23_", ROOT / "data_raw/sgis/boundaries/bnd_oa_23080_2025_2Q/bnd_oa_23080_2025_2Q.shp"),
    ]:
        land, building, floors, selected_parcels, selected_buildings = land_building_metrics(
            region, boundaries[region], parcels, target_pnus[region], buildings
        )
        zone_metrics, zone_features = zoning_metrics(region, boundaries[region], zoning[region])
        sgis, industry, hit = allocate(boundaries[region], prefix, shp)
        hit.to_crs(4326).to_file(
            ROOT / f"data_processed/sgis/{region}_sgis_intersection.geojson",
            driver="GeoJSON",
        )
        parcel_fields = [x for x in ("pnu", "address", "jibun", "jimok", "own_type", "area", "lnd_prc", "is_unbuilt", "geometry") if x in selected_parcels]
        building_fields = [x for x in ("bd_mng_id", "pnu", "bd_nm", "mn_use_nm", "use_category", "tot_fl_ar", "land_ar", "fl_ar_ratio", "bd_coverage", "gr_fl_num", "use_per_dt", "geometry") if x in selected_buildings]
        write_geojson(selected_parcels[parcel_fields], f"{region}_parcels.geojson")
        write_geojson(selected_buildings[building_fields], f"{region}_buildings.geojson")
        write_geojson(zone_features[["uzone_cd", "uzone_nm", "area_sqm", "share", "geometry"]], f"{region}_zoning.geojson")
        land_rows.append(land); building_rows.append(building); floor_rows.append(floors); zoning_rows.append(zone_metrics)
        sgis_rows.append({"region": region, **sgis}); industry.insert(0, "region", region); industry_rows.append(industry)
        osm_rows.append({"region": region, **osm_metrics(region, boundaries[region])})
        access_metrics, access_geometry = accessibility(region)
        access.append(access_metrics); isochrones.append(access_geometry)
    floor_df = pd.concat(floor_rows, ignore_index=True)
    land_df, building_df, zoning_df, sgis_df, industry_df, osm_df, access_df = map(pd.DataFrame, [land_rows, building_rows, pd.concat(zoning_rows), sgis_rows, pd.concat(industry_rows), osm_rows, pd.concat(access)])
    isochrone_df = gpd.GeoDataFrame(pd.concat(isochrones, ignore_index=True), crs=CRS)
    write_geojson(isochrone_df, "cumulative_accessibility_isochrones.geojson")
    write_geojson(isochrone_df[isochrone_df["minutes"].isin([30, 60])], "accessibility_30_60_isochrones.geojson")
    land_df[land_df.region == "cheongna"].to_csv(OUT / "cheongna_landuse_metrics.csv", index=False, encoding="utf-8-sig")
    zoning_df[zoning_df.region == "cheongna"].to_csv(OUT / "cheongna_zoning_metrics.csv", index=False, encoding="utf-8-sig")
    floor_df.query("region == 'cheongna'").to_csv(OUT / "cheongna_building_metrics.csv", index=False, encoding="utf-8-sig")
    sgis_df.query("region == 'cheongna'").to_csv(OUT / "cheongna_sgis_metrics.csv", index=False, encoding="utf-8-sig")
    industry_df.query("region == 'cheongna'").to_csv(OUT / "cheongna_industry_metrics.csv", index=False, encoding="utf-8-sig")
    osm_df.query("region == 'cheongna'").to_csv(OUT / "cheongna_osm_metrics.csv", index=False, encoding="utf-8-sig")
    access_df.query("region == 'cheongna' and minutes in [30,60]").to_csv(OUT / "cheongna_accessibility_30_60.csv", index=False, encoding="utf-8-sig")
    access_df.query("region == 'cheongna'").to_csv(OUT / "cheongna_cumulative_accessibility.csv", index=False, encoding="utf-8-sig")
    zoning_df.to_csv(OUT / "comparison_zoning_metrics.csv", index=False, encoding="utf-8-sig")
    floor_df.to_csv(OUT / "comparison_building_use_metrics.csv", index=False, encoding="utf-8-sig")
    industry_df.to_csv(OUT / "comparison_industry_metrics.csv", index=False, encoding="utf-8-sig")
    access_df.to_csv(OUT / "comparison_cumulative_accessibility.csv", index=False, encoding="utf-8-sig")
    write_json_records(zoning_df, "comparison_zoning_metrics.json")
    write_json_records(floor_df, "comparison_building_use_metrics.json")
    write_json_records(industry_df, "comparison_industry_metrics.json")
    write_json_records(access_df, "comparison_cumulative_accessibility.json")
    comparison = land_df.merge(building_df, on="region").merge(sgis_df, on="region").merge(osm_df, on="region")
    comparison = comparison.merge(access_df[access_df.minutes == 30][["region", "population", "households", "workers"]].rename(columns={"population": "access_30_population", "households": "access_30_households", "workers": "access_30_workers"}), on="region")
    comparison = comparison.merge(access_df[access_df.minutes == 60][["region", "population", "households", "workers"]].rename(columns={"population": "access_60_population", "households": "access_60_households", "workers": "access_60_workers"}), on="region")
    comparison["statistics_year"] = STATISTICS_YEAR
    comparison["prom_reference_year"] = PROM_REFERENCE_YEAR
    comparison["sgis_boundary_period"] = SGIS_BOUNDARY_PERIOD
    comparison["subway_network_cutoff"] = CUTOFF
    comparison.to_csv(OUT / "comparison_summary_metrics.csv", index=False, encoding="utf-8-sig")
    records = [serializable(r) for r in comparison.to_dict("records")]
    (PUBLIC / "comparison_summary_metrics.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    (WEB_DATA / "comparison_summary_metrics.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    cheongna = next(r for r in records if r["region"] == "cheongna")
    (PUBLIC / "cheongna_summary_metrics.json").write_text(json.dumps(cheongna, ensure_ascii=False, indent=2), encoding="utf-8")
    (WEB_DATA / "cheongna_summary_metrics.json").write_text(json.dumps(cheongna, ensure_ascii=False, indent=2), encoding="utf-8")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
