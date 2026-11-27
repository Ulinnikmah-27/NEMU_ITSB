import streamlit as st
from backend.auth import AppError
from backend.dosen import create_dosen
def render_dosen_form(me):
    with st.expander('Akun uji dosen'):
        st.write('Username: dosen_nemu · Satu login untuk tiga POV di ruang latihan terpisah. Peran akun asli tetap mahasiswa.')
        st.caption('Identitas akun: UJI-DOSEN. Aktivitas mode penilaian memakai data demo per sesi dan tidak masuk analisis asli. Akun yang sudah ada tidak perlu dibuat ulang.')
        with st.form('create_dosen_account',clear_on_submit=True):
            pw=st.text_input('Password akun dosen (minimal 8 karakter)',type='password')
            repeat=st.text_input('Ulangi password akun dosen',type='password')
            if st.form_submit_button('Buat akun dosen'):
                if pw!=repeat:st.error('Password tidak sama.')
                else:
                    try:create_dosen(me['id'],pw);st.success('Akun dosen_nemu berhasil dibuat. Berikan password secara pribadi kepada dosen.')
                    except AppError as e:st.error(str(e))
