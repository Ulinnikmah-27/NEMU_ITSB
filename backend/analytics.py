"""Analisis deskriptif; setiap hasil dibatasi role dan periode di sisi backend."""
import json
from collections import Counter
from datetime import datetime,timedelta,timezone
from .db import connect,setting,club
from .auth import require
from .constants import normalize_prodi
WIB=timezone(timedelta(hours=7))
STATUS=['Menunggu','Diterima','Ditolak']
def rows(counter,key):
    return [{key:k,'Jumlah':v} for k,v in sorted(counter.items(),key=lambda item:(-item[1],str(item[0])))]
def describe_counts(values,key,total,label):
    """Menyebut semua pemenang seri; total adalah denominator eksplisit."""
    if not values or total==0:return f'Belum ada data {label} untuk dianalisis.'
    n=max(r['Jumlah'] for r in values);leaders=[str(r[key]) for r in values if r['Jumlah']==n]
    lead=', '.join(leaders[:4])+ (f' dan {len(leaders)-4} kategori lain' if len(leaders)>4 else '')
    each='masing-masing ' if len(leaders)>1 else ''
    return f"{lead} {'sama-sama ' if len(leaders)>1 else ''}memiliki jumlah tertinggi: {each}{n} dari {total} {label} ({100*n/total:.1f}%)."
def summary(actor):
    with connect() as c:
        c.raw.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ') if getattr(c,'is_postgres',False) else c.execute('BEGIN')
        user=require(c,actor,['admin','pengurus','mahasiswa']);role=user['role'];period=setting(c,'periode')
        base='''SELECT p.*,u.nama mahasiswa,u.prodi,k.nama ukm,r.kuesioner_id,q.jawaban
                FROM pendaftaran p JOIN users u ON u.id=p.user_id JOIN ukm k ON k.id=p.ukm_id
                JOIN rekomendasi r ON r.id=p.rekomendasi_id JOIN kuesioner q ON q.id=r.kuesioner_id
                WHERE p.periode=?'''
        args=[period]
        if role=='mahasiswa':base+=' AND p.user_id=?';args.append(actor)
        if role=='pengurus':base+=' AND p.ukm_id=?';args.append(user['ukm_id'])
        allregs=[dict(r) for r in c.execute(base,args)];regs=[r for r in allregs if r['status']!='Dibatalkan']
        unique={}
        for r in sorted(regs,key=lambda r:r['id']):unique[r['user_id']]=r
        counts=Counter(r['status'] for r in regs)
        prodi=Counter(normalize_prodi(r['prodi']) or r['prodi'] or 'Belum diisi' for r in unique.values())
        interests=Counter(x for r in unique.values() for x in set(json.loads(r['jawaban']).get('minat',[])))
        demand=Counter(r['ukm'] for r in regs);accepted=Counter(r['ukm'] for r in regs if r['status']=='Diterima')
        daily=Counter(datetime.fromisoformat(r['created_at']).astimezone(WIB).date().isoformat() for r in regs)
        timeline=[]
        if daily:
            day=datetime.fromisoformat(min(daily));last=datetime.fromisoformat(max(daily))
            while day<=last:
                key=day.date().isoformat();timeline.append({'Tanggal':key,'Jumlah':daily[key]});day+=timedelta(days=1)
        n=len(regs);decided=counts['Diterima']+counts['Ditolak'];accepted_n=counts['Diterima']
        result={'role':role,'periode':period,'pendaftaran':n,'mahasiswa':len(unique),'dibatalkan':len(allregs)-n,
                'status':[{'Status':x,'Jumlah':counts[x]} for x in STATUS],
                'prodi':rows(prodi,'Program studi'),'minat':rows(interests,'Minat'),
                'ukm':[{'UKM':name,'Pendaftar':num,'Diterima':accepted[name]} for name,num in sorted(demand.items(),key=lambda x:(-x[1],x[0]))],
                'harian':timeline,'diputuskan':decided,'diterima':accepted_n,'menunggu':counts['Menunggu'],
                'persen_diterima_dari_keputusan':round(100*accepted_n/decided,1) if decided else None,
                'narasi_status':f"Dari {n} pendaftaran, {counts['Menunggu']} masih menunggu, {accepted_n} diterima, dan {counts['Ditolak']} ditolak. "+(f"Sebanyak {100*accepted_n/decided:.1f}% dari {decided} pendaftaran yang sudah mendapat keputusan diterima." if decided else 'Belum ada keputusan seleksi, sehingga persentase penerimaan belum dapat dihitung.')}
        result['narasi_prodi']=describe_counts(result['prodi'],'Program studi',len(unique),'mahasiswa pendaftar unik')
        result['narasi_minat']=describe_counts(result['minat'],'Minat',len(unique),'mahasiswa pendaftar unik')+' Satu mahasiswa dapat memilih beberapa minat; persentasenya tidak harus berjumlah 100%.'
        result['narasi_ukm']=describe_counts([{'UKM':x['UKM'],'Jumlah':x['Pendaftar']} for x in result['ukm']],'UKM',n,'pendaftaran')+' Satu mahasiswa dapat mendaftar ke dua UKM; jumlah ini bukan jumlah mahasiswa unik.'
        result['narasi_harian']=describe_counts([{'Tanggal':x['Tanggal'],'Jumlah':x['Jumlah']} for x in timeline],'Tanggal',n,'pendaftaran')+' Tanggal menggunakan WIB. Ini pola pendaftaran yang tercatat, bukan prediksi.'
        if role=='pengurus':
            u=c.execute('SELECT * FROM ukm WHERE id=?',(user['ukm_id'],)).fetchone();p=club(u)
            result['ukm_nama']=p['nama'];result['kuota']=p.get('kuota')
            result['kursi_terpakai']=sum(r['status']=='Diterima' and r['konfirmasi']!='Dilepas' for r in regs)
        if role=='mahasiswa':
            rec=c.execute('SELECT * FROM rekomendasi WHERE user_id=? ORDER BY id DESC LIMIT 1',(actor,)).fetchone()
            result['rekomendasi']={'hasil':json.loads(rec['hasil']),'created_at':rec['created_at'],'bobot':json.loads(rec['bobot'])} if rec else None
            # Hanya skor milik pengguna, profil saat perhitungan dipertahankan.
            result['pilihan']=[{'UKM':r['ukm'],'Skor':r['skor'],'Status':r['status'],'Konfirmasi':r['konfirmasi']} for r in regs]
        return result
