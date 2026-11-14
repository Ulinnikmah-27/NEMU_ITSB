"""Halaman Streamlit. SQL dan aturan bisnis berada di backend/."""
import json,csv,io,time
import streamlit as st
import pandas as pd
import plotly.express as px
from backend import auth,service as s
from backend.recommendation import MINAT,BAKAT,SKILL,LEVELS,PREFER,LOC
from .theme import hero
from backend.constants import PROGRAM_STUDI, normalize_prodi
from .analytics_view import render_analytics, recommendation_text

def action(fn,*args,message='Berhasil disimpan.'):
    try:fn(*args)
    except auth.AppError as e:st.error(str(e));return False
    st.session_state['flash']=message;st.rerun()
def csv_data(rows):
    # Lindungi ekspor yang dibuka di spreadsheet dari formula pada teks pengguna.
    if not rows:return b''
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader()
    for row in rows:w.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v) for k,v in row.items()})
    return out.getvalue().encode('utf-8-sig')
def auth_page():
    hero();st.subheader('Selamat datang di NEMU')
    a,b=st.tabs(['Masuk','Daftar mahasiswa'])
    with a,st.form('login'):
        username=st.text_input('Username');password=st.text_input('Password',type='password')
        if st.form_submit_button('Masuk',type='primary'):
            try:
                u=auth.login(username,password);st.session_state['uid']=u['id'];st.session_state['login_at']=time.time();st.rerun()
            except auth.AppError as e:st.error(str(e))
    with b,st.form('register'):
        nama=st.text_input('Nama lengkap');nim=st.text_input('NIM');prodi=st.selectbox('Program studi',PROGRAM_STUDI,index=None,placeholder='Pilih program studi');angkatan=st.text_input('Angkatan',placeholder='2026')
        un=st.text_input('Username baru');pw=st.text_input('Password baru (minimal 8 karakter)',type='password');pw2=st.text_input('Ulangi password',type='password')
        consent=st.checkbox('Saya setuju profil dan jawaban digunakan untuk rekomendasi; pengurus UKM pilihan saya dapat melihat jawaban untuk seleksi.')
        if st.form_submit_button('Buat akun mahasiswa',type='primary'):
            if pw!=pw2:st.error('Password tidak sama.')
            elif not consent:st.error('Persetujuan penggunaan data diperlukan untuk melanjutkan.')
            else:
                try:auth.register(un,pw,nama,nim,prodi,angkatan);st.success('Akun berhasil dibuat. Buka tab Masuk.')
                except auth.AppError as e:st.error(str(e))

def dashboard(me):
    hero();st.subheader('Halo, '+me['nama']+' 👋')
    cfg=s.config(me['id'])
    st.info(f"Periode {cfg['periode']} · Pendaftaran {'dibuka' if cfg['pendaftaran_buka'] else 'ditutup'}")
    render_analytics(me,compact=True)
def profile(me):
    st.header('Profil mahasiswa')
    with st.form('profile'):
        st.text_input('NIM',me['nim'] or '',disabled=True)
        nama=st.text_input('Nama lengkap',me['nama']);prodi=st.selectbox('Program studi',PROGRAM_STUDI,index=PROGRAM_STUDI.index(normalize_prodi(me['prodi'])) if normalize_prodi(me['prodi']) else None,placeholder='Pilih program studi');angkatan=st.text_input('Angkatan',me['angkatan'])
        if st.form_submit_button('Simpan profil',type='primary'):action(s.update_profile,me['id'],nama,prodi,angkatan)
def questionnaire(me):
    st.header('Kuesioner minat dan kemampuan')
    st.write('Pilih sesuai dirimu. Pemula tetap dapat memperoleh rekomendasi; kemampuan bukan syarat wajib pada seluruh UKM.')
    old=s.latest_answers(me['id'])
    with st.form('questionnaire'):
        semester=st.number_input('Semester',1,14,old.get('semester',1))
        mi=st.multiselect('Minat (1–3 pilihan)',MINAT,old.get('minat',[]),max_selections=3)
        ba=st.multiselect('Bakat atau karakter pendukung (maksimal 3)',BAKAT,old.get('bakat',[]),max_selections=3)
        ke=st.multiselect('Kemampuan yang sudah dimiliki (boleh kosong, maksimal 3)',SKILL,old.get('kemampuan',[]),max_selections=3)
        tg=st.selectbox('Tingkat pengalaman secara umum',['Pemula','Menengah','Mahir'],index=['Pemula','Menengah','Mahir'].index(old.get('tingkat','Pemula')))
        po=st.selectbox('Preferensi bentuk kegiatan',PREFER,index=PREFER.index(old.get('pola','keduanya')))
        lo=st.selectbox('Preferensi ruangan kegiatan',LOC,index=LOC.index(old.get('lokasi','keduanya')))
        ko=st.selectbox('Komitmen yang sanggup diberikan',LEVELS,index=LEVELS.index(old.get('komitmen','sedang')))
        st.caption('Rendah: kegiatan sesekali. Sedang: kegiatan rutin dengan fleksibilitas. Tinggi: siap latihan/pertemuan rutin dan persiapan tambahan. Ini kategori kualitatif, bukan jumlah jam.')
        if st.form_submit_button('Simpan dan hitung rekomendasi',type='primary'):
            action(s.save_answers,me['id'],dict(semester=semester,minat=mi,bakat=ba,kemampuan=ke,tingkat=tg,pola=po,lokasi=lo,komitmen=ko),message='Jawaban tersimpan. Lihat menu Rekomendasi.')
def logo(me,key,size=64):
    data=s.asset(me['id'],key)
    if data:st.image(data,width=size)
    else:st.caption('🧭 Logo sementara · dapat diganti admin')
def club_detail(me,u):
    logo(me,'ukm:'+str(u['id']),90)
    st.subheader(u['nama']);st.write(u['deskripsi'])
    if not u.get('terverifikasi'):st.info('Profil dan tag rekomendasi perlu ditinjau pengurus. Informasi yang belum diketahui tetap perlu konfirmasi.')
    def fmt(x):return x if x is not None else 'Perlu konfirmasi'
    st.write('**Kategori:**',u['kategori']);st.write('**Minat:**',', '.join(u['minat']))
    st.write('**Bakat pendukung:**',', '.join(u['bakat']) or 'Tidak ditetapkan')
    st.write('**Kemampuan pendukung:**',', '.join(u['kemampuan']) or 'Tidak diwajibkan secara spesifik')
    st.write('**Menerima pemula:**',{True:'Ya',False:'Tidak',None:'Perlu konfirmasi'}[u.get('pemula')])
    st.write('**Bentuk kegiatan:**',fmt(u.get('pola')));st.write('**Ruangan:**',fmt(u.get('lokasi')));st.write('**Komitmen:**',fmt(u.get('komitmen')))
    st.write('**Persyaratan:**',u.get('syarat') or 'Perlu konfirmasi')
    st.write('**Seleksi:**',u.get('seleksi') or 'Perlu konfirmasi');st.write('**Kuota:**',fmt(u.get('kuota')))
    if u.get('wawancara'):
        with st.expander('Baca hasil wawancara lengkap'):
            for q,a in u['wawancara'].items():st.markdown('**'+q+'**');st.write(a)
    st.caption(u.get('catatan',''))
def catalog(me):
    st.header('Katalog UKM');cs=s.clubs(me['id']);query=st.text_input('Cari nama, kegiatan, atau minat')
    category=st.selectbox('Kategori',['Semua']+sorted({u['kategori'] for u in cs}));beginner=st.checkbox('Hanya yang menerima pemula')
    filtered=[u for u in cs if (category=='Semua' or u['kategori']==category) and (not beginner or u.get('pemula')) and query.lower() in (u['nama']+' '+u['deskripsi']+' '+','.join(u['minat'])).lower()]
    st.caption(f'{len(filtered)} UKM ditemukan')
    for u in filtered:
        with st.expander(u['nama']+' · '+u['kategori']):club_detail(me,u)
def recommendations(me):
    st.header('Rekomendasi UKM');rec=s.recommendations(me['id'])
    if not rec:st.info('Isi kuesioner dahulu.');return
    st.caption('Dihitung '+rec['created_at']+' (UTC) · Skor kecocokan, bukan peluang diterima.')
    st.write('Bobot saat dihitung:',rec['bobot'])
    if st.button('Perbarui rekomendasi dengan data dan bobot terbaru'):action(s.refresh_recommendations,me['id'])
    data=rec['hasil'];active={u['id'] for u in s.clubs(me['id'])};data=[r for r in data if r['ukm_id'] in active]
    if not data:st.info('Belum ada UKM aktif.');return
    frame=pd.DataFrame([{'UKM':r['nama'],'Skor':r['skor'],'Cakupan data (%)':r['cakupan_bobot']} for r in data])
    fig=px.bar(frame.sort_values('Skor'),x='Skor',y='UKM',orientation='h',color_discrete_sequence=['#7568c7'],range_x=[0,100])
    fig.update_layout(height=620,margin=dict(l=0,r=10,t=10,b=10),paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
    st.write(recommendation_text(data))
    for i,r in enumerate(data[:5],1):
        with st.expander(f"{i}. {r['nama']} · {r['skor']}%",expanded=i==1):
            st.write('**Alasan:**');[st.write('• '+x) for x in r['alasan']]
            st.write('**Pertimbangan:**');[st.write('• '+x) for x in r['catatan']]
            st.write('Cakupan bobot yang bisa dinilai:',r['cakupan_bobot'],'%')
    names=[r['nama'] for r in data]
    selected=st.multiselect('Bandingkan maksimal tiga UKM',names,default=names[:2],max_selections=3)
    rows=[]
    for r in data:
        if r['nama'] in selected:
            p=r['profil_snapshot'];rows.append({'UKM':r['nama'],'Skor':r['skor'],'Minat':r['komponen']['minat'],'Bakat':r['komponen']['bakat'],'Kemampuan':r['komponen']['kemampuan'],'Preferensi':r['komponen']['preferensi'],'Komitmen':p.get('komitmen'),'Cakupan bobot':r['cakupan_bobot']})
    if rows:st.dataframe(pd.DataFrame(rows),hide_index=True)
    st.download_button('Unduh hasil rekomendasi CSV',csv_data(frame.to_dict('records')),'rekomendasi_nemu.csv','text/csv')
    st.caption('Komponen yang belum diketahui pada profil UKM tidak dihitung; bobot komponen yang tersedia dinormalisasi. Kelengkapan data dapat memengaruhi perbandingan. Bobot awal masih perlu divalidasi kelompok dan pengurus.')
def registrations(me):
    st.header('Pendaftaran dan hasil seleksi');cfg=s.config(me['id']);rows=s.registrations(me['id'])
    period=cfg['periode'];st.info(f"Periode aktif: {period} · {'Dibuka' if cfg['pendaftaran_buka'] else 'Ditutup'}")
    if me['role']=='mahasiswa':
        current=[r for r in rows if r['periode']==period and r['status']!='Dibatalkan'];rec=s.recommendations(me['id'])
        st.write(f'Pilihan terpakai: {len(current)}/2')
        if len(current)<2 and cfg['pendaftaran_buka'] and rec:
            cs={u['id']:u for u in s.clubs(me['id'])};used={r['ukm_id'] for r in current}
            opts={r['ukm_id']:f"{r['nama']} · {r['skor']}%" for r in rec['hasil'] if r['ukm_id'] in cs and r['ukm_id'] not in used}
            with st.form('apply'):
                picked=st.multiselect('Pilih UKM',list(opts),format_func=opts.get,max_selections=2-len(current))
                acknowledge=st.checkbox('Saya telah membaca persyaratan, jadwal, dan keterangan seleksi UKM pilihan saya.')
                if st.form_submit_button('Kirim pendaftaran',type='primary'):
                    if not acknowledge:st.error('Baca dan setujui informasi pendaftaran dahulu.')
                    else:action(s.register_clubs,me['id'],picked,message='Pendaftaran terkirim.')
        elif not rec:st.write('Isi kuesioner dahulu sebelum mendaftar.')
        st.caption('Maksimal dua pilihan per periode, termasuk yang telah diterima/ditolak. Pendaftaran menunggu dapat dibatalkan. Jika dua pilihan ditolak, coba periode berikutnya.')
    else:
        status=st.selectbox('Filter status',['Semua','Menunggu','Diterima','Ditolak','Dibatalkan']);search=st.text_input('Cari mahasiswa atau UKM')
        rows=[r for r in rows if (status=='Semua' or r['status']==status) and search.lower() in (r['mahasiswa']+' '+r['ukm']).lower()]
        st.download_button('Unduh pendaftaran CSV',csv_data(rows),'pendaftaran_nemu.csv','text/csv')
    if not rows:st.write('Belum ada pendaftaran.')
    for r in rows:
        with st.expander(f"{r['ukm']} · {r['mahasiswa']} · {r['status']} · {r['periode']}"):
            st.write('**Skor saat mendaftar:**',r['skor']);st.write('**Catatan:**',r['catatan'] or 'Belum ada catatan')
            st.write('**Konfirmasi mahasiswa:**',r['konfirmasi'])
            if me['role']=='mahasiswa':
                if r['status']=='Menunggu' and r['periode']==period and st.button('Batalkan pendaftaran',key=f"cancel{r['id']}"):action(s.cancel,me['id'],r['id'])
                if r['status']=='Diterima' and r['periode']==period and r['konfirmasi']!='Dilepas':
                    st.caption('Kamu dapat mengambil satu atau kedua tawaran. Pastikan sesuai kebijakan UKM. Tawaran yang dilepas tidak dapat diambil kembali lewat mahasiswa.')
                    a,b=st.columns(2)
                    if a.button('Ambil tawaran',key=f"take{r['id']}"):action(s.confirm,me['id'],r['id'],'Diambil')
                    if b.button('Lepaskan tawaran',key=f"drop{r['id']}"):action(s.confirm,me['id'],r['id'],'Dilepas')
            elif r['status']!='Dibatalkan':
                st.write('**Profil pendaftar:**',r['nim'],r['prodi'],r['angkatan'])
                st.json(s.applicant_answers(me['id'],r['id']),expanded=False)
                with st.form(f"decide{r['id']}"):
                    status=st.selectbox('Keputusan',['Menunggu','Diterima','Ditolak'],index=['Menunggu','Diterima','Ditolak'].index(r['status']))
                    note=st.text_area('Catatan untuk mahasiswa',r['catatan'],max_chars=2000)
                    if st.form_submit_button('Simpan keputusan'):action(s.decide,me['id'],r['id'],status,note)
            h=s.history(me['id'],r['id'])
            if h:st.dataframe(pd.DataFrame(h),hide_index=True)
def admin_clubs(me):
    st.header('Kelola profil dan kriteria UKM');cs=s.clubs(me['id'],True)
    opts={0:'Tambah UKM baru',**{u['id']:u['nama']+(' (diarsipkan)' if not u['aktif'] else '') for u in cs}}
    uid=st.selectbox('Pilih UKM',list(opts),format_func=opts.get)
    default=dict(slug='',nama='',kategori='',deskripsi='',minat=[],bakat=[],kemampuan=[],pola=None,lokasi=None,komitmen=None,pemula=None,syarat='',seleksi='',kuota=None,catatan='',aktif=True,terverifikasi=False,wawancara={})
    p=next((dict(u) for u in cs if u['id']==uid),default)
    st.caption('Informasi yang belum jelas dibiarkan perlu konfirmasi. Kategori indoor/outdoor berbeda dengan di dalam/luar kampus.')
    with st.form('edit_club'):
        p['nama']=st.text_input('Nama UKM',p['nama']);p['slug']=st.text_input('Slug (huruf kecil, angka, underscore)',p['slug']);p['kategori']=st.text_input('Kategori',p['kategori'])
        p['deskripsi']=st.text_area('Deskripsi dan kegiatan rutin',p['deskripsi'],height=150)
        for key,options in [('minat',MINAT),('bakat',BAKAT),('kemampuan',SKILL)]:p[key]=st.multiselect(key.capitalize(),options,p[key])
        for key,options in [('pola',PREFER),('lokasi',LOC),('komitmen',LEVELS)]:
            choices=[None]+options;p[key]=st.selectbox(key.capitalize(),choices,index=choices.index(p.get(key)),format_func=lambda v:v or 'Perlu konfirmasi')
        p['pemula']=st.selectbox('Menerima pemula',[None,True,False],index=[None,True,False].index(p.get('pemula')),format_func=lambda v:{None:'Perlu konfirmasi',True:'Ya',False:'Tidak'}[v])
        p['syarat']=st.text_area('Syarat anggota dan keterangan syarat pengurus',p['syarat']);p['seleksi']=st.text_area('Tahapan seleksi',p['seleksi'])
        quota=st.number_input('Kuota (0 = belum diketahui)',0,10000,int(p.get('kuota') or 0));p['kuota']=quota or None
        p['catatan']=st.text_area('Catatan verifikasi dan sumber',p.get('catatan',''))
        p['aktif']=st.checkbox('UKM aktif',p['aktif']);p['terverifikasi']=st.checkbox('Profil dan pengodean kriteria sudah ditinjau pengurus',p.get('terverifikasi',False))
        if st.form_submit_button('Simpan UKM',type='primary'):action(s.save_club,me['id'],p)
    if uid and st.button('Arsipkan UKM ini'):action(s.archive_club,me['id'],uid)
    st.caption('Pengarsipan menyembunyikan UKM dari katalog dan pilihan baru. Riwayat pendaftaran tetap disimpan.')
    if p.get('wawancara'):
        with st.expander('Sumber wawancara untuk pencocokan profil'):
            for q,a in p['wawancara'].items():st.markdown('**'+q+'**');st.write(a)
def admin_assets(me):
    st.header('Logo aplikasi dan UKM');cs=s.clubs(me['id'],True)
    opts={'nemu':'Logo NEMU',**{'ukm:'+str(u['id']):u['nama'] for u in cs}}
    key=st.selectbox('Logo yang ingin diganti',list(opts),format_func=opts.get);logo(me,key,130)
    f=st.file_uploader('Unggah PNG, JPG, atau WEBP (maksimal 2 MB)',type=['png','jpg','jpeg','webp'])
    if st.button('Simpan logo',disabled=f is None,type='primary'):action(s.save_asset,me['id'],key,f.getvalue())
    st.caption('Logo yang belum diunggah memakai penanda sementara, bukan logo resmi UKM.')
def admin_users(me):
    st.header('Kelola akun');cs=s.clubs(me['id'],True);opts={u['id']:u['nama'] for u in cs}
    with st.expander('Buat akun pengurus'):
        with st.form('manager'):
            un=st.text_input('Username pengurus');nm=st.text_input('Nama pengurus');pw=st.text_input('Password pengurus',type='password');uid=st.selectbox('UKM yang dikelola',list(opts),format_func=opts.get)
            if st.form_submit_button('Buat pengurus'):action(s.create_manager,me['id'],un,pw,nm,uid)
    us=s.users(me['id']);st.dataframe(pd.DataFrame(us),hide_index=True)
    st.download_button('Unduh data akun tanpa password',csv_data(us),'akun_nemu.csv','text/csv')
    selection=st.selectbox('Pilih akun untuk dikelola',[u['id'] for u in us],format_func=lambda i:next(u['username'] for u in us if u['id']==i))
    u=next(u for u in us if u['id']==selection)
    active=st.checkbox('Akun aktif',bool(u['aktif']))
    if st.button('Simpan status akun'):action(s.set_user_active,me['id'],selection,active)
    with st.form('reset_pw'):
        pw=st.text_input('Password pengganti',type='password')
        if st.form_submit_button('Reset password akun terpilih'):action(s.reset_password,me['id'],selection,pw)
def settings(me):
    st.header('Pengaturan rekomendasi dan periode');cfg=s.config(me['id'])
    with st.form('settings'):
        weights={k:st.number_input('Bobot '+k+' (%)',0,100,int(v)) for k,v in cfg['bobot'].items()}
        st.write('Total bobot:',sum(weights.values()),'%');period=st.text_input('Periode pendaftaran',cfg['periode']);opened=st.checkbox('Pendaftaran dibuka',cfg['pendaftaran_buka'])
        st.caption('Mengubah periode membuka dua pilihan baru untuk mahasiswa. Riwayat periode sebelumnya tetap ada. Jangan mengubah periode hanya untuk mengganti tulisan.')
        if st.form_submit_button('Simpan pengaturan',type='primary'):action(s.update_config,me['id'],weights,period,opened)
    st.caption('Rekomendasi lama menyimpan bobot dan profil saat dihitung. Mahasiswa dapat menekan Perbarui rekomendasi setelah kriteria berubah.')
    with st.expander('Pemeliharaan aplikasi'):
        from backend.db import mode
        if mode()=='sqlite':
            if st.checkbox('Tampilkan alat backup dan pemindahan',key='show_maintenance'):
                from .backup_view import render_backup
                render_backup(me)
        else:st.caption('Cadangan data dikelola melalui layanan penyimpanan oleh administrator.')

def admin_recommendations(me):
    st.header('Riwayat rekomendasi mahasiswa');rows=s.recommendations_admin(me['id'])
    if not rows:st.info('Belum ada perhitungan rekomendasi.');return
    for r in rows:
        with st.expander(f"{r['nama']} · {r['created_at']}"):
            data=json.loads(r['hasil']);st.write('Bobot:',json.loads(r['bobot']))
            st.dataframe(pd.DataFrame([{'UKM':x['nama'],'Skor':x['skor'],'Cakupan bobot':x['cakupan_bobot']} for x in data]),hide_index=True)
def account(me):
    st.header('Keamanan akun')
    with st.form('password'):
        old=st.text_input('Password lama',type='password');new=st.text_input('Password baru',type='password');repeat=st.text_input('Ulangi password baru',type='password')
        if st.form_submit_button('Ganti password'):
            if new!=repeat:st.error('Password baru tidak sama.')
            else:action(auth.change_password,me['id'],old,new)
