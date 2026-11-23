"""SQLite kayit katmani. Tek dosya: sinyaller.db"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import pandas as pd

import config

SEMA = """
CREATE TABLE IF NOT EXISTS sinyaller (
    msg_id     INTEGER PRIMARY KEY,
    time_utc   TEXT NOT NULL,
    ticker     TEXT NOT NULL,
    entry      REAL NOT NULL,
    stop       REAL NOT NULL,
    tp1        REAL NOT NULL,
    tp2        REAL,
    raw        TEXT,
    duzenlendi TEXT,          -- kanal mesaji sonradan degistirdiyse zamani
    ilk_hali   TEXT,          -- degistirilmeden onceki ham mesaj
    silindi    INTEGER DEFAULT 0,
    kayit_utc  TEXT
);
CREATE TABLE IF NOT EXISTS durum (anahtar TEXT PRIMARY KEY, deger TEXT);
"""


@contextmanager
def baglan(path=None):
    con = sqlite3.connect(path or config.DB_PATH)
    try:
        con.executescript(SEMA)
        yield con
        con.commit()
    finally:
        con.close()


def kaydet(msg_id, dt, sig, raw, path=None) -> bool:
    """Yeni sinyal ise True doner."""
    with baglan(path) as con:
        if con.execute("SELECT 1 FROM sinyaller WHERE msg_id=?", (msg_id,)).fetchone():
            return False
        con.execute(
            "INSERT INTO sinyaller(msg_id,time_utc,ticker,entry,stop,tp1,tp2,raw,kayit_utc) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (msg_id, dt.astimezone(timezone.utc).isoformat(), sig.ticker, sig.entry, sig.stop,
             sig.tp1, sig.tp2, raw, datetime.now(timezone.utc).isoformat()))
        return True


def duzenleme(msg_id, yeni_sig, raw, path=None):
    """Kanal mesaji duzenlediyse: ILK HALI korunur (test ilk hale gore yapilir), degisiklik not edilir."""
    with baglan(path) as con:
        row = con.execute("SELECT raw, duzenlendi FROM sinyaller WHERE msg_id=?", (msg_id,)).fetchone()
        if not row:
            return False
        if row[0] == raw:
            return False
        con.execute("UPDATE sinyaller SET duzenlendi=?, ilk_hali=COALESCE(ilk_hali, raw) WHERE msg_id=?",
                    (datetime.now(timezone.utc).isoformat(), msg_id))
        return True


def silindi_isaretle(msg_ids, path=None):
    with baglan(path) as con:
        con.executemany("UPDATE sinyaller SET silindi=1 WHERE msg_id=?", [(i,) for i in msg_ids])
        return con.total_changes


def hepsi(path=None) -> pd.DataFrame:
    with baglan(path) as con:
        df = pd.read_sql_query("SELECT * FROM sinyaller ORDER BY time_utc", con)
    if not df.empty:
        df["time_utc"] = pd.to_datetime(df.time_utc, utc=True)
    return df


def durum_al(k, path=None):
    with baglan(path) as con:
        r = con.execute("SELECT deger FROM durum WHERE anahtar=?", (k,)).fetchone()
        return r[0] if r else None


def durum_yaz(k, v, path=None):
    with baglan(path) as con:
        con.execute("INSERT OR REPLACE INTO durum VALUES(?,?)", (k, v))
