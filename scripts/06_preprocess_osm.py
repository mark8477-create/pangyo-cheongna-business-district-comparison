"""Download and summarize OSM drive networks for the two office districts.

The download area is each district boundary plus a 1 km buffer. Final road
length and intersection metrics are calculated only inside the original
district boundary.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_CRS = "EPSG:5179"
OUTPUT_CRS = "EPSG:4326"
BUFFER_METERS = 1_000
NETWORK_TYPE = "drive"
DOWNLOAD_WALK_NETWORK = False

BOUNDARY_DIR = PROJECT_ROOT / "data_processed/boundaries"
RAW_OSM_DIR = PROJECT_ROOT / "data_raw/osm"
PROCESSED_OSM_DIR = PROJECT_ROOT / "data_processed/osm"
SUMMARY_DIR = PROJECT_ROOT / "data_processed/summary"

REGIONS = {
    "pangyo": BOUNDARY_DIR / "pangyo_main_boundary.geojson",
    "cheongna": BOUNDARY_DIR / "cheongna_main_boundary.geojson",
}

ROAD_TYPES = (
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "residential",
    "service",
    "unclassified",
)


def make_json_safe(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Convert list/dict/set attributes unsupported by GeoJSON to JSON strings."""
    result = frame.copy()
    for column in result.columns.drop("geometry", errors="ignore"):
        if result[column].map(lambda value: isinstance(value, (list, dict, set, tuple))).any():
            result[column] = result[column].map(
                lambda value: json.dumps(
                    sorted(value) if isinstance(value, set) else value,
                    ensure_ascii=False,
                )
                if isinstance(value, (list, dict, set, tuple))
                else value
            )
    return result


def normalize_highway(value: object) -> list[str]:
    if isinstance(value, list):
        values = value
    elif isinstance(value, tuple):
        values = list(value)
    elif pd.isna(value):
        values = []
    else:
        values = [str(value)]
    return [str(item).removesuffix("_link") for item in values]


def download_graph(boundary_5179: gpd.GeoDataFrame, network_type: str):
    buffered = boundary_5179.geometry.union_all().buffer(BUFFER_METERS)
    polygon_4326 = gpd.GeoSeries([buffered], crs=TARGET_CRS).to_crs(OUTPUT_CRS).iloc[0]
    return ox.graph.graph_from_polygon(
        polygon_4326,
        network_type=network_type,
        simplify=True,
        retain_all=True,
        truncate_by_edge=True,
    )


def process_region(region: str, boundary_path: Path) -> dict[str, float | int | str]:
    boundary = gpd.read_file(boundary_path)
    if boundary.crs is None or boundary.empty:
        raise ValueError(f"{boundary_path}: missing CRS or empty boundary")
    boundary_5179 = boundary.to_crs(TARGET_CRS)
    district = boundary_5179.geometry.union_all()
    area_km2 = float(district.area / 1_000_000)

    graph = download_graph(boundary_5179, NETWORK_TYPE)
    ox.io.save_graphml(graph, RAW_OSM_DIR / f"{region}_osm_{NETWORK_TYPE}_1km.graphml")

    nodes, _ = ox.convert.graph_to_gdfs(graph, nodes=True, edges=True)
    nodes_5179 = nodes.to_crs(TARGET_CRS)
    nodes_inside = nodes_5179[nodes_5179.geometry.intersects(district)].copy()
    nodes_inside["street_count"] = pd.to_numeric(
        nodes_inside.get("street_count", 0), errors="coerce"
    ).fillna(0)
    nodes_inside["is_intersection"] = nodes_inside["street_count"] >= 3

    undirected = ox.convert.to_undirected(graph)
    _, edges = ox.convert.graph_to_gdfs(undirected, nodes=True, edges=True)
    edges_5179 = edges.to_crs(TARGET_CRS)
    clipped_edges = gpd.clip(edges_5179, district, keep_geom_type=True)
    clipped_edges = clipped_edges[~clipped_edges.geometry.is_empty].copy()
    clipped_edges["length_m_clipped"] = clipped_edges.geometry.length
    clipped_edges["highway_normalized"] = clipped_edges["highway"].map(
        lambda value: "|".join(normalize_highway(value))
    )

    clipped_edges = clipped_edges.reset_index()
    nodes_inside = nodes_inside.reset_index()
    make_json_safe(clipped_edges.to_crs(OUTPUT_CRS)).to_file(
        PROCESSED_OSM_DIR / f"{region}_osm_edges.geojson",
        driver="GeoJSON",
    )
    make_json_safe(nodes_inside.to_crs(OUTPUT_CRS)).to_file(
        PROCESSED_OSM_DIR / f"{region}_osm_nodes.geojson",
        driver="GeoJSON",
    )

    road_length_km = float(clipped_edges["length_m_clipped"].sum() / 1_000)
    intersection_count = int(nodes_inside["is_intersection"].sum())
    summary: dict[str, float | int | str] = {
        "region": region,
        "area_km2": area_km2,
        "road_length_km": road_length_km,
        "road_density_km_per_km2": road_length_km / area_km2,
        "intersection_count": intersection_count,
        "intersection_density_per_km2": intersection_count / area_km2,
    }
    for road_type in ROAD_TYPES:
        length_m = clipped_edges.loc[
            clipped_edges["highway"].map(
                lambda value: road_type in normalize_highway(value)
            ),
            "length_m_clipped",
        ].sum()
        summary[f"{road_type}_length_km"] = float(length_m / 1_000)

    if DOWNLOAD_WALK_NETWORK:
        walk_graph = download_graph(boundary_5179, "walk")
        ox.io.save_graphml(walk_graph, RAW_OSM_DIR / f"{region}_osm_walk_1km.graphml")

    print(
        f"{region}: {len(nodes_inside)} inside nodes, {len(clipped_edges)} clipped edges, "
        f"{road_length_km:.3f} road km, {intersection_count} intersections"
    )
    return summary


def write_readme(downloaded_at: str) -> None:
    text = f"""# OpenStreetMap road network

- Downloaded at: {downloaded_at}
- Source: OpenStreetMap via OSMnx / Overpass API
- License: Open Database License (ODbL)
- Attribution: © OpenStreetMap contributors
- Network type: `{NETWORK_TYPE}`
- Download area: each office-district boundary buffered by {BUFFER_METERS} meters
- Final metrics: physical undirected road edges clipped to the original boundary
- Metric CRS: `{TARGET_CRS}`

Run `python scripts/06_preprocess_osm.py` to refresh the data. OSM results may
change because OpenStreetMap is continuously edited.
"""
    (RAW_OSM_DIR / "README.md").write_text(text, encoding="utf-8-sig")


def main() -> None:
    for directory in (RAW_OSM_DIR, PROCESSED_OSM_DIR, SUMMARY_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    ox.settings.use_cache = True
    ox.settings.cache_folder = RAW_OSM_DIR / "cache"
    ox.settings.requests_timeout = 180

    downloaded_at = datetime.now().astimezone().isoformat(timespec="seconds")
    summaries = [
        process_region(region, boundary_path)
        for region, boundary_path in REGIONS.items()
    ]
    pd.DataFrame(summaries).to_csv(
        SUMMARY_DIR / "osm_road_network_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    write_readme(downloaded_at)


if __name__ == "__main__":
    main()
