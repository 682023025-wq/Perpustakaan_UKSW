# Sistem Informasi Perpustakaan

Sistem Informasi Perpustakaan berbasis web dengan tema warna merah, menggunakan Flask (Python) dan MySQL/MariaDB untuk database lokal (phpMyAdmin).

## 📋 Fitur Utama

### Admin
- Dashboard dengan statistik perpustakaan
- Manajemen User (CRUD)
- Manajemen Katalog Buku (CRUD)
- Manajemen Kategori Buku
- Manajemen Rak Buku

### Karyawan/Petugas
- Dashboard dengan statistik operasional
- **Peminjaman Buku** - Hanya petugas yang bisa memproses peminjaman
- **Pengembalian Buku** - Hanya petugas yang bisa memproses pengembalian
- Manajemen Denda
- Laporan dan Statistik

### User (Mahasiswa/Dosen)
- View Katalog Buku (hanya baca)
- Riwayat Peminjaman (hanya baca)
- **Tidak bisa melakukan peminjaman langsung** - harus melalui petugas

## 🏗️ Struktur Folder

```
perpustakaan/
├── app.py                  # Main Flask application
├── config.py               # Konfigurasi database & aplikasi
├── requirements.txt        # Dependencies Python
├── database.sql           # Script database MySQL
├── backend/
│   ├── __init__.py
│   ├── auth.py            # Autentikasi & authorization
│   ├── admin/
│   │   ├── dashboard.py
│   │   ├── users.py
│   │   ├── katalog.py
│   │   ├── kategori.py
│   │   └── rak.py
│   └── karyawan/
│       ├── dashboard.py
│       ├── peminjaman.py
│       ├── denda.py
│       └── laporan.py
├── frontend/
│   ├── login.html
│   ├── admin/
│   │   └── dashboard.html
│   └── karyawan/
│       └── dashboard.html
└── static/
    ├── css/
    │   ├── global.css
    │   ├── login.css
    │   └── admin/
    │       └── dashboard.css
    └── js/
        ├── global.js
        ├── login.js
        └── admin/
            └── dashboard.js
```

## 🚀 Instalasi

### 1. Setup Database

1. Buka phpMyAdmin (http://localhost/phpmyadmin)
2. Buat database baru atau import file `database.sql`
3. Database akan otomatis membuat tabel dan data awal

### 2. Install Dependencies

```bash
cd perpustakaan
pip install -r requirements.txt
```

### 3. Konfigurasi Database

Edit file `config.py` jika perlu mengubah konfigurasi database:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP kosong
    'database': 'perpustakaan_db'
}
```

### 4. Jalankan Aplikasi

```bash
python app.py
```

Aplikasi akan berjalan di: http://localhost:5000

## 👤 Akun Default

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Karyawan | petugas | petugas123 |

## 🔐 Sistem Peminjaman

**PENTING**: Sistem ini dirancang agar peminjaman buku HANYA bisa dilakukan oleh petugas perpustakaan ketika peminjam datang langsung.

### Flow Peminjaman:
1. Peminjam datang ke perpustakaan dengan membawa buku
2. Petugas login ke sistem
3. Petugas memasukkan ID peminjam dan scan barcode buku
4. Sistem validasi:
   - Status peminjam aktif
   - Kuota peminjaman (max 5 buku)
   - Tidak ada denda belum lunas
   - Buku tersedia
5. Petugas memproses peminjaman
6. Status buku berubah menjadi "Dipinjam"

### Flow Pengembalian:
1. Peminjam mengembalikan buku ke petugas
2. Petugas mencari ID peminjaman
3. Sistem hitung denda jika terlambat (Rp 1000/hari)
4. Petugas memproses pengembalian
5. Status buku berubah menjadi "Tersedia"

## 🎨 Tema Desain

- **Warna Utama**: Merah (#c62828)
- **Layout**: Desktop-first dengan sidebar navigasi
- **Responsive**: Menyesuaikan untuk layar lebih kecil

## 📊 Database Schema

### Tabel Utama:
- **USER**: Admin, Karyawan, Mahasiswa, Dosen
- **BUKU**: Data buku/katalog
- **ITEM_BUKU**: Eksemplar buku dengan barcode unik
- **KATEGORI**: Kategori buku
- **RAK**: Lokasi rak buku
- **PEMINJAMAN**: Transaksi peminjaman (wajib id_petugas_out)
- **DETAIL_PINJAM**: Detail buku yang dipinjam
- **DENDA**: Denda keterlambatan

## 🛠️ Teknologi

- **Backend**: Flask (Python 3.x)
- **Database**: MySQL/MariaDB (via phpMyAdmin)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **API**: RESTful API dengan JSON response

## 📝 API Endpoints

### Authentication
- `POST /api/login` - Login user
- `POST /api/logout` - Logout user
- `GET /api/me` - Get current user

### Admin
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET/POST/PUT/DELETE /api/admin/users` - CRUD Users
- `GET/POST/PUT/DELETE /api/admin/katalog` - CRUD Books
- `GET/POST/PUT/DELETE /api/admin/kategori` - CRUD Categories
- `GET/POST/PUT/DELETE /api/admin/rak` - CRUD Racks

### Karyawan
- `GET /api/karyawan/dashboard/stats` - Dashboard statistics
- `POST /api/karyawan/peminjaman` - Process borrowing
- `POST /api/karyawan/pengembalian` - Process return
- `GET /api/karyawan/denda` - Get fines
- `POST /api/karyawan/denda/:id/bayar` - Pay fine
- `GET /api/karyawan/laporan/*` - Reports

## ⚠️ Keamanan

- Password di-hash menggunakan SHA2
- Session-based authentication
- Role-based access control (RBAC)
- Input validation di backend

## 📄 License

© 2024 Sistem Informasi Perpustakaan
