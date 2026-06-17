from __future__ import annotations

import html
import os
import re
import shutil
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
OUT_MD = REPORT_DIR / "report_final.md"
OUT_DOCX = REPORT_DIR / "report_final.docx"
OUT_REVISED_DOCX = REPORT_DIR / "report_revised.docx"
MEDIA_DIR = REPORT_DIR / "embedded_media"

PHOTO_DIR = Path(r"C:\Users\dydtm\OneDrive\Desktop\스시론 기말 프로젝트 첨부 사진")
SYSTEM_SCREENSHOT = ROOT / ".tmp" / "system-home.png"


@dataclass
class ImageSpec:
    key: str
    path: Path
    caption: str


def find_photo(contains: str) -> Path | None:
    if not PHOTO_DIR.exists():
        return None
    for path in PHOTO_DIR.iterdir():
        if path.is_file() and contains in path.name:
            return path
    return None


def build_markdown() -> str:
    return """# 계획된 업무지구는 어떻게 실제 일자리 중심지가 되는가?

제1판교테크노밸리와 청라 업무중심지구의 개발 실현, 고용 집적, 광역 접근성 비교

## 목차

1. 서론: 계획된 업무지구와 실제 업무지구는 같은가?
2. 분석 방법: 서로 다른 공간자료를 어떻게 같은 기준으로 비교했는가?
3. 개발 실현도: 계획은 실제 업무공간으로 만들어졌는가?
4. 고용·산업 집적: 건축된 공간은 실제 일자리 중심지가 되었는가?
5. 광역 노동시장 접근성: 핵심역은 얼마나 큰 노동시장과 연결되는가?
6. 성공요인 종합: 판교의 활성화를 설명하는 세 조건
7. 분석의 한계 및 결론

판교와 청라의 차이는 업무용지 지정만으로 설명되지 않는다. 판교는 계획이 고밀도 업무공간과 지식기반 고용으로 이어진 반면, 청라는 계획된 업무중심 기능이 현재까지 충분히 실현되지 못했다.

## 1. 서론: 계획된 업무지구와 실제 업무지구는 같은가?

업무지구의 성공은 토지이용계획에서 업무·상업 기능을 지정했는지만으로 판단하기 어렵다. 계획상 업무용지가 있더라도 실제 건축물이 들어서지 않거나, 건축된 공간이 기업과 종사자 집적으로 이어지지 않거나, 충분한 노동시장과 연결되지 않으면 업무지구 기능은 제한된다. 이 보고서는 이러한 문제의식에서 제1판교테크노밸리와 청라 업무중심지구를 비교한다.

[그림:article_gyeonggi]

[그림:article_moneytoday]

위 언론보도 자료는 청라 국제업무단지와 국제업무지구의 개발 지연, 장기간 미활성화 문제가 반복적으로 제기되어 왔음을 보여준다. 이는 청라를 비교 대상으로 선정하는 외부 근거다. 다만 본 보고서는 언론보도에만 의존하지 않고, 토지이용과 건축물, 고용, 접근성 지표를 같은 기준으로 계산해 현재 상태를 검증한다.

[그림:cheongna_vacant_prom1]

[그림:cheongna_vacant_prom2]

프롭 공간자료에서도 청라 국제업무단지의 현재 상태가 확인된다. 지도상 국제업무단지 핵심 구역은 대부분 회색 필지로 표시되어 있고, 토지이용 현황표에서는 나대지가 272,977.4㎡로 전체 363,305.9㎡ 중 75.1%를 차지한다. 필지 수 기준으로도 나대지는 8필지이며, 실제 업무 건축물로 연결된 필지는 제한적이다. 따라서 청라는 “계획이 없는 지역”이 아니라, 국제업무 기능이 계획되었음에도 현재 기준 실제 업무공간과 일자리 중심지로 충분히 실현되지 못한 사례로 볼 수 있다.

비교 기준 지역은 수도권 지식기반 업무지구의 대표 사례인 제1판교테크노밸리다. 비교 지역은 청라국제도시 안에서 국제업무·국제금융 기능이 계획되었으나, 핵심 국제업무단지의 장기 지연과 높은 나대지 비율이 확인되는 청라 업무중심지구다. 여기서 청라는 도시 전체의 실패가 아니라, 현재 기준 계획된 업무중심 기능이 충분히 실현되지 못한 비교 사례를 뜻한다.

중심 질문은 “유사하게 수도권에 계획된 업무지구라도 왜 판교는 기업과 일자리가 집적된 반면, 청라는 아직 계획 대비 활성화가 저조한가?”이다. 본문은 이 차이를 세 조건의 결합으로 해석한다. 첫째, 계획된 업무용지가 실제 건축 공간으로 실현되었는가. 둘째, 건축된 공간이 기업과 종사자의 집적으로 이어졌는가. 셋째, 핵심역이 충분히 큰 광역 노동시장과 연결되는가.

[그림:project_dashboard]

비교 시스템의 핵심 비교 화면은 본문에서 해석할 주요 격차를 먼저 보여준다. 건축물 수, 총연면적, 평균 용적률, 종사자 밀도, 30분 도달 종사자 수가 뒤 장들의 핵심 근거다.

## 2. 분석 방법: 서로 다른 공간자료를 어떻게 같은 기준으로 비교했는가?

### 2.1 비교 경계

판교의 분석 경계는 성남시 홈페이지의 판교 지구단위계획 실행지침 자료를 기준으로 결정했다. 제1판교테크노밸리의 도시지원시설 성격을 확인한 뒤, 프롭 공간자료의 관련 필지와 대조해 경계를 검증했다. 최종 분석 면적은 0.674km²다.

청라는 경계 설정 방식이 더 복잡하다. 인천경제자유구역청 자료상 청라 국제업무단지는 별도 구역으로 제시되지만, 현재 상당 부분이 나대지 상태이므로 그 단독 경계만으로는 판교와 건축물, 연면적, 고용을 정량적으로 비교하기 어렵다.

따라서 청라는 먼저 인천경제자유구역청 위치도에서 국제업무단지의 대략적 범위를 확인하고, 이어서 획지 및 결정도에서 B1, B2와 같은 업무 관련 구역을 직접 대조했다. 이후 프롭 공간자료에서 이 구역들을 표시해 필지고유번호를 추출하고, 국제업무·국제금융·계획 업무용지·실제 업무시설을 포함하되 공동주택 중심 주거블록은 제외했다. 최종 청라 경계는 117개 필지, 1.037km²다.

이 경계 설정은 비교의 공정성을 위한 조치다. 청라국제도시 전체를 포함하면 업무지구가 아닌 주거·상업 기능까지 과도하게 들어가고, 국제업무단지 단독 경계만 쓰면 실제 조성된 업무시설 일부가 빠질 수 있다. 따라서 본문에서 말하는 청라는 청라 전체가 아니라 “청라 업무중심지구”로 한정한다.

[그림:boundary_pangyo]

판교 경계 설정에는 성남시 판교 지구단위계획 실행지침을 사용했다. 이 자료는 제1판교테크노밸리가 도시지원시설 성격의 업무·연구 중심지로 계획되었음을 확인하는 근거이며, 프롭 공간자료에서 내려받은 판교 관련 필지 자료와 대조해 최종 분석 경계를 검증했다.

[그림:prom_pangyo]

프롭 공간자료의 판교 자료 확인 화면은 지구단위계획에서 확인한 경계를 실제 필지 자료와 대조하는 과정에 사용했다. 즉 판교 경계는 계획도상의 범위와 필지 자료가 함께 맞아떨어지는 구역으로 확정했다.

[그림:boundary_cheongna_location]

청라 경계 설정의 첫 단계에서는 인천경제자유구역청의 청라국제업무단지 구역 위치도를 이용해 국제업무단지의 대략적인 위치와 범위를 확인했다. 이 자료는 뒤의 획지 결정도와 프롭 공간자료를 대조하기 위한 기준 위치로 사용했다.

[그림:boundary_cheongna_plan]

청라의 경우 획지 및 결정도에서 국제업무, 국제금융, 중심상업 등 업무중심 기능을 담당하는 구역을 확인했다. 특히 B1, B2와 같은 획지번호를 위치도와 대조해 실제 분석에 포함할 구역을 선별했다.

[그림:boundary_cheongna_prom]

이후 프롭 공간자료에서 위 업무 관련 구역을 직접 지정해 필지고유번호를 추출했다. 이 과정에서 실제 업무시설과 주변 계획 업무용지를 포함하되 공동주택 중심 주거블록은 제외했다. 그 결과 청라 최종 분석 경계는 117개 필지, 1.037km²로 설정되었다.

### 2.2 자료와 처리 기준

| 자료 | 기준시점 | 공간단위 | 사용 목적 | 처리 기준 |
|---|---:|---|---|---|
| 프롭 필지·건축물·용도지역 | 2026년 확보 자료 | 필지, 건축물, 용도지역 면형자료 | 경계, 용도지역, 건축물, 개발 실현 | 경계와 교차하는 객체 포함, 건축물은 건축물관리번호 기준 중복 제거 |
| 통계지리정보서비스 통계 | 2023년 | 집계구 | 인구, 가구, 사업체, 종사자, 산업 | 분석 경계와 집계구의 교차면적 비율로 배분 |
| 통계지리정보서비스 집계구 경계 | 2025년 2분기 | 집계구 면형자료 | 통계 공간배분 | 2023년 통계 코드와 연결 |
| 지하철 네트워크 | 2023-12-31 운영망 | 역, 구간 | 30·60분 및 누적 접근성 | 방향별 시간과 환승 시간을 포함한 최단시간 |
| OpenStreetMap 도로망 | 2026년 수집 | 도로, 교차로 | 도로·교차로 밀도 | 업무지구 경계 내부 도로망만 추출 |

사회경제 비교 기준연도는 2023년이다. 2024년 인구 자료도 일부 확보할 수 있지만 집계구별 사업체·종사자·산업 자료는 2023년까지 제공되므로, 인구만 2024년으로 교체하면 직주비와 접근권 통계의 기준이 달라진다. 따라서 핵심 비교는 2023년으로 통일했다.

### 2.3 공간단위 통합과 접근성 산식

필지는 최종 필지고유번호 집합을 기본 단위로 사용했다. 건축물은 분석 경계와 공간적으로 교차하면 포함하고, 같은 건축물이 중복 집계되지 않도록 건축물관리번호 기준으로 중복을 제거했다. 미건축 필지는 분석 대상 필지 중 어떤 건축물 면형자료와도 교차하지 않는 필지로 정의했다.

통계지리정보서비스 통계는 집계구 경계가 업무지구 경계와 일치하지 않기 때문에 면적비례 배분을 적용했다. 즉 집계구가 분석 경계와 겹치는 면적 비율만큼 인구·가구·사업체·종사자를 배분했다. 이 방식은 집계구 내부 값이 균등하게 분포한다는 가정을 포함한다.

교통 접근성은 판교역과 청라국제도시역을 각 지역의 핵심역으로 두고 계산했다. 지하철 네트워크의 방향별 이동시간과 환승 시간을 포함해 최단시간을 산출하고, 0~60분을 5분 단위로 집계했다. 도달역별 800m 접근권을 병합해 중복 집계를 방지한 뒤, 병합된 접근권과 집계구를 면적비례 방식으로 결합해 도달가능 인구·종사자를 계산했다.

그림 2. 분석 절차 도식: 프롭 경계·필지·건축물 자료로 개발 실현도를 계산하고, 통계지리정보서비스 집계구와 분석 경계를 결합해 내부 인구·고용을 산출했다. 지하철 최단시간 결과는 도달역 800m 병합 접근권으로 변환해 접근권 인구·고용을 계산했으며, OpenStreetMap 도로망은 경계 내부 도로·교차로 밀도 산출에 사용했다.

## 3. 개발 실현도: 계획은 실제 업무공간으로 만들어졌는가?

두 지역 모두 업무 기능을 수용할 수 있는 계획 기반은 존재한다. 판교는 분석 경계의 97.0%가 준주거지역이고, 청라는 중심상업지역이 80.1%, 자연녹지지역이 12.2%다. 다만 용도지역 명칭만으로 활성화 수준을 판단할 수는 없다. 중요한 것은 업무·상업 기능이 허용된 계획이 실제 건축 공간으로 얼마나 실현되었는가다.

[그림:landuse_development]

그림 3·4는 계획 용도와 실제 개발 실현도의 차이를 보여준다. 두 지역 모두 업무 기능을 수용할 제도적 기반은 있지만, 개발 실현 지표에서는 판교 평균 용적률이 401.9%, 청라는 30.4%이고 청라의 미건축 필지 면적 비율은 91.3%다. 이 그림은 계획 용도보다 실제 건축 공간의 실현 정도가 더 큰 차이를 만든다는 근거다.

| 지표 | 판교 | 청라 | 핵심 차이 |
|---|---:|---:|---|
| 건축물 수 | 85개 | 14개 | 판교 6.1배 |
| 총연면적 | 2,710,137㎡ | 315,593㎡ | 판교 8.6배 |
| 평균 용적률 | 401.9% | 30.4% | 판교 13.2배 |
| 미건축 필지 면적 비율 | 31.2% | 91.3% | 청라 +60.1%p |
| 업무시설 연면적 비율 | 96.1% | 65.3% | 판교 +30.8%p |

개발 실현도에서 차이는 매우 크다. 판교는 건축물 85개, 총연면적 271만㎡, 평균 용적률 401.9%로 고밀도의 업무공간이 이미 형성되어 있다. 반면 청라는 분석 경계가 더 넓지만 건축물은 14개, 총연면적은 31.6만㎡, 평균 용적률은 30.4%에 그친다. 특히 청라는 미건축 필지 면적 비율이 91.3%로, 계획상 업무·상업 중심지가 아직 실제 건축 공간으로 충분히 전환되지 않았음을 보여준다.

청라도 업무시설 연면적 비율이 65.3%로 나타나지만, 경계 내부 오피스텔이 건축물대장상 업무시설로 분류되는 문제가 있다. 따라서 청라의 업무시설 비율은 실제 기업 업무공간의 비율로 그대로 해석하기보다, 건축물대장 주용도 기준의 지표로 제한해 읽어야 한다.

혼합도와 도로망 지표는 중심 주장에 대한 반례를 제공한다. 토지이용 혼합도는 판교 0.151, 청라 0.587로 청라가 더 높다. 도로밀도도 판교 7.83km/km², 청라 14.27km/km²이며, 교차로밀도는 판교 20.76개/km², 청라 57.87개/km²다. 그러나 청라의 고용 집적은 판교보다 낮다. 따라서 높은 혼합도나 조밀한 내부 도로망만으로 업무지구 활성화를 설명할 수 없다.

## 4. 고용·산업 집적: 건축된 공간은 실제 일자리 중심지가 되었는가?

건축 공간의 차이는 고용 집적 차이와 함께 나타난다. 판교와 청라의 사업체 수 차이는 1.9배지만, 종사자 수 차이는 21.8배다. 즉 청라는 사업체 수 자체가 전혀 없는 지역은 아니지만, 사업체당 고용 규모와 업무 중심 산업 집적이 판교에 비해 매우 작다.

[그림:socio_industry]

그림 5는 건축 공간의 차이가 실제 고용과 산업구조 차이로 이어지는지를 보여준다. 청라는 인구와 가구가 더 많지만, 판교의 종사자 규모가 압도적으로 크다. 산업별로도 판교는 정보통신업, 전문·과학기술업, 사업지원 서비스업 중심이고 청라는 건설업, 도소매업, 숙박·음식업 비중이 높다.

| 지표 | 판교 | 청라 | 차이 |
|---|---:|---:|---|
| 내부 인구 | 263명 | 4,659명 | 청라가 큼 |
| 가구 | 137가구 | 2,473가구 | 청라가 큼 |
| 사업체 수 | 1,206개 | 636개 | 판교 1.9배 |
| 종사자 수 | 42,668명 | 1,960명 | 판교 21.8배 |
| 종사자 밀도 | 63,269명/km² | 1,890명/km² | 판교 33.5배 |
| 직주비 | 162.4 | 0.42 | 판교가 현저히 높음 |

판교는 내부 상주인구가 작고 종사자 수가 매우 크기 때문에 직주비가 162.4로 나타난다. 이는 판교가 주거지라기보다 외부에서 인력이 유입되는 업무 중심지라는 점을 보여준다. 청라는 내부 인구가 4,659명으로 판교보다 많지만 종사자는 1,960명에 그쳐 직주비가 0.42다. 2024년 인구를 적용하면 청라의 분모가 더 커지므로 직주비는 낮아지는 방향이다. 따라서 청라의 최근 인구 변화 가능성을 고려해도 고용 집적 격차라는 결론은 유지된다.

산업구조에서도 차이가 뚜렷하다. 판교의 상위 종사 산업은 정보통신업 약 19,166명, 전문·과학기술업 약 8,123명, 사업지원 서비스업 약 5,943명이다. 반면 청라의 상위 종사 산업은 건설업 약 385명, 도소매업 약 309명, 숙박·음식업 약 265명이다. 판교는 지식기반 업무산업이 대규모로 집중되어 있지만, 청라는 아직 업무 중심 산업의 대규모 집적이 확인되지 않는다.

## 5. 광역 노동시장 접근성: 핵심역은 얼마나 큰 노동시장과 연결되는가?

업무지구는 내부 공간만으로 작동하지 않는다. 기업 입지에서는 가까운 시간 안에 접근 가능한 노동시장 규모가 중요하다. 본 분석에서는 판교역과 청라국제도시역을 출발점으로 삼아, 지하철 네트워크 기준 30분과 60분 이내 도달 가능한 인구·종사자를 비교했다.

[그림:accessibility]

그림 6·7은 핵심역 접근성이 어느 시간대에서 차이를 만드는지 보여준다. 판교역 30분 도달 종사자는 151.1만 명, 청라국제도시역은 26.8만 명이다. 60분 기준에서는 격차가 줄어들지만, 가까운 노동시장 접근성은 판교가 더 유리하다.

| 지표 | 판교 | 청라 | 차이 |
|---|---:|---:|---|
| 30분 도달 인구 | 1,424,896명 | 622,716명 | 판교 2.3배 |
| 30분 도달 종사자 | 1,510,528명 | 268,369명 | 판교 5.6배 |
| 60분 도달 인구 | 8,405,399명 | 5,596,149명 | 판교 1.5배 |
| 60분 도달 종사자 | 5,531,047명 | 3,371,925명 | 판교 1.6배 |

접근성 격차는 30분 이내에서 특히 크다. 판교역 기준 30분 도달 종사자는 약 151만 명으로, 청라국제도시역 기준 약 27만 명의 5.6배다. 60분으로 넓히면 청라도 수도권 광역권과 연결되면서 격차가 1.6배로 줄어든다. 이는 청라가 완전히 고립된 위치라는 뜻이 아니라, 업무지구 경쟁에 중요한 가까운 노동시장 접근성에서 판교가 더 유리하다는 뜻이다.

누적 접근성 곡선을 보면 종사자 절대 격차는 50분에서 약 248만 명으로 가장 크다. 그러나 비율 격차는 30분 구간에서 더 크게 나타난다. 기업 입장에서 매일 통근 가능한 인력 풀이 가까운 시간대에 얼마나 형성되는지가 중요하다고 보면, 30분 접근권의 격차는 판교의 고용 집적을 뒷받침하는 조건으로 해석할 수 있다.

## 6. 성공요인 종합: 판교의 활성화를 설명하는 세 조건

[그림:key_metrics]

그림 8은 평균 용적률, 미건축 필지 면적, 종사자 밀도, 30분 도달 종사자 수를 함께 제시해 판교의 우위가 개발 실현, 고용 집적, 광역 접근성의 결합에서 나타난다는 점을 요약한다.

첫 번째 성공요인은 계획의 실제 실현이다. 판교의 평균 용적률은 401.9%이고 청라는 30.4%다. 미건축 필지 면적 비율은 판교 31.2%, 청라 91.3%다. 이 차이는 업무용 토지 지정만으로는 충분하지 않으며, 실제 건축·입주 가능한 공간의 실현이 선행조건임을 보여준다.

두 번째 성공요인은 전문화된 업무공간과 지식기반 고용의 집적이다. 판교의 업무시설 연면적 비율은 96.1%이고, 종사자 밀도는 청라의 33.5배다. 또한 정보통신업과 전문·과학기술업 종사자가 크게 집중되어 있다. 이는 건축된 공간이 특정 업무산업과 대규모 고용으로 연결될 때 업무지구의 산업생태계가 형성될 가능성이 높다는 점을 보여준다.

세 번째 성공요인은 가까운 광역 노동시장과의 연결이다. 판교의 30분 도달 종사자는 약 151만 명이고 청라는 약 27만 명이다. 60분 광역권에서는 격차가 줄어들지만, 30분 이내 가까운 노동시장에서는 판교의 우위가 매우 크다. 이는 기업의 인력 확보 조건과 관련될 수 있다.

이 세 조건은 독립적인 목록이 아니라 서로 강화하는 조건으로 보아야 한다. 개발이 실현되어야 기업이 입주할 수 있고, 기업과 고용이 집적되어야 업무지구의 기능이 강화된다. 동시에 충분히 큰 노동시장과 연결되어야 기업이 필요한 인력을 확보하기 쉽다. 청라는 판교보다 도로밀도와 교차로밀도가 높지만 활성화 수준은 낮다. 따라서 내부 도로망 조성은 필요할 수 있으나 충분조건은 아니다.

## 7. 분석의 한계 및 결론

본 분석은 관찰 비교이므로 상관관계에서 인과관계를 확정할 수 없다. 판교와 청라의 차이가 개발 실현, 고용 집적, 접근성 조건과 함께 나타난다고 해석할 수는 있지만, 이 조건들이 성공을 직접 유발했다고 단정할 수는 없다.

자료 기준시점도 다르다. 프롭 물리자료는 2026년 확보 자료이고 통계지리정보서비스 통계는 2023년이다. 청라는 최근 주거 입주가 이어져 2023년 인구가 현재 인구를 일부 과소추정할 수 있다. 다만 동일 산식의 2024년 인구 민감도 분석에서 청라 인구 증가는 약 4.5%였고, 주요 고용 집적 결론을 바꾸지는 않았다. 집계구별 사업체·종사자 자료가 2023년까지만 제공되므로 최신 인구만 2024년으로 교체하지 않고 사회경제 지표 전체를 2023년으로 통일했다.

공간처리 방식에도 한계가 있다. 집계구 면적비례 배분은 인구와 고용이 집계구 내부에 균등하게 분포한다고 가정한다. 도달역 800m 원형 버퍼는 실제 보행경로와 환승 후 이동을 단순화한다. 또한 핵심역 출발 방식은 업무지구 내부에서 역까지의 접근시간을 포함하지 않는다. 건축물대장은 실제 입주율·공실률을 직접 보여주지 않으며, 청라 오피스텔은 건축물대장상 업무시설로 분류되어 실제 거주 기능을 완전히 구분하지 못한다.

결론적으로, 판교와 청라의 활성화 차이는 단순히 업무용지가 지정되었는지나 내부 도로망이 조성되었는지만으로 설명하기 어렵다. 판교는 평균 용적률 401.9%, 종사자 42,668명, 30분 도달 종사자 151만 명으로 개발 실현·고용 집적·가까운 노동시장 접근성이 함께 나타난다. 청라는 중심상업지역 중심의 계획과 높은 도로밀도에도 불구하고 평균 용적률 30.4%, 미건축 필지 면적 비율 91.3%, 종사자 1,960명에 머문다. 업무지구 정책은 토지와 도로를 공급하는 단계에서 끝나지 않고, 실제 개발 실행과 기업·인력 연결을 함께 관리해야 한다.

## 참고문헌 및 자료 출처

- 프롭 필지·건축물·용도지역 자료, 2026년 확보 자료.
- 성남판교지구 택지개발사업 도시지원시설 지구단위계획 시행지침, 2019-01-28.
- 통계지리정보서비스, 2023년 인구·가구·사업체·종사자·산업 통계.
- 통계지리정보서비스 집계구 경계, 2025년 2분기.
- 수도권 지하철 네트워크 그래프, LMS 제공 자료, 2023-12-31 운영망 필터.
- OpenStreetMap 도로망, 2026년 수집, ODbL.
- 본 프로젝트 산출자료: data/processed/comparison_summary_metrics.csv, comparison_zoning_metrics.csv, comparison_building_use_metrics.csv, comparison_industry_metrics.csv, comparison_cumulative_accessibility.csv.
- 경기일보, 인천 청라 국제업무지구 장기간 미활성화 관련 언론보도.
- 머니투데이, 인천 청라 국제업무단지 개발 지연 관련 언론보도.

## 부록 A. 외부 근거 및 원자료

청라 활성화 저조 문제의식에 사용한 언론보도 자료는 서론에 배치했다. 부록에는 청라 원자료 확인 과정을 보여주는 자료만 남긴다.

[그림:prom_cheongna]

## 부록 B. 시스템 및 저장소

- GitHub Pages URL: 최종 배포 후 입력.
- Repository URL: 최종 공개 저장소 생성 후 입력.
- 로컬 확인 URL: http://localhost:8765/, http://127.0.0.1:8765/.

## 부록 C. AI 활용 내역

보고서 구성안 검토, 평가기준 반영 체크, 문장 초안 작성과 표현 정리에 AI 도구를 활용했다. 수치와 사실관계는 프로젝트의 원데이터 및 data/processed 산출 파일을 기준으로 대조했으며, 최종 제출 전 시스템 화면의 표시값과 보고서 본문 수치를 다시 검증한다.
"""


def image_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        idx = 2
        while idx < len(data):
            if data[idx] != 0xFF:
                idx += 1
                continue
            marker = data[idx + 1]
            idx += 2
            if marker in (0xD8, 0xD9):
                continue
            length = struct.unpack(">H", data[idx:idx + 2])[0]
            if marker in range(0xC0, 0xC4):
                h, w = struct.unpack(">HH", data[idx + 3:idx + 7])
                return w, h
            idx += length
    return 1200, 800


def esc(text: str) -> str:
    return html.escape(text, quote=False)


class DocxBuilder:
    def __init__(self, images: dict[str, ImageSpec]):
        self.images = images
        self.rels: list[tuple[str, str, str]] = []
        self.media: list[tuple[Path, str]] = []
        self.next_rid = 1

    def rel(self, target: str, rel_type: str) -> str:
        rid = f"rId{self.next_rid}"
        self.next_rid += 1
        self.rels.append((rid, rel_type, target))
        return rid

    def paragraph(self, text: str, style: str | None = None) -> str:
        pstyle = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
        runs = []
        for i, part in enumerate(re.split(r"(`[^`]+`)", text)):
            if not part:
                continue
            if part.startswith("`") and part.endswith("`"):
                runs.append(f'<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/></w:rPr><w:t>{esc(part[1:-1])}</w:t></w:r>')
            else:
                runs.append(f'<w:r><w:t xml:space="preserve">{esc(part)}</w:t></w:r>')
        return f"<w:p>{pstyle}{''.join(runs)}</w:p>"

    def bullet(self, text: str) -> str:
        return f'<w:p><w:pPr><w:pStyle w:val="ListBullet"/></w:pPr><w:r><w:t>{esc(text)}</w:t></w:r></w:p>'

    def placeholder(self, text: str) -> str:
        shading = '<w:pPr><w:shd w:fill="F2F2F2"/><w:pBdr><w:top w:val="single" w:sz="6" w:color="BFBFBF"/><w:left w:val="single" w:sz="6" w:color="BFBFBF"/><w:bottom w:val="single" w:sz="6" w:color="BFBFBF"/><w:right w:val="single" w:sz="6" w:color="BFBFBF"/></w:pBdr></w:pPr>'
        return f"<w:p>{shading}<w:r><w:rPr><w:b/><w:color w:val=\"666666\"/></w:rPr><w:t>{esc(text)}</w:t></w:r></w:p>"

    def table(self, rows: list[list[str]]) -> str:
        cells_width = 9000 // max(1, len(rows[0]))
        trs = []
        for r_idx, row in enumerate(rows):
            tcs = []
            for cell in row:
                bold = "<w:b/>" if r_idx == 0 else ""
                fill = '<w:shd w:fill="EAF3F6"/>' if r_idx == 0 else ""
                tcs.append(
                    f'<w:tc><w:tcPr><w:tcW w:w="{cells_width}" w:type="dxa"/>{fill}</w:tcPr>'
                    f'<w:p><w:pPr><w:spacing w:before="20" w:after="20"/></w:pPr>'
                    f'<w:r><w:rPr>{bold}<w:sz w:val="19"/></w:rPr><w:t>{esc(cell)}</w:t></w:r></w:p></w:tc>'
                )
            trs.append(f"<w:tr>{''.join(tcs)}</w:tr>")
        return (
            '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
            '<w:jc w:val="center"/><w:tblLook w:firstRow="1" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
            + "".join(trs)
            + "</w:tbl>"
        )

    def image(self, spec: ImageSpec, max_width_in: float = 5.6) -> str:
        ext = spec.path.suffix.lower().lstrip(".") or "png"
        media_name = f"{spec.key}.{ext}"
        self.media.append((spec.path, media_name))
        rid = self.rel(f"media/{media_name}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
        w_px, h_px = image_dimensions(spec.path)
        width_emu = int(max_width_in * 914400)
        height_emu = int(width_emu * h_px / max(1, w_px))
        return f"""
<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="80" w:after="40"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{width_emu}" cy="{height_emu}"/><wp:docPr id="{self.next_rid + 100}" name="{esc(spec.caption)}"/>
<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:nvPicPr><pic:cNvPr id="0" name="{esc(media_name)}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width_emu}" cy="{height_emu}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>
{self.paragraph(spec.caption, "Caption")}
"""

    def convert(self, md: str) -> str:
        parts = []
        lines = md.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line:
                i += 1
                continue
            if line.startswith("# "):
                parts.append(self.paragraph(line[2:], "Title"))
            elif line.startswith("## "):
                parts.append(self.paragraph(line[3:], "Heading1"))
            elif line.startswith("### "):
                parts.append(self.paragraph(line[4:], "Heading2"))
            elif line.startswith("- "):
                parts.append(self.bullet(line[2:]))
            elif re.match(r"^\d+\. ", line):
                parts.append(self.paragraph(line, "ListNumber"))
            elif line.startswith("[그림:") and line.endswith("]"):
                key = line[4:-1]
                spec = self.images.get(key)
                if spec and spec.path.exists():
                    parts.append(self.image(spec))
                else:
                    parts.append(self.placeholder(f"그림 파일 없음: {key}"))
            elif line.startswith("[필요 캡처:"):
                parts.append(self.placeholder(line[1:-1]))
            elif line.startswith("|"):
                rows = []
                while i < len(lines) and lines[i].startswith("|"):
                    raw = lines[i].strip()
                    if re.match(r"^\|[\s:\-|]+\|$", raw):
                        i += 1
                        continue
                    rows.append([c.strip() for c in raw.strip("|").split("|")])
                    i += 1
                parts.append(self.table(rows))
                continue
            else:
                parts.append(self.paragraph(line))
            i += 1
        return "".join(parts)

    def write(self, body: str, out_path: Path) -> None:
        main_rel_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
        document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
<w:body>{body}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>"""
        styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Malgun Gothic" w:hAnsi="Malgun Gothic" w:eastAsia="Malgun Gothic"/><w:sz w:val="22"/><w:color w:val="1F1F1F"/></w:rPr><w:pPr><w:jc w:val="both"/><w:spacing w:after="120" w:line="320" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="123F58"/><w:rFonts w:eastAsia="Malgun Gothic"/></w:rPr><w:pPr><w:jc w:val="center"/><w:spacing w:before="80" w:after="220"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:sz w:val="27"/><w:color w:val="0E5261"/></w:rPr><w:pPr><w:spacing w:before="260" w:after="110"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:sz w:val="23"/><w:color w:val="2E4756"/></w:rPr><w:pPr><w:spacing w:before="180" w:after="70"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:basedOn w:val="Normal"/><w:rPr><w:i/><w:sz w:val="18"/><w:color w:val="555555"/></w:rPr><w:pPr><w:jc w:val="center"/><w:spacing w:after="120"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="420" w:hanging="180"/><w:spacing w:after="60"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="ListNumber"><w:name w:val="List Number"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="420" w:hanging="180"/><w:spacing w:after="60"/></w:pPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="6" w:color="AEBBC7"/><w:left w:val="single" w:sz="6" w:color="AEBBC7"/><w:bottom w:val="single" w:sz="6" w:color="AEBBC7"/><w:right w:val="single" w:sz="6" w:color="AEBBC7"/><w:insideH w:val="single" w:sz="4" w:color="C9D4DD"/><w:insideV w:val="single" w:sz="4" w:color="C9D4DD"/></w:tblBorders></w:tblPr></w:style>
</w:styles>"""
        doc_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
        for rid, rel_type, target in self.rels:
            doc_rels.append(f'<Relationship Id="{rid}" Type="{rel_type}" Target="{target}"/>')
        doc_rels.append("</Relationships>")
        content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">']
        content_types.append('<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>')
        content_types.append('<Default Extension="xml" ContentType="application/xml"/>')
        for ext in sorted({name.rsplit(".", 1)[1] for _, name in self.media}):
            ctype = "image/png" if ext == "png" else "image/jpeg"
            content_types.append(f'<Default Extension="{ext}" ContentType="{ctype}"/>')
        content_types.append('<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>')
        content_types.append('<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>')
        content_types.append("</Types>")
        root_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="{main_rel_type}" Target="word/document.xml"/>
</Relationships>"""
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", "".join(content_types))
            zf.writestr("_rels/.rels", root_rels)
            zf.writestr("word/document.xml", document_xml)
            zf.writestr("word/styles.xml", styles_xml)
            zf.writestr("word/_rels/document.xml.rels", "".join(doc_rels))
            for src, name in self.media:
                zf.write(src, f"word/media/{name}")


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    MEDIA_DIR.mkdir(exist_ok=True)
    images: dict[str, ImageSpec] = {}
    if SYSTEM_SCREENSHOT.exists():
        images["project_dashboard"] = ImageSpec("project_dashboard", SYSTEM_SCREENSHOT, "그림 1. 비교 시스템의 핵심 지표 화면")
    pairs = {
        "article_gyeonggi": ("경기일보", "그림 1-1. 청라 국제업무지구 장기간 미활성화 관련 언론보도 자료"),
        "article_moneytoday": ("머니투데이", "그림 1-2. 청라 국제업무단지 개발 지연 관련 언론보도 자료"),
        "cheongna_vacant_prom1": ("prom 청라국제업무단지 나대지근거1", "그림 1-3. 프롭 공간자료에서 확인한 청라 국제업무단지 나대지 현황"),
        "cheongna_vacant_prom2": ("prom 청라국제업무단지 나대지근거2", "그림 1-4. 청라 국제업무단지 토지이용 현황표"),
        "prom_pangyo": ("판교테크노벨리구역", "그림 A-3. 프롭 판교테크노밸리 원자료 확인 자료"),
        "prom_cheongna": ("청라 국제업무지구", "그림 A-4. 프롭 청라 국제업무지구 원자료 확인 자료"),
        "boundary_pangyo": ("성남시_홈페이지_판교지구단위계획", "그림 2-1. 성남시 판교 지구단위계획 실행지침 근거자료"),
        "boundary_cheongna_location": ("청라국제업무단지 구역 위치", "그림 2-2. 인천경제자유구역청 청라국제업무단지 구역 위치도"),
        "boundary_cheongna_plan": ("청라국제업무단지_구역확인을 위한_획지및결정도", "그림 2-3. 청라 획지 및 결정도상 업무 관련 구역"),
        "boundary_cheongna_prom": ("prom에서 청라 국제업무지구", "그림 2-4. 프롭에서 청라 업무 관련 필지를 지정해 필지고유번호를 추출한 자료"),
        "key_metrics": ("청라_판교_비교 핵심지표", "그림 8. 개발 실현, 고용 집적, 광역 접근성의 핵심 격차"),
        "accessibility": ("판교_청라_동시간권 비교", "그림 6·7. 판교역·청라국제도시역 접근권 및 0~60분 누적 접근성 곡선"),
        "socio_industry": ("청라_판교_종사자및업무지구규모_비교", "그림 5. 업무지구 내부 규모와 산업 대분류별 종사자 비교"),
        "landuse_development": ("판교_청라_용도지역구성비", "그림 3·4. 용도지역 구성, 건축물 주용도, 개발 실현 지표 비교"),
    }
    for key, (needle, caption) in pairs.items():
        path = find_photo(needle)
        if path:
            copied = MEDIA_DIR / path.name
            if path.resolve() != copied.resolve():
                shutil.copy2(path, copied)
            images[key] = ImageSpec(key, copied, caption)

    md = build_markdown()
    OUT_MD.write_text(md, encoding="utf-8")
    builder = DocxBuilder(images)
    body = builder.convert(md)
    docx_path = OUT_DOCX
    for candidate in [
        OUT_DOCX,
        REPORT_DIR / "report_final_revised.docx",
        REPORT_DIR / "report_final_revised2.docx",
    ]:
        try:
            builder.write(body, candidate)
            docx_path = candidate
            break
        except PermissionError:
            continue
    else:
        raise PermissionError("All report docx output paths are locked.")
    try:
        shutil.copy2(docx_path, OUT_REVISED_DOCX)
    except PermissionError:
        pass
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {docx_path}")


if __name__ == "__main__":
    main()
