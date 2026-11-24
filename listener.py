"""Sinyal Test Botu - canli dinleyici.

    python listener.py               -> gecmisi tamamlar + canli dinler
    python listener.py --gecmis 14   -> ilk calistirmada 14 gun geriye tara
    python listener.py --sadece-gecmis

Ne yapar:
  * Kanaldaki her KIRILIM/STOP/TP mesajini sinyaller.db'ye kaydeder
  * Sana Telegram'da "Kayitli Mesajlar"a anlik bildirim atar (o anki fiyatla birlikte)
  * Kanal bir sinyali DUZENLERSE veya SILERSE bunu kaydeder ve sana haber verir
  * Her is gunu 20:10 (NY) / 04:10 (TR) gun sonu karnesini + rapor.html'i sana yollar
  * Bilgisayar kapaliyken kacan mesajlari acilista tamamlar

GERCEK ISLEM YAPMAZ.
"""
import argparse
import asyncio
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

import config
import db
from sinyal_parser import parse_signal

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%d.%m %H:%M:%S",
    handlers=[logging.FileHandler("bot.log", encoding="utf-8"), logging.StreamHandler(sys.stdout)])
log = logging.getLogger("sinyalbot")
logging.getLogger("telethon").setLevel(logging.WARNING)


def _kontrol():
    eksik = config.eksikler()
    if eksik:
        print("\n❌ .env dosyasinda eksik ayar var: " + ", ".join(eksik))
        print("   README'deki 'Kurulum' adimlarina bak (my.telegram.org'dan API anahtari).")
        sys.exit(3)


async def _fiyat_notu(sig) -> str:
    import piyasa
    loop = asyncio.get_running_loop()
    try:
        fiyat, _ = await asyncio.wait_for(loop.run_in_executor(None, piyasa.anlik_fiyat, sig.ticker), 15)
    except Exception:
        fiyat = None
    if not fiyat:
        return "Anlık fiyat alınamadı."
    uzak = fiyat / sig.entry - 1
    if fiyat >= sig.tp1:
        durum = "⚠️ Fiyat hedefi çoktan geçmiş, artık alınmaz."
    elif uzak > 0.03:
        durum = f"⚠️ Fiyat alış seviyesinin %{uzak*100:.1f} üstünde, kaçmış olabilir."
    elif uzak >= 0:
        durum = "Fiyat tam alış seviyesinde."
    else:
        durum = f"Alış seviyesine %{-uzak*100:.1f} var."
    return f"Şu an: ${fiyat:.4g}  →  {durum}"


async def calistir(gecmis_gun: int, sadece_gecmis: bool):
    from telethon import TelegramClient, events

    _kontrol()
    client = TelegramClient("oturum", config.TG_API_ID, config.TG_API_HASH,
                            connection_retries=None, retry_delay=5, auto_reconnect=True)
    await client.start()
    kanal = await client.get_entity(config.TG_CHANNEL)
    from telethon import utils
    kanal_peer = utils.get_peer_id(kanal)
    log.info(f"✅ Bağlandı: {getattr(kanal, 'title', config.TG_CHANNEL)}")

    async def bildir(metin, dosya=None):
        if not config.BILDIRIM:
            return
        try:
            await client.send_message("me", metin, file=dosya)
        except Exception as e:
            log.warning(f"Bildirim gönderilemedi: {e}")

    # ---------------------------------------------------- kacirilanlari tamamla
    son = db.durum_al("son_tarama")
    sinir = (pd.Timestamp(son) - timedelta(hours=1)) if son else \
        pd.Timestamp(datetime.now(timezone.utc) - timedelta(days=gecmis_gun))
    yeni = 0
    async for msg in client.iter_messages(kanal):
        if msg.date < sinir:
            break
        sig = parse_signal(msg.message or "")
        if sig and db.kaydet(msg.id, msg.date, sig, msg.message):
            yeni += 1
    db.durum_yaz("son_tarama", datetime.now(timezone.utc).isoformat())
    log.info(f"Geçmiş tarandı ({sinir:%d.%m %H:%M} UTC'den beri): {yeni} yeni sinyal. "
             f"Toplam kayıt: {len(db.hepsi())}")
    if sadece_gecmis:
        await client.disconnect()
        return

    # ---------------------------------------------------- canli olaylar
    @client.on(events.NewMessage(chats=kanal))
    async def yeni_mesaj(event):
        msg = event.message
        sig = parse_signal(msg.message or "")
        db.durum_yaz("son_tarama", datetime.now(timezone.utc).isoformat())
        if not sig or not db.kaydet(msg.id, msg.date, sig, msg.message):
            return
        gecikme = (datetime.now(timezone.utc) - msg.date).total_seconds()
        log.info(f"📥 {sig.ticker}  kırılım {sig.entry}  stop {sig.stop}  tp1 {sig.tp1}  tp2 {sig.tp2}  "
                 f"(mesaj gecikmesi {gecikme:.1f} sn)")
        fiyat = await _fiyat_notu(sig)
        risk = sig.entry - sig.stop
        rr = (sig.tp1 - sig.entry) / risk if risk > 0 else 0
        await bildir(
            f"📥 Yeni sinyal: **{sig.ticker}**\n"
            f"Al: ${sig.entry}  ·  Zarar kes: ${sig.stop}  ·  Hedef: ${sig.tp1}" + (f" / ${sig.tp2}" if sig.tp2 else "") + "\n"
            f"Tutarsa: +%{(sig.tp1/sig.entry-1)*100:.1f}  ·  Tutmazsa: -%{risk/sig.entry*100:.1f}\n"
            f"{fiyat}\n"
            f"_(sadece not alındı, gerçek alım yapılmadı)_")

    @client.on(events.MessageEdited(chats=kanal))
    async def duzenlendi(event):
        msg = event.message
        sig = parse_signal(msg.message or "")
        if db.duzenleme(msg.id, sig, msg.message):
            log.info(f"✏️ Mesaj {msg.id} düzenlendi (ilk hali korunuyor)")
            await bildir(f"✏️ Kanal bir sinyali **düzenledi** (mesaj #{msg.id}).\n"
                         f"Yeni hali: {(msg.message or '')[:200]}\nTest ilk hâline göre yapılmaya devam edecek.")

    @client.on(events.MessageDeleted())
    async def silindi(event):
        if event.chat_id != kanal_peer:   # kanal disi silmeler (mesaj id'leri kanala ozel) yok sayilir
            return
        tum = db.hepsi()
        kayitli = set(tum.msg_id) if len(tum) else set()
        silinen = [i for i in event.deleted_ids if i in kayitli]
        if silinen:
            db.silindi_isaretle(silinen)
            tk = ", ".join(tum[tum.msg_id.isin(silinen)].ticker)
            log.info(f"🗑 Kanal sinyal sildi: {tk}")
            await bildir(f"🗑 Kanal **{tk}** sinyalini SİLDİ.\nBot ilk hâlini sakladı; karnede yine sayılacak.")

    # ---------------------------------------------------- gun sonu raporu
    async def gun_sonu_dongusu():
        while True:
            await asyncio.sleep(60)
            ny = pd.Timestamp.now(tz=config.NY)
            bugun = ny.strftime("%Y-%m-%d")
            if (not config.GUN_SONU_RAPORU or ny.weekday() >= 5 or (ny.hour, ny.minute) < (20, 10)
                    or db.durum_al("son_rapor") == bugun):
                continue
            db.durum_yaz("son_rapor", bugun)
            try:
                metin, yol = await asyncio.get_running_loop().run_in_executor(None, rapor_uret)
                await bildir(metin, dosya=str(yol))
                log.info("📊 Gün sonu raporu gönderildi")
            except Exception as e:
                log.exception(f"Rapor üretilemedi: {e}")

    asyncio.create_task(gun_sonu_dongusu())
    log.info("👂 Canlı dinleniyor... (kapatmak için bu pencereyi kapat ya da Ctrl+C)")
    await client.run_until_disconnected()


def rapor_uret():
    import piyasa
    from evaluate import analiz, metin_ozet
    from rapor import html_yaz
    sig = db.hepsi()
    sonuc = analiz(sig, piyasa.sinyal_sonrasi, log=lambda *_: None, once_getir=piyasa.sinyal_oncesi)
    yol = Path("rapor.html")
    html_yaz(sonuc, yol)
    return metin_ozet(sonuc), yol


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gecmis", type=int, default=7, help="ilk calistirmada kac gun geriye taransin")
    ap.add_argument("--sadece-gecmis", action="store_true")
    a = ap.parse_args()
    try:
        asyncio.run(calistir(a.gecmis, a.sadece_gecmis))
    except KeyboardInterrupt:
        print("\nKapatıldı.")
