import sqlite3
import hashlib

# Fungsi untuk hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi untuk membuat koneksi ke database
def create_connection():
    return sqlite3.connect('users.db')

# Fungsi untuk membuat tabel pengguna jika belum ada
def create_user_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE,
                  password TEXT,
                  role TEXT)''')
    conn.commit()
    conn.close()
    create_admin_user()  # Panggil untuk membuat akun admin default

# Fungsi untuk membuat pengguna baru
def create_user(email, password, role='user'):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, hash_password(password), role))
    conn.commit()
    conn.close()

# Fungsi untuk membuat akun admin default
def create_admin_user():
    admin_email = "AdminKelompok3@gmail.com"
    admin_password = "AdminKelompok3"
    if not user_exists(admin_email):
        conn = create_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (admin_email, hash_password(admin_password), 'admin'))
        conn.commit()
        conn.close()

# Fungsi untuk memeriksa apakah pengguna ada
def user_exists(email):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

# Fungsi untuk memeriksa kredensial pengguna
def check_credentials(email, password, role):
    user = user_exists(email)
    if user and user[2] == hash_password(password) and user[3] == role:
        return user
    return None

# Panggil fungsi ini untuk memastikan tabel pengguna dibuat saat modul diimpor
create_user_table()

def create_article_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  description TEXT,
                  image_url TEXT,
                  url TEXT)''')
    conn.commit()
    conn.close()

# Panggil fungsi ini untuk memastikan tabel artikel dibuat saat modul diimpor
create_article_table()
