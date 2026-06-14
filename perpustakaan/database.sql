-- ============================================
-- DATABASE STRUCTURE - Sistem Informasi Perpustakaan
-- Untuk MySQL/MariaDB (phpMyAdmin)
-- ============================================

CREATE DATABASE IF NOT EXISTS perpustakaan_db;
USE perpustakaan_db;


-- 2. Buat Tabel USERS terlebih dahulu (Referensi untuk foreign key)
CREATE TABLE USERS (
    id_user VARCHAR(30) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(100) NOT NULL,
    role ENUM('ADMIN', 'PETUGAS', 'MHS', 'DSN') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Masukkan Data Awal Users (Admin & Petugas)
-- Pastikan jumlah kolom (id_user, password, nama_lengkap, role) = 4 nilai
INSERT INTO USERS (id_user, password, nama_lengkap, role) VALUES
('ADM001', 'admin123', 'Administrator Utama', 'ADMIN'),
('PTG001', 'petugas123', 'Budi Santoso', 'PETUGAS'),
('PTG002', 'petugas123', 'Siti Aminah', 'PETUGAS'),
('MHS001', 'mhs123', 'Ahmad Student', 'MHS'),
('DSN001', 'dsn123', 'Dr. Lecturer', 'DSN');

-- 4. Buat Tabel KATEGORI
CREATE TABLE KATEGORI (
    id_kategori INT AUTO_INCREMENT PRIMARY KEY,
    nama_kategori VARCHAR(50) NOT NULL
);

INSERT INTO KATEGORI (nama_kategori) VALUES 
('Teknologi Informasi'),
('Sains'),
('Sosial Humaniora'),
('Fiksi');

-- 5. Buat Tabel RAK
CREATE TABLE RAK (
    id_rak INT AUTO_INCREMENT PRIMARY KEY,
    lokasi_rak VARCHAR(20) NOT NULL
);

INSERT INTO RAK (lokasi_rak) VALUES 
('A-01'), ('A-02'), ('B-01'), ('B-02');

-- 6. Buat Tabel BUKU (Katalog Utama)
CREATE TABLE BUKU (
    id_buku INT AUTO_INCREMENT PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    pengarang VARCHAR(100),
    penerbit VARCHAR(100),
    tahun_terbit YEAR,
    id_kategori INT,
    FOREIGN KEY (id_kategori) REFERENCES KATEGORI(id_kategori) ON DELETE SET NULL
);

-- 7. Buat Tabel ITEM_BUKU (Barcode per eksemplar)
CREATE TABLE ITEM_BUKU (
    barcode VARCHAR(50) PRIMARY KEY,
    id_buku INT NOT NULL,
    id_rak INT,
    status ENUM('Tersedia', 'Dipinjam', 'Rusak', 'Hilang') DEFAULT 'Tersedia',
    FOREIGN KEY (id_buku) REFERENCES BUKU(id_buku) ON DELETE CASCADE,
    FOREIGN KEY (id_rak) REFERENCES RAK(id_rak) ON DELETE SET NULL
);

-- Masukkan Data Buku & Item Contoh
INSERT INTO BUKU (judul, pengarang, id_kategori) VALUES 
('Belajar Python', 'John Doe', 1),
('Dasar Jaringan', 'Jane Smith', 1);

INSERT INTO ITEM_BUKU (barcode, id_buku, id_rak, status) VALUES 
('BK0001', 1, 1, 'Tersedia'),
('BK0002', 1, 1, 'Tersedia'),
('BK0003', 2, 2, 'Tersedia');

-- 8. Buat Tabel PEMINJAMAN
-- PENTING: id_petugas_out didefinisikan NOT NULL.
-- Karena data PETUGAS sudah ada di langkah 3, foreign key akan valid.
CREATE TABLE PEMINJAMAN (
    id_pinjam INT AUTO_INCREMENT PRIMARY KEY,
    id_user VARCHAR(30) NOT NULL,
    id_petugas_out VARCHAR(30) NOT NULL, -- Wajib diisi saat pinjam
    id_petugas_in VARCHAR(30), -- Diisi saat kembali (bisa NULL awalnya)
    tgl_pinjam DATE NOT NULL,
    tgl_kembali DATE,
    status ENUM('Dipinjam', 'Kembali') DEFAULT 'Dipinjam',
    FOREIGN KEY (id_user) REFERENCES USERS(id_user),
    FOREIGN KEY (id_petugas_out) REFERENCES USERS(id_user),
    FOREIGN KEY (id_petugas_in) REFERENCES USERS(id_user)
);

-- 9. Buat Tabel DENDA
CREATE TABLE DENDA (
    id_denda INT AUTO_INCREMENT PRIMARY KEY,
    id_pinjam INT NOT NULL,
    jumlah_denda DECIMAL(10, 2) NOT NULL,
    status_bayar ENUM('Belum Lunas', 'Lunas') DEFAULT 'Belum Lunas',
    FOREIGN KEY (id_pinjam) REFERENCES PEMINJAMAN(id_pinjam) ON DELETE CASCADE
);

-- Selesai
SELECT 'Database berhasil dibuat tanpa error!' AS Status;