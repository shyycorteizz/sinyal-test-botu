"""Tek bir sinyali dakikalik mumlar uzerinde iki gozle degerlendirir:

1) KANALIN GOZU  -> "Kirilimdan aldim, once TP1'e mi stop'a mi degdi?"
   Kayma yok, gecikme yok. Kanalin ozetinde gordugun hesap budur.

2) BOTUN GOZU    -> Senin botun gercekte ne yapardi?
   - Mesaj geldikten 'gecikme_dk' dakika sonra islem yapabilir
   - Alis/satista kayma + komisyon
   - Fiyat kirilimdan cok yukari kactiysa almaz ("kacti")
   - Ayni mumda hem stop hem TP varsa STOP sayilir (en kotu senaryo)
   - Gun sonunda (20:00 NY) acik kalan pozisyon kapanir
"""
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class Ayar:
    kayma: float = 0.01          # alis/satista %1 kotu fiyat
    komisyon: float = 0.001      # her yon icin %0.1
    giris_dk: int = 60           # sinyalden sonra kac dk icinde kirilim olmazsa vazgec
    maks_kovalama: float = 0.03  # kirilimin %3'unden fazla yukaridan alma
    dusuk_hacim: int = 2000      # TP mumunda bundan az lot islem gorduyse uyari
    gecikme_dk: int = 0          # mesajdan sonra botun ilk islem yapabilecegi dakika (0 = sonraki mum)

    def dict(self):
        return asdict(self)


# ------------------------------------------------------------------ KANALIN GOZU
def kanal_gozu(sig: dict, bars: pd.DataFrame) -> dict:
    """Kayma/gecikme yok. Kirilim -> once TP mi stop mu?"""
    r = {"kanal_sonuc": "veri_yok", "kanal_getiri": 0.0}
    if bars is None or bars.empty:
        return r
    e, s, t1 = sig["entry"], sig["stop"], sig["tp1"]
    t2 = sig.get("tp2")
    girdi = False
    tp1_oldu = False
    for _, b in bars.iterrows():
        if not girdi:
            if b.High >= e:
                girdi = True
            else:
                continue
        if b.Low <= s and not tp1_oldu:
            return {"kanal_sonuc": "STOP", "kanal_getiri": s / e - 1}
        if not tp1_oldu and b.High >= t1:
            tp1_oldu = True
            if not t2:
                return {"kanal_sonuc": "TP1", "kanal_getiri": t1 / e - 1}
        if tp1_oldu and t2 and b.High >= t2:
            return {"kanal_sonuc": "TP1+TP2", "kanal_getiri": t2 / e - 1}
        if tp1_oldu and b.Low <= e:  # TP1 sonrasi geri dondu: kanal yine "TP1 oldu" der
            return {"kanal_sonuc": "TP1", "kanal_getiri": t1 / e - 1}
    if tp1_oldu:
        return {"kanal_sonuc": "TP1", "kanal_getiri": t1 / e - 1}
    return {"kanal_sonuc": "acik_kaldi" if girdi else "kirilim_olmadi", "kanal_getiri": 0.0}


# ------------------------------------------------------------------ BOTUN GOZU
def _giris(sig, bars, a: Ayar):
    for i, (_, b) in enumerate(bars.iterrows()):
        if i >= a.giris_dk:
            return None, None, "kirilim_olmadi"
        if b.High >= sig["entry"]:
            ham = max(sig["entry"], b.Open)
            if ham > sig["entry"] * (1 + a.maks_kovalama) or ham >= sig["tp1"]:
                return None, None, "kacti"
            return i, ham * (1 + a.kayma), "alindi"
    return None, None, "kirilim_olmadi" if len(bars) else "veri_yok"


def bot_gozu(sig: dict, bars: pd.DataFrame, mod: str = "tp1", a: Ayar = Ayar()) -> dict:
    """mod='tp1'      -> hepsini TP1'de sat
       mod='kademeli' -> yarisi TP1, yarisi TP2; TP1 sonrasi stop giris fiyatina cekilir"""
    out = {"durum": None, "alis": None, "satis_ort": None, "getiri": 0.0, "sonuc": None,
           "uyari": "", "sure_dk": None, "mfe": None, "mae": None, "giris_saat": None, "cikis_saat": None}
    if bars is None or bars.empty:
        out["durum"] = "veri_yok"
        return out
    bars = bars.iloc[a.gecikme_dk:]
    i0, alis, durum = _giris(sig, bars, a)
    out["durum"] = durum
    if i0 is None:
        return out
    out["alis"] = round(alis, 4)
    t_giris = bars.index[i0]
    out["giris_saat"] = t_giris.strftime("%H:%M")

    sat = lambda p: p * (1 - a.kayma)
    stop = sig["stop"]
    tp1, tp2 = sig["tp1"], sig.get("tp2") or None
    kalan, gelir, tp1_oldu, sonuc = 1.0, 0.0, False, None
    yuksek, dusuk = alis, alis
    t_cikis = bars.index[-1]

    # Giris mumunda stop seviyesi de goruldu ise sirasi bilinemez -> en kotusu: stop
    if bars.iloc[i0].Low <= stop:
        gelir = sat(stop)
        out.update(satis_ort=round(gelir, 4), getiri=round(gelir / alis - 1 - 2 * a.komisyon, 5),
                   sonuc="STOP", sure_dk=0, mfe=0.0, mae=round(stop / alis - 1, 4),
                   cikis_saat=t_giris.strftime("%H:%M"))
        return out

    for t, b in bars.iloc[i0 + 1:].iterrows():
        yuksek, dusuk = max(yuksek, b.High), min(dusuk, b.Low)
        if b.Low <= stop:                               # 1) stop (once: en kotu senaryo)
            gelir += kalan * sat(min(stop, b.Open))     # bosluklu dususte daha asagidan
            kalan, t_cikis = 0, t
            sonuc = "basabas_stop" if tp1_oldu else "STOP"
            break
        if not tp1_oldu and b.High >= tp1:              # 2) TP1
            if b.Volume < a.dusuk_hacim:
                out["uyari"] = f"TP1 mumunda dusuk hacim ({int(b.Volume)} lot)"
            if mod == "tp1" or not tp2:
                gelir += kalan * sat(max(tp1, b.Open))
                kalan, t_cikis, sonuc = 0, t, "TP1"
                break
            gelir += 0.5 * sat(max(tp1, b.Open))
            kalan, tp1_oldu, stop = 0.5, True, alis     # kalan yari: stop basabas
            if b.High >= tp2:
                gelir += kalan * sat(max(tp2, b.Open))
                kalan, t_cikis, sonuc = 0, t, "TP1+TP2"
                break
            continue
        if tp1_oldu and b.High >= tp2:                  # 3) TP2
            gelir += kalan * sat(max(tp2, b.Open))
            kalan, t_cikis, sonuc = 0, t, "TP1+TP2"
            break

    if kalan > 0:
        gelir += kalan * sat(bars.iloc[-1].Close)
        sonuc = "TP1+gun_sonu" if tp1_oldu else "gun_sonu"

    out.update(
        satis_ort=round(gelir, 4),
        getiri=round(gelir / alis - 1 - 2 * a.komisyon, 5),
        sonuc=sonuc,
        sure_dk=int((t_cikis - t_giris).total_seconds() // 60),
        mfe=round(yuksek / alis - 1, 4),   # pozisyon acikken gorulen en iyi an
        mae=round(dusuk / alis - 1, 4),    # pozisyon acikken gorulen en kotu an
        cikis_saat=t_cikis.strftime("%H:%M"),
    )
    return out


# geriye uyumluluk
def simule(sig, bars, mod="tp1", a: Ayar = Ayar()):
    return bot_gozu(sig, bars, mod, a)
