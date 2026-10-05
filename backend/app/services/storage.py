import json,sqlite3
from pathlib import Path
DB=Path(__file__).resolve().parents[2]/'tendermate.db'
def init_db():
    with sqlite3.connect(DB) as c: c.execute('create table if not exists tenders(id integer primary key autoincrement,filename text,reference text,title text,closing_date text,closing_time text,quantity text,created_at text default current_timestamp,payload text not null)')
def save_tender(p):
    s=p.get('summary',{}); vals=(p.get('filename'),s.get('reference_number',{}).get('value'),s.get('tender_title',{}).get('value'),s.get('closing_date',{}).get('value'),s.get('closing_time',{}).get('value'),s.get('quantity',{}).get('value'),json.dumps(p))
    with sqlite3.connect(DB) as c: return c.execute('insert into tenders(filename,reference,title,closing_date,closing_time,quantity,payload) values(?,?,?,?,?,?,?)',vals).lastrowid
def list_tenders():
    with sqlite3.connect(DB) as c: rows=c.execute('select id,filename,reference,title,closing_date,closing_time,quantity,created_at from tenders order by id desc').fetchall()
    return [dict(zip(['id','filename','reference','title','closing_date','closing_time','quantity','created_at'],r)) for r in rows]
def get_tender(i):
    with sqlite3.connect(DB) as c: row=c.execute('select payload from tenders where id=?',(i,)).fetchone()
    return json.loads(row[0]) if row else None
