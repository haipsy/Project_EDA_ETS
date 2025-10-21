# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from streamlit_option_menu import option_menu

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="✈️ Dashboard Kelompok 2", layout="wide")
st.markdown("""
<style>
/* ====== Sidebar ====== */
[data-testid="stSidebar"] {
    background-color: #0a1a3f; /* navy gelap */
    color: white;
}

/* ====== Judul Sidebar ====== */
h2, h3, h4, label, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1cypcdb {
    color: #a9d6e5 !important; /* biru lembut */
    font-weight: 600;
}

/* ====== Multiselect Box ====== */
.stMultiSelect > div {
    background-color: #1d65a6 !important;
    border-radius: 10px;
}
.stMultiSelect [data-baseweb="tag"] {
    background-color: #007bff !important;
    color: white !important;
    border-radius: 5px;
    font-weight: 500;
}

/* ====== Dropdown ====== */
.stSelectbox > div, .stMultiSelect > div {
    background-color: #1d65a6 !important;
    color: white !important;
}
.stSelectbox div[role="listbox"] {
    background-color: #1d65a6 !important;
    color: white !important;
}

/* ====== Slider ====== */
.stSlider > div[data-baseweb="slider"] > div {
    color: white !important;
}
.stSlider > div[data-baseweb="slider"] > div > div {
    background-color: #00BFFF !important; /* biru muda slider */
}
.stSlider [role="slider"] {
    background-color: #1e90ff !important;
    border: 2px solid #89cff0 !important;
}

/* ====== Date Input ====== */
.stDateInput > div > input {
    background-color: #1d65a6 !important;
    color: white !important;
    border-radius: 8px;
    border: 1px solid #5dade2;
}

/* ====== Tombol Download ====== */
.stDownloadButton > button {
    background-color: #1e90ff !important;
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
.stDownloadButton > button:hover {
    background-color: #007acc !important;
    color: #eaf6ff !important;
}

/* ====== Expander ====== */
.streamlit-expanderHeader {
    background-color: #13315c !important;
    color: white !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ==============================
# OPTIONAL CUSTOM CSS
# ==============================
css_path = "style.css"
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==============================
# COLOR PALETTE
# ==============================
color_palette = [
    "#0b3c5d",  # deep navy
    "#1d65a6",  # steel blue
    "#2e8bc0",  # blue
    "#89cff0",  # sky blue
    "#a9d6e5",  # light pastel blue
    "#13315c",  # dark indigo
    "#006494",  # bright cyan-blue
    "#247ba0",  # soft ocean blue
    "#5dade2",  # light blue
    "#7fb3d5"   # muted soft blue
]

# ==============================
# LOAD DATA
# ==============================
DEFAULT_FILE = "flights_weather_sampled.csv"

@st.cache_data
def load_csv(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.duplicated()]
    return df

df = None
if os.path.exists(DEFAULT_FILE):
    try:
        df = load_csv(DEFAULT_FILE)
        st.sidebar.success(f"✅ File dimuat: {DEFAULT_FILE}")
    except Exception as e:
        st.sidebar.error(f"Gagal membaca file: {e}")
else:
    uploaded = st.sidebar.file_uploader("📂 Upload dataset CSV", type=["csv"])
    if uploaded:
        try:
            df = load_csv(uploaded)
            st.sidebar.success("✅ Dataset berhasil di-upload.")
        except Exception as e:
            st.sidebar.error(f"Gagal memuat file upload: {e}")

if df is None:
    st.warning("⚠️ Silakan upload file CSV atau pastikan file 'flights_weather_sampled.csv' ada di folder project.")
    st.stop()

# ==============================
# CLEANING
# ==============================
df = df.copy()
df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
numeric_cols = ["dep_delay","arr_delay","total_delay","distance","air_time",
                "humidity","pressure","temperature","wind_speed","delay_difference","temperature_c"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")


# SIDEBAR MENU
# ==============================
# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "Dashboard Menu",
        ["Home", "Statistics & KPI", "Visualization & Interpretation", "About"],
        icons=["house", "bar-chart", "activity", "info-circle"],
        menu_icon="chat-square-text",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0a1a3f"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {
                "color": "white",
                "font-size": "15px",
                "text-align": "left",
                "margin": "5px 0",
                "border-radius": "10px",
            },
            "nav-link-selected": {
                "background-color": "#1e90ff",  # warna biru aktif
                "font-weight": "700",
                "color": "white",
            },
            "nav-link:hover": {"background-color": "#005bbb"},
        },
    )
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.sidebar.markdown("---")
use_full = st.sidebar.checkbox("Gunakan seluruh dataset (bisa lambat)", value=False)
sample_n = None if use_full else st.sidebar.slider("Sample data (rows):", 1000, 20000, 10000, 1000)

# ==============================
# PAGE: HOME
# ==============================
if selected == "Home":
    # ====== Header dengan Logo dan Judul sejajar ======
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        st.image("upn_logo.png", width=130)

    with col2:
        st.markdown(
            """
            <h1 style='text-align:center; margin-bottom:0;'> Dashboard Analisis Delay Penerbangan & Cuaca</h1>
            <h4 style='text-align:center; color:#00BFFF; margin-top:4px;'>
                Analisis keterlambatan penerbangan dan pengaruh cuaca di New York 2013 
            </h4>
            <p style='text-align:center; font-size:15px; margin-top:-10px;'>
                Via Amanda, Muhammad Haikal Pasya Abdillah, Angelina Nirmala Puteri Dika Praktiko, Siti Rania Azaria, Aurelia Krisnanti Wijaya, Maulida Shifa Annisa | Kelompok 2 |  UPN "Veteran" Jawa Timur
            </p>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.image("airplane_icon.png", width=120)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ====== Konten Tengah ======
    colA, colB, colC = st.columns([1, 2, 1])
    with colB:
        st.markdown(
            """
            <h3 style='text-align:center;'>🌦️ Bagaimana Cuaca Mempengaruhi Keterlambatan Penerbangan?</h3>
            <p style='text-align:justify; font-size:16px;'>
                Perusahaan penerbangan harus menjaga kepuasan pelanggan karena kualitas pelayanan, terutama ketepatan waktu, sangat berpengaruh terhadap citra dan kinerja perusahaan. Peningkatan kualitas pelayanan memang membutuhkan biaya operasional yang lebih tinggi, namun citra baik yang terbentuk dapat meningkatkan kepercayaan dan penjualan tiket. Ketepatan waktu menjadi indikator penting dalam menilai kualitas pelayanan maskapai karena keterlambatan dapat merugikan penumpang dan perusahaan. Oleh sebab itu, setiap bentuk keterlambatan perlu dianalisis untuk menemukan faktor penyebabnya.
            </p>
            <p style='text-align:justify; font-size:16px;'>
                Salah satu faktor yang diduga mempengaruhi keterlambatan adalah kondisi cuaca, seperti hujan deras, angin kencang, kabut tebal, atau badai, yang bisa mengganggu proses lepas landas dan mendarat demi menjaga keselamatan.  Kondisi tersebut tidak hanya membuat pelanggan kecewa, tetapi juga menimbulkan penumpukan jadwal, peningkatan biaya operasional, dan gangguan terhadap jadwal kru serta armada. Jika keterlambatan terjadi terus-menerus, citra maskapai dapat menurun dan pelanggan beralih ke maskapai lain. Oleh karena itu, penting bagi perusahaan penerbangan untuk menganalisis pengaruh cuaca terhadap keterlambatan guna meningkatkan efisiensi dan kinerja operasional.

            </p>
            <p style='text-align:center; font-size:18px;'>
                ✨ Jelajahi data dan temukan hubungannya hanya di dashboard ini! ✨
            </p>
            """,
            unsafe_allow_html=True
        )

    # ====== Footer ======
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; font-size:14px;'>© 2025 Kelompok 2 | Exploratory Data Analysis Project</p>",
        unsafe_allow_html=True
    )

# ==============================
# PAGE: STATISTICS & KPI
# ==============================
elif selected == "Statistics & KPI":
    st.header("📈 Statistik & KPI")

    df_stats = df if use_full else df.sample(n=min(sample_n, len(df)), random_state=42)

    total_flights = len(df_stats)
    avg_total_delay = df_stats["total_delay"].mean() if "total_delay" in df_stats else float("nan")
    avg_temp = df_stats["temperature_c"].mean() if "temperature_c" in df_stats else float("nan")
    max_delay = df_stats["total_delay"].max() if "total_delay" in df_stats else float("nan")
    top_origin = df_stats["origin"].mode()[0] if "origin" in df_stats and not df_stats["origin"].mode().empty else "N/A"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Flights", f"{total_flights:,}")
    c2.metric("Avg Total Delay (min)", f"{avg_total_delay:.2f}" if pd.notna(avg_total_delay) else "N/A")
    c3.metric("Avg Temperature (°C)", f"{avg_temp:.1f}" if pd.notna(avg_temp) else "N/A")
    c4.metric("Max Delay (min)", f"{max_delay:.1f}" if pd.notna(max_delay) else "N/A")
    c5.metric("Most Frequent Origin", top_origin)

    st.markdown("---")
    num_cols = df_stats.select_dtypes(include=["number"]).columns.tolist()
    if num_cols:
        st.dataframe(df_stats[num_cols].describe().T)
    else:
        st.warning("Tidak ada kolom numerik ditemukan.")
    st.caption("📋 Statistik deskriptif berdasarkan data aktif.")

# ==============================
# PAGE: VISUALIZATION & INTERPRETATION
# ==============================
elif selected == "Visualization & Interpretation":
    st.header("📊 Visualisasi & Interpretasi Data")

    # ---------- Sidebar Filters ----------
    st.sidebar.subheader("🎛️ Filter Data Visualisasi")
    df_vis = df.copy()

    origins = sorted(df_vis["origin"].dropna().unique()) if "origin" in df_vis else []
    dests = sorted(df_vis["dest"].dropna().unique()) if "dest" in df_vis else []
    carriers = sorted(df_vis["carrier"].dropna().unique()) if "carrier" in df_vis else []

    sel_origins = st.sidebar.multiselect("Origin:", origins, default=origins[:5] if origins else [])
    sel_dests = st.sidebar.multiselect("Destination:", dests, default=dests[:5] if dests else [])
    sel_carriers = st.sidebar.multiselect("Carrier:", carriers, default=[])

    if "date" in df_vis.columns:
        min_date, max_date = df_vis["date"].min(), df_vis["date"].max()
        sel_date = st.sidebar.date_input("Rentang tanggal:", [min_date, max_date])

    if "total_delay" in df_vis.columns:
        min_delay, max_delay = int(df_vis["total_delay"].min()), int(df_vis["total_delay"].max())
        sel_delay = st.sidebar.slider("Rentang delay (menit):", min_delay, max_delay, (min_delay, max_delay))
    else:
        sel_delay = None

    # ---------- FILTER INTERAKTIF (diletakkan setelah bagian visualisasi utama) ----------
st.sidebar.header("🎛️ Filter Data")

# Pilihan filter keren tapi ringan
with st.sidebar.expander("✈️ Bandara & Maskapai", expanded=True):
    sel_origins = st.multiselect(
        "Pilih Bandara Asal",
        sorted(df["origin"].unique()),
        default=None,
        placeholder="Bandara asal..."
    )
    sel_dests = st.multiselect(
        "Pilih Bandara Tujuan",
        sorted(df["dest"].unique()),
        default=None,
        placeholder="Bandara tujuan..."
    )
    sel_carriers = st.multiselect(
        "Pilih Maskapai",
        sorted(df["carrier"].unique()),
        default=None,
        placeholder="Maskapai..."
    )

with st.sidebar.expander("🗓️ Rentang Waktu & Delay", expanded=True):
    if "date" in df.columns:
        sel_date = st.date_input(
            "Pilih Rentang Tanggal",
            value=(df["date"].min(), df["date"].max())
        )
    else:
        sel_date = None

    if "total_delay" in df.columns:
        sel_delay = st.slider(
            "Filter Delay (menit)",
            min_value=int(df["total_delay"].min()),
            max_value=int(df["total_delay"].max()),
            value=(int(df["total_delay"].min()), int(df["total_delay"].max()))
        )
    else:
        sel_delay = None

# ---------- Apply Filters ----------
df_vis = df.copy()

if sel_origins:
    df_vis = df_vis[df_vis["origin"].isin(sel_origins)]
if sel_dests:
    df_vis = df_vis[df_vis["dest"].isin(sel_dests)]
if sel_carriers:
    df_vis = df_vis[df_vis["carrier"].isin(sel_carriers)]
if "date" in df_vis.columns and sel_date:
    start_d, end_d = pd.to_datetime(sel_date[0]), pd.to_datetime(sel_date[1])
    df_vis = df_vis[(df_vis["date"] >= start_d) & (df_vis["date"] <= end_d)]
if sel_delay and "total_delay" in df_vis.columns:
    df_vis = df_vis[(df_vis["total_delay"] >= sel_delay[0]) & (df_vis["total_delay"] <= sel_delay[1])]

# Sampling (biar gak berat)
df_vis_sample = df_vis if use_full else df_vis.sample(n=min(len(df_vis), sample_n), random_state=42)

# Info dan download hasil filter
st.sidebar.success(f"✅ Data aktif: {len(df_vis_sample):,} baris")
st.sidebar.download_button(
    "💾 Download filtered CSV",
    data=df_vis_sample.to_csv(index=False).encode("utf-8"),
    file_name="filtered_flights.csv",
    mime="text/csv"
)

 # ---------- Tabs ----------
tabs = st.tabs([
    "Histogram Delay", "Scatter Suhu vs Delay", "Bubble Delay vs Jarak",
    "Area Delay Harian", "Pie Origin", "Bar Delay per Destinasi",
    "Polar Wind", "Lollipop Distance", "Correlation Heatmap", "Tabel Statistik"
])

# Histogram
with tabs[0]:
    if "total_delay" in df_vis_sample:
        fig = px.histogram(df_vis_sample, x="total_delay", nbins=50,
                           color_discrete_sequence=[color_palette[2]],
                           title="Distribusi Total Delay")
        st.plotly_chart(fig, use_container_width=True)

# Scatter
with tabs[1]:
    if {"temperature_c", "total_delay"}.issubset(df_vis_sample.columns):
        fig = px.scatter(df_vis_sample, x="temperature_c", y="total_delay",
                         color="origin", color_discrete_sequence=color_palette,
                         title="Suhu vs Total Delay (per Origin)")
        st.plotly_chart(fig, use_container_width=True)

# Bubble
with tabs[2]:
    if {"distance", "total_delay"}.issubset(df_vis_sample.columns):
        fig = px.scatter(df_vis_sample, x="distance", y="total_delay",
                         size="wind_speed" if "wind_speed" in df_vis_sample else None,
                         color="origin", color_discrete_sequence=color_palette,
                         title="Bubble Chart: Distance vs Delay")
        st.plotly_chart(fig, use_container_width=True)

# Area
with tabs[3]:
    if {"date", "total_delay"}.issubset(df_vis_sample.columns):
        df_trend = df_vis_sample.groupby("date")["total_delay"].mean().reset_index()
        fig = px.area(df_trend, x="date", y="total_delay",
                      color_discrete_sequence=[color_palette[4]],
                      title="Rata-rata Delay per Hari")
        st.plotly_chart(fig, use_container_width=True)

# Pie
with tabs[4]:
    if "origin" in df_vis_sample.columns:
        top5 = df_vis_sample["origin"].value_counts().nlargest(5)
        fig = px.pie(values=top5.values, names=top5.index,
                     color_discrete_sequence=color_palette,
                     title="Distribusi 5 Bandara Asal Teratas")
        st.plotly_chart(fig, use_container_width=True)

# Bar
with tabs[5]:
    if {"dest", "total_delay"}.issubset(df_vis_sample.columns):
        delay_dest = df_vis_sample.groupby("dest")["total_delay"].mean().sort_values(ascending=False).head(10)
        fig = px.bar(x=delay_dest.index, y=delay_dest.values,
                     color=delay_dest.values, color_continuous_scale="Blues",
                     labels={"x": "Destinasi", "y": "Rata-rata Delay"},
                     title="Top 10 Destinasi dengan Delay Tertinggi")
        st.plotly_chart(fig, use_container_width=True)

# Polar
with tabs[6]:
    if {"wind_speed", "wind_direction"}.issubset(df_vis_sample.columns):
        fig = px.scatter_polar(df_vis_sample, r="wind_speed", theta="wind_direction",
                               color="origin", color_discrete_sequence=color_palette,
                               title="Distribusi Arah & Kecepatan Angin")
        st.plotly_chart(fig, use_container_width=True)

# Lollipop
with tabs[7]:
    if {"distance", "total_delay"}.issubset(df_vis_sample.columns):
        avg_dist = df_vis_sample.groupby("distance")["total_delay"].mean().reset_index().sort_values("distance").tail(30)
        fig = px.scatter(avg_dist, x="distance", y="total_delay",
                         color_discrete_sequence=[color_palette[1]],
                         title="Lollipop Chart: Delay vs Distance (30 terakhir)")
        fig.update_traces(marker=dict(size=10))
        st.plotly_chart(fig, use_container_width=True)

# Heatmap
with tabs[8]:
    num_cols = df_vis_sample.select_dtypes(include=["number"]).columns
    if len(num_cols) > 1:
        corr = df_vis_sample[num_cols].corr()
        fig = px.imshow(corr, text_auto=True, aspect="auto",
                        color_continuous_scale="PuBu",
                        title="Heatmap Korelasi Variabel Numerik")
        st.plotly_chart(fig, use_container_width=True)
# ==============================
# PAGE: ABOUT
# ============================
# ⬇️ PENTING: Ini harus sejajar dengan "elif selected == 'Visualization & Interpretation':"
if selected == "About":
    st.title("ℹ️ Tentang Dashboard")
    st.markdown("""
    Dashboard ini dikembangkan untuk **analisis keterlambatan penerbangan dan faktor cuaca** 
    menggunakan dataset penerbangan New York 2013.  
    Dibuat oleh **Kelompok 2**, dalam rangka proyek **Exploratory Data Analysis (EDA)**.
    """)
    st.info("📘 Data diolah menggunakan Streamlit, Pandas, Plotly, dan NumPy.")
