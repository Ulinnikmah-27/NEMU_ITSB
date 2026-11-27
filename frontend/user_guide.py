"""Detailed, role-specific instructions with collapsible sections."""
import streamlit as st
COMMON=[
('Akses aplikasi dan navigasi', '''**Tujuan:** mengenali halaman dan menu NEMU.
1. Buka web NEMU melalui browser dengan koneksi internet.
2. Pilih **Masuk** untuk akun yang sudah ada atau **DAFTAR** untuk akun mahasiswa baru.
3. Setelah login, klik menu pada sidebar. Menu aktif memiliki gradasi dan garis kuning.
4. Gunakan tombol menu untuk memperkecil sidebar menjadi ikon. Klik lagi untuk memperlebar. Arahkan kursor ke ikon untuk melihat nama menu.
5. Buka **Panduan Penggunaan** kapan pun dibutuhkan.
**Pesan aplikasi:** pesan berhasil berarti tindakan selesai; peringatan atau kesalahan perlu dibaca sebelum mengulang tindakan. Halaman login dirancang berdampingan di laptop; pendaftaran dan panduan boleh bergulir. Di HP, bagian tersusun vertikal.'''),
('Membuat akun dan login', '''**DAFTAR digunakan untuk akun mahasiswa.** Akun pengurus dan admin disediakan pengelola.
1. Isi nama lengkap, NIM sendiri, pilih program studi dan isi tahun angkatan empat digit.
2. Buat username 3–32 karakter berupa huruf, angka atau underscore, tanpa spasi. Username dan NIM harus belum dipakai.
3. Buat password 8–128 karakter, lalu ulangi dengan nilai sama.
4. Baca dan centang persetujuan penggunaan profil serta jawaban untuk rekomendasi dan seleksi UKM pilihan.
5. Klik **Buat akun mahasiswa**. Tunggu pesan berhasil, lalu buka tab **Masuk**.
6. Masukkan username dan password lalu klik **Masuk**. Ikon mata membantu memeriksa ketikan; gunakan dengan memperhatikan orang di sekitar.
**Simpan password browser:** jika browser menawarkan penyimpanan, gunakan hanya pada perangkat pribadi. Username dan password dapat diisi otomatis pada kunjungan berikutnya. Tawaran bergantung pada browser; NEMU tidak bisa memaksanya. Jika tidak muncul setelah daftar, coba login terlebih dahulu.
**Jika gagal:** periksa kolom wajib, pilihan prodi, Caps Lock dan spasi. Jangan mendaftar ulang jika akun sudah ada.''')]
STUDENT=[
('Dashboard dan profil', '''**Dashboard** menampilkan ringkasan aktivitas, periode dan status pendaftaran. Nilai nol dapat berarti belum ada aktivitas.
1. Buka **Profil** dan periksa NIM, nama, prodi dan angkatan.
2. Perbarui kolom yang dapat diedit; NIM terkunci.
3. Klik **Simpan profil** dan tunggu pesan berhasil.
Jika NIM keliru, hubungi admin. Profil yang akurat membantu pencatatan pendaftaran dan ringkasan analisis.'''),
('Mengisi kuesioner langkah demi langkah', '''**Tujuan:** menghasilkan rekomendasi berdasarkan kondisi diri.
1. Buka **Kuesioner**, isi semester yang sedang dijalani.
2. Pilih **1–3 minat**, maksimal tiga bakat atau karakter, dan maksimal tiga kemampuan. Kemampuan boleh kosong.
3. Pilih tingkat pengalaman: Pemula, Menengah atau Mahir.
4. Pilih pola kegiatan: individu, kelompok atau keduanya.
5. Pilih ruangan: indoor, outdoor atau keduanya.
6. Pilih komitmen waktu: rendah untuk kegiatan sesekali; sedang untuk kegiatan rutin dengan fleksibilitas; tinggi untuk kesiapan latihan/pertemuan dan persiapan tambahan. Ini kategori kualitatif, bukan jumlah jam.
7. Periksa jawaban dan klik **Simpan dan hitung rekomendasi**.
8. Setelah berhasil, buka **Rekomendasi**.
**Tips:** karakter kerja sama berbeda dari kemampuan seperti bermain musik. Jawab sesuai kondisi diri; pemula tetap dapat mengeksplorasi UKM. Jika preferensi berubah, buka kembali kuesioner dan simpan jawaban baru. Perbaiki pesan validasi jika formulir belum dapat dikirim.'''),
('Membaca katalog UKM', '''1. Buka **Katalog UKM** dan gunakan pencarian nama, kegiatan atau minat.
2. Buka detail UKM untuk membaca kegiatan, kategori, minat, bakat pendukung, kemampuan, keterbukaan bagi pemula, pola/ruangan, komitmen, syarat, seleksi dan kuota.
3. Jika tersedia, buka **Baca hasil wawancara lengkap**.
4. Konfirmasikan informasi yang belum lengkap kepada pengurus sebelum mendaftar.
**Perlu konfirmasi** tidak berarti tidak ada persyaratan. Profil yang belum terverifikasi perlu ditinjau. Lokasi di dalam/luar kampus berbeda dari indoor/outdoor.'''),
('Memahami dan memperbarui rekomendasi', '''1. Buka **Rekomendasi** setelah mengirim kuesioner.
2. Periksa waktu perhitungan, bobot, grafik peringkat dan skor.
3. Buka detail untuk membaca alasan, catatan persyaratan dan cakupan data/bobot.
4. Bandingkan dengan katalog, jadwal dan kemampuan mengikuti kegiatan.
**Skor** merupakan kecocokan menurut aturan aplikasi, bukan peluang diterima, hasil tes psikologis atau jaminan kelulusan. Pengurus tetap menetapkan hasil seleksi.
**Cakupan bobot** menunjukkan komponen profil UKM yang tersedia untuk penilaian. Komponen UKM yang belum diketahui dikeluarkan sementara dan bobot yang tersedia dinormalisasi; kelengkapan data memengaruhi perbandingan.
Jika kriteria atau bobot berubah, klik **Perbarui rekomendasi dengan data dan bobot terbaru**. Jika jawabanmu berubah, simpan kuesioner baru dahulu. Riwayat hasil sebelumnya tidak otomatis berubah.'''),
('Mendaftar dan membatalkan pilihan UKM', '''1. Pastikan rekomendasi sudah tersedia dan pendaftaran sedang dibuka.
2. Buka **Rekomendasi**, pelajari detail UKM dan gunakan pilihan pendaftaran yang tersedia.
3. Pilih satu atau dua UKM yang berbeda dan kirim pengajuan.
4. Buka **Pendaftaran** untuk memastikan pengajuan tercatat.
**Batas:** maksimal dua pendaftaran yang tidak dibatalkan per periode, termasuk yang sudah diterima atau ditolak. Tidak boleh duplikat pada UKM/periode yang sama.
**Pembatalan:** buka Pendaftaran, pilih pengajuan berstatus **Menunggu**, gunakan tombol pembatalan dan pastikan status berubah menjadi **Dibatalkan**. Pengajuan Diterima/Ditolak tidak dibatalkan lewat tindakan untuk status Menunggu.
Jika pengajuan gagal, periksa pembukaan periode, batas pilihan dan pesan aplikasi. Jangan mengulang tanpa memeriksa apakah pengajuan sudah tersimpan.'''),
('Hasil seleksi dan konfirmasi', '''Buka **Pendaftaran** dan baca status serta catatan pengurus:
- **Menunggu:** belum ada keputusan akhir.
- **Diterima:** pengajuan diterima.
- **Ditolak:** pengajuan tidak diterima.
- **Dibatalkan:** mahasiswa membatalkan pengajuan.
Untuk status Diterima, periksa konfirmasi:
- **Belum:** belum menentukan pilihan.
- **Diambil:** memilih mengikuti UKM.
- **Dilepas:** tidak mengambil tawaran.
Periksa keputusan sebelum menyimpan. Jika diterima dua UKM, kamu dapat mengambil keduanya atau melepas salah satu sesuai komitmen.
**Tawaran yang sudah dilepas tidak dapat diambil kembali secara mandiri.** Hubungi pengurus jika salah. Status Diterima berbeda dari konfirmasi Diambil. Jika belum diterima, riwayat tetap tercatat; pantau periode berikutnya.'''),
('Analisis pribadi', '''1. Buka **Analisis** dan periksa periode.
2. Lihat grafik rekomendasi, komponen kecocokan dan status pilihanmu.
3. Baca narasi di bawah grafik; data hanya mencakup akun sendiri.
Jika belum ada data, kirim kuesioner atau lakukan pendaftaran sesuai kebutuhan. Data kosong tidak diganti angka contoh pada akun pengguna biasa.''')]
MANAGER=[
('Dashboard dan hak akses pengurus', '''Akun pengurus dihubungkan dengan UKM tertentu oleh admin. Periksa nama UKM dan periode pada Dashboard.
Buka **Katalog UKM** untuk membaca profil. Jika salah UKM atau informasi perlu diubah dan tidak ada formulir pengeditan, hubungi admin. Pengurus tidak mempunyai akses pengelolaan seluruh UKM.'''),
('Memeriksa pendaftar dan menetapkan hasil', '''1. Buka **Pendaftar UKM** dan periksa periode serta data mahasiswa.
2. Baca informasi pendukung yang tersedia. Lakukan seleksi sesuai ketentuan UKM; skor rekomendasi bukan satu-satunya dasar penilaian.
3. Pilih pengajuan, tetapkan Diterima atau Ditolak, dan tambahkan catatan yang jelas.
4. Klik **Simpan keputusan** dan periksa status terbaru.
Jika kuota diterapkan, aplikasi memeriksa ketersediaan saat menerima pengajuan. Pengajuan yang dibatalkan tidak diproses sebagai pengajuan aktif. Data mahasiswa digunakan untuk seleksi, bukan untuk dibagikan di luar kebutuhan pengelolaan.'''),
('Memantau konfirmasi dan analisis UKM', '''Pada daftar yang diterima, periksa konfirmasi Belum, Diambil atau Dilepas. Diterima adalah keputusan pengurus; Diambil adalah konfirmasi mahasiswa.
Buka **Analisis** untuk melihat jumlah pendaftar, status seleksi, minat/prodi dan kuota bila tersedia pada UKM sendiri. Angka berubah mengikuti aktivitas tersimpan. Jika belum ada data, periksa periode dan pengajuan yang masuk.''')]
ADMIN=[
('Dashboard dan pengelolaan UKM', '''1. Periksa ringkasan, periode dan status pembukaan pada Dashboard.
2. Buka **Kelola UKM**, pilih UKM atau Tambah UKM baru.
3. Lengkapi profil, kategori, kriteria, kegiatan, syarat, kuota dan status aktif.
4. Konfirmasikan keterangan dengan pengurus sebelum menandai profil terverifikasi.
5. Klik **Simpan UKM** dan periksa melalui katalog.
Arsipkan UKM jika ingin menyembunyikannya dari pilihan baru tanpa menghapus riwayat. Jangan mengganti informasi yang belum diketahui dengan klaim pasti.'''),
('Mengelola akun dan akun dosen', '''1. Buka **Kelola akun**, tinjau identitas pengguna.
2. Untuk pengurus, buka **Buat akun pengurus**, isi username, nama, password dan UKM yang ditugaskan, lalu simpan.
3. Untuk akun yang ada, pilih pengguna lalu ubah status aktif atau reset password melalui formulir terkait.
4. Periksa kembali pengguna yang dipilih sebelum menyimpan.
Untuk akun dosen yang belum ada, buka **Akun uji dosen**, tentukan password minimal delapan karakter dan ulangi, lalu buat. Username **dosen_nemu** tetap disimpan sebagai mahasiswa pada data asli; akses tiga POV hanya berlangsung di ruang latihan terpisah. Akun yang sudah ada tidak ditimpa.
Jika password akun demo ditampilkan di halaman awal, nilainya di Secrets harus sama dengan password akun yang benar. Mengubah tulisan/Secrets tidak mengganti password akun lama.'''),
('Periode pendaftaran dan bobot rekomendasi', '''1. Buka **Pengaturan**, tentukan periode dan buka/tutup pendaftaran.
2. Periksa bobot minat, bakat, kemampuan, preferensi serta komitmen.
3. Pastikan total 100% dan simpan.
Menutup pendaftaran menghentikan pengajuan baru sesuai aturan, bukan menghapus riwayat. Periode baru menyediakan cakupan pilihan baru; jangan mengganti periode hanya untuk mengganti tulisan.
Bobot baru dipakai pada perhitungan berikutnya, tidak otomatis mengubah riwayat. Bobot perlu ditinjau sesuai kebutuhan pengguna dan bukan ukuran psikologis tervalidasi.'''),
('Riwayat dan analisis keseluruhan', '''Buka **Pendaftaran** untuk memantau pengajuan, **Riwayat rekomendasi** untuk melihat perhitungan tersimpan dan **Analisis** untuk ringkasan lintas UKM. Periksa periode dan waktu sebelum membandingkan data. Pendaftaran terhubung dengan hasil rekomendasi yang digunakan ketika pengajuan dibuat.'''),
('Logo dan aset', '''Buka **Logo dan aset**, pilih logo, unggah PNG/JPG/WEBP sesuai ketentuan, lalu klik **Simpan logo**. Gunakan gambar jelas dan proporsional. Periksa tampilan setelah menyimpan. Logo UKM yang belum diunggah ditampilkan sebagai penanda sementara.''')]
EXTRA=[
('Memahami grafik dan kondisi data kosong', '''**Mahasiswa unik berbeda dari pendaftaran:** satu mahasiswa yang memilih dua UKM dihitung satu orang dan dua pendaftaran.
**Persentase penerimaan:** menggunakan pengajuan yang sudah mendapat keputusan sebagai penyebut sesuai penjelasan halaman. Belum ada keputusan berbeda dari nol persen penerimaan.
**Minat:** satu mahasiswa bisa memilih beberapa minat sehingga total pilihan/persentase tidak harus 100%.
**Pembatalan:** pengajuan Dibatalkan dikeluarkan dari ringkasan aktif, tetapi riwayat tetap ada.
**Data kosong:** angka nol/grafik belum tersedia berarti belum ada aktivitas yang sesuai periode serta akses. Bukan kesimpulan tentang minat seluruh mahasiswa. Pada mode dosen, seluruh angka berasal dari data latihan yang diberi label demo.'''),
('Akun demo dosen dan pergantian tiga POV', '''1. Buka **Akun Demo untuk Dosen** di halaman awal, lalu login dengan akun yang ditampilkan.
2. Setelah login, pilih **Lihat sebagai** pada sidebar: Mahasiswa, Pengurus UKM atau Admin. Tidak perlu logout.
3. Pada POV Pengurus UKM, pilih **UKM demo yang dikelola**.
4. Coba formulir, rekomendasi, seleksi dan analisis seperti peran tersebut. Akun asli tidak dinaikkan menjadi admin.
5. Gunakan **Mulai ulang demo** untuk menghapus perubahan latihan sesi ini dan mengembalikan contoh awal. Ini hanya menghapus data demo.
Ruang demo terpisah per sesi dan tidak memuat identitas atau pendaftaran pengguna asli. Data contoh UKM berasal dari katalog awal paket. Perubahan latihan dapat hilang setelah sesi/server berakhir. Login akun biasa tetap memakai data asli. Password akun internal latihan yang digunakan pada halaman Keamanan akun adalah **LatihanNEMU2026!**; menggantinya di demo tidak mengganti password login dosen.
**Jika tidak masuk mode dosen:** pastikan username dosen_nemu, akun aktif dan perannya mahasiswa. Pengaturan tersebut dikelola admin.'''),
('Keamanan akun dan keluar', '''Pada akun pribadi, buka **Keamanan akun**, isi password lama, password baru dan ulangi, lalu simpan. Jika browser masih mengisi password lama, perbarui pengelola password browser.
Klik **Keluar** dan pastikan kembali ke halaman awal, terutama di perangkat bersama. Sesi yang berakhir memerlukan login ulang.
Jangan membagikan password pribadi, memasukkan password database pada formulir, atau menyebarkan screenshot yang berisi data pribadi. Data demo digunakan bersama hanya jika seseorang memakai sesi/perangkat yang sama; jangan menaruh data pribadi di ruang latihan.'''),
('Kendala dan pelaporan masalah', '''- **Login salah:** periksa username, Caps Lock, spasi dan password tersimpan. Jika terkunci, tunggu sesuai pesan, lalu hubungi admin bila berlanjut.
- **Username/NIM terpakai:** gunakan akun yang telah dibuat; jangan membuat identitas ganda.
- **Formulir gagal:** periksa kolom wajib, batas pilihan, kesamaan password dan pesan validasi.
- **Rekomendasi kosong:** kirim kuesioner. Hasil lama perlu diperbarui setelah profil/bobot berubah.
- **Pendaftaran gagal:** periksa periode, batas dua pengajuan dan kemungkinan sudah terdaftar.
- **Belum ada hasil:** pantau status Menunggu atau hubungi pengurus.
- **Tidak bisa batal/ambil kembali:** hanya pengajuan Menunggu dapat dibatalkan; tawaran yang Dilepas memerlukan bantuan pengurus.
- **Grafik kosong:** periksa aktivitas, periode dan hak akses.
- **Data gagal dimuat:** periksa internet dan muat ulang; laporkan bila berlanjut.
- **Tawaran simpan password tidak muncul:** periksa pengaturan browser; aplikasi tidak dapat memaksanya.
**Saat melapor:** sertakan halaman, peran, langkah sebelum masalah, pesan kesalahan, waktu dan screenshot seperlunya. Jangan sertakan password, isi Secrets atau kredensial database.''')]

def render_guide(me=None):
    st.header('Panduan Penggunaan NEMU')
    st.write('Buka bagian yang diperlukan untuk melihat fungsi, langkah penggunaan, ketentuan dan solusi kendala.')
    role=me['role'] if me else None
    if role:st.caption('Panduan '+{'mahasiswa':'Mahasiswa','pengurus':'Pengurus UKM','admin':'Admin'}[role])
    else:st.caption('Panduan awal dan mahasiswa. Panduan pengurus/admin mengikuti peran setelah login.')
    topics=COMMON+(ADMIN if role=='admin' else MANAGER if role=='pengurus' else STUDENT)+EXTRA
    for i,(title,body) in enumerate(topics,1):
        with st.expander(f'{i}. {title}',expanded=False):st.markdown(body)
