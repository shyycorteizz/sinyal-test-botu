"""Tum ayarlar .env dosyasindan okunur."""
import os
from dotenv import load_dotenv

load_dotenv()


def _get(key, default=None, cast=str):
    v = os.environ.get(key, default)
    if v is None or v == "":
        return default
    return cast(v)


TG_API_ID = _get("TG_API_ID", None, int)
TG_API_HASH = _get("TG_API_HASH")
TG_CHANNEL = _get("TG_CHANNEL")
BILDIRIM = _get("BILDIRIM", "1") == "1"
GUN_SONU_RAPORU = _get("GUN_SONU_RAPORU", "1") == "1"     # her gun 20:10 NY'de rapor at
SANAL_SERMAYE = _get("SANAL_SERMAYE", 10000, float)
POZISYON_ORANI = _get("POZISYON_ORANI", 0.10, float)       # her isleme sermayenin %10'u
DB_PATH = _get("DB_PATH", "sinyaller.db")
NY = "America/New_York"


def eksikler():
    return [k for k, v in {"TG_API_ID": TG_API_ID, "TG_API_HASH": TG_API_HASH,
                           "TG_CHANNEL": TG_CHANNEL}.items() if not v]
