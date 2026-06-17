"""Validate static GitHub Pages files without requiring a browser."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    html = read(WEB / "index.html")
    script = read(WEB / "app.js")

    required_ids = {
        "key-metrics",
        "map-pangyo",
        "map-cheongna",
        "layer-select",
        "time-select",
        "zoning-chart",
        "building-chart",
        "development-chart",
        "access-chart",
        "social-chart",
        "industry-chart",
    }
    html_ids = set(re.findall(r'id="([^"]+)"', html))
    missing_ids = required_ids - html_ids
    assert not missing_ids, f"Missing HTML ids: {sorted(missing_ids)}"

    required_html_text = {
        "SGIS 2023: 인구·가구·사업체·종사자",
        "SGIS 집계구 경계: 2025년 2분기",
        "지하철 네트워크 컷오프: 2023-12-31",
        "판교테크노밸리",
        "청라 국제업무중심지구",
    }
    missing_html_text = {text for text in required_html_text if text not in html}
    assert not missing_html_text, f"Missing HTML text: {sorted(missing_html_text)}"

    required_script_text = {
        "30·60분 도달 종사자",
        "30·60분 도달 인구",
        "시스템 초기화 오류",
        "판교",
        "청라",
    }
    missing_script_text = {text for text in required_script_text if text not in script}
    assert not missing_script_text, f"Missing script text: {sorted(missing_script_text)}"

    data_files = set(re.findall(r'"([a-z0-9_]+\.(?:json|geojson))"', script))
    assert data_files, "No static data references found in app.js"
    for filename in sorted(data_files):
      path = WEB / "data" / filename
      assert path.exists() and path.stat().st_size > 0, filename
      json.loads(read(path))

    summary = json.loads(read(WEB / "data/comparison_summary_metrics.json"))
    assert {row["region"] for row in summary} == {"pangyo", "cheongna"}
    assert all(row["statistics_year"] == 2023 for row in summary)
    assert all(row["prom_reference_year"] == 2026 for row in summary)

    isochrones = json.loads(read(WEB / "data/accessibility_30_60_isochrones.geojson"))
    pairs = {(f["properties"]["region"], f["properties"]["minutes"]) for f in isochrones["features"]}
    assert pairs == {("pangyo", 30), ("pangyo", 60), ("cheongna", 30), ("cheongna", 60)}

    workflow = read(ROOT / ".github/workflows/pages.yml")
    assert "actions/deploy-pages@v4" in workflow
    assert "path: web" in workflow

    print(f"Static web validation passed: {len(data_files)} data files")


if __name__ == "__main__":
    main()
