# 판교·청라 업무지구 비교분석

판교테크노밸리와 청라 국제업무중심지구를 동일한 공간 경계와 동일한 산식으로 비교하는 기말고사 제출용 프로젝트입니다. 결과물은 GitHub Pages에서 바로 열리는 정적 웹 시스템과 분석 보고서 PDF로 구성됩니다.

## 제출 링크

- Repository URL: https://github.com/mark8477-create/pangyo-cheongna-business-district-comparison
- GitHub Pages URL: 배포 후 `https://mark8477-create.github.io/pangyo-cheongna-business-district-comparison/`
- 보고서 PDF: `report/스마트시티의 이론과 실제 기말고사 프로젝트 보고서.pdf`

## 시스템 구성

- `web/index.html`: 제출용 정적 웹앱
- `web/app.js`: 지도, 지표 카드, 차트, 상호작용 로직
- `web/styles.css`: 반응형 화면 스타일
- `web/data/`: GitHub Pages에서 직접 읽는 전처리 완료 JSON/GeoJSON
- `scripts/`: 경계 검증, SGIS/OSM 전처리, 비교지표 재산출, 보고서 생성 스크립트
- `data/processed/`: 분석 산출물 CSV/GeoJSON
- `data_raw/source_inventory.csv`: 원천 데이터 출처와 기준 시점 목록
- `docs/`: 배포 및 시스템 점검 문서
- `.github/workflows/pages.yml`: GitHub Pages 자동 배포 워크플로

## 필수 기능 대응

- 지도 기반 시각화: 판교·청라 경계, 용도지역, 건축물 주용도, 필지·미건축 여부를 지도에서 전환합니다.
- 등시간권 레이어: 중심역 기준 30분/60분 접근권과 도달 인구·종사자 수를 표시합니다.
- 통계 패널: 토지이용, 개발 실현, 누적 접근성, 인구·고용·산업 지표를 카드와 차트로 비교합니다.
- 상호작용: 레이어 전환, 시간권 전환, 지도 객체 클릭 팝업, 섹션 이동을 제공합니다.

## 기술 조건 대응

이 시스템은 별도 서버나 DB 없이 GitHub Pages에서 동작하는 정적 사이트입니다. 모든 분석 데이터는 `web/data/`에 전처리된 JSON/GeoJSON 파일로 포함되어 있으며, 브라우저는 `fetch()`로 해당 파일을 읽습니다.

외부 라이브러리는 CDN으로 불러옵니다.

- Leaflet 1.9.4: 지도 렌더링
- Chart.js 4.4.7: 비교 차트
- OpenStreetMap tile: 기본 지도
- Google Fonts Noto Sans KR: 한글 표시

## 재현 방법

로컬 실행:

```powershell
python -m http.server 8765 --directory web
```

브라우저에서 `http://127.0.0.1:8765/`에 접속합니다. `index.html`을 파일 탐색기에서 직접 열면 브라우저 보안 정책 때문에 JSON/GeoJSON `fetch()`가 실패할 수 있습니다.

정적 웹 검증:

```powershell
python tests/test_web_system.py
```

주요 비교지표 재산출:

```powershell
python scripts/08_rebuild_comparison_metrics.py
```

OSM 원천 데이터를 다시 수집해야 하는 경우:

```powershell
python scripts/06_preprocess_osm.py
```

## 배포 방법

1. 이 폴더를 GitHub 저장소 `pangyo-cheongna-business-district-comparison`에 push합니다.
2. GitHub 저장소의 `Settings > Pages`에서 Source를 `GitHub Actions`로 설정합니다.
3. `main` 브랜치에 push되면 `.github/workflows/pages.yml`이 `web/` 폴더를 GitHub Pages로 배포합니다.
4. 배포 완료 후 Pages URL에서 지도, 차트, 데이터 로딩이 정상인지 확인합니다.

Actions를 사용하지 않고 `Deploy from a branch` 방식으로 배포해도 루트 `index.html`이 `web/`으로 이동시키므로 `https://mark8477-create.github.io/pangyo-cheongna-business-district-comparison/web/`에서 확인할 수 있습니다.

## 분석 기준

- 비교 대상: 판교테크노밸리, 청라 국제업무중심지구
- PROM 토지·건축물 자료: 2026년 기준
- SGIS 통계: 2023년
- SGIS 집계구 경계: 2025년 2분기
- 지하철 네트워크 컷오프: 2023-12-31
- 공간 통합: 지구 경계와 집계구가 일치하지 않는 통계는 교차면적 비율로 배분했습니다.
- 건축물 중복 처리: 경계와 교차하는 건축물을 포함하고 `bd_mng_id` 기준으로 중복을 제거했습니다.
- 미건축 필지: 대상 필지 중 건축물 geometry와 교차하지 않는 필지로 정의했습니다.

## 주요 결과 파일

- `data/processed/comparison_summary_metrics.csv`
- `data/processed/comparison_zoning_metrics.csv`
- `data/processed/comparison_building_use_metrics.csv`
- `data/processed/comparison_industry_metrics.csv`
- `data/processed/comparison_cumulative_accessibility.csv`
- `data/processed/accessibility_30_60_isochrones.geojson`
- `data/processed/cumulative_accessibility_isochrones.geojson`

## AI 사용 내역

AI 도구는 코드 작성 보조, 정적 웹 배포 구조 점검, README 문서 정리, 제출 요구사항 대비 검증 목록 작성에 사용했습니다. 분석 수치와 결론은 포함된 원천 데이터와 전처리 산출물을 기준으로 검토했습니다.
