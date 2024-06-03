import streamlit as st
from streamlit_option_menu import option_menu
import auth
import pickle
import requests
import re
from PIL import Image
import sqlite3

# Fungsi untuk memuat model machine learning
def load_model():
    with open("CP_kmeans.pkl", "rb") as file:
        CP_kmeans = pickle.load(file)
    return CP_kmeans

# CSS untuk latar belakang, gaya, dan animasi
def load_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://img.freepik.com/free-vector/world-vegetarian-day-flat-design-background_23-2149655002.jpg?t=st=1717383434~exp=1717387034~hmac=f1abac5fbf69b2ed772f2c03f8da7f89fd947f1905d65678f86d8bd0cbb138c6&w=996");
            background-size: cover;
            transition: background 0.5s ease;
        }
        .title-box {
            text-align: center;
            margin-top: 2rem;
        }
        .title-box h1 {
            font-size: 3rem;
            color: #fff;
        }
        .info-box {
            text-align: center;
            margin-top: 2rem;
            color: #fff;
            background: rgba(0, 0, 0, 0.5);
            padding: 1rem;
            border-radius: 1rem;
        }
        .center-buttons {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 4rem;
        }
        .center-buttons button {
            font-weight: bold;
            font-size: 1.1rem;
            padding: 0.5rem 1rem;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 0.5rem;
            transition: background-color 0.3s ease;
        }
        .center-buttons button:hover {
            background-color: #0056b3;
        }
        .extra-box {
            text-align: center;
            margin-top: 1rem;
            color: #fff;
            background: rgba(0, 0, 0, 0.5);
            padding: 1rem;
            border-radius: 1rem;
        }
        .top-menu {
            display: flex;
            justify-content: flex-end;
            background: rgba(0, 0, 0, 0.7);
            padding: 0.5rem 1rem;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .top-menu a {
            color: #fff;
            margin: 0 1rem;
            text-decoration: none;
            font-weight: bold;
        }
        .button-container {
            display: flex;
            justify-content: center;
            margin-top: 4rem;
        }
        .button-container .stButton {
            margin: 0 0.5rem;
        }
        .article-container {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            padding: 10px;
            margin-top: 10px;
            text-align: center;
        }
        .article-container img {
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True
    )

# Fungsi Validasi
def check_uppercase(password):
    return any(c.isupper() for c in password)

def check_lowercase(password):
    return any(c.islower() for c in password)

def check_digit(password):
    return any(c.isdigit() for c in password)

def is_valid_password(password):
    return check_uppercase(password) and check_lowercase(password) and check_digit(password)

def is_valid_email(email):
    return email.endswith('@gmail.com')

# Fungsi untuk menyimpan artikel yang diunggah
def save_article(title, description, image, link):
    if 'articles' not in st.session_state:
        st.session_state['articles'] = []
    st.session_state['articles'].append({
        "title": title,
        "description": description,
        "image": image,
        "link": link
    })

# Fungsi untuk membuat koneksi ke database
def create_connection():
    return sqlite3.connect('users.db')

# Halaman registrasi
def signup():
    st.title("Daftar")

    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Konfirmasi Password", type="password")
        role = st.selectbox("Role", ["user", "admin"])
        submit_button = st.form_submit_button(label="Daftar")

        # Checkbox ketentuan password
        st.write("Password harus memiliki:")
        st.checkbox("Setidaknya memiliki huruf kapital", value=check_uppercase(password), disabled=True)
        st.checkbox("Setidaknya memiliki huruf kecil", value=check_lowercase(password), disabled=True)
        st.checkbox("At least one digit", value=check_digit(password), disabled=True)

        if submit_button:
            if not email or not password:
                st.error("Email and Password cannot be empty")
            elif not is_valid_email(email):
                st.error("Email harus diakhiri dengan @gmail.com")
            elif not is_valid_password(password):
                st.error("Password harus mengandung huruf besar, huruf kecil, dan angka. Tidak boleh ada simbol.")
            elif password != confirm_password:
                st.error("Password dan konfirmasi password tidak cocok.")
            elif auth.user_exists(email):
                st.error("Email sudah terdaftar")
            elif role == 'admin':
                st.error("Maaf, anda tidak bisa daftar sebagai admin")
            else:
                auth.create_user(email, password, role)
                st.success("Akunmu berhasil dibuat")

    if st.button("Kembali"):
        st.session_state['page'] = 'landing'
        st.experimental_rerun()

# Halaman login
def login():
    st.title("Masuk")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["user", "admin"])
        submit_button = st.form_submit_button(label="Masuk")

        if submit_button:
            if not email or not password:
                st.error("Email dan Password tidak boleh kosong")
            elif not is_valid_password(password):
                st.error("Password harus memiliki huruf besar, huruf kecil, dan angka. Tidak boleh ada simbol.")
            else:
                user = auth.check_credentials(email, password, role)
                if user:
                    st.success("Login successful")
                    st.session_state['logged_in'] = True
                    st.session_state['email'] = email
                    st.session_state['role'] = user[3]
                    st.experimental_rerun()
                else:
                    st.error("Email atau password tidak benar")

    if st.button("Kembali"):
        st.session_state['page'] = 'landing'
        st.experimental_rerun()

# Halaman utama setelah login
def main_page():
    st.title("Selamat Datang di Healthy Me")
    st.write(f"Halo sobat sehat, {st.session_state['email']}! Sekarang kamu login sebagai {st.session_state['role']}.")
    st.write("Ini adalah halaman utama aplikasi.")

# Halaman artikel
def articles_page():
    st.title("Artikel")
    st.write("Here are some interesting articles for you to read.")
    display_articles()

# Halaman hitung kalori sebagai template untuk model ML
def kalori_page():
    st.title("Kalkulator Kalori")
    KalkulatorKalori().show()

class KalkulatorKalori:
    def show(self):
        st.title("Pengukuran Kalori")
        berat_badan = st.number_input("Masukkan berat badan Anda (kg)")
        tinggi_badan = st.number_input("Masukkan tinggi badan Anda (cm)")
        usia = st.number_input("Masukkan usia Anda (tahun)")
        jenis_kelamin = st.selectbox("Pilih jenis kelamin", ["Laki-laki", "Perempuan"])

        if st.button("Hitung Kalori"):
            if jenis_kelamin == "Laki-laki":
                bmr = 88.362 + (13.397 * berat_badan) + (4.799 * tinggi_badan) - (5.677 * usia)
            else:
                bmr = 447.593 + (9.247 * berat_badan) + (3.098 * tinggi_badan) - (4.330 * usia)
            
            st.write(f"Kebutuhan kalori harian Anda adalah {bmr:.2f} kkal")

# Halaman bantuan
def rekomendasi_page():
    st.title("Rekomendasi Makanan")
    st.write("Ini adalah halaman rekomendasi makanan. Bagaimana kami bisa membantumu?")

# Fungsi untuk menampilkan form penambahan artikel dan menyimpan artikel
def add_article_page():
    st.title("Tambah Artikel Baru")

    with st.form("article_form"):
        title = st.text_input("Judul Artikel")
        description = st.text_area("Deskripsi")
        image_url = st.text_input("Link Gambar")
        article_link = st.text_input("Link Artikel")
        submit_button = st.form_submit_button(label="Tambah Artikel")

        if submit_button:
            if not title or not description or not image_url or not article_link:
                st.error("Tidak boleh ada kolom yang kosong")
            else:
                save_article(title, description, image_url, article_link)
                st.success("Artikel berhasil ditambahkan")

    if st.button("Back"):
        st.session_state['page'] = 'main'
        st.experimental_rerun()

# Fungsi untuk menampilkan artikel yang sudah diunggah
def display_articles():
    if 'articles' in st.session_state:
        for article in st.session_state['articles']:
            st.write(f"### {article['title']}")
            st.write(f"![Gambar Artikel]({article['image']})")
            st.write(f"{article['description']}")
            st.write(f"[Baca Selengkapnya]({article['link']})")
    else:
        st.write("Tidak dapat menemukan artikel.")

# Halaman admin untuk menambahkan artikel
def admin_page():
    st.title("Halaman Admin")
    st.write("Tambah Artikel Baru")

    with st.form("article_form"):
        title = st.text_input("Judul Artikel")
        description = st.text_area("Deskripsi")
        image_url = st.text_input("Link Gambar")
        url = st.text_input("Link Artikel")
        submit_button = st.form_submit_button(label="Tambah Artikel")

        if submit_button:
            if title and description and image_url and url:
                conn = create_connection()
                c = conn.cursor()
                c.execute("INSERT INTO Artikel (title, description, image_url, url) VALUES (?, ?, ?, ?)", (title, description, image_url, url))
                conn.commit()
                conn.close()
                st.success("Artikel berhasil ditambahkan")
            else:
                st.error("Kolom tidak boleh ada yang kosong")

# Halaman bantuan
def help_page():
    st.title("Bantuan")
    st.write("Ini adalah halaman bantuan. Bagaimana kami bisa membantumu?")

# Halaman landing
def landing_page():
    st.markdown("""
    <div class="title-box">
        <h1>Selamat Datang di Healthy Me</h1>
    </div>
    <div class="info-box">
        <p>Platform untuk menjaga kesehatan anda dengan mengonsumsi makanan yang sehat</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 2])
    with col1:
        if st.button("Daftar"):
            st.session_state['page'] = 'signup'
            st.experimental_rerun()
    with col2:
        if st.button("Masuk"):
            st.session_state['page'] = 'login'
            st.experimental_rerun()

    st.markdown("""
    <div class="extra-box">
        <p>Tentang Kami</p>
    </div>
    """, unsafe_allow_html=True)

# Fungsi logout
def logout():
    st.session_state['logged_in'] = False
    st.session_state['email'] = None
    st.session_state['role'] = None
    st.session_state['page'] = 'landing'
    st.experimental_rerun()

# Main function
def main():
    st.set_page_config(page_title="Healthy Me")
    load_css()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if 'page' not in st.session_state:
        st.session_state['page'] = 'landing'

    if st.session_state['logged_in']:
        if st.session_state['role'] == 'admin':
            selected = option_menu(
                menu_title=None,
                options=["Home Admin", "Tambah Artikel", "Artikel", "Logout"],
                icons=["house", "file-earmark-plus", "file-earmark", "box-arrow-right"],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal"
            )
            if selected == "Home Admin":
                main_page()
            elif selected == "Tambah Artikel":
                add_article_page()
            elif selected == "Artikel":
                articles_page()
            elif selected == "Logout":
                logout()
        else:
            selected = option_menu(
                menu_title=None,
                options=["Menu Utama", "Kalkulator Kalori", "Rekomendasi Makanan", "Artikel", "Logout"],
                icons=["house", "calculator", "activity", "file-earmark", "box-arrow-right"],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal"
            )
            if selected == "Menu Utama":
                main_page()
            elif selected == "Kalkulator Kalori":
                kalori_page()
            elif selected == "Rekomendasi Makanan":
                rekomendasi_page()
            elif selected == "Artikel":
                articles_page()
            elif selected == "Logout":
                logout()
    else:
        if st.session_state['page'] == 'landing':
            landing_page()
        elif st.session_state['page'] == 'login':
            login()
        elif st.session_state['page'] == 'signup':
            signup()

if __name__ == "__main__":
    main()
