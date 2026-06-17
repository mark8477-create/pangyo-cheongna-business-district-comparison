# 판교·청라 업무지구 비교분석

판교테크노밸리와 청라 국제업무중심지구를 동일한 공간 경계와 동일한 산식으로 비교한 기말고사 제출용 프로젝트입니다. 별도 서버나 데이터베이스 없이 GitHub Pages에서 바로 실행되는 정적 웹 시스템입니다.

## 제출물 확인

| 구분 | 링크 / 파일 |
| --- | --- |
| 배포 시스템 | https://mark8477-create.github.io/pangyo-cheongna-business-district-comparison/ |
| 공개 저장소 | https://github.com/mark8477-create/pangyo-cheongna-business-district-comparison |
| 보고서 PDF | `report/스마트시티의 이론과 실제 기말고사 프로젝트 보고서.pdf` |

## 시스템 사용 방법

교수자 또는 평가자는 위의 **배포 시스템 URL**을 브라우저에서 열면 됩니다. 로컬 서버 실행이나 별도 설치는 필요하지 않습니다.

화면에서 다음 항목을 확인할 수 있습니다.

- 핵심 비교 카드: 개발 실현도, 고용 집적, 30분·60분 접근성 지표
- 공간 비교 지도: 판교와 청라를 나란히 놓고 용도지역, 건축물 주용도, 필지·미건축 여부, 등시간권을 전환
- 등시간권 레이어: 중심역 기준 30분/60분 접근권과 도달 인구·종사자 수
- 통계 차트: 토지이용, 개발 실현, 누적 접근성, 인구·고용·산업 비교
- 지도 팝업: 필지, 건축물, 용도지역, 접근권 객체 클릭 시 세부 속성 확인

## 시스템 구현 방식

이 시스템은 GitHub Pages에 배포된 정적 웹앱입니다.

- `web/index.html`: 실제 배포 화면
- `web/app.js`: 지도, 차트, 지표 카드, 상호작용 로직
- `web/styles.css`: 반응형 화면 스타일
- `web/data/`: 배포 시스템이 직접 읽는 전처리 완료 JSON/GeoJSON
- `.github/workflows/pages.yml`: GitHub Actions 기반 Pages 자동 배포 설정

사용 라이브러리:

- Leaflet 1.9.4: 지도 렌더링
- Chart.js 4.4.7: 비교 차트
- OpenStreetMap tile: 기본 지도
- Google Fonts Noto Sans KR: 한글 표시

## 재현 및 검증 방법

아래 절차는 평가자가 코드를 직접 내려받아 확인할 때 사용하는 선택 검증 절차입니다. 배포 시스템 확인만 할 경우에는 실행하지 않아도 됩니다.

### 1. 저장소 받기

```powershell
git clone https://github.com/mark8477-create/pangyo-cheongna-business-district-comparison.git
cd pangyo-cheongna-business-district-comparison
```

### 2. 정적 웹앱 로컬 확인

```powershell
python -m http.server 8765 --directory web
```

브라우저에서 `http://127.0.0.1:8765/`에 접속합니다. 이 주소는 로컬 검증용이며 제출 URL이 아닙니다.

### 3. 정적 파일 검증

```powershell
python tests/test_web_system.py
```

이 검증은 HTML 필수 요소, JavaScript 데이터 참조, JSON/GeoJSON 파일 존재 여부, 핵심 접근권 데이터 조합을 확인합니다.

### 4. 주요 비교지표 재산출

```powershell
python scripts/08_rebuild_comparison_metrics.py
```

원천자료와 전처리 환경이 준비된 경우 위 스크립트로 `data/processed/` 및 `web/data/`의 주요 비교지표를 다시 생성할 수 있습니다.

## 분석 기준

- 비교 대상: 판교테크노밸리, 청라 국제업무중심지구
- PROM 토지·건축물 자료: 2026년 기준
- SGIS 통계: 2023년
- SGIS 집계구 경계: 2025년 2분기
- 지하철 네트워크 컷오프: 2023-12-31
- 공간 통합: 지구 경계와 집계구가 일치하지 않는 통계는 교차면적 비율로 배분
- 건축물 중복 처리: 경계와 교차하는 건축물을 포함하고 `bd_mng_id` 기준으로 중복 제거
- 미건축 필지: 대상 필지 중 건축물 geometry와 교차하지 않는 필지로 정의

## 주요 산출 파일

- `data/processed/comparison_summary_metrics.csv`
- `data/processed/comparison_zoning_metrics.csv`
- `data/processed/comparison_building_use_metrics.csv`
- `data/processed/comparison_industry_metrics.csv`
- `data/processed/comparison_cumulative_accessibility.csv`
- `data/processed/accessibility_30_60_isochrones.geojson`
- `data/processed/cumulative_accessibility_isochrones.geojson`
- `web/data/*.json`, `web/data/*.geojson`

## 데이터 출처 및 문서

- 원천 데이터 목록: `data_raw/source_inventory.csv`
- 데이터 수집 안내: `docs/DATA_COLLECTION_GUIDE.md`
- 시스템 요구사항 점검: `docs/system_requirements_audit.md`
- 배포 계획 및 점검: `docs/github_deployment_plan.md`

## AI 사용 내역

AI 도구는 코드 작성 보조, 정적 웹 배포 구조 점검, README 문서 정리, 제출 요구사항 대비 검증 목록 작성에 사용했습니다. 분석 수치와 결론은 포함된 원천 데이터와 전처리 산출물을 기준으로 검토했습니다.
