import streamlit as st
import pandas as pd
import pydeck as pdk

# ==========================================
# 1. STRUKTUR DATA STATIS (HARDCODE DATA)
# Bersih dari pengaturan teks manual (Lebih dinamis!)
# ==========================================
DATA_FLORA = [
    {
        "nama": "Majegau",
        "nama_ilmiah": "Dysoxylum densiflorum",
        "status": "Rentan",
        "deskripsi": "Pohon yang kayunya sangat harum dan erat kaitannya dengan kegiatan adat setempat. Flora identitas yang tumbuh di hutan tropis.",
        "gambar": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSC7ErCedTlpY5fdxwXz4f7QO0L50Q2X04V-FxyRghQtMKJ-S5CXvHjo68O&s=10",
        "lat": -8.3405, 
        "lon": 115.0919
    },
    {
        "nama": "Bunga Sandat",
        "nama_ilmiah": "Cananga odorata",
        "status": "Aman",
        "deskripsi": "Bunga tradisional yang tumbuh subur di dataran rendah. Wanginya sangat khas dan bernilai budaya tinggi.",
        "gambar": "https://bibitbunga.com/wp-content/uploads/2015/09/bunga-kenanga.jpg",
        "lat": -8.4095,
        "lon": 115.1889
    },
    {
        "nama": "Bunga Bangkai",
        "nama_ilmiah": "Amorphophallus titanum",
        "status": "Terancam Punah",
        "deskripsi": "Tanaman endemik Sumatera yang memiliki perbungaan terbesar di dunia dan mengeluarkan bau khas.",
        "gambar": "https://yiari.or.id/wp-content/uploads/2024/07/1-amorphophallus-titanum-1-66a88ebc0a6f3.webp",
        "lat": -0.7893, 
        "lon": 100.9649
    },
    {
        "nama": "Kantong Semar",
        "nama_ilmiah": "Nepenthes",
        "status": "Rentan",
        "deskripsi": "Tanaman karnivora unik yang memakan serangga. Habitat alaminya tersebar luas di hutan Kalimantan dan Sumatera.",
        "gambar": "https://upload.wikimedia.org/wikipedia/commons/c/cf/SulawesiNepenthes7.jpg",
        "lat": -0.2295, 
        "lon": 111.9423
    }
]

# ==========================================
# 2. PENGATURAN HALAMAN & STATE MANAGEMENT
# ==========================================
st.set_page_config(page_title="Florapedia", page_icon="🌿", layout="wide")

# Menginisialisasi memori sesi untuk kuis
if 'skor' not in st.session_state:
    st.session_state.skor = 0
if 'soal_selesai' not in st.session_state:
    st.session_state.soal_selesai = False

# ==========================================
# 3. NAVIGASI SIDEBAR
# ==========================================
st.sidebar.title("🌿 Florapedia")
menu = st.sidebar.radio("Navigasi Menu:", ["📖 Galeri Flora", "🗺️ Peta Persebaran", "🎮 Kuis Edukasi"])

st.sidebar.divider()
st.sidebar.info("Florapedia: Code to Preserve Life.")

# ==========================================
# 4. HALAMAN 1: GALERI FLORA (CARD LAYOUT)
# ==========================================
if menu == "📖 Galeri Flora":
    st.title("Galeri Flora Endemik")
    st.write("Jelajahi dan kenali tanaman langka yang menjadi kekayaan alam kita.")

    # Widget Filter Interaktif
    kolom_cari, kolom_filter = st.columns(2)
    with kolom_cari:
        kata_kunci = st.text_input("Cari nama tanaman:")
    with kolom_filter:
        pilihan_status = st.selectbox("Status Conservasi:", ["Semua", "Aman", "Rentan", "Terancam Punah"])

    st.divider()

    # Logika Pencarian
    hasil_pencarian = []
    for tanaman in DATA_FLORA:
        cocok_kata = kata_kunci.lower() in tanaman["nama"].lower() or kata_kunci == ""
        cocok_status = pilihan_status == "Semua" or tanaman["status"] == pilihan_status
        if cocok_kata and cocok_status:
            hasil_pencarian.append(tanaman)

    # Layout Kolom (Grid)
    if len(hasil_pencarian) > 0:
        kolom1, kolom2 = st.columns(2)
        for index, tanaman in enumerate(hasil_pencarian):
            kolom_tujuan = kolom1 if index % 2 == 0 else kolom2
            with kolom_tujuan:
                with st.expander(f"🌱 {tanaman['nama']}", expanded=True):
                    # Menggunakan use_container_width agar aman di semua versi Streamlit
                    st.image(tanaman["gambar"], use_container_width=True)
                    st.subheader(tanaman["nama"])
                    st.caption(f"_{tanaman['nama_ilmiah']}_")
                    
                    if tanaman["status"] == "Terancam Punah":
                        st.error(f"Status: {tanaman['status']}")
                    elif tanaman["status"] == "Rentan":
                        st.warning(f"Status: {tanaman['status']}")
                    else:
                        st.success(f"Status: {tanaman['status']}")
                        
                    st.write(tanaman["deskripsi"])
    else:
        st.warning("Tanaman tidak ditemukan.")

# ==========================================
# 5. HALAMAN 2: PETA GEOSPASIAL (LOGIKA GLOBAL AUTOMATIC OFFSET)
# ==========================================
elif menu == "🗺️ Peta Persebaran":
    st.title("Peta Habitat Flora")
    
    st.write("Lihat lokasi habitat alami flora endemik beserta garis penunjuk otomatis di bawah ini.")
    st.info("💡 Arahkan kursor (*hover*) tepat pada **Teks Nama Flora** atau **Titik Koordinat** untuk melihat detail tanaman.")
    
    filter_peta = st.selectbox("Tampilkan flora berdasarkan status:", ["Semua", "Aman", "Rentan", "Terancam Punah"], key="filter_peta")
    
    data_koordinat = []
    
    # Kunci Otomatisasi: Menggunakan urutan indeks yang lolos filter
    idx_lolos = 0
    for tanaman in DATA_FLORA:
        if filter_peta == "Semua" or tanaman["status"] == filter_peta:
            
            if tanaman["status"] == "Terancam Punah":
                warna_rgb = [255, 0, 0, 255]      # Merah 
            elif tanaman["status"] == "Rentan":
                warna_rgb = [255, 140, 0, 255]    # Oranye 
            else:
                warna_rgb = [0, 200, 0, 255]      # Hijau 

            # Mengatur letak teks mengambang agar tidak menumpuk secara zig-zag
            if idx_lolos % 2 == 0:
                hitung_teks_lat = tanaman["lat"] + 1.5
                hitung_teks_lon = tanaman["lon"] + 0.5
            else:
                hitung_teks_lat = tanaman["lat"] - 1.5
                hitung_teks_lon = tanaman["lon"] - 0.5
                
            data_koordinat.append({
                "nama_flora": tanaman["nama"],
                "status_konservasi": tanaman["status"],
                "lat": tanaman["lat"], 
                "lon": tanaman["lon"],
                "teks_lat": hitung_teks_lat,   
                "teks_lon": hitung_teks_lon,   
                "warna": warna_rgb,
                "gambar": tanaman["gambar"],
                "deskripsi": tanaman["deskripsi"]
            })
            idx_lolos += 1
    
    if len(data_koordinat) > 0:
        df_peta = pd.DataFrame(data_koordinat)
        
        # --- LAYER 1: Garis Penunjuk ---
        layer_garis = pdk.Layer(
            "LineLayer",
            data=df_peta,
            get_source_position="[lon, lat]",             
            get_target_position="[teks_lon, teks_lat]",   
            get_color="[150, 150, 150, 200]",             
            get_width=1,
            pickable=False,
        )

        # --- LAYER 2: ScatterplotLayer (Titik Koordinat) ---
        layer_titik = pdk.Layer(
            "ScatterplotLayer",
            data=df_peta,
            get_position="[lon, lat]",
            get_fill_color="warna",
            get_radius=20000,   
            pickable=False,
        )
                
        # --- LAYER 3: TextLayer (Nama Flora Mengambang) ---
        layer_teks = pdk.Layer(
            "TextLayer",
            data=df_peta,
            get_position="[teks_lon, teks_lat]", 
            get_text="nama_flora",     
            get_color="warna",
            get_size=12,               
            get_alignment_baseline="'center'",
            font_weight="'bold'",
            pickable=True,             
        )

        # Mengatur posisi kamera awal peta
        kamera_peta = pdk.ViewState(
            latitude=-2.5,
            longitude=117.0,
            zoom=4,
            pitch=0
        )

        # Desain Struktur Tampilan Tooltip HTML saat di-hover
        html_tooltip = """
        <div style="font-family: Arial, sans-serif; padding: 8px; max-width: 260px; background-color: #ffffff; border-radius: 8px;">
            <h4 style="margin: 0 0 4px 0; color: #333;">{nama_flora}</h4>
            <p style="margin: 0 0 8px 0; font-size: 11px; color: #777;"><b>Status:</b> {status_konservasi}</p>
            <img src="{gambar}" style="width: 100%; max-height: 140px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;" />
            <p style="margin: 0; font-size: 12px; color: #444; line-height: 1.4;">{deskripsi}</p>
        </div>
        """

        # Menampilkan Peta PyDeck ke Antarmuka
        st.pydeck_chart(
            pdk.Deck(
                map_style=None,
                initial_view_state=kamera_peta,
                layers=[layer_garis, layer_titik, layer_teks], 
                tooltip={
                    "html": html_tooltip,
                    "style": {
                        "backgroundColor": "white",
                        "color": "black",
                        "boxShadow": "0px 2px 6px rgba(0,0,0,0.3)",
                        "zIndex": "1000"
                    }
                }
            ),
            use_container_width=True
        )
    else:
        st.warning("Tidak ada data titik habitat untuk status tersebut.")

# ==========================================
# 6. HALAMAN 3: KUIS EDUKASI (STATE MANAGEMENT)
# ==========================================
elif menu == "🎮 Kuis Edukasi":
    st.title("Kuis Ekosistem")
    st.write("Uji pengetahuanmu tentang flora endemik!")

    if not st.session_state.soal_selesai:
        st.info("Jawab pertanyaan berikut untuk mendapatkan skor.")
        
        st.subheader("Pertanyaan 1:")
        st.write("Tanaman karnivora yang memakan serangga dan banyak ditemukan di Kalimantan adalah...")
        jawaban_1 = st.radio("Pilih jawaban:", ["Majegau", "Bunga Bangkai", "Kantong Semar"], key="j1")
        
        st.subheader("Pertanyaan 2:")
        st.write("Pohon yang kayunya sangat harum dan sering digunakan untuk kegiatan adat adalah...")
        jawaban_2 = st.radio("Pilih jawaban:", ["Majegau", "Bunga Sandat", "Pohon Jati"], key="j2")
        
        if st.button("Kirim Jawaban"):
            skor_sementara = 0
            if jawaban_1 == "Kantong Semar":
                skor_sementara += 50
            if jawaban_2 == "Majegau":
                skor_sementara += 50
                
            st.session_state.skor = skor_sementara
            st.session_state.soal_selesai = True
            st.rerun() 
            
    else:
        st.success("Kuis Selesai!")
        st.metric(label="Total Skor Kamu", value=f"{st.session_state.skor} / 100")
        
        if st.session_state.skor == 100:
            st.balloons()
            st.write("🌟 Sempurna! Kamu sangat peduli dengan keanekaragaman hayati kita.")
        elif st.session_state.skor >= 50:
            st.write("👍 Bagus! Mari kita pelajari lebih lanjut di halaman Galeri.")
        else:
            st.write("💪 Jangan menyerah, baca lagi deskripsi di Galeri dan coba lagi!")
            
        if st.button("Coba Lagi"):
            st.session_state.skor = 0
            st.session_state.soal_selesai = False
            st.rerun()