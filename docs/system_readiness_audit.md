# 시스템 구상 전 준비상태 점검

점검일: 2026-06-13

## 판정

`final_exam.html`의 §3 필수 분석과 §4 시스템 구현에 필요한 정적 입력자료가
준비되었다. 다음 단계는 시스템 화면·차트·상호작용 구상 및 구현이다.

## §3 필수 분석

| 영역 | 상태 | 산출물 |
|---|---|---|
| 용도지역 구성비 | 완료 | `comparison_zoning_metrics.csv` |
| 건축물 주용도 구성비 | 완료 | `comparison_building_use_metrics.csv` |
| LUM·개발 실현도 | 완료 | `comparison_summary_metrics.csv` |
| 30·60분 등시간권 | 완료 | `accessibility_30_60_isochrones.geojson` |
| 누적 접근성 곡선 | 완료 | `comparison_cumulative_accessibility.csv` |
| OSM 도로망 보조 지표 | 완료 | `comparison_summary_metrics.csv` |
| 인구·가구·사업체·종사자 | 완료 | `comparison_summary_metrics.csv` |
| 산업 구성·직주비 | 완료 | `comparison_industry_metrics.csv`, `comparison_summary_metrics.csv` |

청라 활성화 저조는 동일 산식의 내부 비교 결과로 검증한다. 청라의 미건축 필지
면적 비율은 약 91.3%이며 판교보다 건축물 수, 총연면적, 종사자 밀도, 직주비가
낮다.

## §4 시스템 입력자료

| 필수 기능 | 준비상태 |
|---|---|
| 두 지역 경계 및 필지·건축물 컬러맵 | 경계·필지·건축물·용도지역 GeoJSON 완료 |
| 30·60분 등시간권 레이어 | 4개 폴리곤 완료 |
| 시간대 전환·누적 접근성 | 0~60분 5분 단위 26개 폴리곤 및 JSON 완료 |
| 통계 패널 | 요약·용도지역·건축물·산업·접근성 JSON 완료 |
| 필지·건축물 클릭 팝업 | 팝업용 속성 포함 GeoJSON 완료 |

## 검증 결과

- 판교 용도지역 구성비 합계: 100.0000%
- 청라 용도지역 구성비 합계: 99.9678%
- 판교·청라 접근성: 지역별 13개 시간구간
- 30·60분 등시간권: 총 4개
- 지도용 GeoJSON geometry: 모두 유효
- 비교 요약 결측값: 없음
- `source_inventory.csv`의 미확보(`needed`) 항목: 없음

청라 용도지역 구성비의 약 0.0322% 미집계는 PROM 용도지역 레이어와 최종 PNU
경계 사이의 미세한 경계 차이이며 보고서의 공간자료 한계로 기록한다.
