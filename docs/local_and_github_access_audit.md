# 로컬 지속 실행 및 GitHub Pages 호환성 점검

점검일: 2026-06-13

## 로컬 서버

### 접속 링크

- 기본 접속 링크: [http://localhost:8765/](http://localhost:8765/)
- 대체 접속 링크: [http://127.0.0.1:8765/](http://127.0.0.1:8765/)

두 링크는 이 프로젝트가 저장된 현재 컴퓨터에서만 접속할 수 있다.

- Windows 예약 작업: `OfficeDistrictComparisonLocalWeb`
- 실행 조건: 사용자 로그인 시 자동 시작
- 재시작 테스트: 서버 종료 후 예약 작업 실행, 새 PID로 HTTP 200 확인
- 현재 관리 스크립트:
  - `scripts/start_local_web_server.ps1`
  - `scripts/stop_local_web_server.ps1`
  - `scripts/check_local_web_server.ps1`
  - `scripts/register_local_web_server_startup.ps1`

컴퓨터가 종료되거나 사용자가 로그아웃하면 로컬 서버도 종료되지만, 다음 로그인
시 예약 작업으로 자동 시작된다. 절전 중에는 접속할 수 없다.

## GitHub Pages 호환성

- 시스템은 HTML·CSS·JavaScript·GeoJSON·JSON만 사용하는 정적 사이트다.
- 내부 파일과 데이터 경로는 모두 상대경로다.
- 저장소 하위 경로 `/office-district-comparison/` 형태의 로컬 모의 배포에서
  `index.html`, CSS, JavaScript, 요약 JSON이 모두 HTTP 200으로 응답했다.
- `web/` 전체 용량은 약 4.6MB이며 개별 파일이 GitHub 제한을 초과하지 않는다.
- 따라서 `web/` 내용을 GitHub Pages 배포 대상으로 설정하면 동작 가능한 구조다.

## 아직 확인할 수 없는 항목

- 실제 GitHub Pages URL 접속은 저장소 URL과 배포 브랜치가 정해지지 않아 확인하지
  않았다.
- Leaflet, Chart.js, Google Fonts, OSM 타일은 외부 네트워크를 사용한다.
  GitHub 배포 정제 단계에서 CDN 유지 또는 라이브러리 로컬 포함을 결정한다.

## 최종 재점검 결과

- `http://localhost:8765/`: HTTP 200
- `http://127.0.0.1:8765/`: HTTP 200
- CSS, JavaScript, 요약 JSON, 30·60분 등시간권 GeoJSON: 모두 HTTP 200
- 서버 PID `33528`: 실행 중
- 예약 작업 `OfficeDistrictComparisonLocalWeb`: `Ready`
- Edge 렌더링: 핵심 지표 카드, 판교 지도, 청라 지도, 차트 생성 확인
- 시스템 초기화 오류: 없음
