import sqlite3
from pathlib import Path
DB_PATH=Path("ap_audit.db")
def connect():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; return conn
def init_db():
    conn=connect(); conn.execute("""CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT,vendor TEXT NOT NULL,invoice_number TEXT NOT NULL,invoice_date TEXT,description TEXT,quantity REAL DEFAULT 1,unit_price REAL DEFAULT 0,total REAL DEFAULT 0,paid INTEGER DEFAULT 1)"""); conn.commit(); conn.close()
def add_transaction(data):
    conn=connect(); cur=conn.execute("INSERT INTO transactions(vendor,invoice_number,invoice_date,description,quantity,unit_price,total,paid) VALUES(?,?,?,?,?,?,?,?)",(data["vendor"],data["invoice_number"],data.get("invoice_date"),data.get("description",""),data.get("quantity",1),data.get("unit_price",0),data.get("total",0),data.get("paid",1))); conn.commit(); row=conn.execute("SELECT * FROM transactions WHERE id=?",(cur.lastrowid,)).fetchone(); conn.close(); return dict(row)
def all_transactions():
    conn=connect(); rows=[dict(r) for r in conn.execute("SELECT * FROM transactions ORDER BY id DESC")]; conn.close(); return rows
def find_invoice(vendor,invoice_number):
    conn=connect(); row=conn.execute("SELECT * FROM transactions WHERE lower(vendor)=lower(?) AND lower(invoice_number)=lower(?) LIMIT 1",(vendor,invoice_number)).fetchone(); conn.close(); return dict(row) if row else None
def vendor_prices(vendor,description):
    conn=connect(); rows=conn.execute("SELECT unit_price FROM transactions WHERE lower(vendor)=lower(?) AND lower(description) LIKE ? AND unit_price>0",(vendor,"%"+description.lower()+"%")).fetchall(); conn.close(); return [float(r["unit_price"]) for r in rows]
