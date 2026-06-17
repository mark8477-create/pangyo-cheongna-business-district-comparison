# 원천데이터 투입 위치

원본 파일은 압축을 풀지 않아도 됩니다. 파일을 받은 그대로 아래 위치에 넣고
`source_inventory.csv`에 한 줄씩 기록해 주세요.

| 폴더 | 넣을 데이터 |
|---|---|
| `boundary/` | 판교 제2테크노밸리 경계, 청라 B1·B2·B9·B10·C1·C2·M5·M6 경계 |
| `building/` | 건축물대장, 건축물 공간정보 또는 건물 폴리곤 |
| `landuse/` | 용도지역·지구, 토지이용계획, 획지 및 개발계획 도면/공간자료 |
| `sgis/` | 집계구 경계, 인구, 가구, 사업체, 종사자 및 업종 자료 |
| `subway_network/` | LMS 제공 `subway_network.zip` 또는 `nodes.tsv`, `links.tsv` |
| `osm/` | 두 대상지 주변 도로망 자료 (`.pbf`, `.graphml`, `.gpkg` 등) |

## 파일명 권장 규칙

`출처_지역_데이터종류_기준연도.확장자`

예:

- `ifez_cheongna_block_boundary_2025.pdf`
- `sgis_seongnam_population_2025.zip`
- `buildinghub_pangyo_building_2025.zip`

파일명이 모호해도 원본 이름은 바꾸지 않아도 됩니다. 대신 인벤토리에 설명을
정확히 적어 주세요.

