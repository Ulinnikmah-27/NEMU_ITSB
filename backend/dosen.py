"""Pembuatan akun uji dosen harus melalui admin aktif, tanpa password bawaan."""
from .db import connect
from .auth import require,create_user,AppError
def create_dosen(actor,password):
    with connect(True) as c:
        require(c,actor,['admin'])
        if c.execute('SELECT id FROM users WHERE username=?',('dosen_nemu',)).fetchone():
            raise AppError('Akun dosen_nemu sudah ada. Tidak ada akun atau password yang ditimpa.')
        return create_user(c,'dosen_nemu',password,'Dosen Penguji NEMU','mahasiswa',nim='UJI-DOSEN',prodi='Sains Data',angkatan='2026')
