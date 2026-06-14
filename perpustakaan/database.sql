-- ============================================
-- DATABASE STRUCTURE - Sistem Informasi Perpustakaan
-- Untuk MySQL/MariaDB (phpMyAdmin)
-- ============================================

CREATE DATABASE IF NOT EXISTS db_perpustakaan;
USE db_perpustakaan;

-- ====================================================================
-- 1. PEMBUATAN STRUKTUR TABEL 
-- ====================================================================

-- Tabel Master: ROLES
CREATE TABLE IF NOT EXISTS ROLES (
    id_role       VARCHAR(10) NOT NULL,
    nama_role     VARCHAR(20) NOT NULL,
    max_kuota     INT NOT NULL,
    durasi_pinjam INT NOT NULL,
    max_extend    INT NOT NULL,
    CONSTRAINT ROLES_PK PRIMARY KEY (id_role),
    CONSTRAINT ROLES_NAMA_UK UNIQUE (nama_role)
);

-- Tabel Master: USERS 
CREATE TABLE IF NOT EXISTS USERS (
    id_user            VARCHAR(30)  NOT NULL,
    username           VARCHAR(50)  NOT NULL,
    password           VARCHAR(255) NOT NULL,
    nama_lengkap       VARCHAR(100) NOT NULL,
    email              VARCHAR(100) NOT NULL,
    no_telepon         VARCHAR(15)  NOT NULL,
    program_studi      VARCHAR(50),
    fakultas           VARCHAR(50),
    status_aktif       VARCHAR(15)  DEFAULT 'Aktif' NOT NULL,
    alasan_nonaktif    VARCHAR(50),
    tgl_nonaktif       DATE,
    dinonaktifkan_oleh VARCHAR(30),
    id_role            VARCHAR(10)  NOT NULL,
    created_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT USERS_PK PRIMARY KEY (id_user),
    CONSTRAINT USERS_U_UK UNIQUE (username),
    CONSTRAINT USERS_E_UK UNIQUE (email),
    CONSTRAINT USERS_ROLES_FK FOREIGN KEY (id_role) REFERENCES ROLES(id_role),
    CONSTRAINT USERS_SELF_FK FOREIGN KEY (dinonaktifkan_oleh) REFERENCES USERS(id_user)
);

-- Tabel Master: KATEGORI_BUKU
CREATE TABLE IF NOT EXISTS KATEGORI_BUKU (
    id_kategori   INT NOT NULL,
    nama_kategori VARCHAR(50) NOT NULL,
    CONSTRAINT KATEGORI_BUKU_PK PRIMARY KEY (id_kategori),
    CONSTRAINT KATEGORI_NAMA_UK UNIQUE (nama_kategori)
);

-- Tabel Master: RAK
CREATE TABLE IF NOT EXISTS RAK (
    id_rak        VARCHAR(10) NOT NULL,
    nama_rak      VARCHAR(50) NOT NULL,
    lokasi_detail VARCHAR(100) NOT NULL,
    CONSTRAINT RAK_PK PRIMARY KEY (id_rak)
);

-- Tabel Master: KATALOG_BUKU
CREATE TABLE IF NOT EXISTS KATALOG_BUKU (
    isbn           VARCHAR(20)  NOT NULL,
    judul          VARCHAR(200) NOT NULL,
    pengarang      VARCHAR(150) NOT NULL,
    penerbit       VARCHAR(100) NOT NULL,
    tahun_terbit   INT          NOT NULL,
    sinopsis       VARCHAR(4000),
    bahasa         VARCHAR(30)  NOT NULL,
    jumlah_halaman INT          NOT NULL,
    url_cover      VARCHAR(255),
    id_kategori    INT          NOT NULL,
    CONSTRAINT KATALOG_BUKU_PK PRIMARY KEY (isbn),
    CONSTRAINT KATALOG_KATEGORI_FK FOREIGN KEY (id_kategori) REFERENCES KATEGORI_BUKU(id_kategori)
);

-- Tabel Detail: ITEM_BUKU 
CREATE TABLE IF NOT EXISTS ITEM_BUKU (
    id_barcode    VARCHAR(30) NOT NULL,
    isbn          VARCHAR(20) NOT NULL,
    status_pinjam VARCHAR(20) DEFAULT 'Tersedia' NOT NULL,
    id_rak        VARCHAR(10) NOT NULL,
    CONSTRAINT ITEM_BUKU_PK PRIMARY KEY (id_barcode),
    CONSTRAINT ITEM_KATALOG_FK FOREIGN KEY (isbn) REFERENCES KATALOG_BUKU(isbn),
    CONSTRAINT ITEM_RAK_FK FOREIGN KEY (id_rak) REFERENCES RAK(id_rak)
);

-- Tabel Utama: PEMINJAMAN
CREATE TABLE IF NOT EXISTS PEMINJAMAN (
    id_pinjam        VARCHAR(20) NOT NULL,
    id_peminjam      VARCHAR(30) NOT NULL,
    id_barcode       VARCHAR(30) NOT NULL,
    tgl_pinjam       DATE         NOT NULL,
    tgl_jatuh_tempo  DATE         NOT NULL,
    tgl_kembali      DATE,
    jumlah_extend    INT          DEFAULT 0 NOT NULL,
    id_petugas_out   VARCHAR(30) NOT NULL,
    id_petugas_in    VARCHAR(30),
    status_transaksi VARCHAR(20) NOT NULL,
    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at       TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT PEMINJAMAN_PK PRIMARY KEY (id_pinjam),
    CONSTRAINT PEMINJAM_USER_FK FOREIGN KEY (id_peminjam) REFERENCES USERS(id_user),
    CONSTRAINT PEMINJAM_ITEM_FK FOREIGN KEY (id_barcode) REFERENCES ITEM_BUKU(id_barcode),
    CONSTRAINT PEMINJAM_PETUGAS_OUT_FK FOREIGN KEY (id_petugas_out) REFERENCES USERS(id_user),
    CONSTRAINT PEMINJAM_PETUGAS_IN_FK FOREIGN KEY (id_petugas_in) REFERENCES USERS(id_user)
);

-- Tabel Detail: DENDA (Relasi 1:1 Terikat via Unique FK)
CREATE TABLE IF NOT EXISTS DENDA (
    id_denda      VARCHAR(20)   NOT NULL,
    id_pinjam     VARCHAR(20)   NOT NULL,
    nominal_denda DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    status_bayar  VARCHAR(15)   DEFAULT 'Belum Lunas' NOT NULL,
    tgl_bayar     DATE,
    created_at    TIMESTAMP      DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at    TIMESTAMP      NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT DENDA_PK PRIMARY KEY (id_denda),
    CONSTRAINT DENDA_PINJAM_UK UNIQUE (id_pinjam),
    CONSTRAINT DENDA_PINJAM_FK FOREIGN KEY (id_pinjam) REFERENCES PEMINJAMAN(id_pinjam)
);

-- Tabel Operasional: RESERVASI
CREATE TABLE IF NOT EXISTS RESERVASI (
    id_reservasi   VARCHAR(20) NOT NULL,
    id_pemesan     VARCHAR(30) NOT NULL,
    isbn           VARCHAR(20) NOT NULL,
    id_barcode     VARCHAR(30),
    tgl_pemesanan  DATE         DEFAULT (CURRENT_DATE) NOT NULL,
    status_antrian VARCHAR(20) DEFAULT 'Menunggu' NOT NULL,
    tgl_notifikasi DATE,
    created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at     TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT RESERVASI_PK PRIMARY KEY (id_reservasi),
    CONSTRAINT RESERVASI_USER_FK FOREIGN KEY (id_pemesan) REFERENCES USERS(id_user),
    CONSTRAINT RESERVASI_KATALOG_FK FOREIGN KEY (isbn) REFERENCES KATALOG_BUKU(isbn),
    CONSTRAINT RESERVASI_ITEM_FK FOREIGN KEY (id_barcode) REFERENCES ITEM_BUKU(id_barcode)
);

-- Tabel Operasional: MARKAH_BUKU
CREATE TABLE IF NOT EXISTS MARKAH_BUKU (
    id_markah  VARCHAR(20) NOT NULL,
    id_user    VARCHAR(30) NOT NULL,
    isbn       VARCHAR(20) NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT MARKAH_BUKU_PK PRIMARY KEY (id_markah),
    CONSTRAINT MARKAH_USER_FK FOREIGN KEY (id_user) REFERENCES USERS(id_user),
    CONSTRAINT MARKAH_KATALOG_FK FOREIGN KEY (isbn) REFERENCES KATALOG_BUKU(isbn),
    CONSTRAINT MARKAH_USER_ISBN_UK UNIQUE (id_user, isbn)
);

-- ====================================================================
-- 2. PENGISIAN DATA DUMMY
-- ====================================================================

-- Master Data: ROLES
INSERT INTO ROLES (id_role, nama_role, max_kuota, durasi_pinjam, max_extend) VALUES
('SPRADM', 'Super Admin', 0, 0, 0),
('PTGS', 'Petugas Biasa', 0, 0, 0),
('DSN', 'Dosen', 7, 14, 2),
('MHS', 'Mahasiswa', 3, 7, 1);

-- Master Data: KATEGORI_BUKU
INSERT INTO KATEGORI_BUKU (id_kategori, nama_kategori) VALUES
(10, 'Teknologi'),
(20, 'Sains'),
(30, 'Hukum');

-- Master Data: RAK
INSERT INTO RAK (id_rak, nama_rak, lokasi_detail) VALUES
('R-01', 'Rak FTI Teo', 'Lantai 2, Sayap Kanan'),
('R-02', 'Rak MIPA Eks', 'Lantai 1, Sayap Kiri');

-- Master Data: USERS
INSERT INTO USERS (id_user, username, password, nama_lengkap, email, no_telepon, program_studi, fakultas, status_aktif, id_role) VALUES
('USR-ADM01', 'bryan_admin', 'admin123', 'Bryan Grannesa', 'bryan@perpus.ac.id', '08123456789', NULL, NULL, 'Aktif', 'SPRADM'),
('USR-PTG01', 'budi_ops', 'petugas123', 'Budi Santoso', 'budi@perpus.ac.id', '08234567890', NULL, NULL, 'Aktif', 'PTGS'),
('USR-DSN01', 'prof_eko', 'dosen123', 'Prof. Eko Wijaya', 'eko@univ.ac.id', '08345678901', 'Sistem Informasi', 'FTI', 'Aktif', 'DSN'),
('USR-MHS01', 'andi_s', 'mhs123', 'Andi Saputra', 'andi@student.ac.id', '08456789012', 'Sistem Informasi', 'FTI', 'Aktif', 'MHS'),
('USR-MHS02', 'citra_d', 'mhs123', 'Citra Dewi', 'citra@student.ac.id', '08567890123', 'Informatika', 'FTI', 'Nonaktif', 'MHS');

-- Master Data: KATALOG_BUKU
INSERT INTO KATALOG_BUKU (isbn, judul, pengarang, penerbit, tahun_terbit, sinopsis, bahasa, jumlah_halaman, id_kategori) VALUES
('978-602-02-1111', 'Arsitektur Oracle Database 19c', 'Iwan Kurniawan', 'Elex Media', 2023, 'Panduan mendalam DBA tingkat lanjut.', 'Indonesia', 350, 10),
('978-602-04-2222', 'Matematika Diskrit Lanjut', 'Suryono', 'Andi Offset', 2024, 'Logika dan Himpunan untuk Mahasiswa IT.', 'Indonesia', 240, 20);

-- Master Data: ITEM_BUKU
INSERT INTO ITEM_BUKU (id_barcode, isbn, status_pinjam, id_rak) VALUES
('BC-ORC-001', '978-602-02-1111', 'Dipinjam', 'R-01'),
('BC-ORC-002', '978-602-02-1111', 'Tersedia', 'R-01'),
('BC-MAT-001', '978-602-04-2222', 'Tersedia', 'R-02');

-- Operational Data: PEMINJAMAN
INSERT INTO PEMINJAMAN (id_pinjam, id_peminjam, id_barcode, tgl_pinjam, tgl_jatuh_tempo, tgl_kembali, jumlah_extend, id_petugas_out, id_petugas_in, status_transaksi) VALUES
('P-2026-001', 'USR-MHS01', 'BC-ORC-001', '2026-06-01', '2026-06-08', NULL, 0, 'USR-PTG01', NULL, 'Dipinjam'),
('P-2026-002', 'USR-DSN01', 'BC-MAT-001', '2026-05-10', '2026-05-24', '2026-05-28', 1, 'USR-PTG01', 'USR-PTG01', 'Selesai');

-- Operational Data: DENDA
INSERT INTO DENDA (id_denda, id_pinjam, nominal_denda, status_bayar, tgl_bayar) VALUES
('D-2026-001', 'P-2026-002', 20000.00, 'Lunas', '2026-05-28');

-- Operational Data: RESERVASI
INSERT INTO RESERVASI (id_reservasi, id_pemesan, isbn, tgl_pemesanan, status_antrian) VALUES
('RSV-001', 'USR-MHS01', '978-602-02-1111', '2026-06-05', 'Menunggu');

-- Operational Data: MARKAH_BUKU
INSERT INTO MARKAH_BUKU (id_markah, id_user, isbn) VALUES
('M-001', 'USR-MHS01', '978-602-04-2222');
