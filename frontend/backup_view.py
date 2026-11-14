import streamlit as st
from datetime import datetime,timezone
from backend.auth import AppError
from backend.backup import freeze_snapshot,resume,is_frozen
from backend.db import mode

def render_backup(me):
    st.header('Backup dan pemindahan database')
    if mode()=='postgres':
        st.success('Aplikasi memakai PostgreSQL. Akun dan pendaftaran dibaca dari database tersebut.')
        st.write('Backup penuh PostgreSQL menggunakan pg_dump. Lihat panduan dalam paket.');return
    st.write('Buat backup penuh dari database aplikasi yang sedang dibuka. Jika dibuka melalui web online, file ini berisi data web online; jika dibuka di localhost, file ini berisi data laptop.')
    st.warning('Membuat backup migrasi akan membekukan perubahan data agar tidak ada pendaftaran baru yang tertinggal. Akun admin tetap bisa login dan mengunduh ulang. Jika migrasi belum jadi, gunakan Buka kembali aplikasi.')
    with st.form('backup_full_form'):
        password=st.text_input('Password admin saat ini',type='password')
        save=st.form_submit_button('Bekukan dan siapkan backup penuh',type='primary')
        reopen=st.form_submit_button('Buka kembali aplikasi')
    if save:
        try:
            data,counts=freeze_snapshot(me['id'],password)
            st.session_state['full_backup_bytes']=data;st.session_state['full_backup_counts']=counts
        except AppError as e:st.error(str(e))
    if reopen:
        try:resume(me['id'],password);st.session_state.pop('full_backup_bytes',None);st.success('Aplikasi dibuka kembali. Jika nanti migrasi, buat backup terbaru dahulu.')
        except AppError as e:st.error(str(e))
    if st.session_state.get('full_backup_bytes'):
        st.write('Jumlah data pada backup:',st.session_state['full_backup_counts'])
        st.download_button('Unduh BACKUP PENUH NEMU (.db)',st.session_state['full_backup_bytes'],'nemu_backup_migrasi_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')+'.db','application/octet-stream')
        st.info('Simpan file ini di laptop. File memuat password hash dan data pribadi; jangan unggah ke GitHub atau bagikan lewat tautan publik. Jangan beralih ke Supabase sebelum file berhasil diunduh.')
    if is_frozen():st.caption('Status: perubahan data SQLite sedang dibekukan untuk migrasi.')
