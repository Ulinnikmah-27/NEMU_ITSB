"""Panduan umum dan panduan berdasarkan peran; tidak membaca data pribadi."""
import streamlit as st
STUDENT=[
('Membuat akun','Buka Daftar mahasiswa. Isi nama, NIM sendiri, program studi dan angkatan. Buat username serta password minimal 8 karakter. Ulangi password dan setujui penggunaan data, lalu klik Buat akun mahasiswa. Setelah berhasil, buka tab Masuk.'),
('Melengkapi profil','Buka Profil. Periksa nama, NIM, program studi dan angkatan. Perbarui kolom yang tersedia lalu klik Simpan profil.'),
('Mengisi kuesioner','Buka Kuesioner. Isi semester, minat (1–3), bakat (maksimal 3), kemampuan (boleh kosong, maksimal 3), tingkat pengalaman, pola kegiatan, ruangan, dan komitmen waktu. Klik Simpan dan hitung rekomendasi.'),
('Membaca rekomendasi','Buka Rekomendasi. Periksa urutan, skor, alasan kecocokan dan catatan UKM. Pelajari persyaratan sebelum memilih. Skor adalah kecocokan berdasarkan aturan aplikasi, bukan peluang diterima atau hasil tes psikologis.'),
('Mendaftar UKM','Pastikan pendaftaran dibuka. Pada Rekomendasi, gunakan tombol pendaftaran UKM pilihan. Periksa menu Pendaftaran. Maksimal dua pendaftaran yang tidak dibatalkan per periode. Pendaftaran yang masih Menunggu dapat dibatalkan.'),
('Melihat hasil dan konfirmasi','Pada Pendaftaran, lihat status Menunggu, Diterima, Ditolak atau Dibatalkan serta catatan pengurus. Untuk yang Diterima, konfirmasi Diambil atau Dilepas. Jika diterima dua UKM, keduanya dapat diambil. Tawaran yang dilepas tidak dapat diambil kembali secara mandiri; hubungi pengurus jika keliru.'),
('Melihat analisis pribadi','Buka Analisis untuk melihat rekomendasi dan perkembangan pendaftaran sendiri. Grafik bergantung pada aktivitas yang tercatat. Jika kosong, selesaikan kuesioner atau pendaftaran terlebih dahulu sesuai kebutuhan.')]
MANAGER=[
('Memeriksa akses UKM','Masuk dengan akun pengurus yang disediakan admin. Periksa UKM yang terhubung pada Dashboard. Jika salah, hubungi admin.'),
('Memproses pendaftar','Buka Pendaftar UKM. Tinjau informasi pendaftar dan lakukan seleksi sesuai ketentuan UKM. Tetapkan Diterima atau Ditolak dan catatan, lalu simpan. Perhatikan batas kuota dan pesan validasi.'),
('Memantau analisis UKM','Buka Analisis untuk melihat pendaftar dan perkembangan seleksi UKM sendiri. Katalog UKM menyediakan detail kegiatan. Hubungi admin jika informasi perlu diubah dan tidak tersedia formulir pengeditan.')]
ADMIN=[
('Mengelola UKM','Buka Kelola UKM. Perbarui profil, kriteria, persyaratan dan kuota melalui formulir yang tersedia. Konfirmasikan informasi kepada pengurus sebelum menandainya sebagai terverifikasi.'),
('Mengelola akun','Buka Kelola akun. Buat akun pengurus dan hubungkan dengan UKM yang tepat. Periksa peran serta status aktif pengguna. Akun dosen dapat dibuat lewat bagian Akun uji dosen dengan peran mahasiswa.'),
('Mengatur periode dan bobot','Buka Pengaturan. Tentukan periode dan buka atau tutup pendaftaran. Total bobot rekomendasi harus 100%. Simpan perubahan. Bobot baru berlaku untuk perhitungan berikutnya, bukan mengubah riwayat hasil yang sudah tersimpan.'),
('Memantau pendaftaran dan analisis','Buka Pendaftaran, Riwayat rekomendasi atau Analisis. Jumlah mahasiswa unik berbeda dari jumlah pendaftaran karena satu mahasiswa dapat memilih dua UKM. Data pengujian dosen ikut tercatat sebagai aktivitas akun mahasiswa.'),
('Mengganti logo','Buka Logo dan aset. Unggah gambar melalui formulir yang tersedia, simpan, lalu periksa tampilannya.')]
def render_guide(me=None):
    st.header('Panduan Penggunaan NEMU')
    st.write('Pelajari cara memakai NEMU dari mengenali UKM sampai mengonfirmasi pilihan.')
    role=me['role'] if me else None
    if not role:
        st.info('Panduan mahasiswa dapat dibaca sebelum masuk. Panduan pengurus dan admin tersedia setelah login dengan peran yang sesuai.')
    else:st.caption('Panduan untuk '+{'mahasiswa':'Mahasiswa','pengurus':'Pengurus UKM','admin':'Admin'}[role])
    steps=MANAGER if role=='pengurus' else ADMIN if role=='admin' else STUDENT
    for i,(title,body) in enumerate(steps,1):
        with st.expander(f'{i}. {title}'):
            st.write(body)
    with st.expander('Navigasi dan keamanan akun'):
        st.write('Gunakan sidebar untuk berpindah halaman. Tombol menu di atas mengecilkan sidebar menjadi ikon; klik lagi untuk memperlebar. Arahkan kursor ke ikon untuk melihat nama menu. Ganti password lewat Keamanan akun dan klik Keluar setelah selesai memakai perangkat bersama.')
    with st.expander('Kendala yang sering ditemui'):
        st.markdown('- **Tidak bisa login:** periksa username dan password; jika terkunci, tunggu sesuai pesan. Hubungi admin jika tetap gagal.\n- **Belum ada rekomendasi:** kirim kuesioner terlebih dahulu.\n- **Tidak bisa mendaftar:** periksa periode, batas dua UKM dan pesan aplikasi.\n- **Data atau grafik belum muncul:** periksa aktivitas yang sudah tercatat dan koneksi internet, lalu muat ulang.\n- **Pilihan terlanjur dilepas:** hubungi pengurus.')
        st.caption('Saat melaporkan kendala, sertakan halaman, langkah dan pesan kesalahan. Jangan sertakan password atau konfigurasi rahasia.')
