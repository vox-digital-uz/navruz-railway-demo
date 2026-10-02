import logging
import sqlite3
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("buyurtma")

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
    conn.execute(
        """CREATE TABLE IF NOT EXISTS arizalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT NOT NULL,
            telefon TEXT NOT NULL,
            tajriba TEXT NOT NULL,
            vaqt TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


db_init()


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    log.info("422 VALIDATION FAIL | body=%r | errors=%s", body, exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "xom_body": body.decode(errors="replace")})


@app.get("/")
def home():
    return {"salom": "Sut mahsulotlari buyurtma API ishlayapti"}


@app.post("/buyurtma")
async def buyurtma_qabul(request: Request):
    data = await request.json()
    ism = str(data.get("ism", "")).strip()
    telefon = str(data.get("telefon", "")).strip()
    mahsulot = str(data.get("mahsulot", "")).strip()
    miqdor = str(data.get("miqdor", "")).strip()
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO buyurtmalar (ism, telefon, mahsulot, miqdor, vaqt) VALUES (?,?,?,?,?)",
        (ism, telefon, mahsulot, miqdor, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return {"holat": "qabul qilindi", "ism": ism}


@app.post("/ariza")
async def ariza_qabul(request: Request):
    data = await request.json()
    ism = str(data.get("ism", "")).strip()
    telefon = str(data.get("telefon", "")).strip()
    tajriba = str(data.get("tajriba", "")).strip()
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO arizalar (ism, telefon, tajriba, vaqt) VALUES (?,?,?,?)",
        (ism, telefon, tajriba, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return {"holat": "qabul qilindi", "ism": ism}


@app.get("/admin-ariza")
def admin_ariza_royxat():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT id, ism, telefon, tajriba, vaqt FROM arizalar ORDER BY id DESC"
    ).fetchall()
    conn.close()
    satrlar = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
        for r in rows
    )
    html = f"""<html><head><meta charset="utf-8"><title>Arizalar</title>
    <style>
    body{{font-family:Arial;padding:24px;background:#fdf6ec;}}
    table{{border-collapse:collapse;width:100%;background:#fff;}}
    th,td{{border:1px solid #ddd;padding:10px;text-align:left;}}
    th{{background:#f5a623;color:#1f2833;}}
    h1{{color:#1f2833;}}
    </style></head><body>
    <h1>Avtomexanik arizalari ({len(rows)} ta)</h1>
    <table><tr><th>ID</th><th>Ism</th><th>Telefon</th><th>Tajriba</th><th>Vaqt</th></tr>
    {satrlar}
    </table></body></html>"""
    return HTMLResponse(html)


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
