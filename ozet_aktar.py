"""Kanalin paylastigi HAFTALIK OZET metnini okuyup sinyal olarak kaydeder.

Kullanim:
    python ozet_aktar.py ozet.txt                 -> ozeti ice aktar
    python ozet_aktar.py ozet.txt --stop 7.5      -> zarar kes seviyesi girisin %7.5 alti (varsayilan)

Ozette ZARAR KES (stop) seviyesi yazmiyor. Kanalin normal sinyallerinde (orn. RAYA: giris 0.80, stop 0.74)
stop yaklasik %7.5 asagida oldugu icin varsayilan olarak bunu kullaniyoruz. Bu bir TAHMIN; raporda belirtilir.
Telegram kurulumu GEREKMEZ, sadece Python + internet (fiyat verisi icin) yeter.
"""
import argparse
import re
import sys
import zlib
from datetime import datetime

import pandas as pd

import db
from sinyal_parser import Signal

AYLAR = {"ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5, "haziran": 6,
         "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11, "kasim": 11,
         "aralık": 12, "aralik": 12}

GUN_RE = re.compile(r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(Pazartesi|Salı|Sali|Çarşamba|Carsamba|Perşembe|Persembe|Cuma|Cumartesi|Pazar)", re.I)
SATIR_RE = re.compile(
    r"\$([A-Z]{1,5})\s*(?:\((\d+)\.\s*giri[şs]\))?\s*[—–-]+\s*Giri[şs]\s*\$([\d.,]+)\s*\((\d{1,2}:\d{2})\)"
    r"\s*→\s*TP1\s*\$([\d.,]+)\s*\((\d{1,2}:\d{2})\)"
    r"(?:\s*→\s*TP2\s*\$([\d.,]+)\s*\((\d{1,2}:\d{2})\))?"
    r"(?:\s*\|\s*yaln[ıi]z\s*TP1)?\s*\|\s*\+?%?([\d.,]+)", re.I)


def _f(x):
    return float(x.replace(",", "."))


def ozet_oku(metin: str, stop_yuzde: float = 7.5, yil: int | None = None):
    """[(msg_id, zaman_utc, Signal, kanal_iddiasi_yuzde, ham_satir)]"""
    m_yil = re.search(r"(20\d\d)", metin)
    yil = yil or (int(m_yil.group(1)) if m_yil else datetime.now().year)
    gun = None
    out = []
    for satir in metin.splitlines():
        g = GUN_RE.search(satir)
        if g:
            ay = AYLAR.get(g.group(2).lower())
            if ay:
                gun = (yil, ay, int(g.group(1)))
            continue
        m = SATIR_RE.search(satir)
        if not m or not gun:
            continue
        tk, sira, giris, saat, tp1, _, tp2, _, iddia = m.groups()
        giris, tp1 = _f(giris), _f(tp1)
        tp2 = _f(tp2) if tp2 else None
        stop = round(giris * (1 - stop_yuzde / 100), 4)
        hh, mm = map(int, saat.split(":"))
        # kanalin yazdigi giris dakikasini da teste dahil etmek icin 1 dk oncesini sinyal zamani sayiyoruz
        # (yani "bot tam o dakikada alsa" - kanala karsi en comert varsayim)
        t = pd.Timestamp(year=gun[0], month=gun[1], day=gun[2], hour=hh, minute=mm, tz="America/New_York") - pd.Timedelta(minutes=1)
        sig = Signal(tk, giris, stop, tp1, tp2)
        # ozetten gelenler negatif id alir (Telegram mesajlariyla karismasin), ayni satir hep ayni id
        mid = -(zlib.crc32(f"{t.isoformat()}|{tk}|{sira or 1}|{giris}".encode()) & 0x7FFFFFFF)
        out.append((mid, t.tz_convert("UTC"), sig, _f(iddia), satir.strip()))
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("dosya", nargs="?", default="ozet.txt")
    ap.add_argument("--stop", type=float, default=7.5, help="zarar kes: girisin yuzde kac alti (varsayilan 7.5)")
    a = ap.parse_args()
    metin = open(a.dosya, encoding="utf-8").read()
    sinyaller = ozet_oku(metin, a.stop)
    if not sinyaller:
        print("Özette sinyal satırı bulunamadı. Metni olduğu gibi yapıştırdığından emin ol.")
        return
    yeni = 0
    for mid, t, sig, iddia, ham in sinyaller:
        if db.kaydet(mid, t, sig, f"[HAFTALIK ÖZETTEN · stop tahmini %{a.stop}] {ham}"):
            yeni += 1
    toplam_iddia = sum(x[3] for x in sinyaller)
    print(f"Özetten {len(sinyaller)} sinyal okundu, {yeni} tanesi yeni kaydedildi.")
    print(f"Kanalın iddiası: {len(sinyaller)}/{len(sinyaller)} kâr, toplam +%{toplam_iddia:.2f}")
    print(f"Zarar kes seviyesi tahmini: girişin %{a.stop} altı.")
    print("Şimdi RAPOR.bat ile gerçek fiyatlarla test edebilirsin.")


if __name__ == "__main__":
    main()
