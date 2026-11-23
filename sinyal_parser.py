"""Kanal mesajlarindan sinyal ayiklayici.

Beklenen format (kanaldaki gibi):
    RAYA
    KIRILIM: 0.8
    STOP: 0.74
    TP1: 0.86
    TP2: 0.89
"""
import re
from dataclasses import dataclass, asdict
from typing import Optional

NUM = r"([0-9]+(?:[.,][0-9]+)?)"

FIELD_PATTERNS = {
    "entry": re.compile(r"(?:KIRILIM|KIRILMA|BREAKOUT|G[İI]R[İI][ŞS]|ENTRY)\s*[:=\-]?\s*\$?" + NUM, re.I),
    "stop": re.compile(r"(?:STOP|SL|ZARAR\s*KES)\s*[:=\-]?\s*\$?" + NUM, re.I),
    "tp1": re.compile(r"TP\s*1\s*[:=\-]?\s*\$?" + NUM, re.I),
    "tp2": re.compile(r"TP\s*2\s*[:=\-]?\s*\$?" + NUM, re.I),
}

# Ticker olamayacak kelimeler
STOPWORDS = {"KIRILIM", "KIRILMA", "STOP", "TP", "TP1", "TP2", "GIRIS", "GİRİŞ", "ENTRY",
             "SL", "AL", "SAT", "NOT", "PRE", "USD", "ET", "TEPESI", "VAR"}


@dataclass
class Signal:
    ticker: str
    entry: float
    stop: float
    tp1: float
    tp2: Optional[float]

    def to_dict(self):
        return asdict(self)


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def _find_ticker(text: str) -> Optional[str]:
    # Once $TICKER ara
    m = re.search(r"\$([A-Z]{1,5})\b", text)
    if m and m.group(1) not in STOPWORDS:
        return m.group(1)
    # Sonra ilk satirlarda tek basina buyuk harfli kelime
    for line in text.strip().splitlines()[:3]:
        line = line.strip().strip("🚨*_ ")
        m = re.fullmatch(r"([A-Z]{1,5})", line)
        if m and m.group(1) not in STOPWORDS:
            return m.group(1)
    return None


def parse_signal(text: str) -> Optional[Signal]:
    if not text:
        return None
    vals = {}
    for key, pat in FIELD_PATTERNS.items():
        m = pat.search(text)
        if m:
            vals[key] = _num(m.group(1))
    if not all(k in vals for k in ("entry", "stop", "tp1")):
        return None
    ticker = _find_ticker(text)
    if not ticker:
        return None
    s = Signal(ticker, vals["entry"], vals["stop"], vals["tp1"], vals.get("tp2"))
    # Mantik kontrolu: stop < giris < tp1
    if not (s.stop < s.entry < s.tp1):
        return None
    return s


if __name__ == "__main__":
    ornek = "RAYA\nKIRILIM: 0.8\nSTOP: 0.74\nTP1: 0.86\nTP2: 0.89"
    print(parse_signal(ornek))
