"""python tests/test_hepsi.py  -> tum testler (internet gerekmez)"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from sinyal_parser import parse_signal
from simulate import bot_gozu, kanal_gozu, Ayar

NY = "America/New_York"
IDX = pd.date_range("2026-11-20 04:10", periods=10, freq="min", tz=NY)
def B(rows):
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close", "Volume"], index=IDX[:len(rows)])
SIG = {"entry": 0.80, "stop": 0.74, "tp1": 0.86, "tp2": 0.89}
ok = 0

def check(ad, kosul):
    global ok
    assert kosul, ad
    ok += 1
    print("  ✓", ad)

print("Parser")
s = parse_signal("RAYA\nKIRILIM: 0.8\nSTOP: 0.74\nTP1: 0.86\nTP2: 0.89")
check("kanal formati", s and s.ticker == "RAYA" and s.entry == 0.8 and s.tp2 == 0.89)
s = parse_signal("🚨🚨\n$GMM\nKırılım: 3,00\nStop: 2.80\nTP1: 3.50")
check("$ + virgul + TP2'siz", s and s.ticker == "GMM" and s.entry == 3.0 and s.tp2 is None)
check("sus mesaji yok sayilir", parse_signal("RAYA UCUSLARDAA") is None)
check("kar alma mesaji yok sayilir", parse_signal("raya kar aliyorum") is None)
check("haftalik ozet sinyal sanilmaz", parse_signal("$CLRO — Giriş $4.90 (04:07) → TP1 $5.10") is None)
check("mantiksiz seviye reddedilir", parse_signal("ABC\nKIRILIM: 1\nSTOP: 1.2\nTP1: 1.1") is None)

print("Simulasyon")
kazanc = B([[0.78, .81, .77, .80, 9e3], [.80, .84, .79, .83, 9e3], [.83, .87, .82, .86, 9e3], [.86, .90, .85, .89, 9e3]])
r = bot_gozu(SIG, kazanc, "tp1")
check("TP1 kazanci kayma+komisyonla ~%5", r["sonuc"] == "TP1" and 0.045 < r["getiri"] < 0.055)
r = bot_gozu(SIG, kazanc, "kademeli")
check("kademeli TP1+TP2", r["sonuc"] == "TP1+TP2" and r["getiri"] > 0.06)
stop = B([[.79, .81, .78, .80, 9e3], [.80, .82, .76, .77, 9e3], [.77, .77, .70, .71, 9e3]])
r = bot_gozu(SIG, stop, "tp1")
check("stop zarari ~%-9.5", r["sonuc"] == "STOP" and -0.10 < r["getiri"] < -0.09)
kacti = B([[.88, .92, .87, .90, 9e3]])
check("bosluklu acilis -> kacti", bot_gozu(SIG, kacti)["durum"] == "kacti")
check("kanal ise bunu TP sayar", kanal_gozu(SIG, kacti)["kanal_sonuc"].startswith("TP"))
ayni = B([[.79, .81, .78, .80, 9e3], [.80, .87, .73, .80, 9e3]])
check("ayni mumda stop+TP -> STOP (en kotu)", bot_gozu(SIG, ayni)["sonuc"] == "STOP")
check("gecikme: 1 dk gec kalan bot kacirir",
      bot_gozu(SIG, B([[.79, .805, .78, .80, 9e3], [.85, .90, .84, .89, 9e3]]), a=Ayar(gecikme_dk=1))["durum"] == "kacti")
dusus = B([[.79, .81, .78, .80, 9e3], [.80, .82, .79, .81, 9e3], [.72, .73, .70, .71, 9e3]])
r = bot_gozu(SIG, dusus)
check("bosluklu dusus stop'tan asagida dolar", r["getiri"] < -0.10)
gun = B([[.79, .81, .78, .80, 9e3], [.80, .82, .79, .81, 9e3]])
check("gun sonu kapanis", bot_gozu(SIG, gun)["sonuc"] == "gun_sonu")

print("Veritabani")
import db
yol = os.path.join(tempfile.mkdtemp(), "t.db")
s = parse_signal("RAYA\nKIRILIM: 0.8\nSTOP: 0.74\nTP1: 0.86")
t = pd.Timestamp("2026-11-20 09:10", tz="UTC")
check("kaydet yeni", db.kaydet(1, t, s, "ham", yol))
check("ayni mesaj ikinci kez kaydedilmez", not db.kaydet(1, t, s, "ham", yol))
check("duzenleme isaretlenir", db.duzenleme(1, s, "degisti", yol))
db.silindi_isaretle([1], yol)
df = db.hepsi(yol)
check("silindi + ilk hali korunur", df.silindi[0] == 1 and df.ilk_hali[0] == "ham")

print("Rapor (demo)")
from evaluate import demo_veri, analiz
from rapor import html_yaz
sig, getir = demo_veri()
sonuc = analiz(sig, getir, 10000, 0.1, log=lambda *_: None)
out = os.path.join(tempfile.mkdtemp(), "r.html")
html_yaz(sonuc, out)
check("html uretildi", os.path.getsize(out) > 20000 and "NaN" not in open(out, encoding="utf-8").read())
check("6 senaryo", len(sonuc["senaryolar"]) == 6)
from evaluate import mum_paketle
m = mum_paketle(kazanc)
check("mum zamanlari dakika dakika paketlenir", m["dt"] == [0, 1, 2, 3] and m["o"][0] == 7800)

r = bot_gozu(SIG, B([[.79, .7999999, .78, .79, 9e3], [.79, .80, .78, .80, 9e3]]))
check("ham Yahoo verisi (0.7999999) yuvarlanmadan girilmez", r["durum"] != "alindi" or r["giris_saat"] == "04:11")
print(f"\n✅ {ok} test geçti")
