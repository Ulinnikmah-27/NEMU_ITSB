"""PostgreSQL driver. SQL values remain bound parameters, never concatenated."""
import re,sqlite3
import psycopg
from psycopg.rows import dict_row
class Record(dict):
    def __getitem__(self,key):return list(self.values())[key] if isinstance(key,int) else super().__getitem__(key)
class Result:
    def __init__(self,cursor,lastrowid=None):self.cursor=cursor;self.lastrowid=lastrowid
    def fetchone(self):
        row=self.cursor.fetchone();return Record(row) if row is not None else None
    def fetchall(self):return [Record(row) for row in self.cursor.fetchall()]
    def __iter__(self):
        for row in self.cursor:yield Record(row)
class Connection:
    is_postgres=True
    def __init__(self,raw,write=False):self.raw=raw;self.write=write
    def execute(self,sql,args=()):
        # Compatibility is deliberately limited to the SQL statements used by NEMU.
        sql=sql.strip().rstrip(';')
        if sql.upper()=='BEGIN':
            return Result(self.raw.execute('SELECT 1')) # transaction already opened by connect()
        if sql.startswith('INSERT OR REPLACE INTO login_attempts'):
            sql='INSERT INTO login_attempts(username,attempts,locked_until) VALUES(?,?,?) ON CONFLICT(username) DO UPDATE SET attempts=EXCLUDED.attempts,locked_until=EXCLUDED.locked_until'
        elif sql.startswith('INSERT OR REPLACE INTO assets'):
            sql='INSERT INTO assets(key,data,mime) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET data=EXCLUDED.data,mime=EXCLUDED.mime'
        elif sql.startswith('INSERT OR IGNORE INTO settings'):
            sql='INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO NOTHING'
        inserted=bool(re.match(r'INSERT INTO (users|ukm|kuesioner|rekomendasi|pendaftaran|hasil_seleksi)\b',sql,re.I)) and 'RETURNING' not in sql.upper()
        if inserted:sql+=' RETURNING id'
        if args:sql=sql.replace('%','%%').replace('?','%s')
        try:
            cur=self.raw.execute(sql,args or None)
            return Result(cur,cur.fetchone()['id'] if inserted else None)
        except psycopg.IntegrityError:raise sqlite3.IntegrityError('Data tidak memenuhi aturan database.') from None
