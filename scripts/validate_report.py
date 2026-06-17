from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "report" / "report_final.md"
CHECK_MD = ROOT / "report" / "report_validation_check.md"
SUMMARY_JSON = ROOT / "public" / "data" / "comparison_summary_metrics.json"
ZONING_JSON = ROOT / "public" / "data" / "comparison_zoning_metrics.json"
INDUSTRY_JSON = ROOT / "public" / "data" / "comparison_industry_metrics.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_int(value: float) -> str:
    return f"{round(value):,}"


def fmt_one(value: float) -> str:
    return f"{value:.1f}"


def compact_man(value: float) -> str:
    return f"{value / 10000:.1f}만"


def ratio(a: float, b: float) -> str:
    return f"{a / b:.1f}배"


def contains(text: str, snippet: str) -> str:
    return "일치" if snippet in text else "불일치"


def main() -> None:
    report = REPORT_MD.read_text(encoding="utf-8")
    summary = {row["region"]: row for row in load_json(SUMMARY_JSON)}
    zoning = load_json(ZONING_JSON)
    industry = load_json(INDUSTRY_JSON)

    p = summary["pangyo"]
    c = summary["cheongna"]

    pangyo_zoning = {row["uzone_nm"]: row["share"] for row in zoning if row["region"] == "pangyo"}
    cheongna_zoning = {row["uzone_nm"]: row["share"] for row in zoning if row["region"] == "cheongna"}

    workers = {(row["region"], row["metric"]): row["value"] for row in industry if row["measure"] == "workers"}

    checks = [
        ("판교 분석 면적", "0.674km²"),
        ("청라 분석 면적", "1.037km²"),
        ("판교 건축물 수", f"{fmt_int(p['building_count'])}개"),
        ("청라 건축물 수", f"{fmt_int(c['building_count'])}개"),
        ("판교 총연면적", f"{fmt_int(p['total_floor_area_sqm'])}㎡"),
        ("청라 총연면적", f"{fmt_int(c['total_floor_area_sqm'])}㎡"),
        ("판교 평균 용적률", f"{fmt_one(p['average_far_pct'])}%"),
        ("청라 평균 용적률", f"{fmt_one(c['average_far_pct'])}%"),
        ("판교 미건축 필지 면적 비율", f"{fmt_one(p['unbuilt_parcel_area_ratio'] * 100)}%"),
        ("청라 미건축 필지 면적 비율", f"{fmt_one(c['unbuilt_parcel_area_ratio'] * 100)}%"),
        ("판교 업무시설 연면적 비율", f"{fmt_one(p['office_floor_area_ratio'] * 100)}%"),
        ("청라 업무시설 연면적 비율", f"{fmt_one(c['office_floor_area_ratio'] * 100)}%"),
        ("판교 내부 인구", f"{fmt_int(p['population'])}명"),
        ("청라 내부 인구", f"{fmt_int(c['population'])}명"),
        ("판교 사업체 수", f"{fmt_int(p['businesses'])}개"),
        ("청라 사업체 수", f"{fmt_int(c['businesses'])}개"),
        ("판교 종사자 수", f"{fmt_int(p['workers'])}명"),
        ("청라 종사자 수", f"{fmt_int(c['workers'])}명"),
        ("판교 종사자 밀도", f"{fmt_int(p['worker_density_per_km2'])}명/km²"),
        ("청라 종사자 밀도", f"{fmt_int(c['worker_density_per_km2'])}명/km²"),
        ("판교 직주비", fmt_one(p["job_housing_ratio_workers_per_resident"])),
        ("청라 직주비", f"{c['job_housing_ratio_workers_per_resident']:.2f}"),
        ("30분 판교 도달 인구", f"{fmt_int(p['access_30_population'])}명"),
        ("30분 청라 도달 인구", f"{fmt_int(c['access_30_population'])}명"),
        ("30분 판교 도달 종사자", f"{fmt_int(p['access_30_workers'])}명"),
        ("30분 청라 도달 종사자", f"{fmt_int(c['access_30_workers'])}명"),
        ("60분 판교 도달 인구", f"{fmt_int(p['access_60_population'])}명"),
        ("60분 청라 도달 인구", f"{fmt_int(c['access_60_population'])}명"),
        ("60분 판교 도달 종사자", f"{fmt_int(p['access_60_workers'])}명"),
        ("60분 청라 도달 종사자", f"{fmt_int(c['access_60_workers'])}명"),
        ("판교 준주거지역 비율", f"{fmt_one(pangyo_zoning['준주거지역'] * 100)}%"),
        ("청라 중심상업지역 비율", f"{fmt_one(cheongna_zoning['중심상업지역'] * 100)}%"),
        ("청라 자연녹지지역 비율", f"{fmt_one(cheongna_zoning['자연녹지지역'] * 100)}%"),
        ("판교 정보통신업 종사자", f"{fmt_int(workers[('pangyo', 'cp_bem_010')])}명"),
        ("판교 전문·과학기술업 종사자", f"{fmt_int(workers[('pangyo', 'cp_bem_013')])}명"),
        ("판교 사업지원 종사자", f"{fmt_int(workers[('pangyo', 'cp_bem_014')])}명"),
        ("청라 건설업 종사자", f"{fmt_int(workers[('cheongna', 'cp_bem_006')])}명"),
        ("청라 도소매업 종사자", f"{fmt_int(workers[('cheongna', 'cp_bem_007')])}명"),
        ("청라 숙박·음식업 종사자", f"{fmt_int(workers[('cheongna', 'cp_bem_009')])}명"),
        ("판교 30분 도달 종사자 축약", f"{compact_man(p['access_30_workers'])} 명"),
        ("청라 30분 도달 종사자 축약", f"{compact_man(c['access_30_workers'])} 명"),
    ]

    requirement_rows = [
        ("비교 지역 선정 근거와 실패 판단 데이터·출처", "충족", "서론에 언론보도와 나대지 면적 272,977.4㎡, 비율 75.1%, 8필지 제시"),
        ("구역계 정의와 출처 명시", "충족", "판교 실행지침, 인천경제자유구역청 위치도·획지결정도, 프롭 공간자료 사용"),
        ("시간범위·공간범위·공간단위·공간단위 통합", "충족", "2장에 모두 명시"),
        ("토지이용 분석 4개 지표", "충족", "용도지역 구성, 건축물 주용도, 혼합도, 개발 실현도 제시"),
        ("교통망 분석: 핵심역·30분·60분·도달 인구·종사자", "충족", "5장과 관련 그림에 제시"),
        ("인구사회 분석: 인구·가구·사업체·종사자·직주 지표", "충족", "4장 표와 본문에 제시"),
        ("성공요인 3가지 이상", "충족", "6장에 세 가지 조건 정리"),
        ("분석의 한계", "충족", "7장에 제시"),
        ("부록: 시스템 주소·저장소 주소·자료 출처·인공지능 활용 내역", "부분 충족", "자료 출처와 인공지능 활용 내역은 있음. 공개 저장소 주소와 배포 주소는 미기재"),
        ("GitHub Pages 배포 주소", "미충족", "현재 문서에는 최종 입력 전 상태로 남아 있음"),
        ("공개 저장소 주소", "미충족", "현재 작업 폴더는 깃 저장소가 아님"),
        ("분석보고서 PDF 제출물", "미충족", "워드 파일까지만 생성됨"),
    ]

    lines = ["# 보고서 검증 결과", "", "## 1. 시스템 수치와 보고서 수치 대조", "", "| 항목 | 시스템 기준값 | 보고서 포함 여부 |", "|---|---|---|"]
    for label, value in checks:
        lines.append(f"| {label} | {value} | {contains(report, value)} |")

    lines.extend(["", "## 2. 과제 요구사항 점검", "", "| 요구사항 | 상태 | 점검 내용 |", "|---|---|---|"])
    for requirement, status, note in requirement_rows:
        lines.append(f"| {requirement} | {status} | {note} |")

    CHECK_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {CHECK_MD}")


if __name__ == "__main__":
    main()
