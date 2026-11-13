"""Grafik interaktif dan interpretasi yang hanya menggunakan angka dari data aktual."""
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from backend.analytics import summary
COLORS=['#8174c8','#79b9cf','#e5b178','#8bbfa8','#ce9cbb']
LABELS={'minat':'Minat','bakat':'Bakat','kemampuan':'Kemampuan','preferensi':'Preferensi','komitmen':'Komitmen'}
def plot(frame,x,y,title,horizontal=False):
    fig=px.bar(frame,x=x,y=y,orientation='h' if horizontal else 'v',color_discrete_sequence=COLORS,text_auto=True,title=title)
    fig.update_layout(height=max(330,len(frame)*35+130) if horizontal else 340,margin=dict(l=10,r=15,t=60,b=20),paper_bgcolor='rgba(0,0,0,0)',showlegend=False)
    if horizontal:fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig,use_container_width=True)
def recommendation_text(data):
    if not data:return 'Belum ada hasil rekomendasi. Isi kuesioner terlebih dahulu.'
    best=max(r['skor'] for r in data);leaders=[r['nama'] for r in data if r['skor']==best]
    names=', '.join(leaders[:3])+(f' dan {len(leaders)-3} UKM lain' if len(leaders)>3 else '')
    return f"{names} {'sama-sama ' if len(leaders)>1 else ''}memiliki skor tertinggi, yaitu {best:.1f}%. Selisih skor tertinggi dan terendah adalah {best-min(r['skor'] for r in data):.1f} poin. Skor menunjukkan kecocokan profil, bukan peluang diterima atau syarat kelulusan seleksi."
def personal(d):
    rec=d['rekomendasi']
    if rec and rec['hasil']:
        data=rec['hasil'];st.subheader('1. UKM yang paling sesuai dengan profilmu')
        plot(pd.DataFrame([{'UKM':r['nama'],'Skor kecocokan (%)':r['skor']} for r in data[:5]]),'Skor kecocokan (%)','UKM','Lima rekomendasi tertinggi',True)
        st.write('**Analisis:** '+recommendation_text(data))
        st.caption('Hasil disimpan saat '+rec['created_at']+' (UTC). Profil yang berubah setelah waktu ini belum tercermin; gunakan Perbarui rekomendasi di menu Rekomendasi.')
        names={r['ukm_id']:r for r in data}
        selected=st.selectbox('Analisis komponen UKM',list(names),format_func=lambda k:names[k]['nama'],key='analytics_personal_ukm')
        r=names[selected];comp=[{'Komponen':LABELS.get(k,k),'Skor (%)':v} for k,v in r['komponen'].items() if v is not None]
        if comp:
            plot(pd.DataFrame(comp),'Komponen','Skor (%)','Rincian kecocokan '+r['nama'])
            highest=max(x['Skor (%)'] for x in comp);lowest=min(x['Skor (%)'] for x in comp)
            high=', '.join(x['Komponen'] for x in comp if x['Skor (%)']==highest);low=', '.join(x['Komponen'] for x in comp if x['Skor (%)']==lowest)
            text=f"Komponen dengan nilai tertinggi: {high} ({highest:.1f}%). "
            text+=f"Komponen dengan nilai terendah: {low} ({lowest:.1f}%)." if lowest!=highest else 'Semua komponen yang dapat dinilai memiliki nilai yang sama.'
            st.write('**Analisis:** '+text+' Nilai komponen menunjukkan kecocokan terhadap profil UKM, bukan ukuran kemampuan akademikmu.')
            st.write(f"Cakupan bobot yang dapat dinilai: {r['cakupan_bobot']}%. Komponen UKM yang belum diketahui tidak dihitung.")
            for note in r['catatan']:st.caption(note)
    else:st.info('Isi kuesioner terlebih dahulu agar grafik dan analisis kecocokanmu muncul.')
    st.subheader('Status pilihanmu pada periode ini')
    if d['pendaftaran']:
        plot(pd.DataFrame(d['status']),'Status','Jumlah','Status pendaftaran UKM milikmu')
        st.write('**Analisis:** '+d['narasi_status']);st.dataframe(pd.DataFrame(d['pilihan']),hide_index=True)
        st.caption('Persentase hanya merangkum keputusan yang sudah ada dan bukan prediksi hasil pilihan lain.')
    else:st.info('Belum ada pendaftaran yang tidak dibatalkan pada periode ini. Pilih UKM melalui menu Pendaftaran.')

def render_analytics(me,compact=False):
    d=summary(me['id'])
    st.header('Grafik dan analisis' if not compact else 'Ringkasan grafik dan analisis')
    if d['role']=='mahasiswa':
        st.caption('Analisis pribadi · hanya menggunakan rekomendasi dan pendaftaran akunmu · periode '+d['periode'])
        personal(d);return
    scope='Seluruh UKM' if d['role']=='admin' else d['ukm_nama']
    st.caption(scope+' · periode '+d['periode']+' · data diperbarui saat halaman dijalankan ulang')
    cols=st.columns(4);cols[0].metric('Mahasiswa pendaftar unik',d['mahasiswa']);cols[1].metric('Pendaftaran',d['pendaftaran']);cols[2].metric('Menunggu',d['menunggu']);cols[3].metric('Diterima',d['diterima'])
    st.caption(f"{d['dibatalkan']} pendaftaran dibatalkan dikeluarkan dari grafik. Pendaftaran berarti pilihan mahasiswa ke satu UKM; satu mahasiswa bisa punya dua pilihan.")
    if not d['pendaftaran']:
        st.info('Belum ada pendaftaran yang tidak dibatalkan untuk cakupan dan periode ini. Grafik dan analisis akan muncul setelah mahasiswa mendaftar. Tidak ada data contoh yang dicampur ke hasil.')
        return
    st.subheader('1. Proses seleksi')
    plot(pd.DataFrame(d['status']),'Status','Jumlah','Jumlah pendaftaran menurut status')
    st.write('**Analisis:** '+d['narasi_status'])
    if d['menunggu']:st.write(f"**Tindak lanjut:** tinjau {d['menunggu']} pendaftaran yang masih menunggu sesuai jadwal seleksi UKM.")
    if d['role']=='admin':
        st.subheader('2. Pendaftaran dan penerimaan setiap UKM')
        frame=pd.DataFrame(d['ukm']).melt(id_vars='UKM',var_name='Keterangan',value_name='Jumlah')
        fig=px.bar(frame,x='Jumlah',y='UKM',color='Keterangan',orientation='h',barmode='group',color_discrete_sequence=COLORS[:2],text_auto=True)
        fig.update_layout(height=max(380,len(d['ukm'])*48+130),legend_title_text='',margin=dict(l=10,r=15,t=30,b=20));fig.update_yaxes(autorange='reversed')
        st.plotly_chart(fig,use_container_width=True);st.write('**Analisis:** '+d['narasi_ukm'])
        st.caption('Grafik memuat UKM yang sudah memiliki pendaftaran pada periode ini. Diterima adalah bagian dari pendaftar, sehingga kedua seri tidak dijumlahkan.')
    else:
        if d['kuota'] is None:st.info('Kuota UKM belum dikonfirmasi, sehingga persentase keterisian kuota belum dihitung.')
        else:
            remaining=max(0,d['kuota']-d['kursi_terpakai'])
            plot(pd.DataFrame([{'Kursi':'Terpakai','Jumlah':d['kursi_terpakai']},{'Kursi':'Tersisa','Jumlah':remaining}]),'Kursi','Jumlah','Pemakaian kuota UKM')
            st.write(f"**Analisis kuota:** {d['kursi_terpakai']} dari {d['kuota']} kursi terpakai ({100*d['kursi_terpakai']/d['kuota']:.1f}%). Mahasiswa yang sudah melepas tawaran tidak dihitung sebagai kursi terpakai.")
    st.subheader('3. Program studi mahasiswa pendaftar')
    plot(pd.DataFrame(d['prodi']),'Jumlah','Program studi','Sebaran mahasiswa pendaftar unik menurut prodi',True)
    st.write('**Analisis:** '+d['narasi_prodi'])
    st.caption('Jumlah ini tidak menunjukkan tingkat partisipasi seluruh prodi karena jumlah populasi mahasiswa per prodi belum dimasukkan.')
    st.subheader('4. Minat mahasiswa pendaftar')
    plot(pd.DataFrame(d['minat']),'Jumlah','Minat','Minat yang dipilih mahasiswa pendaftar unik',True)
    st.write('**Analisis:** '+d['narasi_minat'])
    st.caption('Menggunakan jawaban pada rekomendasi yang dipakai saat pendaftaran terakhir mahasiswa pada periode ini. Bukan semua akun mahasiswa kampus.')
    st.subheader('5. Waktu pendaftaran')
    daily=pd.DataFrame(d['harian'])
    plot(daily,'Tanggal','Jumlah','Jumlah pendaftaran per hari (WIB)')
    st.write('**Analisis:** '+d['narasi_harian'])
    with st.expander('Lihat data ringkasan untuk laporan'):
        st.dataframe(pd.DataFrame(d['ukm']),hide_index=True)
        # Ekspor agregat, tidak memuat identitas mahasiswa.
        from .views import csv_data
        st.download_button('Unduh ringkasan UKM CSV',csv_data(d['ukm']),'analisis_ukm_nemu.csv','text/csv')
    st.caption('Analisis ini deskriptif: merangkum angka yang tersimpan. Tidak menyimpulkan penyebab, memprediksi penerimaan, atau menilai mutu UKM.')
