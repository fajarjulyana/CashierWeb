from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import bcrypt

import subprocess
import platform

app = Flask(__name__)
app.secret_key = 'secret_key'  # Ganti dengan secret key yang lebih aman

# ==========================
# DATABASE CONNECTION
# ==========================
def get_db_connection():
    conn = sqlite3.connect('kasir.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==========================
# AUTHENTICATION ROUTES
# ==========================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['role'] = user['role']
            flash("Login berhasil!", "success")
            return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'kasir_dashboard'))

        flash("Username atau password salah!", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if role not in ['admin', 'kasir']:
            flash("Role tidak valid!", "danger")
            return redirect(url_for('register'))

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                         (username, hashed_password.decode('utf-8'), role))
            conn.commit()
            flash("Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for('login'))
        except:
            flash("Username sudah terdaftar!", "danger")
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Anda telah logout!", "info")
    return redirect(url_for('login'))

# ==========================
# ADMIN DASHBOARD (MENGELOLA BARANG)
# ==========================
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    barang_list = conn.execute('SELECT * FROM barang').fetchall()
    conn.close()

    return render_template('admin_dashboard.html', barang_list=barang_list)

@app.route('/admin/tambah_barang', methods=['POST'])
def tambah_barang():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    nama = request.form['nama']
    harga = request.form['harga']
    jumlah = request.form['jumlah']

    conn = get_db_connection()
    conn.execute('INSERT INTO barang (nama, harga, jumlah) VALUES (?, ?, ?)', (nama, harga, jumlah))
    conn.commit()
    conn.close()

    flash("Barang berhasil ditambahkan!", "success")
    return redirect(url_for('admin_dashboard'))

# ==========================
# ROUTE TAMBAH BARANG DENGAN QR CODE
# ==========================
@app.route('/admin/add_barang', methods=['GET', 'POST'])
def add_barang():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        id_barang = request.form['id']
        nama = request.form['nama']
        harga = request.form['harga']
        harga_beli = request.form['harga_beli']
        jumlah = request.form['jumlah']

        conn = get_db_connection()
        conn.execute('INSERT INTO barang (id, nama, harga, harga_beli, jumlah) VALUES (?, ?, ?, ?, ?)',
                     (id_barang, nama, harga, harga_beli, jumlah))
        conn.commit()
        conn.close()

        flash("Barang berhasil ditambahkan!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_barang.html')

@app.route('/admin/edit_barang/<int:id>', methods=['GET', 'POST'])
def edit_barang(id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    barang = conn.execute('SELECT * FROM barang WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        harga_beli = request.form['harga_beli']
        jumlah = request.form['jumlah']

        conn.execute('UPDATE barang SET nama = ?, harga = ?, harga_beli = ?, jumlah = ? WHERE id = ?',
                     (nama, harga, harga_beli, jumlah, id))
        conn.commit()
        conn.close()
        flash("Barang berhasil diperbarui!", "success")
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('edit_barang.html', barang=barang)

@app.route('/admin/delete_barang/<int:id>', methods=['POST'])
def delete_barang(id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM barang WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("Barang berhasil dihapus!", "success")
    return redirect(url_for('admin_dashboard'))

# ==========================
# KASIR DASHBOARD (LIHAT PRODUK)
# ==========================
@app.route('/kasir')
def kasir_dashboard():
    cart = session.get('cart', [])  # Ambil data keranjang dari session
    return render_template('kasir_dashboard.html', cart=cart)


# ==========================
# KERANJANG BELANJA (SESSION)
# ==========================
@app.route('/get_keranjang', methods=['GET'])
def get_keranjang():
    return jsonify({"cart": session.get('cart', [])})

@app.route('/tambah_keranjang', methods=['POST'])
def tambah_keranjang():
    if 'cart' not in session:
        session['cart'] = []  # Buat list kosong jika cart belum ada

    data = request.get_json()
    id_barang = data.get('id_barang')
    jumlah = int(data.get('jumlah', 1))

    conn = get_db_connection()
    barang = conn.execute('SELECT * FROM barang WHERE id = ?', (id_barang,)).fetchone()
    conn.close()

    if not barang:
        return jsonify({'success': False, 'message': 'Barang tidak ditemukan!'})

    # Tambahkan ke keranjang
    session['cart'].append({
        'id': barang['id'],
        'nama': barang['nama'],
        'harga': barang['harga'],
        'jumlah': jumlah
    })

    session.modified = True  # Penting agar perubahan tersimpan!

    return jsonify({'success': True, 'message': 'Barang berhasil ditambahkan!'})


@app.route('/hapus_dari_keranjang', methods=['POST'])
def hapus_dari_keranjang():
    data = request.get_json()  # Ambil data dari request body JSON
    if not data or 'id_barang' not in data:
        return jsonify({'error': 'ID barang tidak ditemukan'}), 400

    id_barang = data['id_barang']
    
    # Hapus item dari session['cart']
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != id_barang]
        session.modified = True

    return jsonify({'success': True, 'message': 'Barang berhasil dihapus'})


# ==========================
# CHECKOUT
# ==========================
import os

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session or 'cart' not in session or not session['cart']:
        flash("Keranjang kosong!", "error")
        return redirect(url_for('kasir_dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        total = sum(item['harga'] * item['jumlah'] for item in session['cart'])

        # Cek stok sebelum transaksi
        for item in session['cart']:
            barang = cursor.execute('SELECT jumlah FROM barang WHERE id = ?', (item['id'],)).fetchone()
            if not barang or barang['jumlah'] < item['jumlah']:
                flash(f"Stok barang {item['nama']} tidak mencukupi!", "error")
                return redirect(url_for('kasir_dashboard'))

        # Insert transaksi utama
        cursor.execute('INSERT INTO transaksi_log (total, tanggal) VALUES (?, datetime("now", "localtime"))', (total,))

        transaksi_id = cursor.lastrowid

        # Ambil tanggal transaksi
        tanggal_transaksi = cursor.execute('SELECT datetime("now", "localtime")').fetchone()[0]


        # Insert detail transaksi & update stok
        for item in session['cart']:
            cursor.execute('INSERT INTO detail_transaksi (transaksi_id, id_barang, jumlah, harga) VALUES (?, ?, ?, ?)',
                        (transaksi_id, item['id'], item['jumlah'], item['harga']))
            cursor.execute('UPDATE barang SET jumlah = jumlah - ? WHERE id = ?', (item['jumlah'], item['id']))

        conn.commit()

        # Buat struk dalam bentuk string
        struk = f"====== STRUK PEMBELIAN ======\n"
        struk += f"ID Transaksi: {transaksi_id}\n"
        struk += f"Tanggal: {tanggal_transaksi}\n"
        struk += "----------------------------------\n"
        for item in session['cart']:
            struk += f"{item['nama']} x{item['jumlah']}  Rp {item['harga'] * item['jumlah']:,}\n"
        struk += "----------------------------------\n"
        struk += f"Total: Rp {total:,}\n"
        struk += "Terima kasih!\n"

        # Cetak ke printer
        cetak_struk(struk)

        session.pop('cart', None)
        flash('Transaksi berhasil!', 'success')

    except Exception as e:
        conn.rollback()
        flash(f"Terjadi kesalahan saat checkout: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for('kasir_dashboard'))


# Fungsi untuk mencetak struk
def cetak_struk(struk):
    try:
        with open("/tmp/struk.txt", "w") as f:
            f.write(struk)
        os.system("lp /tmp/struk.txt")  # Mencetak ke printer default
    except Exception as e:
        print(f"Error mencetak struk: {e}")
# ==========================
# RUN SERVER
# ==========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('ssl_cert.pem', 'ssl_key.pem'))


