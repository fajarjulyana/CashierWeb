import sqlite3

conn = sqlite3.connect('kasir.db')
cursor = conn.cursor()

# Buat tabel users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'kasir')) NOT NULL
    )
''')

# Tambahkan admin dan kasir default
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('kasir', 'kasir123', 'kasir')")

# Buat tabel barang
cursor.execute('''
    CREATE TABLE IF NOT EXISTS barang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        harga REAL NOT NULL,
        harga_beli REAL NOT NULL,
        jumlah INTEGER NOT NULL
    )
''')

# Buat tabel transaksi_log
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaksi_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL NOT NULL,
        tanggal TEXT NOT NULL
    )
''')

# Buat tabel detail_transaksi
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detail_transaksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaksi_id INTEGER NOT NULL,
        id_barang INTEGER NOT NULL,
        jumlah INTEGER NOT NULL,
        harga REAL NOT NULL,
        FOREIGN KEY (transaksi_id) REFERENCES transaksi_log(id),
        FOREIGN KEY (id_barang) REFERENCES barang(id)
    )
''')

conn.commit()
conn.close()

print("Database berhasil dibuat dan diinisialisasi!")
