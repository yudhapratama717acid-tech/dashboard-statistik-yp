import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

# 1. PENGATURAN HALAMAN & LAYOUT STREAMLIT
st.set_page_config(
    page_title="Statistik Deskriptif Mahasiswa",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. SUNTIK CSS KUSTOM AGAR MIRIP DENGAN TAMPILAN FLASK
st.markdown("""
    <style>
    /* Mengubah font & warna background utama aplikasi */
    @import url('https://googleapis.com');
    
    .stApp {
        background: linear-gradient(135deg, #0d0b21 0%, #080616 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #ffffff !important;
    }
    
    /* Menghilangkan padding atas bawaan Streamlit */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Mengubah gaya kotak metrik (Metric Card) agar gelap dan memiliki border glow */
    div[data-testid="stMetric"] {
        background: rgba(22, 19, 58, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        border-bottom: 4px solid #a259ff !important; /* Efek garis ungu di bawah */
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px 0 rgba(162, 89, 255, 0.2) !important;
    }

    /* Modifikasi teks di dalam Metric Card */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-top: 5px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* Desain untuk Card Radial Gauge (Rata-rata Nilai) */
    .gauge-card {
        background: rgba(22, 19, 58, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    .radial-gauge {
        position: relative;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }

    .radial-gauge::before {
        content: "";
        position: absolute;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: #0d0b21;
    }

    .gauge-value {
        position: relative;
        font-size: 26px;
        font-weight: 700;
        color: white;
        z-index: 1;
    }

    .gauge-label {
        color: #94a3b8;
        font-size: 13px;
        margin: 0;
    }

    /* Mengubah gaya teks Input Selectbox */
    .stSelectbox label p {
        color: #94a3b8 !important;
        font-size: 14px !important;
    }
    
    div[data-baseweb="select"] {
        background-color: #16133a !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] div {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. MEMBACA DATASET & MEMBERSIHKAN KOLOM (PENCEGAH KEYERROR)
@st.cache_data
def load_data():
    try:
        # Mencoba membaca dengan path folder lokal / github
        df = pd.read_csv("dashboard/latihan1.csv")
    except:
        # Fallback jika posisi file sejajar dengan script
        df = pd.read_csv("latihan1.csv")
        
    # Otomatis menghapus spasi liar di awal/akhir nama kolom agar tidak memicu KeyError
    df.columns = df.columns.str.strip()
    return df

# Memuat data ke dalam aplikasi
df = load_data()

# 4. PROSES PERHITUNGAN STATISTIK UTAMA
total_mahasiswa = len(df)
total_kolom = len(df.columns)

# Memastikan kolom 'Study Hours' dan 'Exam Score' aman dibaca
nama_kolom_belajar = 'Study Hours' if 'Study Hours' in df.columns else df.columns[0]
nama_kolom_nilai = 'Exam Score' if 'Exam Score' in df.columns else df.columns[-1]

rata_jam_belajar = round(df[nama_kolom_belajar].mean(), 2)
rata_nilai = round(df[nama_kolom_nilai].mean(), 2)
nilai_di_bawah_60 = len(df[df[nama_kolom_nilai] < 60])

# 5. LAYOUT HULU: JUDUL UTAMA & DIAGRAM BULAT DI KANAN
col_header_left, col_header_right = st.columns([3, 1])

with col_header_left:
    st.markdown("<h1 style='font-weight:700; margin-bottom:0;'>Statistik Deskriptif Mahasiswa</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:16px;'>Sumber data: latihan1.csv. Kebiasaan belajar, tidur, layar, dan nilai ujian.</p>", unsafe_allow_html=True)

with col_header_right:
    # Render radial gauge estetik dengan nilai persentase rata-rata nilai ujian
    st.markdown(f"""
        <div class="gauge-card">
            <div class="radial-gauge" style="background: conic-gradient(#a259ff 0%, #ec4899 {rata_nilai}%, #16133a {rata_nilai}% 100%);">
                <div class="gauge-value">{rata_nilai}</div>
            </div>
            <p class="gauge-label">Rata-rata nilai ujian</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. LAYOUT METRIK UTAMA (KARTU KOTAK ATAS)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total mahasiswa", value=f"{total_mahasiswa}")
with col2:
    st.metric(label="Kolom data", value=f"{total_kolom}")
with col3:
    st.metric(label="Rata-rata jam belajar", value=f"{rata_jam_belajar}")
with col4:
    st.metric(label="Nilai di bawah 60", value=f"{nilai_di_bawah_60}")

st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)

# 7. BAGIAN JELAJAHI VARIABEL & GRAFIK (LAYOUT TENGAH)
col_tengah_kiri, col_tengah_kanan = st.columns([2.5, 1.5])

with col_tengah_kiri:
    st.markdown("<h3 style='font-weight:600; margin-top:0;'>Jelajahi satu variabel</h3>", unsafe_allow_html=True)
    
    # Memilih kolom bertipe numerik saja untuk pilihan drop-down
    fitur_numerik = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Menentukan default drop-down ke 'Study Hours' jika tersedia
    default_index = fitur_numerik.index('Study Hours') if 'Study Hours' in fitur_numerik else 0
    pilihan_variabel = st.selectbox("Pilih Variabel untuk Visualisasi:", fitur_numerik, index=default_index)

    # Menghitung data distribusi frekuensi untuk chart histogram kustom
    counts, bins = np.histogram(df[pilihan_variabel], bins=10)
    df_bin = pd.DataFrame({
        'Interval': [f"{round(bins[i],1)}-{round(bins[i+1],1)}" for i in range(len(counts))],
        'Frekuensi': counts
    })

    # Membuat Grafik Batang Interaktif dengan Warna Gradasi Cyan ke Ungu
    fig = px.bar(
        df_bin, 
        x='Interval', 
        y='Frekuensi',
        title=f"Distribusi {pilihan_variabel}",
        color='Frekuensi',
        color_continuous_scale=['#38bdf8', '#a259ff']
    )
    
    # Mengatur background chart menjadi transparan agar menyatu dengan CSS Aplikasi
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#94a3b8',
        title_font_color='#ffffff',
        title_font_size=16,
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Frekuensi")
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_tengah_kanan:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 8. MENGHITUNG STATISTIK RINCI DARI VARIABEL PILIHAN
    data_kolom = df[pilihan_variabel]
    
    mean_val = round(data_kolom.mean(), 2)
    median_val = round(data_kolom.median(), 2)
    
    # Mengamankan perhitungan modus dari fungsi scipy
    mode_res = stats.mode(data_kolom, keepdims=True)
    mode_val = round(mode_res.mode[0], 2) if len(mode_res.mode) > 0 else "N/A"
    
    std_val = round(data_kolom.std(), 2)
    var_val = round(data_kolom.var(), 2)
    range_val = round(data_kolom.max() - data_kolom.min(), 2)
    q1_val = round(data_kolom.quantile(0.25), 2)
    q3_val = round(data_kolom.quantile(0.75), 2)
    iqr_val = round(q3_val - q1_val, 2)

    # Menampilkan 9 Parameter Statistik Pendukung berbentuk Grid 3x3
    c_stat1, c_stat2, c_stat3 = st.columns(3)
    with c_stat1:
        st.metric(label="Mean", value=f"{mean_val}")
        st.metric(label="Std Dev", value=f"{std_val}")
        st.metric(label="Q1", value=f"{q1_val}")
    with c_stat2:
        st.metric(label="Median", value=f"{median_val}")
        st.metric(label="Variansi", value=f"{var_val}")
        st.metric(label="Q3", value=f"{q3_val}")
    with c_stat3:
        st.metric(label="Modus", value=f"{mode_val}")
        st.metric(label="Range", value=f"{range_val}")
        st.metric(label="IQR", value=f"{iqr_val}")
