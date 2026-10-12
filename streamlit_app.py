"""Dashboard Statistik Deskriptif Mahasiswa versi Streamlit.

Jalankan:
    python -m pip install streamlit pandas numpy
    python -m streamlit run streamlit_app.py
"""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

PRIMARY, ACCENT, SUN, INK, MUTED = "#2748d9", "#f0566a", "#ffc43d", "#101a3a", "#5b6585"

st.set_page_config(page_title="Statistik Deskriptif Mahasiswa", layout="wide")

st.markdown(f"""
<style>
.stApp {{background:#f3f5fb;}}
.block-container {{padding-top:0; max-width:1300px;}}
header[data-testid="stHeader"] {{background:transparent;}}
.hero {{background:{PRIMARY};color:#fff;padding:34px 28px 80px;border-bottom:6px solid {SUN};
        margin:0 -4rem 0; }}
.hero h1 {{margin:0 0 6px;font-size:32px;color:#fff;padding:0}}
.hero p {{margin:0;color:#d6defc}}
.kpis {{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:-52px 0 18px}}
.kpi {{background:#fff;border:2px solid {INK};border-radius:6px;padding:14px 18px}}
.kpi b {{display:block;font-size:30px;font-family:Consolas,monospace;color:{INK}}}
.kpi span {{color:{MUTED};font-size:14px}}
.tiles {{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.tile {{background:#eaeefb;border-left:4px solid {PRIMARY};border-radius:3px;padding:10px 12px}}
.tile b {{display:block;font-size:19px;font-family:Consolas,monospace;color:{INK}}}
.tile span {{font-size:12px;color:{MUTED}}}
.badge {{display:inline-block;color:#fff;background:{PRIMARY};font-weight:600;font-size:12px;
         padding:3px 10px;border-radius:99px;margin-top:10px}}
.badge.warn {{background:{ACCENT}}}
.box {{position:relative;height:22px;margin:14px 0 6px}}
.box .line {{position:absolute;top:10px;left:0;right:0;height:2px;background:{INK}}}
.box .iqr {{position:absolute;top:0;height:22px;background:#c5d0f7;border:2px solid {PRIMARY};border-radius:3px}}
.box .med {{position:absolute;top:-3px;width:4px;height:28px;background:{ACCENT}}}
.boxlbl {{display:flex;justify-content:space-between;font-size:12px;color:{MUTED}}}
.seg {{display:flex;align-items:center;gap:10px;margin:8px 0;font-size:14px}}
.seg .bar {{height:16px;border-radius:2px;background:{PRIMARY}}}
.seg .bar.risk {{background:{ACCENT}}}
.seg .n {{width:60px;color:{MUTED}}}
div[data-testid="stVerticalBlockBorderWrapper"] {{background:#fff;}}
@media(max-width:900px){{.kpis{{grid-template-columns:1fr 1fr}}}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).parent / "latihan1.csv")


df = load()
NUM = [c for c in df.select_dtypes("number").columns if c != "Student_ID"]
lab = lambda c: c.replace("_", " ")


def show(chart):
    try:
        st.altair_chart(chart, width="stretch")
    except TypeError:  # Streamlit versi lama
        st.altair_chart(chart, use_container_width=True)


def n(x, nd=2):
    x = round(float(x), nd)
    return f"{int(x):,}".replace(",", ".") if x == int(x) else f"{x:,.{nd}f}".rstrip("0").rstrip(".")


def describe(col):
    s = df[col].dropna()
    q1, med, q3 = s.quantile([.25, .5, .75])
    iqr = q3 - q1
    out = int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
    skew, mean, std = float(s.skew()), float(s.mean()), float(s.std())
    shape = "Condong kanan" if skew > .5 else "Condong kiri" if skew < -.5 else "Simetris"
    edges = np.linspace(s.min(), s.max(), 11)
    counts = pd.cut(s, bins=edges, include_lowest=True).value_counts(sort=False).values
    nd = 0 if s.max() - s.min() >= 100 else 1
    labels = [f"{edges[i]:.{nd}f}-{edges[i+1]:.{nd}f}" for i in range(10)]
    stats = [("Mean", mean), ("Median", med), ("Modus", s.mode().iloc[0]),
             ("Std Dev", std), ("Variansi", s.var()), ("Range", s.max() - s.min()),
             ("Q1", q1), ("Q3", q3), ("IQR", iqr),
             ("Skewness", skew), ("CV %", std / mean * 100), ("Outlier", out)]
    return stats, shape, labels, counts, s.min(), s.max(), q1, med, q3


# ---------- Header & KPI ----------
st.markdown(f"""
<div class="hero"><h1>Statistik Deskriptif Mahasiswa</h1>
<p>Sumber data: latihan1.csv. Kebiasaan belajar, tidur, layar, dan nilai ujian.</p></div>
<div class="kpis">
 <div class="kpi"><b>{len(df)}</b><span>Total mahasiswa</span></div>
 <div class="kpi"><b>{df.shape[1]}</b><span>Kolom data</span></div>
 <div class="kpi"><b>{df.Exam_Score.mean():.2f}</b><span>Rata-rata nilai ujian</span></div>
 <div class="kpi"><b>{df.Study_Hours.mean():.2f}</b><span>Rata-rata jam belajar</span></div>
</div>""", unsafe_allow_html=True)

# ---------- Satu variabel ----------
with st.container(border=True):
    h1, h2 = st.columns([3, 1])
    h1.subheader("Jelajahi satu variabel")
    col = h2.selectbox("Variabel", NUM, index=NUM.index("Study_Hours"),
                       format_func=lab, label_visibility="collapsed")
    stats, shape, labels, counts, mn, mx, q1, med, q3 = describe(col)

    left, right = st.columns([1.9, 1])
    with left:
        hist = pd.DataFrame({"Rentang": labels, "Frekuensi": counts})
        show(alt.Chart(hist, title=f"Distribusi {lab(col)}").mark_bar(color=PRIMARY).encode(
            x=alt.X("Rentang:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelFontSize=10)),
            y=alt.Y("Frekuensi:Q"),
            tooltip=["Rentang", "Frekuensi"]).properties(height=320))
        span = (mx - mn) or 1
        p = lambda v: (v - mn) / span * 100
        st.markdown(f"""
        <div class="box"><div class="line"></div>
          <div class="iqr" style="left:{p(q1)}%;width:{p(q3)-p(q1)}%"></div>
          <div class="med" style="left:calc({p(med)}% - 2px)"></div></div>
        <div class="boxlbl"><span>Min {n(mn)}</span>
          <span>Q1 {n(q1)} | Median {n(med)} | Q3 {n(q3)}</span><span>Max {n(mx)}</span></div>
        """, unsafe_allow_html=True)
    with right:
        tiles = "".join(f"<div class='tile'><b>{n(v)}</b><span>{k}</span></div>" for k, v in stats)
        warn = "" if shape == "Simetris" else " warn"
        st.markdown(f"<div class='tiles'>{tiles}</div><span class='badge{warn}'>{shape}</span>",
                    unsafe_allow_html=True)

# ---------- Gender & dua variabel ----------
c1, c2 = st.columns([1, 1.5])
with c1, st.container(border=True):
    st.subheader("Komposisi gender dan rata-rata nilai")
    g = df.groupby("Gender").agg(Jumlah=("Gender", "size"), Nilai=("Exam_Score", "mean")).reset_index()
    color = alt.Color("Gender:N", scale=alt.Scale(domain=["F", "M"], range=[ACCENT, PRIMARY]),
                      legend=alt.Legend(orient="bottom", title=None))
    a, b = st.columns(2)
    with a:
        show(alt.Chart(g).mark_arc(innerRadius=55).encode(
            theta="Jumlah:Q", color=color, tooltip=["Gender", "Jumlah"]).properties(height=240))
    with b:
        show(alt.Chart(g, title="Rata-rata Exam Score").mark_bar().encode(
            x=alt.X("Gender:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Nilai:Q", scale=alt.Scale(domain=[0, 100]), title=None),
            color=color, tooltip=["Gender", alt.Tooltip("Nilai:Q", format=".2f")]).properties(height=240))

with c2, st.container(border=True):
    t1, t2, t3 = st.columns([2, 1, 1])
    t1.subheader("Hubungan dua variabel")
    xv = t2.selectbox("X", NUM, index=NUM.index("Study_Hours"), format_func=lab, label_visibility="collapsed")
    yv = t3.selectbox("Y", NUM, index=NUM.index("Exam_Score"), format_func=lab, label_visibility="collapsed")
    d = df[[xv, yv]].rename(columns={xv: "x", yv: "y"})
    r = float(d.x.corr(d.y))
    slope, icpt = np.polyfit(d.x, d.y, 1) if xv != yv else (1.0, 0.0)
    line = pd.DataFrame({"x": [d.x.min(), d.x.max()]})
    line["y"] = slope * line.x + icpt
    pts = alt.Chart(d).mark_circle(size=60, color=PRIMARY, opacity=.8).encode(
        x=alt.X("x:Q", title=lab(xv), scale=alt.Scale(zero=False)),
        y=alt.Y("y:Q", title=lab(yv), scale=alt.Scale(zero=False)), tooltip=["x", "y"])
    reg = alt.Chart(line).mark_line(color=ACCENT, strokeWidth=2).encode(x="x:Q", y="y:Q")
    show((pts + reg).properties(height=260))
    kuat = "kuat" if abs(r) >= .7 else "sedang" if abs(r) >= .4 else "lemah"
    arah = "positif" if r >= 0 else "negatif"
    st.markdown(f"r = **{r:.3f}** &nbsp; R² = **{r*r:.3f}** &nbsp; y = {slope:.3f}x + {icpt:.3f} "
                f"&nbsp; **Korelasi {kuat} {arah}**")

# ---------- Insight ----------
i1, i2 = st.columns(2)
with i1, st.container(border=True):
    st.subheader("Faktor yang paling berkaitan dengan nilai")
    cr = df[NUM].corr()["Exam_Score"].drop("Exam_Score")
    cr = cr.reindex(cr.abs().sort_values(ascending=False).index).round(2)
    cdf = pd.DataFrame({"Variabel": [lab(i) for i in cr.index], "r": cr.values})
    show(alt.Chart(cdf).mark_bar().encode(
        y=alt.Y("Variabel:N", sort=None, title=None),
        x=alt.X("r:Q", scale=alt.Scale(domain=[-1, 1]), title="Korelasi (r) dengan Exam Score"),
        color=alt.condition(alt.datum.r > 0, alt.value(PRIMARY), alt.value(ACCENT)),
        tooltip=["Variabel", "r"]).properties(height=280))
    st.caption("Korelasi menunjukkan keterkaitan, bukan sebab-akibat.")

with i2, st.container(border=True):
    st.subheader("Sebaran mahasiswa menurut nilai")
    segs = [("< 60", 0, 60, True), ("60-69", 60, 70, False), ("70-79", 70, 80, False), (">= 80", 80, 101, False)]
    vals = [(lb, int(df.Exam_Score.between(lo, hi, inclusive="left").sum()), rk) for lb, lo, hi, rk in segs]
    top = max(v for _, v, _ in vals)
    st.markdown("".join(
        f"<div class='seg'><span class='n'>{lb}</span>"
        f"<div class='bar {'risk' if rk else ''}' style='width:{v/top*55}%'></div><b>{v}</b></div>"
        for lb, v, rk in vals), unsafe_allow_html=True)
    st.caption("Merah: nilai di bawah 60, perlu perhatian.")
