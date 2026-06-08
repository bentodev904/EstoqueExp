from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3, uuid, time, os

app = FastAPI(title="Clínica Estoque API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "estoque.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '🧸',
                category TEXT DEFAULT 'outro',
                quantity INTEGER DEFAULT 1,
                location TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at INTEGER
            );
            CREATE TABLE IF NOT EXISTS loans (
                id TEXT PRIMARY KEY,
                item_id TEXT NOT NULL,
                person TEXT NOT NULL,
                staff TEXT DEFAULT '',
                due_at TEXT,
                loaned_at INTEGER,
                returned_at INTEGER,
                FOREIGN KEY (item_id) REFERENCES items(id)
            );
        """)

init_db()

# ── MODELS ──
class ItemIn(BaseModel):
    name: str
    emoji: str = '🧸'
    category: str = 'outro'
    quantity: int = 1
    location: str = ''
    notes: str = ''

class LoanIn(BaseModel):
    item_id: str
    person: str
    staff: str = ''
    due_at: Optional[str] = None

# ── ITEMS ──
@app.get("/api/items")
def list_items():
    with get_db() as db:
        rows = db.execute("SELECT * FROM items ORDER BY name").fetchall()
        return [dict(r) for r in rows]

@app.post("/api/items", status_code=201)
def create_item(body: ItemIn):
    item_id = str(uuid.uuid4())[:8]
    with get_db() as db:
        db.execute(
            "INSERT INTO items VALUES (?,?,?,?,?,?,?,?)",
            (item_id, body.name, body.emoji, body.category,
             body.quantity, body.location, body.notes, int(time.time()))
        )
    return {"id": item_id, **body.dict()}

@app.put("/api/items/{item_id}")
def update_item(item_id: str, body: ItemIn):
    with get_db() as db:
        r = db.execute("SELECT id FROM items WHERE id=?", (item_id,)).fetchone()
        if not r:
            raise HTTPException(404, "Item não encontrado")
        db.execute(
            "UPDATE items SET name=?,emoji=?,category=?,quantity=?,location=?,notes=? WHERE id=?",
            (body.name, body.emoji, body.category, body.quantity,
             body.location, body.notes, item_id)
        )
    return {"id": item_id, **body.dict()}

@app.delete("/api/items/{item_id}")
def delete_item(item_id: str):
    with get_db() as db:
        db.execute("DELETE FROM loans WHERE item_id=?", (item_id,))
        db.execute("DELETE FROM items WHERE id=?", (item_id,))
    return {"ok": True}

# ── LOANS ──
@app.get("/api/loans")
def list_loans(active_only: bool = False):
    with get_db() as db:
        q = "SELECT * FROM loans"
        if active_only:
            q += " WHERE returned_at IS NULL"
        q += " ORDER BY loaned_at DESC"
        return [dict(r) for r in db.execute(q).fetchall()]

@app.post("/api/loans", status_code=201)
def create_loan(body: LoanIn):
    with get_db() as db:
        item = db.execute("SELECT * FROM items WHERE id=?", (body.item_id,)).fetchone()
        if not item:
            raise HTTPException(404, "Item não encontrado")
        active = db.execute(
            "SELECT COUNT(*) as c FROM loans WHERE item_id=? AND returned_at IS NULL",
            (body.item_id,)
        ).fetchone()["c"]
        if active >= item["quantity"]:
            raise HTTPException(400, "Sem unidades disponíveis")
        loan_id = str(uuid.uuid4())[:8]
        db.execute(
            "INSERT INTO loans VALUES (?,?,?,?,?,?,?)",
            (loan_id, body.item_id, body.person, body.staff,
             body.due_at, int(time.time()), None)
        )
    return {"id": loan_id, **body.dict()}

@app.post("/api/loans/{loan_id}/return")
def return_loan(loan_id: str):
    with get_db() as db:
        r = db.execute("SELECT id FROM loans WHERE id=?", (loan_id,)).fetchone()
        if not r:
            raise HTTPException(404, "Empréstimo não encontrado")
        db.execute(
            "UPDATE loans SET returned_at=? WHERE id=?",
            (int(time.time()), loan_id)
        )
    return {"ok": True}

# ── SERVE FRONTEND (se existir) ──
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
