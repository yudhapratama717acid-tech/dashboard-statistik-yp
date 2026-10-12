const CYAN = "#38e1ff", VIOLET = "#8b5cf6", PINK = "#ff4fa3", AMBER = "#ffc857";
const $ = id => document.getElementById(id);
const fetchJSON = async url => (await fetch(url)).json();
const fmt = v => Number(v).toLocaleString("id-ID", {maximumFractionDigits: 2});
const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

Chart.defaults.font.family = '"Sora", "Segoe UI", system-ui, sans-serif';
Chart.defaults.color = "#93a4d0";
Chart.defaults.borderColor = "rgba(255,255,255,.08)";
Chart.defaults.animation.duration = calm ? 0 : 1000;
Object.assign(Chart.defaults.plugins.tooltip, {backgroundColor: "rgba(10,15,40,.96)", borderColor: "rgba(255,255,255,.15)", borderWidth: 1, padding: 10, cornerRadius: 8});

// gradien vertikal untuk batang
const grad = (c1, c2) => ctx => {
  const a = ctx.chart.chartArea;
  if (!a) return c1;
  const g = ctx.chart.ctx.createLinearGradient(0, a.bottom, 0, a.top);
  g.addColorStop(0, c1); g.addColorStop(1, c2);
  return g;
};

// angka naik dari 0
function countUp(el, to, dec = 0, ms = 1300) {
  if (calm) { el.textContent = to.toFixed(dec); return; }
  const t0 = performance.now();
  const step = t => {
    const p = Math.min((t - t0) / ms, 1), e = 1 - Math.pow(1 - p, 3);
    el.textContent = (to * e).toFixed(dec);
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

let histChart, donutChart, gbarChart, scatterChart, corrChart;

async function init() {
  const s = await fetchJSON("/api/summary");
  countUp($("k-total"), s.total);
  countUp($("k-cols"), s.columns);
  countUp($("k-study"), s.avg_study, 2);
  countUp($("g-val"), s.avg_exam, 1, 1800);
  requestAnimationFrame(() => $("ring").style.strokeDashoffset = 440 * (1 - s.avg_exam / 100));

  for (const id of ["var-select", "x-select", "y-select"])
    $(id).innerHTML = s.variables.map(v => `<option value="${v.value}">${v.label}</option>`).join("");
  $("var-select").value = "Study_Hours";
  $("x-select").value = "Study_Hours";
  $("y-select").value = "Exam_Score";
  $("var-select").onchange = loadVariable;
  $("x-select").onchange = $("y-select").onchange = loadScatter;
  $("swap").onclick = () => {
    const t = $("x-select").value;
    $("x-select").value = $("y-select").value;
    $("y-select").value = t;
    loadScatter();
  };

  loadVariable(); loadGender(); loadScatter(); loadInsights(); loadMatrix();
}

async function loadVariable() {
  const d = await fetchJSON("/api/variable/" + $("var-select").value);
  const st = d.stats;
  if (histChart) histChart.destroy();
  histChart = new Chart($("hist"), {
    type: "bar",
    data: {labels: d.histogram.labels,
           datasets: [{data: d.histogram.counts, backgroundColor: grad(VIOLET, CYAN), borderRadius: 8, borderSkipped: false, barPercentage: .88}]},
    options: {responsive: true, maintainAspectRatio: false,
      plugins: {legend: {display: false}, title: {display: true, text: "Distribusi " + d.label, color: "#eaf0ff", font: {size: 13, weight: 600}}},
      scales: {y: {title: {display: true, text: "Frekuensi"}, beginAtZero: true, ticks: {precision: 0}}, x: {grid: {display: false}}}}
  });

  const items = [[st.mean, "Mean"], [st.median, "Median"], [st.mode, "Modus"], [st.std, "Std Dev"], [st.variance, "Variansi"],
    [st.range, "Range"], [st.q1, "Q1"], [st.q3, "Q3"], [st.iqr, "IQR"], [st.skewness, "Skewness"], [st.cv, "CV %"], [st.outliers, "Outlier"]];
  $("tiles").innerHTML = items.map(([v, l]) => `<div class="tile"><b class="mono">${fmt(v)}</b><span>${l}</span></div>`).join("") +
    `<div class="shape"><span class="badge ${d.shape === "Simetris" ? "" : "warn"}">${d.shape}</span></div>`;

  const span = (d.max - d.min) || 1, pct = v => (v - d.min) / span * 100;
  $("b-iqr").style.left = pct(st.q1) + "%";
  $("b-iqr").style.width = (pct(st.q3) - pct(st.q1)) + "%";
  $("b-med").style.left = `calc(${pct(st.median)}% - 2px)`;
  $("l-min").textContent = "Min " + fmt(d.min);
  $("l-mid").textContent = `Q1 ${fmt(st.q1)} | Median ${fmt(st.median)} | Q3 ${fmt(st.q3)}`;
  $("l-max").textContent = "Max " + fmt(d.max);
}

async function loadGender() {
  const g = await fetchJSON("/api/gender");
  const colors = g.labels.map(l => l === "F" ? PINK : CYAN);
  donutChart = new Chart($("donut"), {
    type: "doughnut",
    data: {labels: g.labels, datasets: [{data: g.counts, backgroundColor: colors, borderColor: "#070b1f", borderWidth: 4, hoverOffset: 8}]},
    options: {responsive: true, maintainAspectRatio: false, cutout: "68%", plugins: {legend: {position: "bottom", labels: {usePointStyle: true}}}}
  });
  gbarChart = new Chart($("gbar"), {
    type: "bar",
    data: {labels: g.labels, datasets: [{data: g.avg_exam, backgroundColor: colors, borderRadius: 10, borderSkipped: false, barPercentage: .6}]},
    options: {responsive: true, maintainAspectRatio: false,
      plugins: {legend: {display: false}, title: {display: true, text: "Rata-rata Exam Score", color: "#eaf0ff", font: {size: 13, weight: 600}}},
      scales: {y: {min: 0, max: 100}, x: {grid: {display: false}}}}
  });
}

async function loadScatter() {
  const d = await fetchJSON(`/api/scatter?x=${$("x-select").value}&y=${$("y-select").value}`);
  if (scatterChart) scatterChart.destroy();
  scatterChart = new Chart($("scatter"), {
    type: "scatter",
    data: {datasets: [
      {label: "Mahasiswa", data: d.points, backgroundColor: "rgba(56,225,255,.7)", borderColor: "rgba(139,92,246,.9)", borderWidth: 1, pointRadius: 5, pointHoverRadius: 8},
      {label: "Garis regresi", data: d.line, type: "line", borderColor: PINK, borderWidth: 3, pointRadius: 0, fill: false}]},
    options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}},
      scales: {x: {title: {display: true, text: d.x_label}}, y: {title: {display: true, text: d.y_label}}}}
  });
  $("corr").innerHTML = `r = <b class="mono">${d.r}</b> &nbsp; R² = <b class="mono">${d.r2}</b> &nbsp; ` +
    `y = ${d.slope}x + ${d.intercept} &nbsp; <b>${d.interpretation}</b>`;
}

async function loadInsights() {
  const c = await fetchJSON("/api/correlation");
  if (corrChart) corrChart.destroy();
  corrChart = new Chart($("corrbar"), {
    type: "bar",
    data: {labels: c.labels, datasets: [{data: c.values, backgroundColor: c.values.map(v => v >= 0 ? CYAN : PINK), borderRadius: 6, borderSkipped: false}]},
    options: {indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}},
      scales: {x: {min: -1, max: 1, title: {display: true, text: "Korelasi (r) dengan Exam Score"}}, y: {grid: {display: false}, afterFit: ax => { ax.width = Math.max(ax.width, 140); }}}}
  });
  const sg = await fetchJSON("/api/segments");
  const max = Math.max(...sg.map(s => s.count));
  countUp($("k-risk"), sg.filter(s => s.risk).reduce((a, s) => a + s.count, 0));
  $("segments").innerHTML = sg.map(s =>
    `<div class="seg"><span class="n">${s.label}</span><div class="bar ${s.risk ? "risk" : ""}" style="width:${s.count / max * 60}%"></div><b class="mono">${s.count}</b></div>`).join("");
}

async function loadMatrix() {
  const m = await fetchJSON("/api/matrix");
  const cell = (v, i, j) => {
    const rgb = v >= 0 ? "56,225,255" : "255,79,163";
    return `<td class="${i === j ? "diag" : ""}" style="background:rgba(${rgb},${(Math.abs(v) * .7).toFixed(2)})">${v.toFixed(2)}</td>`;
  };
  $("matrix").innerHTML =
    `<thead><tr><th></th>${m.labels.map(l => `<th>${l}</th>`).join("")}</tr></thead><tbody>` +
    m.values.map((row, i) => `<tr><th>${m.labels[i]}</th>${row.map((v, j) => cell(v, i, j)).join("")}</tr>`).join("") +
    "</tbody>";
}

// tunggu font Sora siap supaya lebar label sumbu terukur benar
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(init);
