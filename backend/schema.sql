PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE COLLATE NOCASE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','mahasiswa','pengurus')),
 nama TEXT NOT NULL, nim TEXT UNIQUE, prodi TEXT NOT NULL DEFAULT '', angkatan TEXT NOT NULL DEFAULT '',
 ukm_id INTEGER REFERENCES ukm(id) ON DELETE RESTRICT,
 aktif INTEGER NOT NULL DEFAULT 1 CHECK(aktif IN (0,1)), created_at TEXT NOT NULL,
 CHECK(role != 'pengurus' OR ukm_id IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS ukm (
 id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE, nama TEXT NOT NULL,
 kategori TEXT NOT NULL, profil TEXT NOT NULL CHECK(json_valid(profil)),
 aktif INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL CHECK(json_valid(value)));
CREATE TABLE IF NOT EXISTS kuesioner (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
 versi TEXT NOT NULL, jawaban TEXT NOT NULL CHECK(json_valid(jawaban)), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rekomendasi (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
 kuesioner_id INTEGER NOT NULL REFERENCES kuesioner(id),
 bobot TEXT NOT NULL, hasil TEXT NOT NULL CHECK(json_valid(hasil)), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pendaftaran (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
 ukm_id INTEGER NOT NULL REFERENCES ukm(id), periode TEXT NOT NULL,
 rekomendasi_id INTEGER NOT NULL REFERENCES rekomendasi(id), skor REAL NOT NULL CHECK(skor>=0 AND skor<=100),
 status TEXT NOT NULL DEFAULT 'Menunggu' CHECK(status IN ('Menunggu','Diterima','Ditolak','Dibatalkan')),
 konfirmasi TEXT NOT NULL DEFAULT 'Belum' CHECK(konfirmasi IN ('Belum','Diambil','Dilepas')),
 catatan TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
 UNIQUE(user_id,ukm_id,periode)
);
CREATE TABLE IF NOT EXISTS hasil_seleksi (
 id INTEGER PRIMARY KEY, pendaftaran_id INTEGER NOT NULL REFERENCES pendaftaran(id),
 actor_id INTEGER NOT NULL REFERENCES users(id), status TEXT NOT NULL,
 catatan TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assets (key TEXT PRIMARY KEY, data BLOB NOT NULL, mime TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS login_attempts (username TEXT PRIMARY KEY, attempts INTEGER NOT NULL, locked_until REAL NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS idx_kuesioner_user ON kuesioner(user_id,id);
CREATE INDEX IF NOT EXISTS idx_rekomendasi_user ON rekomendasi(user_id,id);
CREATE INDEX IF NOT EXISTS idx_pendaftaran_ukm ON pendaftaran(ukm_id,periode,status);
CREATE TRIGGER IF NOT EXISTS max_two_insert BEFORE INSERT ON pendaftaran
WHEN NEW.status!='Dibatalkan' AND (SELECT count(*) FROM pendaftaran WHERE user_id=NEW.user_id AND periode=NEW.periode AND status!='Dibatalkan')>=2
BEGIN SELECT RAISE(ABORT,'Maksimal dua UKM per periode.'); END;
CREATE TRIGGER IF NOT EXISTS max_two_update BEFORE UPDATE OF status ON pendaftaran
WHEN OLD.status='Dibatalkan' AND NEW.status!='Dibatalkan' AND (SELECT count(*) FROM pendaftaran WHERE user_id=NEW.user_id AND periode=NEW.periode AND status!='Dibatalkan')>=2
BEGIN SELECT RAISE(ABORT,'Maksimal dua UKM per periode.'); END;
