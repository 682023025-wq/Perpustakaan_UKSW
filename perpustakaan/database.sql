-- ============================================
-- DATABASE STRUCTURE - Sistem Informasi Perpustakaan
-- Untuk MySQL/MariaDB (phpMyAdmin)
-- ============================================

CREATE DATABASE IF NOT EXISTS perpustakaan_db;
USE perpustakaan_db;

-- Tabel USER (untuk Admin, Karyawan, Mahasiswa, Dosen)
CREATE TABLE IF NOT EXISTS USER (
    id_user VARCHAR(30) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    nim_nip VARCHAR(20),
    role ENUM('ADMIN', 'KARYAWAN', 'MHS', 'DSN') NOT NULL DEFAULT 'MHS',
    status ENUM('Aktif', 'Nonaktif') DEFAULT 'Aktif',
    tgl_daftar TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel KATEGORI
CREATE TABLE IF NOT EXISTS KATEGORI (
    id_kategori INT AUTO_INCREMENT PRIMARY KEY,
    nama_kategori VARCHAR(100) NOT NULL,
    deskripsi TEXT
);

-- Tabel RAK
CREATE TABLE IF NOT EXISTS RAK (
    id_rak INT AUTO_INCREMENT PRIMARY KEY,
    kode_rak VARCHAR(20) UNIQUE NOT NULL,
    lokasi VARCHAR(100) NOT NULL,
    kapasitas INT DEFAULT 50
);

-- Tabel BUKU
CREATE TABLE IF NOT EXISTS BUKU (
    id_buku INT AUTO_INCREMENT PRIMARY KEY,
    judul VARCHAR(255) NOT NULL,
    penulis VARCHAR(100),
    penerbit VARCHAR(100),
    tahun_terbit YEAR,
    isbn VARCHAR(20),
    id_kategori INT,
    deskripsi TEXT,
    FOREIGN KEY (id_kategori) REFERENCES KATEGORI(id_kategori) ON DELETE SET NULL
);

-- Tabel ITEM_BUKU (Eksemplar Buku dengan Barcode)
CREATE TABLE IF NOT EXISTS ITEM_BUKU (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_buku INT NOT NULL,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    id_rak INT,
    status ENUM('Tersedia', 'Dipinjam', 'Rusak', 'Hilang') DEFAULT 'Tersedia',
    FOREIGN KEY (id_buku) REFERENCES BUKU(id_buku) ON DELETE CASCADE,
    FOREIGN KEY (id_rak) REFERENCES RAK(id_rak) ON DELETE SET NULL
);

-- Tabel PEMINJAMAN
-- Peminjaman HANYA bisa dilakukan oleh petugas (Karyawan/Admin)
CREATE TABLE IF NOT EXISTS PEMINJAMAN (
    id_pinjam INT AUTO_INCREMENT PRIMARY KEY,
    id_peminjam VARCHAR(30) NOT NULL,
    id_petugas_out VARCHAR(30) NOT NULL,  -- Petugas yang memproses peminjaman (WAJIB)
    id_petugas_in VARCHAR(30),            -- Petugas yang menerima pengembalian
    tgl_pinjam DATE NOT NULL,
    tgl_kembali_wajib DATE NOT NULL,
    tgl_kembali DATE,
    status ENUM('Dipinjam', 'Dikembalikan') DEFAULT 'Dipinjam',
    FOREIGN KEY (id_peminjam) REFERENCES USER(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_petugas_out) REFERENCES USER(id_user) ON DELETE SET NULL,
    FOREIGN KEY (id_petugas_in) REFERENCES USER(id_user) ON DELETE SET NULL
);

-- Tabel DETAIL_PINJAM
CREATE TABLE IF NOT EXISTS DETAIL_PINJAM (
    id_detail INT AUTO_INCREMENT PRIMARY KEY,
    id_pinjam INT NOT NULL,
    id_item INT NOT NULL,
    FOREIGN KEY (id_pinjam) REFERENCES PEMINJAMAN(id_pinjam) ON DELETE CASCADE,
    FOREIGN KEY (id_item) REFERENCES ITEM_BUKU(id_item) ON DELETE CASCADE
);

-- Tabel DENDA
CREATE TABLE IF NOT EXISTS DENDA (
    id_denda INT AUTO_INCREMENT PRIMARY KEY,
    id_pinjam INT NOT NULL,
    jumlah_denda DECIMAL(10, 2) NOT NULL DEFAULT 0,
    status ENUM('Belum Lunas', 'Lunas') DEFAULT 'Belum Lunas',
    tgl_bayar DATE,
    FOREIGN KEY (id_pinjam) REFERENCES PEMINJAMAN(id_pinjam) ON DELETE CASCADE
);

-- ============================================
-- DATA AWAL (SEED DATA)
-- ============================================

-- Password default: admin123 (di-hash dengan SHA2)
INSERT INTO USER (id_user, username, password, nama, email, role) VALUES
('ADM001', 'admin', SHA2('admin123', 256), 'Administrator', 'admin@perpustakaan.com', 'ADMIN'),
('KAR001', 'petugas', SHA2('petugas123', 256), 'Petugas Perpustakaan', 'petugas@perpustakaan.com', 'KARYAWAN');

-- Kategori Buku
INSERT INTO KATEGORI (nama_kategori, deskripsi) VALUES
('Teknologi Informasi', 'Buku-buku tentang teknologi dan pemrograman'),
('Sains', 'Buku-buku ilmu pengetahuan alam'),
('Sosial Humaniora', 'Buku-buku ilmu sosial dan humaniora'),
('Sastra', 'Novel, cerpen, dan karya sastra lainnya'),
('Bisnis & Ekonomi', 'Buku-buku tentang bisnis dan ekonomi');

-- Rak Buku
INSERT INTO RAK (kode_rak, lokasi, kapasitas) VALUES
('A01', 'Lantai 1 - Area A', 50),
('A02', 'Lantai 1 - Area A', 50),
('B01', 'Lantai 1 - Area B', 50),
('B02', 'Lantai 2 - Area B', 50),
('C01', 'Lantai 2 - Area C', 50);

-- Contoh Data Buku
INSERT INTO BUKU (judul, penulis, penerbit, tahun_terbit, isbn, id_kategori, deskripsi) VALUES
('Pemrograman Web Modern', 'John Doe', 'Tech Publisher', 2023, '978-1234567890', 1, 'Panduan lengkap pemrograman web modern'),
('Algoritma dan Struktur Data', 'Jane Smith', 'Edu Books', 2022, '978-0987654321', 1, 'Dasar-dasar algoritma dan struktur data'),
('Fisika Dasar', 'Dr. Ahmad', 'Science Press', 2021, '978-1122334455', 2, 'Pengantar fisika untuk mahasiswa'),
('Sejarah Indonesia', 'Prof. Budi', 'History Books', 2020, '978-5566778899', 3, 'Sejarah lengkap Indonesia'),
('Laskar Pelangi', 'Andrea Hirata', 'Bentang Pustaka', 2005, '978-9793062006', 4, 'Novel bestseller Indonesia');

-- Contoh Item Buku dengan Barcode
INSERT INTO ITEM_BUKU (id_buku, barcode, id_rak, status) VALUES
(1, 'BK001001', 1, 'Tersedia'),
(1, 'BK001002', 1, 'Tersedia'),
(2, 'BK002001', 1, 'Tersedia'),
(3, 'BK003001', 2, 'Tersedia'),
(4, 'BK004001', 3, 'Tersedia'),
(5, 'BK005001', 4, 'Tersedia'),
(5, 'BK005002', 4, 'Tersedia');

-- ============================================
-- CONSTRAINT TAMBAHAN
-- ============================================

-- Pastikan setiap peminjaman WAJIB memiliki petugas
ALTER TABLE PEMINJAMAN 
MODIFY COLUMN id_petugas_out VARCHAR(30) NOT NULL;

-- Index untuk performa pencarian
CREATE INDEX idx_buku_judul ON BUKU(judul);
CREATE INDEX idx_buku_penulis ON BUKU(penulis);
CREATE INDEX idx_peminjaman_status ON PEMINJAMAN(status);
CREATE INDEX idx_peminjaman_tgl ON PEMINJAMAN(tgl_pinjam);
CREATE INDEX idx_item_barcode ON ITEM_BUKU(barcode);
CREATE INDEX idx_user_role ON USER(role);
