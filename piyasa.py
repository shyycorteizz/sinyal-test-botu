"""Fiyat verisi: Yahoo Finance 1 dakikalik mumlar (piyasa oncesi + sonrasi dahil).

- Tamamlanmis gunler cache/ klasorune kaydedilir (Yahoo sadece son ~30 gunu verir, sonra kaybolur).
- Hata olursa 3 kez tekrar dener.
"""
import os
import time
from datetime import timedelta

import pandas as pd

import config

CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)
_yf = None


def _yfinance():
    global _yf
    if _yf is None:
        import yfinance as yf
        _yf = yf
    return _yf


def _oku(yol):
    df = pd.read_csv(yol, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(config.NY)
    return df


def gun_mumlari(ticker: str, gun: pd.Timestamp, deneme: int = 3) -> pd.DataFrame:
    gun = gun.tz_convert(config.NY) if gun.tzinfo else gun.tz_localize(config.NY)
    yol = os.path.join(CACHE, f"{ticker}_{gun.date()}.csv")
    if os.path.exists(yol):
        return _oku(yol)
    bas = gun.normalize()
    son_hata = None
    for i in range(deneme):
        try:
            df = _yfinance().Ticker(ticker).history(
                start=bas.date(), end=(bas + timedelta(days=1)).date(),
                interval="1m", prepost=True, auto_adjust=False)
            break
        except Exception as e:  # ag hatasi vs.
            son_hata = e
            time.sleep(2 * (i + 1))
    else:
        raise RuntimeError(f"{ticker} verisi alinamadi: {son_hata}")
    if df.empty:
        return df
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = df.index.tz_convert(config.NY)
    df = df[df.index.normalize() == bas]
    simdi = pd.Timestamp.now(tz=config.NY)
    if bas.date() < simdi.date() or simdi.hour >= 20:
        df.to_csv(yol)  # tamamlanmis gun -> kalici sakla
    return df


def sinyal_sonrasi(ticker: str, t_utc: pd.Timestamp) -> pd.DataFrame:
    """Mesajin geldigi dakikadan SONRAKI mumdan gun sonuna kadar."""
    t_ny = t_utc.tz_convert(config.NY)
    gun = gun_mumlari(ticker, t_ny)
    if gun.empty:
        return gun
    return gun[gun.index >= t_ny.floor("min") + timedelta(minutes=1)]


def anlik_fiyat(ticker: str):
    """Son 1 dakikalik mumun kapanisi (piyasa oncesi dahil). Bulamazsa None."""
    try:
        df = _yfinance().Ticker(ticker).history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return float(df.Close.iloc[-1]), df.index[-1]
    except Exception:
        pass
    return None, None
