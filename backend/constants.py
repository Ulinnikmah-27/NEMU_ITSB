"""Daftar program studi sesuai daftar pengguna untuk NEMU."""
PROGRAM_STUDI = [
    'Sains Data', 'Bisnis Digital', 'Teknik Sipil',
    'Perencanaan Wilayah dan Kota', 'Teknik Pertambangan', 'Teknik Metalurgi',
    'Teknik Perminyakan', 'Desain Produk', 'Informatika', 'Teknik Pengolahan Sawit',
    'Teknologi Pengolahan Pulp dan Kertas', 'Pengelolaan dan Teknologi Perkebunan',
]
def normalize_prodi(value):
    normalized=' '.join(str(value or '').split()).casefold()
    return next((p for p in PROGRAM_STUDI if p.casefold()==normalized),None)
def validate_prodi(value):
    from .auth import AppError
    result=normalize_prodi(value)
    if result is None:raise AppError('Pilih program studi dari 12 pilihan yang tersedia.')
    return result
