"""Weighted content matching v2; bobot awal adalah rancangan, belum tervalidasi empiris."""
MINAT=['olahraga','seni','musik','budaya','bahasa','lingkungan','energi','keagamaan','pelayanan','kepemimpinan','sosial','jurnalistik','media','kesehatan']
BAKAT=['fisik','kerja sama','kreatif','rasa ingin tahu','komunikasi','konsistensi','kepedulian','kepemimpinan','analitis']
SKILL=['futsal','voli','bulu tangkis','basket','menari','bernyanyi','alat musik','memanah','P3K','menulis','fotografi','videografi','desain','bahasa asing','bela diri','riset','public speaking']
LEVELS=['rendah','sedang','tinggi'];PREFER=['individu','kelompok','keduanya'];LOC=['indoor','outdoor','keduanya']
def validate(a):
    from .auth import AppError
    for key,options,minimum in [('minat',MINAT,1),('bakat',BAKAT,0),('kemampuan',SKILL,0)]:
        x=a.get(key)
        if not isinstance(x,list) or not minimum<=len(x)<=3 or len(set(x))!=len(x) or any(v not in options for v in x):raise AppError(f'Pilihan {key} tidak valid (maksimal tiga).')
    if a.get('pola') not in PREFER or a.get('lokasi') not in LOC or a.get('komitmen') not in LEVELS:raise AppError('Lengkapi preferensi dan komitmen.')
    if a.get('tingkat') not in ['Pemula','Menengah','Mahir']:raise AppError('Tingkat kemampuan tidak valid.')
    if not isinstance(a.get('semester'),int) or not 1<=a['semester']<=14:raise AppError('Semester tidak valid.')
    return a
def match(selected,tags):
    return 100*len(set(selected)&set(tags))/len(tags) if tags else None
def score(a,u,w):
    comp={'minat':match(a['minat'],u['minat']), 'bakat':match(a['bakat'],u['bakat']), 'kemampuan':match(a['kemampuan'],u['kemampuan'])}
    # Kosong pada sisi mahasiswa berarti belum punya kemampuan, bukan informasi UKM yang hilang.
    prefs=[]
    for field in ['pola','lokasi']:
        if u.get(field):prefs.append(100 if u[field]=='keduanya' or a[field]=='keduanya' or a[field]==u[field] else 0)
    comp['preferensi']=sum(prefs)/len(prefs) if prefs else None
    kom=u.get('komitmen')
    comp['komitmen']=(100 if LEVELS.index(a['komitmen'])>=LEVELS.index(kom) else 50 if LEVELS.index(kom)-LEVELS.index(a['komitmen'])==1 else 0) if kom in LEVELS else None
    den=sum(w[k] for k,v in comp.items() if v is not None)
    result=round(sum(w[k]*v for k,v in comp.items() if v is not None)/den,1) if den else 0
    reasons=[]
    for k in ['minat','bakat','kemampuan']:
        shared=sorted(set(a[k])&set(u[k]))
        if shared:reasons.append(f"{k.capitalize()} sesuai: {', '.join(shared)}")
    notes=[]
    if a['tingkat']=='Pemula' and u.get('pemula'):reasons.append('Terbuka bagi pemula; kemampuan dapat dikembangkan.')
    if a['tingkat']=='Pemula' and u.get('pemula') is False:notes.append('Persyaratan pengalaman perlu diperhatikan.')
    if comp['komitmen'] is not None and comp['komitmen']<100:notes.append('Komitmen kegiatan melebihi ketersediaan yang kamu pilih.')
    missing=[k for k,v in comp.items() if v is None]
    if missing:notes.append('Data belum lengkap: '+', '.join(missing)+'. Bobot komponen ini dikeluarkan sementara.')
    if not u.get('terverifikasi'):notes.append('Profil dan pengodean kriteria belum diverifikasi pengurus.')
    notes.append('Periksa persyaratan keanggotaan dan jadwal langsung pada detail UKM.')
    return {'ukm_id':u['id'],'nama':u['nama'],'skor':result,'komponen':comp,'cakupan_bobot':den,'alasan':reasons or ['Belum banyak kecocokan pada pilihanmu.'],'catatan':notes,'profil_snapshot':u}
def rank(a,clubs,w):return sorted([score(a,u,w) for u in clubs if u['aktif']],key=lambda r:(-r['skor'],r['nama']))
