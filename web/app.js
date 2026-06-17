const DATA = "data/";

const COLORS = { pangyo: "#176b87", cheongna: "#d66b32" };
const REGION_NAME = { pangyo: "판교", cheongna: "청라" };
const REGION_FULL_NAME = {
  pangyo: "판교테크노밸리",
  cheongna: "청라 국제업무중심지구",
};

const USE_NAME = {
  office_research: "업무·연구",
  residential: "주거",
  retail_neighborhood: "판매·근린생활",
  education: "교육",
  culture_assembly: "문화·집회",
  lodging: "숙박",
  industrial: "산업·창고",
  other: "기타",
};

const USE_COLOR = {
  office_research: "#287fa0",
  residential: "#dd9870",
  retail_neighborhood: "#e2bd55",
  education: "#7b9b62",
  culture_assembly: "#9875ad",
  lodging: "#b16b79",
  industrial: "#657d8a",
  other: "#a7afb2",
};

const ZONE_NAME = {
  UQA111: "제1종전용주거지역",
  UQA121: "제1종일반주거지역",
  UQA122: "제2종일반주거지역",
  UQA123: "제3종일반주거지역",
  UQA130: "준주거지역",
  UQA210: "중심상업지역",
  UQA410: "보전녹지지역",
  UQA430: "자연녹지지역",
};

const ZONE_COLOR = {
  UQA111: "#e5ad91",
  UQA121: "#dd9870",
  UQA122: "#d78364",
  UQA123: "#c76f58",
  UQA130: "#3b87a1",
  UQA210: "#c66b45",
  UQA410: "#608b69",
  UQA430: "#8eaa74",
};

const INDUSTRY_NAME = {
  "001": "농림어업",
  "002": "광업",
  "003": "제조업",
  "004": "전기·가스",
  "005": "수도·환경",
  "006": "건설업",
  "007": "도소매업",
  "008": "운수·창고",
  "009": "숙박·음식",
  "010": "정보통신",
  "011": "금융·보험",
  "012": "부동산",
  "013": "전문·과학기술",
  "014": "사업지원",
  "015": "공공행정",
  "016": "교육서비스",
  "017": "보건·사회복지",
  "018": "예술·스포츠",
  "019": "기타서비스",
};

const state = {
  data: {},
  maps: {},
  layers: {},
  charts: {},
  currentLayer: "zoning",
  currentTime: 30,
};

const fmt = (value, digits = 0) =>
  Number(value || 0).toLocaleString("ko-KR", { maximumFractionDigits: digits });
const pct = value => `${fmt(Number(value || 0) * 100, 1)}%`;
const compact = value =>
  new Intl.NumberFormat("ko-KR", { notation: "compact", maximumFractionDigits: 1 }).format(value || 0);
const ratioText = (a, b) => (b ? `${fmt(a / b, 1)}배` : "-");
const fetchJSON = file =>
  fetch(DATA + file).then(response => {
    if (!response.ok) throw new Error(`${file} 로드 실패`);
    return response.json();
  });

async function loadData() {
  const files = [
    "comparison_summary_metrics.json",
    "comparison_zoning_metrics.json",
    "comparison_building_use_metrics.json",
    "comparison_industry_metrics.json",
    "comparison_cumulative_accessibility.json",
    "comparison_boundaries.geojson",
    "pangyo_parcels.geojson",
    "cheongna_parcels.geojson",
    "pangyo_buildings.geojson",
    "cheongna_buildings.geojson",
    "pangyo_zoning.geojson",
    "cheongna_zoning.geojson",
    "accessibility_30_60_isochrones.geojson",
  ];
  const values = await Promise.all(files.map(fetchJSON));
  files.forEach((file, index) => {
    state.data[file.replace(/\.(json|geojson)$/, "")] = values[index];
  });
}

function summary(region) {
  return state.data.comparison_summary_metrics.find(row => row.region === region);
}

function renderMetrics() {
  const p = summary("pangyo");
  const c = summary("cheongna");
  const metrics = [
    { name: "건축물 수", key: "building_count", unit: "개" },
    { name: "총 연면적", key: "total_floor_area_sqm", unit: "㎡" },
    { name: "평균 용적률", key: "average_far_pct", unit: "%", digits: 1 },
    { name: "미건축 필지 면적", key: "unbuilt_parcel_area_ratio", unit: "%", digits: 1, isPct: true },
    { name: "종사자 밀도", key: "worker_density_per_km2", unit: "명/㎢" },
    { name: "직주비", key: "job_housing_ratio_workers_per_resident", unit: "", digits: 1 },
    { name: "30·60분 도달 종사자", pairedKey: "workers" },
    { name: "30·60분 도달 인구", pairedKey: "population" },
  ];

  document.querySelector("#key-metrics").innerHTML = metrics.map(metric => {
    if (metric.pairedKey) {
      const key30 = `access_30_${metric.pairedKey}`;
      const key60 = `access_60_${metric.pairedKey}`;
      return `<article class="metric-card metric-card-paired">
        <h3>${metric.name}</h3>
        <div class="metric-values">
          <div><span>판교</span><strong><small>30분</small>${fmt(p[key30])}명</strong><strong><small>60분</small>${fmt(p[key60])}명</strong></div>
          <div><span>청라</span><strong><small>30분</small>${fmt(c[key30])}명</strong><strong><small>60분</small>${fmt(c[key60])}명</strong></div>
        </div>
        <div class="ratio">판교/청라: 30분 ${ratioText(p[key30], c[key30])}, 60분 ${ratioText(p[key60], c[key60])}</div>
      </article>`;
    }

    const pv = metric.isPct ? p[metric.key] * 100 : p[metric.key];
    const cv = metric.isPct ? c[metric.key] * 100 : c[metric.key];
    return `<article class="metric-card">
      <h3>${metric.name}</h3>
      <div class="metric-values">
        <div><span>판교</span><strong>${fmt(pv, metric.digits || 0)}${metric.unit}</strong></div>
        <div><span>청라</span><strong>${fmt(cv, metric.digits || 0)}${metric.unit}</strong></div>
      </div>
      <div class="ratio">판교/청라: ${ratioText(pv, cv)}</div>
    </article>`;
  }).join("");

  document.querySelector("#development-insight").textContent =
    `청라 미건축 면적 ${pct(c.unbuilt_parcel_area_ratio)}, 판교의 ${fmt(c.unbuilt_parcel_area_ratio / p.unbuilt_parcel_area_ratio, 1)}배`;
  document.querySelector("#employment-insight").textContent =
    `판교 종사자 밀도는 청라의 ${fmt(p.worker_density_per_km2 / c.worker_density_per_km2, 1)}배`;
  document.querySelector("#access-insight").textContent =
    `판교 30분 도달 종사자는 청라의 ${fmt(p.access_30_workers / c.access_30_workers, 1)}배`;
}

function createMaps() {
  for (const region of ["pangyo", "cheongna"]) {
    const map = L.map(`map-${region}`, { zoomControl: true, attributionControl: true });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);
    state.maps[region] = map;
    state.layers[region] = {};

    const boundary = state.data.comparison_boundaries.features.find(f => f.properties.region === region);
    const boundaryLayer = L.geoJSON(boundary, {
      style: { color: COLORS[region], weight: 3, fillOpacity: 0 },
    }).addTo(map);
    state.layers[region].boundary = boundaryLayer;
    map.fitBounds(boundaryLayer.getBounds(), { padding: [20, 20] });
  }

  document.querySelector("#layer-select").addEventListener("change", event => {
    state.currentLayer = event.target.value;
    document.querySelector("#time-control").classList.toggle("hidden", state.currentLayer !== "isochrone");
    renderMapLayers();
  });
  document.querySelector("#time-select").addEventListener("change", event => {
    state.currentTime = Number(event.target.value);
    renderMapLayers();
  });
  renderMapLayers();
}

function popupRows(title, rows) {
  return `<div class="popup-title">${title || "정보 없음"}</div>${rows
    .map(([key, value]) => `<div class="popup-row"><span>${key}</span><strong>${value ?? "-"}</strong></div>`)
    .join("")}`;
}

function clearRegionLayer(region) {
  const current = state.layers[region].current;
  if (current) state.maps[region].removeLayer(current);
}

function zoneLabel(feature) {
  return ZONE_NAME[feature.properties.uzone_cd] || feature.properties.uzone_cd || "용도지역";
}

function renderMapLayers() {
  const legends = new Map();

  for (const region of ["pangyo", "cheongna"]) {
    clearRegionLayer(region);
    let geojson;
    let options;
    let stat = "";

    if (state.currentLayer === "zoning") {
      geojson = state.data[`${region}_zoning`];
      options = {
        style: feature => ({
          color: "#fff",
          weight: 0.7,
          fillColor: ZONE_COLOR[feature.properties.uzone_cd] || "#87959a",
          fillOpacity: 0.72,
        }),
        onEachFeature: (feature, layer) => layer.bindPopup(popupRows(zoneLabel(feature), [
          ["면적", `${fmt(feature.properties.area_sqm)}㎡`],
          ["구성비", pct(feature.properties.share)],
        ])),
      };
      geojson.features.forEach(feature => {
        legends.set(zoneLabel(feature), ZONE_COLOR[feature.properties.uzone_cd] || "#87959a");
      });
      stat = "용도지역을 클릭하면 면적과 구성비를 확인할 수 있습니다.";
    } else if (state.currentLayer === "buildings") {
      geojson = state.data[`${region}_buildings`];
      options = {
        style: feature => ({
          color: "#fff",
          weight: 0.7,
          fillColor: USE_COLOR[feature.properties.use_category] || USE_COLOR.other,
          fillOpacity: 0.85,
        }),
        onEachFeature: (feature, layer) => layer.bindPopup(popupRows(USE_NAME[feature.properties.use_category] || "건축물", [
          ["주용도", USE_NAME[feature.properties.use_category] || feature.properties.use_category],
          ["연면적", `${fmt(feature.properties.tot_fl_ar)}㎡`],
          ["용적률", `${fmt(feature.properties.fl_ar_ratio, 1)}%`],
          ["지상층", `${fmt(feature.properties.gr_fl_num)}층`],
        ])),
      };
      Object.entries(USE_COLOR).forEach(([key, value]) => legends.set(USE_NAME[key], value));
      stat = `건축물 ${fmt(summary(region).building_count)}개, 업무시설 연면적 비율 ${pct(summary(region).office_floor_area_ratio)}`;
    } else if (state.currentLayer === "parcels") {
      geojson = state.data[`${region}_parcels`];
      options = {
        style: feature => ({
          color: "#fff",
          weight: 0.7,
          fillColor: feature.properties.is_unbuilt ? "#d66b32" : "#4c8a70",
          fillOpacity: 0.7,
        }),
        onEachFeature: (feature, layer) => layer.bindPopup(popupRows(feature.properties.pnu || "필지", [
          ["PNU", feature.properties.pnu],
          ["대장면적", `${fmt(feature.properties.area)}㎡`],
          ["미건축", feature.properties.is_unbuilt ? "예" : "아니오"],
        ])),
      };
      legends.set("미건축 필지", "#d66b32");
      legends.set("건축 필지", "#4c8a70");
      stat = `미건축 필지 ${fmt(summary(region).unbuilt_parcel_count)}개, 면적 비율 ${pct(summary(region).unbuilt_parcel_area_ratio)}`;
    } else {
      const all = state.data.accessibility_30_60_isochrones;
      geojson = {
        type: "FeatureCollection",
        features: all.features.filter(
          feature => feature.properties.region === region && feature.properties.minutes === state.currentTime,
        ),
      };
      options = {
        style: { color: COLORS[region], weight: 2, fillColor: COLORS[region], fillOpacity: 0.25 },
        onEachFeature: (feature, layer) => layer.bindPopup(popupRows(`${REGION_NAME[region]} ${state.currentTime}분 접근권`, [
          ["인구", `${fmt(feature.properties.population)}명`],
          ["가구", `${fmt(feature.properties.households)}가구`],
          ["종사자", `${fmt(feature.properties.workers)}명`],
        ])),
      };
      legends.set(`${REGION_NAME[region]} ${state.currentTime}분 접근권`, COLORS[region]);
      const feature = geojson.features[0]?.properties;
      stat = feature
        ? `${state.currentTime}분 도달 인구 ${fmt(feature.population)}명, 종사자 ${fmt(feature.workers)}명`
        : "접근권 데이터 없음";
    }

    state.layers[region].current = L.geoJSON(geojson, options).addTo(state.maps[region]);
    document.querySelector(`#map-stat-${region}`).textContent = stat;
  }

  document.querySelector("#map-legend").innerHTML = [...legends]
    .map(([name, color]) => `<span class="legend-item"><i class="legend-swatch" style="background:${color}"></i>${name}</span>`)
    .join("");
}

function groupedRows(data, key, labeler = value => value) {
  const values = [...new Set(data.map(row => row[key]))];
  return {
    labels: values.map(labeler),
    pangyo: values.map(value => data.find(row => row.region === "pangyo" && row[key] === value)?.share * 100 || 0),
    cheongna: values.map(value => data.find(row => row.region === "cheongna" && row[key] === value)?.share * 100 || 0),
  };
}

function baseChart(id, config) {
  state.charts[id] = new Chart(document.querySelector(`#${id}`), config);
}

function renderCharts() {
  Chart.defaults.font.family = "'Noto Sans KR', sans-serif";
  Chart.defaults.color = "#667985";
  const commonScales = { x: { grid: { display: false } }, y: { grid: { color: "#e8edef" } } };

  const zoning = groupedRows(state.data.comparison_zoning_metrics, "uzone_cd", code => ZONE_NAME[code] || code);
  baseChart("zoning-chart", {
    type: "bar",
    data: {
      labels: zoning.labels,
      datasets: [
        { label: "판교", data: zoning.pangyo, backgroundColor: COLORS.pangyo },
        { label: "청라", data: zoning.cheongna, backgroundColor: COLORS.cheongna },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false, scales: commonScales },
  });

  const building = groupedRows(state.data.comparison_building_use_metrics, "use_category", code => USE_NAME[code] || code);
  baseChart("building-chart", {
    type: "bar",
    data: {
      labels: building.labels,
      datasets: [
        { label: "판교", data: building.pangyo, backgroundColor: COLORS.pangyo },
        { label: "청라", data: building.cheongna, backgroundColor: COLORS.cheongna },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false, scales: commonScales },
  });

  const p = summary("pangyo");
  const c = summary("cheongna");
  baseChart("development-chart", {
    type: "bar",
    data: {
      labels: ["평균 용적률", "미건축 필지 면적 비율", "업무시설 연면적 비율"],
      datasets: [
        { label: "판교", data: [p.average_far_pct, p.unbuilt_parcel_area_ratio * 100, p.office_floor_area_ratio * 100], backgroundColor: COLORS.pangyo },
        { label: "청라", data: [c.average_far_pct, c.unbuilt_parcel_area_ratio * 100, c.office_floor_area_ratio * 100], backgroundColor: COLORS.cheongna },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false, scales: commonScales },
  });

  const access = state.data.comparison_cumulative_accessibility;
  const minutes = [...new Set(access.map(row => row.minutes))];
  baseChart("access-chart", {
    type: "line",
    data: {
      labels: minutes.map(minute => `${minute}분`),
      datasets: [
        ...["pangyo", "cheongna"].map(region => ({
          label: `${REGION_NAME[region]} 인구`,
          data: minutes.map(minute => access.find(row => row.region === region && row.minutes === minute).population),
          borderColor: COLORS[region],
          backgroundColor: COLORS[region],
          tension: 0.25,
        })),
        ...["pangyo", "cheongna"].map(region => ({
          label: `${REGION_NAME[region]} 종사자`,
          data: minutes.map(minute => access.find(row => row.region === region && row.minutes === minute).workers),
          borderColor: COLORS[region],
          borderDash: [6, 4],
          backgroundColor: COLORS[region],
          tension: 0.25,
        })),
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: { x: { grid: { display: false } }, y: { ticks: { callback: compact }, grid: { color: "#dbe5e6" } } },
    },
  });

  baseChart("social-chart", {
    type: "bar",
    data: {
      labels: ["인구", "가구", "사업체", "종사자"],
      datasets: [
        { label: "판교", data: [p.population, p.households, p.businesses, p.workers], backgroundColor: COLORS.pangyo },
        { label: "청라", data: [c.population, c.households, c.businesses, c.workers], backgroundColor: COLORS.cheongna },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { ...commonScales, y: { type: "logarithmic", grid: { color: "#e8edef" } } } },
  });

  const workers = state.data.comparison_industry_metrics.filter(row => row.measure === "workers" && row.metric !== "secret_or_unprovided_gap");
  const industryRows = [...new Set(workers.map(row => row.metric.slice(-3)))]
    .map(code => ({
      name: INDUSTRY_NAME[code] || code,
      pangyo: workers.find(row => row.region === "pangyo" && row.metric.endsWith(code))?.value || 0,
      cheongna: workers.find(row => row.region === "cheongna" && row.metric.endsWith(code))?.value || 0,
    }))
    .sort((a, b) => b.pangyo + b.cheongna - (a.pangyo + a.cheongna))
    .slice(0, 10);

  baseChart("industry-chart", {
    type: "bar",
    data: {
      labels: industryRows.map(row => row.name),
      datasets: [
        { label: "판교", data: industryRows.map(row => row.pangyo), backgroundColor: COLORS.pangyo },
        { label: "청라", data: industryRows.map(row => row.cheongna), backgroundColor: COLORS.cheongna },
      ],
    },
    options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, scales: commonScales },
  });
}

function renderAccessCards() {
  const cards = [];
  for (const minutes of [30, 60]) {
    for (const region of ["pangyo", "cheongna"]) {
      const row = summary(region);
      cards.push(`<article class="access-card ${region}">
        <span>${REGION_FULL_NAME[region]} · ${minutes}분 접근권</span>
        <div class="access-values">
          <div><span>도달 종사자</span><strong>${compact(row[`access_${minutes}_workers`])}명</strong></div>
          <div><span>도달 인구</span><strong>${compact(row[`access_${minutes}_population`])}명</strong></div>
        </div>
      </article>`);
    }
  }
  document.querySelector("#access-cards").innerHTML = cards.join("");
}

function setupNavigation() {
  document.querySelectorAll(".nav-button").forEach(button => button.addEventListener("click", () => {
    document.querySelector(`#${button.dataset.target}`).scrollIntoView({ behavior: "smooth" });
  }));

  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) {
      document.querySelectorAll(".nav-button").forEach(button => {
        button.classList.toggle("active", button.dataset.target === entry.target.id);
      });
    }
  }), { rootMargin: "-30% 0px -60% 0px" });

  document.querySelectorAll("main section").forEach(section => observer.observe(section));
}

async function init() {
  try {
    await loadData();
    renderMetrics();
    createMaps();
    renderCharts();
    renderAccessCards();
    setupNavigation();
  } catch (error) {
    console.error(error);
    const box = document.querySelector("#error");
    box.textContent = `시스템 초기화 오류: ${error.message}. 로컬 파일 직접 열기 대신 HTTP 서버로 실행하세요.`;
    box.classList.remove("hidden");
  } finally {
    document.querySelector("#loading").classList.add("hidden");
  }
}

init();
