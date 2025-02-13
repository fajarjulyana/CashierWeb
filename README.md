# Aplikasi Kasir dengan Flask

Aplikasi ini adalah sistem kasir berbasis web menggunakan Flask dan SQLite. Aplikasi ini memiliki fitur autentikasi pengguna, manajemen barang, serta transaksi penjualan dengan pencetakan struk.

## Fitur Utama
- **Autentikasi Pengguna**: Login, registrasi, dan logout untuk admin dan kasir.
- **Manajemen Barang**: Admin dapat menambah, mengedit, dan menghapus barang.
- **Transaksi**: Kasir dapat menambahkan barang ke keranjang dan melakukan checkout.
- **Struk Pembelian**: Cetak struk transaksi setelah checkout.

## Teknologi yang Digunakan
- Python + Flask
- SQLite
- HTML, CSS, JavaScript
- bcrypt untuk enkripsi password

## Instalasi
### 1. Clone Repository
```bash
$ git clone https://github.com/username/repo-kasir.git
$ cd repo-kasir
```

### 2. Buat Virtual Environment dan Install Dependencies
```bash
$ python -m venv venv
$ source venv/bin/activate  # Untuk Linux/macOS
$ venv\Scripts\activate    # Untuk Windows
$ pip install -r requirements.txt
```

### 3. Konfigurasi Database
Buat file database `kasir.db` dengan menjalankan skrip berikut:
```bash
$ python
>>> import sqlite3
>>> conn = sqlite3.connect('kasir.db')
>>> cursor = conn.cursor()

# Buat tabel users
>>> cursor.execute('''CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'kasir'))
)''')

# Buat tabel barang
>>> cursor.execute('''CREATE TABLE barang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    harga INTEGER NOT NULL,
    harga_beli INTEGER NOT NULL,
    jumlah INTEGER NOT NULL
)''')

# Buat tabel transaksi
>>> cursor.execute('''CREATE TABLE transaksi_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total INTEGER NOT NULL,
    tanggal TEXT NOT NULL
)''')

# Buat tabel detail transaksi
>>> cursor.execute('''CREATE TABLE detail_transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_id INTEGER NOT NULL,
    id_barang INTEGER NOT NULL,
    jumlah INTEGER NOT NULL,
    harga INTEGER NOT NULL,
    FOREIGN KEY (transaksi_id) REFERENCES transaksi_log(id),
    FOREIGN KEY (id_barang) REFERENCES barang(id)
)''')

>>> conn.commit()
>>> conn.close()
```

### 4. Jalankan Aplikasi
```bash
$ python app.py
```
Aplikasi akan berjalan di `http://127.0.0.1:5000/`.

## Penggunaan
### 1. Login
- **Admin**: Bisa mengelola barang (tambah, edit, hapus).
- **Kasir**: Bisa melihat daftar barang dan melakukan transaksi.

### 2. Tambah Barang
Admin dapat menambah barang dengan nama, harga, dan jumlah stok.

### 3. Transaksi dan Checkout
- Kasir menambahkan barang ke keranjang.
- Kasir melakukan checkout, sistem akan mengurangi stok barang.
- Struk pembelian akan dicetak.

## Keamanan
- Menggunakan bcrypt untuk enkripsi password.
- Session management untuk login/logout.

## Lisensi
Proyek ini menggunakan lisensi MIT. Silakan digunakan dan dikembangkan lebih lanjut.

---
**Dibuat dengan Flask & SQLite ❤️**

