# 정적 비교분석 웹 시스템

이 폴더는 GitHub Pages에 배포되는 실제 화면입니다. 별도 빌드 과정 없이 `index.html`, `app.js`, `styles.css`, `data/`만으로 동작합니다.

## 실행

프로젝트 루트에서:

```powershell
python -m http.server 8765 --directory web
```

접속 주소:

- http://127.0.0.1:8765/
- http://localhost:8765/

## 포함 기능

- 판교·청라 지도 병렬 비교
- 용도지역, 건축물 주용도, 필지·미건축 여부, 30분/60분 등시간권 레이어 전환
- 지도 객체 클릭 팝업
- 핵심 지표 카드
- 토지이용, 개발 실현, 누적 접근성, 인구·산업 차트

## 배포 안정성 메모

GitHub Pages는 정적 파일만 배포하므로 `web/data/`의 JSON/GeoJSON 파일이 저장소에 포함되어야 합니다. CDN 장애를 제외하면 서버 상태나 데이터베이스 상태에 의존하지 않습니다.
