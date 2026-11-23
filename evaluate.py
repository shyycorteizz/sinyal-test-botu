"""Kaydedilen tum sinyalleri gercek dakikalik fiyatlarla test eder.

    python evaluate.py           -> rapor.html + rapor.txt uretir
    python evaluate.py --demo    -> sahte verilerle ornek rapor (kurulumdan once paneli gormek icin)
    python evaluate.py --ac      -> rapor bitince tarayicida ac
"""
import argparse
import sys
import json
import webbrowser
from datetime import datetime
from pathlib import Path

import pandas as pd

import config
from simulate import Ayar, bot_gozu, kanal_gozu

SENARYOLAR = [
    ("g0", 0, "Bot anında alırsa"),
    ("g1", 1, "Bot 1 dk geç kalırsa"),
    ("g3", 3, "Telefondan elle alırsan"),
]
MODLAR = [("tp1", "ilk hedefte hepsini satarsan"), ("kademeli", "yarısını 1., yarısını 2. hedefte satarsan")]


def ozet(islemler: list, sermaye0: float, poz: float) -> dict:
    df = pd.DataFrame(islemler)
    say = lambda d: int((df.durum == d).sum()) if len(df) else 0
    o = {"sinyal": len(df), "alinan": say("alindi"), "kacti": say("kacti"),
         "iptal": say("iptal_once_stop"), "kirilim_yok": say("kirilim_olmadi"), "veri_yok": say("veri_yok")}
    al = df[df.durum == "alindi"] if len(df) else df
    n = len(al)
    sermaye, tepe, dd = sermaye0, sermaye0, 0.0
    egri = [{"i": 0, "t": None, "v": round(sermaye0, 2), "tk": None, "g": None}]
    if n:
        for k, (_, r) in enumerate(al.sort_values("time").iterrows(), 1):
            sermaye += sermaye * poz * r.getiri
            tepe = max(tepe, sermaye)
            dd = max(dd, 1 - sermaye / tepe)
            egri.append({"i": k, "t": r.time, "v": round(sermaye, 2), "tk": r.ticker, "g": r.getiri})
        kaz, kay = al[al.getiri > 0], al[al.getiri <= 0]
        brut_kaz, brut_kay = kaz.getiri.sum(), -kay.getiri.sum()
        o.update(
            kazanma=len(kaz) / n, kazanc_say=len(kaz), kayip_say=len(kay),
            ort_kaz=float(kaz.getiri.mean()) if len(kaz) else None,
            ort_kay=float(kay.getiri.mean()) if len(kay) else None,
            beklenti=float(al.getiri.mean()),
            en_iyi=float(al.getiri.max()), en_iyi_tk=al.loc[al.getiri.idxmax(), "ticker"],
            en_kotu=float(al.getiri.min()), en_kotu_tk=al.loc[al.getiri.idxmin(), "ticker"],
            profit_factor=(brut_kaz / brut_kay) if brut_kay > 0 else None,
            sonuc_dagilim=al.sonuc.value_counts().to_dict(),
            ort_sure=float(al.sure_dk.mean()),
        )
        if o["ort_kaz"] and o["ort_kay"]:
            o["basabas_orani"] = -o["ort_kay"] / (o["ort_kaz"] - o["ort_kay"])
    o.update(son_sermaye=round(sermaye, 2), toplam_getiri=sermaye / sermaye0 - 1, maks_dd=dd, egri=egri)
    return o


def analiz(sinyaller: pd.DataFrame, mum_getir, sermaye0=None, poz=None, ayar: Ayar = None, log=print) -> dict:
    """mum_getir(ticker, time_utc) -> sinyal sonrasi dakikalik mumlar"""
    sermaye0 = sermaye0 or config.SANAL_SERMAYE
    poz = poz or config.POZISYON_ORANI
    ayar = ayar or Ayar()
    satirlar, islemler = [], {f"{g}_{m}": [] for g, _, _ in SENARYOLAR for m, _ in MODLAR}

    for _, s in sinyaller.iterrows():
        t_ny = s.time_utc.tz_convert(config.NY)
        try:
            bars = mum_getir(s.ticker, s.time_utc)
        except Exception as e:
            log(f"  ! {s.ticker}: {e}")
            bars = pd.DataFrame()
        d = {"entry": s.entry, "stop": s.stop, "tp1": s.tp1,
             "tp2": None if pd.isna(s.tp2) else float(s.tp2)}
        kg = kanal_gozu(d, bars)
        satirlar.append({
            "id": int(s.msg_id), "time": t_ny.isoformat(), "tarih": t_ny.strftime("%d.%m"),
            "saat": t_ny.strftime("%H:%M"), "saat_tr": s.time_utc.tz_convert("Europe/Istanbul").strftime("%H:%M"),
            "ticker": s.ticker, **d, **kg,
            "silindi": bool(s.get("silindi", 0)), "duzenlendi": bool(isinstance(s.get("duzenlendi"), str)),
        })
        for g, gec, _ in SENARYOLAR:
            a = Ayar(**{**ayar.dict(), "gecikme_dk": gec})
            for m, _ in MODLAR:
                r = bot_gozu(d, bars, m, a)
                islemler[f"{g}_{m}"].append({"id": int(s.msg_id), "time": t_ny.isoformat(),
                                             "ticker": s.ticker, **r})
        log(f"  {t_ny:%d.%m %H:%M} {s.ticker:<6} kanal: {kg['kanal_sonuc']:<14} "
            f"bot: {islemler['g0_tp1'][-1]['durum']} {islemler['g0_tp1'][-1]['sonuc'] or ''}")

    kdf = pd.DataFrame(satirlar)
    kanal = {}
    if len(kdf):
        girdi = kdf[~kdf.kanal_sonuc.isin(["kirilim_olmadi", "veri_yok"])]
        tp = girdi[girdi.kanal_sonuc.str.startswith("TP")]
        kanal = {
            "girilen": len(girdi), "tp": len(tp), "stop": int((girdi.kanal_sonuc == "STOP").sum()),
            "acik": int((girdi.kanal_sonuc == "acik_kaldi").sum()),
            "tp_orani": len(tp) / len(girdi) if len(girdi) else None,
            "basit_toplam_sadece_tp": float(tp.kanal_getiri.sum()),       # kanalin ozette yaptigi hesap
            "basit_toplam_dogru": float(girdi.kanal_getiri.sum()),       # stop'lar dahil
            "silinen": int(kdf.silindi.sum()), "duzenlenen": int(kdf.duzenlendi.sum()),
        }
    senaryolar = {}
    for g, gec, gad in SENARYOLAR:
        for m, mad in MODLAR:
            k = f"{g}_{m}"
            senaryolar[k] = {"ad": gad, "mod": mad, "gecikme": gec,
                             "ozet": ozet(islemler[k], sermaye0, poz), "islemler": islemler[k]}
    aralik = (f"{kdf.time.min()[:10]} → {kdf.time.max()[:10]}") if len(kdf) else "-"
    return {"meta": {"kanal": config.TG_CHANNEL or "-", "uretim": datetime.now().strftime("%d.%m.%Y %H:%M"),
                     "aralik": aralik, "ayar": ayar.dict(), "sermaye": sermaye0, "poz": poz},
            "kanal": kanal, "sinyaller": satirlar, "senaryolar": senaryolar}


def yuzde(x, isaret=True):
    if x is None:
        return "-"
    return f"{'-' if x < 0 else '+' if isaret and x > 0 else ''}%{abs(100 * x):.2f}"


def metin_ozet(sonuc: dict, ana="g0_tp1") -> str:
    k, o, m = sonuc["kanal"], sonuc["senaryolar"][ana]["ozet"], sonuc["meta"]
    if not k:
        return "Henüz sinyal yok."
    para = lambda x: f"${x:,.0f}".replace(",", ".")
    fark = o["son_sermaye"] - m["sermaye"]
    satir = [f"📊 SİNYAL KARNESİ ({m['aralik']}, {o['sinyal']} sinyal)", ""]
    if o["alinan"]:
        if fark >= 0:
            satir.append(f"Kısacası: Bu sinyallere uysaydın {para(m['sermaye'])} → {para(o['son_sermaye'])} olurdu. {para(fark)} KÂR ✅")
        else:
            satir.append(f"Kısacası: Bu sinyallere uysaydın {para(m['sermaye'])} → {para(o['son_sermaye'])} olurdu. {para(-fark)} ZARAR ❌")
        satir.append(f"Kanal ise bunu {yuzde(k['basit_toplam_sadece_tp'])} diye gösteriyor.")
        satir.append("")
        satir.append(f"• 10 sinyalden {round(o['kazanma'] * 10)} tanesi kâr ettirdi"
                     + (f" (kâra geçmek için gereken: 10'da {round(o['basabas_orani'] * 10)})" if o.get('basabas_orani') is not None else ""))
        satir.append(f"• Sinyal başına ortalama: {yuzde(o['beklenti'])}")
        if o["kacti"]:
            satir.append(f"• {o['kacti']} sinyale yetişilemedi (fiyat çoktan kaçmıştı)")
    else:
        satir.append("Henüz girilebilen sinyal yok.")
    if k["silinen"]:
        satir.append(f"• ⚠️ Kanal {k['silinen']} sinyali sonradan sildi")
    satir.append("")
    satir.append("Güven: " + ("düşük, daha çok sinyal lazım" if o["sinyal"] < 50 else "orta" if o["sinyal"] < 100 else "yeterli")
                 + f" ({o['sinyal']}/100 sinyal)")
    satir.append("Detaylar ekteki panelde. (Sanal hesap, gerçek para yok)")
    return "\n".join(satir)


def demo_veri():
    """Gercekci gorunen sahte sinyaller + mumlar (sadece paneli gostermek icin)."""
    import numpy as np
    rng = np.random.default_rng(7)
    tickers = ["RAYA", "GP", "GMM", "GDHG", "CLRO", "PAVS", "CUE", "SVRE", "MEDS", "NXAT", "SEAT", "POAS"]
    rows, mumlar = [], {}
    gun0 = pd.Timestamp("2026-11-16 04:00", tz=config.NY)
    mid = 1000
    for d in range(10):
        gun = gun0 + pd.Timedelta(days=d + 2 * (d // 5))
        for _ in range(rng.integers(3, 7)):
            tk = rng.choice(tickers)
            fiyat = float(np.round(rng.uniform(0.7, 5), 2))
            t = gun + pd.Timedelta(minutes=int(rng.integers(0, 600)))
            e = round(fiyat * 1.005, 2)
            rows.append({"msg_id": mid, "time_utc": t.tz_convert("UTC"), "ticker": tk, "entry": e,
                         "stop": round(e * 0.925, 2), "tp1": round(e * 1.075, 2), "tp2": round(e * 1.11, 2),
                         "silindi": int(rng.random() < 0.04), "duzenlendi": None})
            # rastgele yuruyus: biraz yukari egimli ama oynak, bazen pump-dump
            n = 300
            ret = rng.normal(0.0002, 0.012, n)
            if rng.random() < 0.2:
                ret[0] += 0.06         # sinyal gelir gelmez fiyat ziplar -> takipci yetisemez
            if rng.random() < 0.35:
                ret[:8] += 0.012       # ilk dakikalarda pump
                ret[8:40] -= 0.006     # sonra dump
            c = fiyat * np.exp(np.cumsum(ret))
            o = np.r_[fiyat, c[:-1]] * (1 + rng.normal(0, 0.002, n))
            if ret[0] > 0.04:
                o[0] = c[0]                # bosluklu acilis
            h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.006, n)))
            l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.006, n)))
            v = rng.integers(200, 60000, n)
            idx = pd.date_range(t.floor("min") + pd.Timedelta(minutes=1), periods=n, freq="min")
            mumlar[mid] = pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v}, index=idx)
            mid += 1
    df = pd.DataFrame(rows)
    by_id = {r["msg_id"]: r for r in rows}
    getir = lambda tk, t: mumlar[[m for m, r in by_id.items() if r["time_utc"] == t and r["ticker"] == tk][0]]
    return df, getir


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--ac", action="store_true", help="raporu tarayicida ac")
    ap.add_argument("--sermaye", type=float)
    ap.add_argument("--pozisyon", type=float)
    a = ap.parse_args()

    from rapor import html_yaz
    if a.demo:
        sig, getir = demo_veri()
        print("DEMO: sahte verilerle rapor uretiliyor...")
    else:
        import db
        import piyasa
        sig = db.hepsi()
        getir = piyasa.sinyal_sonrasi
        if sig.empty:
            print("Henuz kayitli sinyal yok. Once baslat.bat ile kanali dinlet.")
            return
    print(f"{len(sig)} sinyal test ediliyor...")
    sonuc = analiz(sig, getir, a.sermaye, a.pozisyon)
    if a.demo:
        sonuc["meta"]["kanal"] = "DEMO (sahte veri)"
    yol = Path("rapor_demo.html" if a.demo else "rapor.html")
    html_yaz(sonuc, yol)
    txt = metin_ozet(sonuc)
    Path("rapor.txt").write_text(txt, encoding="utf-8")
    pd.DataFrame(sonuc["senaryolar"]["g0_tp1"]["islemler"]).to_csv("trades.csv", index=False)
    print("\n" + txt)
    print(f"\nPanel: {yol.resolve()}")
    if a.ac:
        webbrowser.open(yol.resolve().as_uri())


if __name__ == "__main__":
    main()
