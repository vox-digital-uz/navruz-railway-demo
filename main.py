import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "buyurtmalar.db"


def db_init():
    conn = sqlite3.connect(DB)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS buyurtmalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT NOT NULL,
            telefon TEXT NOT NULL,
            mahsulot TEXT NOT NULL,
            miqdor TEXT NOT NULL,
            vaqt TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


db_init()


class Buyurtma(BaseModel):
    ism: str
    telefon: str
    mahsulot: str
    miqdor: str


@app.get("/")
def home():
    return {"salom": "Sut mahsulotlari buyurtma API ishlayapti"}


@app.post("/buyurtma")
def buyurtma_qabul(b: Buyurtma):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO buyurtmalar (ism, telefon, mahsulot, miqdor, vaqt) VALUES (?,?,?,?,?)",
        (b.ism, b.telefon, b.mahsulot, b.miqdor, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return {"holat": "qabul qilindi", "ism": b.ism}


@app.get("/admin")
def admin_royxat():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT id, ism, telefon, mahsulot, miqdor, vaqt FROM buyurtmalar ORDER BY id DESC"
    ).fetchall()
    conn.close()
    satrlar = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"
        for r in rows
    )
    html = f"""<html><head><meta charset="utf-8"><title>Buyurtmalar</title>
    <style>
    body{{font-family:Arial;padding:24px;background:#fff8ef;}}
    table{{border-collapse:collapse;width:100%;background:#fff;}}
    th,td{{border:1px solid #ddd;padding:10px;text-align:left;}}
    th{{background:#e8a33d;color:#fff;}}
    h1{{color:#5a3e2b;}}
    </style></head><body>
    <h1>Buyurtmalar ro'yxati ({len(rows)} ta)</h1>
    <table><tr><th>ID</th><th>Ism</th><th>Telefon</th><th>Mahsulot</th><th>Miqdor</th><th>Vaqt</th></tr>
    {satrlar}
    </table></body></html>"""
    return HTMLResponse(html)
