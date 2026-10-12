"""Dashboard Statistik Deskriptif Mahasiswa versi Streamlit.

Tampilan SAMA PERSIS dengan versi Flask (app.py), karena memakai
templates/index.html + static/style.css + static/app.js yang sama.
Data diambil dari fungsi-fungsi di app.py, lalu ditanam langsung ke halaman.

Jalankan:
    python -m pip install -r requirements.txt
    python -m streamlit run streamlit_app.py
"""
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from app import NUMERIC_COLS, app as flask_app  # sumber data & logika yang sama

BASE = Path(__file__).parent

st.set_page_config(page_title="Statistik Deskriptif Mahasiswa", layout="wide")

# Hilangkan header/padding bawaan Streamlit dan samakan warna latar
st.markdown(
    """
<style>
html, body, .stApp, [data-testid="stAppViewContainer"] {background:#070b1f !important;}
[data-testid="stHeader"], [data-testid="stToolbar"], footer {display:none !important;}
.block-container {padding:0 !important; max-width:100% !important;}
iframe {border:0; display:block;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def build_html() -> str:
    # 1) Kumpulkan semua respons API Flask (hasilnya sama dengan yang dipakai app.js)
    client = flask_app.test_client()
    get = lambda url: client.get(url).get_json()

    data = {
        "/api/summary": get("/api/summary"),
        "/api/gender": get("/api/gender"),
        "/api/correlation": get("/api/correlation"),
        "/api/matrix": get("/api/matrix"),
        "/api/segments": get("/api/segments"),
    }
    for c in NUMERIC_COLS:
        data[f"/api/variable/{c}"] = get(f"/api/variable/{c}")
    for x in NUMERIC_COLS:
        for y in NUMERIC_COLS:
            data[f"/api/scatter?x={x}&y={y}"] = get(f"/api/scatter?x={x}&y={y}")

    # 2) Baca template, CSS, dan JS versi Flask
    html = (BASE / "templates" / "index.html").read_text(encoding="utf-8")
    css = (BASE / "static" / "style.css").read_text(encoding="utf-8")
    js = (BASE / "static" / "app.js").read_text(encoding="utf-8")

    # 3) fetch() ke server diganti dengan pencarian di data yang sudah ditanam
    old = "const fetchJSON = async url => (await fetch(url)).json();"
    assert old in js, "Baris fetchJSON di app.js berubah; sesuaikan streamlit_app.py"
    js = js.replace(old, "const fetchJSON = async url => window.DATA[url];")

    link = "<link rel=\"stylesheet\" href=\"{{ url_for('static', filename='style.css') }}\">"
    script = "<script src=\"{{ url_for('static', filename='app.js') }}\"></script>"
    assert link in html and script in html, "Template index.html berubah"

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace(link, f"<style>{css}</style>")
    html = html.replace(script, f"<script>window.DATA = {payload};</script><script>{js}</script>")
    return html


# Tinggi iframe: naikkan angkanya bila bagian bawah (matriks/footer) terpotong
components.html(build_html(), height=2900, scrolling=True)
