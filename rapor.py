"""Sinyal Karnesi v2 - sade, tek dosyalik, internetsiz calisan HTML panel.

Tasarim ilkesi: once tek cumlelik cevap, sonra "neden", sonra kanit.
Ayarlar ve yontem kapali bolumlerde; isteyen acar.
Hesaplar sayfanin icinde (JavaScript) simulate.py ile ayni kurallarla tekrar yapilir.
"""
import json
from pathlib import Path

import numpy as np


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return str(o)


def _temiz(x):
    if isinstance(x, dict):
        return {k: _temiz(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_temiz(v) for v in x]
    if isinstance(x, float) and x != x:
        return None
    return x


def html_yaz(sonuc: dict, yol: Path):
    hafif = {k: v for k, v in sonuc.items() if k != "senaryolar"}
    veri = json.dumps(_temiz(hafif), default=_json_default, ensure_ascii=False, separators=(",", ":"))
    veri = veri.replace("</", "<\\/")
    fontlar = Path(__file__).with_name("fonts.css")
    css = fontlar.read_text(encoding="utf-8") if fontlar.exists() else ""
    Path(yol).write_text(SABLON.replace("/*__FONTS__*/", css).replace("/*__VERI__*/null", veri), encoding="utf-8")


SABLON = r"""<!DOCTYPE html>
<html lang="tr" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sinyal Karnesi</title>
<style>
/*__FONTS__*/
:root{--font:'Geist',Inter,system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'Geist Mono',ui-monospace,Menlo,monospace;--serif:'Instrument Serif',Georgia,serif;--ease:cubic-bezier(.22,.8,.24,1);--spring:cubic-bezier(.3,1.5,.5,1)}
[data-theme="dark"]{color-scheme:dark;--bg:#040405;--s1:rgba(255,255,255,.025);--solid:#0d0d11;--s2:#15151b;--line:rgba(255,255,255,.07);--line2:rgba(255,255,255,.13);
  --t1:#f3f4f8;--t2:#c4c7d4;--t3:#8a8ea0;--t4:#5d6174;--accent:#b8c4ff;--accent2:#8ee6d4;--series:#8b9bff;
  --good:#3ddc84;--bad:#ff6b6b;--warn:#fab219;--grid:rgba(255,255,255,.055);--aur1:rgba(110,125,255,.09);--aur2:rgba(94,234,212,.04);
  --shadow:0 30px 80px -30px rgba(0,0,0,.9);--snow:220,225,255;--up:#3ddc84;--down:#ff6b6b}
[data-theme="light"]{color-scheme:light;--bg:#f6f7fb;--s1:rgba(255,255,255,.85);--solid:#fff;--s2:#eef0f7;--line:rgba(20,24,48,.08);--line2:rgba(20,24,48,.16);
  --t1:#12131a;--t2:#3c3f50;--t3:#646879;--t4:#9497a6;--accent:#4f5bd5;--accent2:#0e9f84;--series:#4f5bd5;
  --good:#0b8a3e;--bad:#d03b3b;--warn:#b7791f;--grid:rgba(20,24,48,.07);--aur1:rgba(129,140,248,.2);--aur2:rgba(45,212,191,.12);
  --shadow:0 30px 70px -34px rgba(40,50,110,.35);--snow:150,165,220;--up:#0b8a3e;--down:#d03b3b}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--t1);font:15px/1.6 var(--font);-webkit-font-smoothing:antialiased;overflow-x:hidden;transition:background .5s,color .5s}
body.modal-open{overflow:hidden}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:8px}
button{font:inherit;color:inherit}
.aurora{position:fixed;inset:-20vh -10vw auto;height:100vh;z-index:-1;pointer-events:none;overflow:hidden}
.aurora i{position:absolute;border-radius:50%;filter:blur(70px)}
.aurora i:nth-child(1){width:50vw;height:40vh;left:35%;top:2%;background:var(--aur1);animation:d1 24s ease-in-out infinite}
.aurora i:nth-child(2){width:36vw;height:32vh;left:60%;top:26%;background:var(--aur2);animation:d2 28s ease-in-out infinite}
@keyframes d1{50%{transform:translate(-8vw,6vh) scale(1.1)}}@keyframes d2{50%{transform:translate(-10vw,-4vh) scale(.9)}}
#snow{position:fixed;inset:0;z-index:0;pointer-events:none}
.wrap{position:relative;z-index:1;max-width:820px;margin:0 auto;padding:0 22px 70px}
.serif{font-family:var(--serif);font-style:italic;font-weight:400;letter-spacing:-.02em;background:linear-gradient(100deg,var(--t1) 0%,var(--accent) 55%,var(--accent2) 110%);-webkit-background-clip:text;background-clip:text;color:transparent;padding-right:.08em}
h1,h2,h3{margin:0;font-weight:600;letter-spacing:-.04em}
p{margin:0}
.pos{color:var(--good)}.neg{color:var(--bad)}.mut{color:var(--t3)}
.card{background:var(--s1);border:1px solid var(--line);border-radius:22px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.lbl{font:500 11px var(--mono);letter-spacing:.05em;color:var(--t3);text-transform:uppercase}
.fi{animation:fu .8s var(--ease) both}@keyframes fu{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}

.top{height:64px;display:flex;align-items:center;justify-content:space-between}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:17px;letter-spacing:-.045em}
.logo-ic{width:28px;height:28px;border-radius:9px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:grid;place-items:center;color:#fff}
.icon-btn{width:34px;height:34px;border-radius:50%;border:1px solid var(--line);background:var(--s1);display:grid;place-items:center;cursor:pointer;transition:transform .3s var(--spring)}
.icon-btn:hover{transform:rotate(-14deg)}

.hero{padding:36px 0 0}
.eyebrow{font:400 12.5px var(--mono);color:var(--t3)}
.hero h1{margin-top:10px;font-size:clamp(34px,5.4vw,54px);line-height:1.02;letter-spacing:-.055em}

/* cevap karti */
.answer{margin-top:28px;display:grid;grid-template-columns:1.35fr 1fr;overflow:hidden}
.answer>div{padding:28px 30px}
.answer .real{position:relative}
.answer .real::before{content:"";position:absolute;width:280px;height:280px;left:-60px;top:-140px;border-radius:50%;background:color-mix(in srgb,var(--res) 16%,transparent);filter:blur(50px)}
.answer .real>*{position:relative}
.answer .claim{border-left:1px solid var(--line);background:color-mix(in srgb,var(--s2) 40%,transparent)}
.flow{display:flex;align-items:baseline;flex-wrap:wrap;gap:8px 14px;margin-top:14px;font-variant-numeric:tabular-nums}
.flow .from{font:500 22px var(--mono);color:var(--t3)}
.flow .arr{color:var(--t4);font-size:20px}
.flow .to{font-size:clamp(44px,7vw,64px);font-weight:600;letter-spacing:-.06em;line-height:1;color:var(--res)}
.diff{margin-top:10px;font:600 17px var(--mono);color:var(--res)}
.claim .big{margin-top:14px;font-size:clamp(34px,5vw,44px);font-weight:600;letter-spacing:-.05em;line-height:1;color:var(--t2)}
.claim .note{margin-top:10px;font-size:13.5px;color:var(--t3)}
.sentence{margin-top:16px;font-size:17px;line-height:1.6;color:var(--t2)}
.sentence b{color:var(--t1)}

/* bolumler */
.sec{margin-top:56px}
.sec h2{font-size:clamp(24px,3vw,30px);letter-spacing:-.045em}
.sec h2 .serif{font-size:1.06em}
.sec .lead{margin-top:6px;color:var(--t3);font-size:14.5px}
.box{margin-top:16px;padding:24px 26px}

/* esik cubugu */
.thr-bar{position:relative;margin:40px 0 34px;height:18px;border-radius:10px;background:var(--s2)}
.thr-bar .fill{position:absolute;left:0;top:0;bottom:0;border-radius:10px;transition:width .6s var(--ease),background .3s}
.thr-bar .ticks{position:absolute;inset:0;display:grid;grid-template-columns:repeat(10,1fr);pointer-events:none}
.thr-bar .ticks i{border-right:2px solid var(--bg)}.thr-bar .ticks i:last-child{border:0}
.thr-bar .need{position:absolute;top:-14px;bottom:-14px;border-left:2px dashed var(--t1);transition:left .6s var(--ease)}
.thr-bar .need span{position:absolute;bottom:calc(100% + 4px);left:50%;transform:translateX(-50%);white-space:nowrap;font:600 12px var(--mono)}
.thr-bar .have{position:absolute;top:calc(100% + 10px);transform:translateX(-50%);white-space:nowrap;font:600 12px var(--mono);transition:left .6s var(--ease)}
.why{font-size:15px;color:var(--t2);line-height:1.65}
.why b{color:var(--t1)}

svg text{fill:var(--t3);font-size:10.5px;font-family:var(--mono)}
.chartbox{position:relative}
.tip{position:absolute;pointer-events:none;background:var(--solid);border:1px solid var(--line2);border-radius:12px;padding:8px 12px;font-size:12.5px;white-space:nowrap;opacity:0;transition:opacity .1s;z-index:3;box-shadow:var(--shadow)}

/* sinyal listesi */
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.fchip{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:7px;height:34px;padding:0 14px;border-radius:999px;border:1px solid var(--line);background:var(--s1);font-size:13px;color:var(--t2)}
.fchip b{font:600 11px var(--mono);opacity:.6}
.fchip[aria-pressed="true"]{background:var(--t1);color:var(--bg);border-color:var(--t1)}
.fchip:focus-visible{outline:2px solid var(--accent)}
.list{margin-top:12px;overflow:hidden}
.row{all:unset;box-sizing:border-box;cursor:pointer;width:100%;display:grid;grid-template-columns:110px 1fr auto 18px;gap:14px;align-items:center;padding:14px 20px;border-bottom:1px solid var(--line);transition:background .15s}
.row:last-child{border-bottom:0}
.row:hover{background:var(--s2)}
.row:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.row .tk{font-weight:650;font-size:15.5px;letter-spacing:-.02em}
.row .tm{font:400 11.5px var(--mono);color:var(--t3)}
.row .cmp{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px;color:var(--t2)}
.row .cmp .ar{color:var(--t4)}
.row .res{font:600 14px var(--mono);text-align:right;min-width:70px}
.row .chev{color:var(--t4)}
.badge{display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;border:1px solid var(--line);white-space:nowrap}
.badge i{width:7px;height:7px;border-radius:50%;display:inline-block}
.more{display:flex;justify-content:center;margin-top:14px}
.btn{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 18px;border-radius:999px;border:1px solid var(--line2);background:transparent;cursor:pointer;font-size:13.5px}
.btn:hover{background:var(--s2)}

/* acilir bolumler */
details.fold{margin-top:14px}
details.fold>summary{cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:18px 24px;font-weight:600;font-size:15.5px}
details.fold>summary::-webkit-details-marker{display:none}
details.fold>summary .pl{width:26px;height:26px;border-radius:50%;border:1px solid var(--line2);display:grid;place-items:center;font:500 14px var(--mono);transition:transform .3s var(--spring);flex:none}
details.fold[open]>summary .pl{transform:rotate(45deg)}
details.fold>summary small{display:block;font-weight:400;font-size:13px;color:var(--t3);margin-top:2px}
.fold-in{padding:4px 24px 24px}
.opt{padding:16px 0;border-top:1px solid var(--line)}
.opt:first-child{border-top:0;padding-top:4px}
.opt .t{font-weight:600;font-size:14px}
.opt .d{font-size:13px;color:var(--t3);margin:2px 0 10px}
.seg{display:inline-flex;flex-wrap:wrap;background:var(--s2);border:1px solid var(--line);border-radius:999px;padding:3px}
.seg button{all:unset;cursor:pointer;padding:7px 14px;border-radius:999px;color:var(--t3);font-size:13px}
.seg button[aria-pressed="true"]{background:var(--t1);color:var(--bg)}
.seg button:focus-visible{outline:2px solid var(--accent)}
.rng{display:flex;align-items:center;gap:14px}
input[type=range]{-webkit-appearance:none;appearance:none;flex:1;height:4px;border-radius:2px;background:linear-gradient(var(--accent),var(--accent)) 0/var(--p,50%) 100% no-repeat,var(--line2);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:var(--t1);border:3px solid var(--accent)}
input[type=range]::-moz-range-thumb{width:12px;height:12px;border-radius:50%;background:var(--t1);border:3px solid var(--accent)}
.rng .v{font:600 15px var(--mono);min-width:56px;text-align:right}
.money{display:inline-flex;align-items:center;gap:4px;font:600 18px var(--mono)}
.money input{all:unset;width:130px;font:inherit;color:var(--t1);border-bottom:1px dashed var(--line2)}
.money input:focus{border-bottom-color:var(--accent)}
.reset{margin-top:14px;font-size:13px;color:var(--t3)}
.reset button{all:unset;cursor:pointer;color:var(--accent);text-decoration:underline;text-underline-offset:3px}
.est{display:inline-block;margin-left:6px;padding:1px 6px;border-radius:6px;background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn);font:600 10px var(--mono);letter-spacing:.04em;vertical-align:2px}
.changed{display:none;margin-top:12px;padding:8px 12px;border-radius:10px;background:color-mix(in srgb,var(--warn) 12%,transparent);color:var(--warn);font-size:12.5px}
.changed.on{display:block}
.rules{margin:0;padding-left:18px;color:var(--t2);font-size:14px}
.rules li{margin:7px 0}
.gl{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}
.gl div{padding:12px 14px;border-radius:12px;background:var(--s2)}
.gl b{font-size:13.5px}.gl p{margin-top:2px;font-size:12.5px;color:var(--t2)}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);color:var(--t4);font-size:12px}

/* kanit penceresi */
.modal{position:fixed;inset:0;z-index:60;display:none;align-items:center;justify-content:center;padding:16px}
.modal.open{display:flex}
.modal .bd{position:absolute;inset:0;background:rgba(0,0,0,.65);backdrop-filter:blur(6px)}
.modal .mbox{position:relative;width:min(900px,100%);max-height:calc(100vh - 32px);overflow:auto;padding:22px 24px;border-radius:24px;background:var(--solid);border:1px solid var(--line2);box-shadow:var(--shadow);animation:pop .3s var(--spring)}
@keyframes pop{from{opacity:0;transform:translateY(14px) scale(.98)}}
.m-h{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.m-h h3{font-size:22px}
.m-story{margin-top:10px;font-size:15px;color:var(--t2);line-height:1.6}
.m-story b{color:var(--t1)}
.m-chart{margin-top:14px;border:1px solid var(--line);border-radius:16px;padding:10px;background:var(--bg)}
.m-legend{display:flex;flex-wrap:wrap;gap:14px;margin-top:8px;font:400 11px var(--mono);color:var(--t3)}
.m-legend i{display:inline-block;width:12px;height:2px;vertical-align:middle;margin-right:5px}
.m-msg{margin-top:14px}
.m-msg pre{white-space:pre-wrap;margin:8px 0 0;font:400 12.5px/1.6 var(--mono);padding:12px 14px;border-radius:12px;background:var(--s2);color:var(--t2)}
.m-src{margin-top:10px;font-size:11.5px;color:var(--t4)}

@media(max-width:700px){
  .answer{grid-template-columns:1fr}.answer .claim{border-left:0;border-top:1px solid var(--line)}
  .row{grid-template-columns:1fr auto 14px}.row .cmp{grid-column:1/-1;grid-row:2}
  .gl{grid-template-columns:1fr}
}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important}}
</style>
</head>
<body>
<div class="aurora" aria-hidden="true"><i></i><i></i></div>
<canvas id="snow" aria-hidden="true"></canvas>
<div class="wrap">
  <div class="top">
    <div class="logo"><span class="logo-ic"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8M15 7h6v6"/></svg></span>sinyal karnesi</div>
    <button class="icon-btn" id="themeBtn" aria-label="tema değiştir">
      <svg id="i-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
      <svg id="i-sun" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
    </button>
  </div>

  <section class="hero">
    <div class="eyebrow fi" id="eyebrow"></div>
    <h1 class="fi">Bu sinyallere uysaydın <span class="serif">paran ne olurdu?</span></h1>

    <div class="answer card fi" style="animation-delay:.1s">
      <div class="real" id="real">
        <div class="lbl">Gerçekte · sanal hesapla</div>
        <div class="flow"><span class="from" id="from"></span><span class="arr">→</span><span class="to" id="to"></span></div>
        <div class="diff" id="diff"></div>
      </div>
      <div class="claim">
        <div class="lbl" id="claimLbl">Kanalın gösterdiği</div>
        <div class="big" id="claim"></div>
        <div class="note" id="claimNote"></div>
      </div>
    </div>
    <p class="sentence fi" style="animation-delay:.2s" id="sentence"></p>

    <details class="fold card" id="opts">
      <summary><span>Farklı varsayımlarla dene<small>Kasa, alım hızı, satış zamanı, zarar kes. Değiştirdikçe yukarıdaki sonuç güncellenir.</small></span><span class="pl">+</span></summary>
      <div class="fold-in">
        <div class="opt"><div class="t">Kasan</div><div class="d">Sanal para. Her sinyale bunun %10'u konur.</div><div class="money">$<input id="inCap" inputmode="numeric" aria-label="kasa (dolar)"></div></div>
        <div class="opt"><div class="t">Ne kadar hızlı alıyorsun?</div><div class="d">Telefondan elle almak birkaç dakika sürer, bot saniyeler içinde alır.</div><div class="seg" id="segSpeed"></div></div>
        <div class="opt"><div class="t">Ne zaman satıyorsun?</div><div class="d">Hepsini ilk hedefte mi, yarısını ilk yarısını ikinci hedefte mi?</div><div class="seg" id="segMode"></div></div>
        <div class="opt" id="stopOpt"><div class="t">Zarar kes seviyesi <span class="est">TAHMİN</span></div><div class="d">Kanalın özetinde yazmıyor; normal sinyallerindeki gibi %7,5 varsaydık. Farklı değerleri kendin dene.</div><div class="rng"><input type="range" id="inStop" min="3" max="25" step="0.5" aria-label="zarar kes yüzdesi"><span class="v" id="stopV"></span></div></div>
        <div class="changed" id="changed"></div>
        <div class="reset"><button id="resetBtn">Varsayılanlara dön</button></div>
      </div>
    </details>
  </section>

  <section class="sec">
    <h2>Neden <span class="serif" id="whyTitle">zarar?</span></h2>
    <p class="lead">10 sinyalden kaçının tuttuğu ve kâra geçmek için kaçının tutması gerektiği.</p>
    <div class="box card">
      <div class="thr-bar"><div class="fill" id="thrFill"></div><div class="ticks"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div><div class="need" id="thrNeed"><span></span></div><div class="have" id="thrHave"></div></div>
      <p class="why" id="why"></p>
    </div>
  </section>

  <section class="sec">
    <h2>Kasan <span class="serif">nasıl değişti?</span></h2>
    <p class="lead">Her nokta bir sinyal. Kesikli çizgi başladığın para. Üstünde gezin.</p>
    <div class="box card"><div class="chartbox" id="eqBox"><div class="tip" id="tip"></div></div></div>
  </section>

  <section class="sec">
    <h2>Tek tek <span class="serif">sinyaller</span></h2>
    <p class="lead">Bir satıra tıkla: o anın gerçek fiyat grafiği ve kanalın mesajı açılır. Kendin kontrol et.</p>
    <div class="filters" id="filters"></div>
    <div class="list card" id="list"></div>
    <div class="more" id="more"></div>
  </section>

  <details class="fold card sec" style="margin-top:56px">
    <summary><span>Nasıl hesapladık?<small>Bütün kurallar, verinin sınırları ve terimler.</small></span><span class="pl">+</span></summary>
    <div class="fold-in"><ul class="rules" id="rules"></ul><div class="gl" id="gloss"></div></div>
  </details>
  <footer id="foot"></footer>
</div>

<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="mTitle">
  <div class="bd" data-close></div>
  <div class="mbox">
    <div class="m-h"><div><div class="lbl" id="mSub"></div><h3 id="mTitle"></h3></div><button class="icon-btn" data-close aria-label="kapat"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg></button></div>
    <p class="m-story" id="mStory"></p>
    <div class="m-chart" id="mChart"></div>
    <div class="m-legend"><span><i style="background:var(--t1)"></i>alış</span><span><i style="background:var(--bad)"></i>zarar kes</span><span><i style="background:var(--good)"></i>hedef</span><span><i style="background:var(--accent);width:2px;height:10px"></i>mesaj anı</span><span>▲ alındı ▼ satıldı</span></div>
    <div class="m-msg"><div class="lbl">Kanalın mesajı</div><pre id="mMsg"></pre></div>
    <div class="m-src">Fiyatlar: Yahoo Finance, 1 dakikalık mumlar. Her mum bir dakika; yeşil = o dakika yükseldi, kırmızı = düştü.</div>
  </div>
</div>

<script>
"use strict";
const V = /*__VERI__*/null;
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const A = V.meta.ayar;
const fmtPct = (x, sign = true, d = 1) => x == null || !isFinite(x) ? "–" : (x < 0 ? "−" : sign && x > 0 ? "+" : "") + "%" + Math.abs(100 * x).toFixed(d).replace(".", ",");
const fmtUsd = (x, sign = false) => (x < 0 ? "−" : sign && x > 0 ? "+" : "") + "$" + Math.round(Math.abs(x)).toLocaleString("tr-TR");
const fmtP = x => x == null ? "–" : (x < 1 ? x.toFixed(4).replace(/0{1,2}$/, "") : x.toFixed(2)).replace(".", ",");
const cls = x => x == null ? "" : x > 0 ? "pos" : x < 0 ? "neg" : "";
const store = {get(k){ try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v){ try { localStorage.setItem(k, v); } catch (e) {} }};
/* ---------- veri ---------- */
const decode = m => m ? {t: m.dt.map(d => m.t0 + d), o: m.o.map(x => x / 1e4), h: m.h.map(x => x / 1e4), l: m.l.map(x => x / 1e4), c: m.c.map(x => x / 1e4), v: m.v, n: m.dt.length} : null;
const SIG = V.sinyaller.map(s => ({...s, B: decode(s.m), P: decode(s.pre)}));
const HAS_EST = SIG.some(s => s.stop_tahmin);

/* ---------- simulasyon (simulate.py ile birebir) ---------- */
function kanalGozu(g, B){
  if (!B || !B.n) return {sonuc: "veri_yok", ret: 0};
  const {entry: e, stop: s, tp1: t1, tp2: t2} = g;
  let girdi = false, tp1 = false;
  for (let i = 0; i < B.n; i++){
    if (!girdi){ if (B.h[i] >= e) girdi = true; else continue; }
    if (B.l[i] <= s && !tp1) return {sonuc: "STOP", ret: s / e - 1};
    if (!tp1 && B.h[i] >= t1){ tp1 = true; if (!t2) return {sonuc: "TP1", ret: t1 / e - 1}; }
    if (tp1 && t2 && B.h[i] >= t2) return {sonuc: "TP1+TP2", ret: t2 / e - 1};
    if (tp1 && B.l[i] <= e) return {sonuc: "TP1", ret: t1 / e - 1};
  }
  if (tp1) return {sonuc: "TP1", ret: t1 / e - 1};
  return {sonuc: girdi ? "acik_kaldi" : "kirilim_olmadi", ret: 0};
}
function botGozu(g, B, mod, gec){
  const out = {durum: null, alis: null, ret: 0, sonuc: null, uyari: "", sure: null, mfe: null, mae: null, gi: null, ci: null, cikis: null};
  if (!B || !B.n){ out.durum = "veri_yok"; return out; }
  const st = gec, n = B.n, sat = p => p * (1 - A.kayma);
  let i0 = null, alis = null;
  for (let i = st; i < n; i++){
    if (i - st >= A.giris_dk){ out.durum = "kirilim_olmadi"; return out; }
    if (B.h[i] >= g.entry){
      const ham = Math.max(g.entry, B.o[i]);
      if (ham > g.entry * (1 + A.maks_kovalama) || ham >= g.tp1){ out.durum = "kacti"; out.gi = i; return out; }
      i0 = i; alis = ham * (1 + A.kayma); break;
    }
  }
  if (i0 == null){ out.durum = n - st > 0 ? "kirilim_olmadi" : "veri_yok"; return out; }
  out.durum = "alindi"; out.alis = alis; out.gi = i0;
  let stop = g.stop, kalan = 1, gelir = 0, tp1o = false, sonuc = null, hi = alis, lo = alis, ci = n - 1;
  if (B.l[i0] <= stop){
    gelir = sat(stop);
    return Object.assign(out, {ret: gelir / alis - 1 - 2 * A.komisyon, sonuc: "STOP", sure: 0, mfe: 0, mae: stop / alis - 1, ci: i0, cikis: gelir});
  }
  for (let j = i0 + 1; j < n; j++){
    hi = Math.max(hi, B.h[j]); lo = Math.min(lo, B.l[j]);
    if (B.l[j] <= stop){ gelir += kalan * sat(Math.min(stop, B.o[j])); kalan = 0; ci = j; sonuc = tp1o ? "basabas_stop" : "STOP"; break; }
    if (!tp1o && B.h[j] >= g.tp1){
      if (B.v[j] < A.dusuk_hacim) out.uyari = "az alıcı vardı";
      if (mod === "tp1" || !g.tp2){ gelir += kalan * sat(Math.max(g.tp1, B.o[j])); kalan = 0; ci = j; sonuc = "TP1"; break; }
      gelir += .5 * sat(Math.max(g.tp1, B.o[j])); kalan = .5; tp1o = true; stop = alis;
      if (B.h[j] >= g.tp2){ gelir += kalan * sat(Math.max(g.tp2, B.o[j])); kalan = 0; ci = j; sonuc = "TP1+TP2"; break; }
      continue;
    }
    if (tp1o && B.h[j] >= g.tp2){ gelir += kalan * sat(Math.max(g.tp2, B.o[j])); kalan = 0; ci = j; sonuc = "TP1+TP2"; break; }
  }
  if (kalan > 0){ gelir += kalan * sat(B.c[n - 1]); sonuc = tp1o ? "TP1+gun_sonu" : "gun_sonu"; }
  return Object.assign(out, {ret: gelir / alis - 1 - 2 * A.komisyon, sonuc, sure: B.t[ci] - B.t[i0], mfe: hi / alis - 1, mae: lo / alis - 1, ci, cikis: gelir});
}


/* ---------- durum ---------- */
const DEF = {cap: V.meta.sermaye, stop: 7.5, gec: 0, mod: "tp1"};
const S = {...DEF, filt: "all", show: 10};
const POZ = V.meta.poz;
const SPEEDS = [[0, "Bot (anında)"], [1, "1 dk geç"], [3, "Elle (~3 dk)"]];
const MODES = [["tp1", "Hepsini 1. hedefte"], ["kademeli", "Yarı 1. / yarı 2. hedef"]];
const sigOf = s => ({entry: s.entry, tp1: s.tp1, tp2: s.tp2, stop: s.stop_tahmin ? +(s.entry * (1 - S.stop / 100)).toFixed(4) : s.stop});

function hesapla(gec, mod){
  const rows = SIG.map(s => { const g = sigOf(s); return {s, g, k: kanalGozu(g, s.B), b: botGozu(g, s.B, mod, gec)}; });
  const al = rows.filter(r => r.b.durum === "alindi").sort((a, b) => a.s.time < b.s.time ? -1 : a.s.time > b.s.time ? 1 : a.s.id - b.s.id);
  const kaz = al.filter(r => r.b.ret > 0), kay = al.filter(r => r.b.ret <= 0);
  const mean = a => a.length ? a.reduce((x, r) => x + r.b.ret, 0) / a.length : null;
  let cap = S.cap; const eq = [{v: cap}];
  for (const r of al){ cap += cap * POZ * r.b.ret; eq.push({v: cap, r}); }
  const oKaz = mean(kaz), oKay = mean(kay);
  const girdi = rows.filter(r => !["kirilim_olmadi", "veri_yok"].includes(r.k.sonuc)), ktp = girdi.filter(r => r.k.sonuc.startsWith("TP"));
  const iddialar = SIG.map(s => s.iddia).filter(x => x != null);
  return {rows, al, n: rows.length, alinan: al.length, kazanc: kaz.length, kazanma: al.length ? kaz.length / al.length : null,
    oKaz, oKay, basabas: oKaz != null && oKay != null ? -oKay / (oKaz - oKay) : null, son: cap, eq,
    kacti: rows.filter(r => r.b.durum === "kacti").length,
    iddia: iddialar.length === SIG.length && SIG.length ? {toplam: iddialar.reduce((a, b) => a + b, 0), kendi: true}
                                                       : {toplam: ktp.reduce((x, r) => x + r.k.ret, 0), kendi: false, tp: ktp.length, girilen: girdi.length}};
}

const SON = {"TP1": ["Kâr", "var(--good)"], "TP1+TP2": ["Kâr", "var(--good)"], "TP1+gun_sonu": ["Kâr", "var(--good)"], "basabas_stop": ["Başa baş", "var(--warn)"],
  "STOP": ["Zarar", "var(--bad)"], "gun_sonu": ["Gün sonu", "var(--warn)"], "kacti": ["Yetişilemedi", "var(--t3)"], "kirilim_olmadi": ["Fiyat gelmedi", "var(--t3)"],
  "veri_yok": ["Veri yok", "var(--t3)"], "acik_kaldi": ["Sonuçlanmadı", "var(--warn)"]};
const badge = k => { const [t, c] = SON[k] || [k, "var(--t3)"]; return `<span class="badge"><i style="background:${c}"></i>${t}</span>`; };

let R = null;
function render(){
  R = hesapla(S.gec, S.mod);
  const kar = R.son - S.cap, res = !R.alinan ? "var(--t3)" : kar >= 0 ? "var(--good)" : "var(--bad)";
  const ilk = V.meta.aralik.split(" → ")[0], son = V.meta.aralik.split(" → ")[1] || ilk;
  const tr = d => { const [y, m, g] = d.split("-"); return `${+g} ${["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"][+m - 1]} ${y}`; };
  $("#eyebrow").textContent = `${tr(ilk)}${son !== ilk ? " – " + tr(son) : ""} · ${R.n} sinyal${V.meta.kanal && V.meta.kanal !== "-" ? " · " + V.meta.kanal : ""}`;
  $("#real").style.setProperty("--res", res);
  $("#from").textContent = fmtUsd(S.cap);
  $("#to").textContent = R.alinan ? fmtUsd(R.son) : "–";
  $("#diff").textContent = R.alinan ? `${fmtUsd(kar, true)} (${fmtPct(kar / S.cap)})` : "Henüz girilebilen sinyal yok";
  const I = R.iddia;
  $("#claimLbl").textContent = I.kendi ? "Kanalın kendi özetinde" : "Kanalın usulüyle";
  $("#claim").textContent = fmtPct(I.toplam, true, 0);
  $("#claimNote").textContent = I.kendi ? `${R.n} sinyalin ${R.n}'i "kâr" olarak yazılmış ve yüzdeleri toplanmış.` : `Sadece hedefe ulaşan ${I.tp} sinyalin yüzdeleri toplanmış; kaybettirenler sayılmamış.`;
  const changed = S.cap !== DEF.cap || S.stop !== DEF.stop || S.gec !== DEF.gec || S.mod !== DEF.mod;
  $("#sentence").innerHTML = !R.alinan ? "" : `Kanalın gösterdiği <b>${fmtPct(I.toplam, true, 0)}</b> ile gerçek sonuç <b class="${cls(kar)}">${fmtPct(kar / S.cap)}</b> arasında büyük fark var. ` +
    `Aşağıda nedenini ve her sinyalin gerçek grafiğini görebilirsin.`;
  // ayarlar
  $("#inCap").value = Math.round(S.cap).toLocaleString("tr-TR");
  $("#segSpeed").innerHTML = SPEEDS.map(([g, t]) => `<button data-g="${g}" aria-pressed="${g === S.gec}">${t}</button>`).join("");
  $("#segMode").innerHTML = MODES.map(([m, t]) => `<button data-m="${m}" aria-pressed="${m === S.mod}">${t}</button>`).join("");
  $$("#segSpeed button").forEach(b => b.onclick = () => { S.gec = +b.dataset.g; render(); });
  $$("#segMode button").forEach(b => b.onclick = () => { S.mod = b.dataset.m; render(); });
  $("#stopOpt").style.display = SIG.some(s => s.stop_tahmin) ? "" : "none";
  $("#inStop").value = S.stop; $("#inStop").style.setProperty("--p", ((S.stop - 3) / 22 * 100) + "%"); $("#stopV").textContent = "%" + String(S.stop).replace(".", ",");
  $("#changed").className = "changed" + (changed ? " on" : "");
  $("#changed").textContent = changed ? "Varsayılan ayarlardan farklı bir durumu görüyorsun. Sayfadaki bütün rakamlar bu ayarlara göre." : "";
  // neden
  const have = R.kazanma ?? 0, need = R.basabas, ok = need != null && have >= need;
  $("#whyTitle").textContent = !R.alinan ? "?" : kar >= 0 ? "kâr?" : "zarar?";
  $("#thrFill").style.width = (have * 100) + "%"; $("#thrFill").style.background = ok ? "var(--good)" : "var(--bad)";
  $("#thrNeed").style.display = need == null ? "none" : ""; $("#thrNeed").style.left = ((need ?? 0) * 100) + "%";
  const on = x => (x * 10).toFixed(1).replace(".0", "").replace(".", ",");
  $("#thrNeed span").textContent = need == null ? "" : `kâr için gereken: 10'da ${on(need)}`;
  $("#thrHave").style.left = Math.max(5, Math.min(95, have * 100)) + "%"; $("#thrHave").style.color = ok ? "var(--good)" : "var(--bad)";
  $("#thrHave").textContent = R.alinan ? `tutan: 10'da ${on(have)}` : "";
  $("#why").innerHTML = R.oKaz == null || R.oKay == null ? "Yeterli veri yok." :
    `Bir sinyal tutunca ortalama <b class="pos">${fmtPct(R.oKaz)}</b> kazanılıyor, tutmayınca ortalama <b class="neg">${fmtPct(R.oKay)}</b> kaybediliyor. ` +
    `Kayıplar kazançlardan büyük olduğu için yarısının tutması yetmiyor; <b>10'da ${on(need)}</b> tutması lazım. Gerçekte <b>10'da ${on(have)}</b> tuttu` +
    (ok ? `, yani şimdilik yetiyor.` : `, yani yetmiyor.`) + (R.kacti ? ` Ayrıca ${R.kacti} sinyalde fiyat, mesaj gelene kadar çok yükselmişti; o sinyallere girilemedi.` : "");
  equity(); list();
}

function equity(){
  const box = $("#eqBox"), tip = $("#tip"); box.querySelectorAll("svg").forEach(s => s.remove());
  const pts = R.eq, W = box.clientWidth || 600, H = 230, p = {l: 62, r: 10, t: 10, b: 22}, n = pts.length - 1;
  const vs = pts.map(d => d.v).concat([S.cap]), lo = Math.min(...vs), hi = Math.max(...vs), pad = (hi - lo) * .12 || hi * .02, y0 = lo - pad, y1 = hi + pad;
  const X = i => p.l + (n ? i / n : 0) * (W - p.l - p.r), Y = v => p.t + (1 - (v - y0) / (y1 - y0)) * (H - p.t - p.b);
  let g = `<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--series)" stop-opacity=".22"/><stop offset="1" stop-color="var(--series)" stop-opacity="0"/></linearGradient></defs>`;
  for (let k = 0; k <= 3; k++){ const v = y0 + (y1 - y0) * k / 3; g += `<line x1="${p.l}" x2="${W - p.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--grid)"/><text x="${p.l - 8}" y="${Y(v) + 4}" text-anchor="end">${fmtUsd(v)}</text>`; }
  g += `<line x1="${p.l}" x2="${W - p.r}" y1="${Y(S.cap)}" y2="${Y(S.cap)}" stroke="var(--t3)" stroke-dasharray="3 4"/>`;
  const path = pts.map((d, i) => (i ? "L" : "M") + X(i).toFixed(1) + "," + Y(d.v).toFixed(1)).join("");
  if (n) g += `<path d="${path}L${X(n)},${H - p.b}L${X(0)},${H - p.b}Z" fill="url(#ag)"/>`;
  g += `<path d="${path}" fill="none" stroke="var(--series)" stroke-width="2" stroke-linejoin="round"/>`;
  g += `<circle cx="${X(n)}" cy="${Y(pts[n].v)}" r="4.5" fill="${R.son >= S.cap ? "var(--good)" : "var(--bad)"}" stroke="var(--solid)" stroke-width="2"/>`;
  g += `<text x="${p.l}" y="${H - 4}">ilk sinyal</text><text x="${W - p.r}" y="${H - 4}" text-anchor="end">son sinyal</text>`;
  g += `<line id="cx" y1="${p.t}" y2="${H - p.b}" stroke="var(--t3)" opacity="0"/><circle id="cd" r="5" fill="var(--series)" stroke="var(--solid)" stroke-width="2" opacity="0"/><rect id="hit" x="${p.l}" y="0" width="${W - p.l - p.r}" height="${H}" fill="transparent"/>`;
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("width", "100%"); svg.setAttribute("height", H); svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "Sanal kasanın sinyal sinyal değişimi");
  svg.innerHTML = g; box.appendChild(svg);
  const cx = svg.querySelector("#cx"), cd = svg.querySelector("#cd");
  svg.querySelector("#hit").addEventListener("pointermove", ev => {
    const r = svg.getBoundingClientRect(), x = (ev.clientX - r.left) * W / r.width, i = Math.max(0, Math.min(n, Math.round((x - p.l) / (W - p.l - p.r) * n))), d = pts[i];
    cx.setAttribute("x1", X(i)); cx.setAttribute("x2", X(i)); cx.setAttribute("opacity", 1); cd.setAttribute("cx", X(i)); cd.setAttribute("cy", Y(d.v)); cd.setAttribute("opacity", 1);
    tip.innerHTML = !d.r ? `<b>Başlangıç</b> · ${fmtUsd(d.v)}` : `<b>${d.r.s.ticker}</b> <span class="mut">${d.r.s.tarih} ${d.r.s.saat_tr}</span><br><span class="${cls(d.r.b.ret)}">${fmtPct(d.r.b.ret)}</span> → kasa ${fmtUsd(d.v)}`;
    tip.style.left = Math.min(X(i) * r.width / W + 12, r.width - tip.offsetWidth - 4) + "px"; tip.style.top = Math.max(0, Y(d.v) * r.height / H - 50) + "px"; tip.style.opacity = 1;
  });
  svg.querySelector("#hit").addEventListener("pointerleave", () => { tip.style.opacity = 0; cx.setAttribute("opacity", 0); cd.setAttribute("opacity", 0); });
}

function list(){
  const win = r => r.b.durum === "alindi" && r.b.ret > 0, loss = r => r.b.durum === "alindi" && r.b.ret <= 0, miss = r => r.b.durum !== "alindi";
  const F = [["all", "Hepsi", R.rows.length], ["win", "Kâr", R.rows.filter(win).length], ["loss", "Zarar", R.rows.filter(loss).length], ["miss", "Girilemedi", R.rows.filter(miss).length]];
  $("#filters").innerHTML = F.map(([k, t, c]) => `<button class="fchip" aria-pressed="${k === S.filt}" data-f="${k}">${t} <b>${c}</b></button>`).join("");
  $$("#filters .fchip").forEach(b => b.onclick = () => { S.filt = b.dataset.f; S.show = 10; list(); });
  const L = R.rows.filter(S.filt === "win" ? win : S.filt === "loss" ? loss : S.filt === "miss" ? miss : () => true).sort((a, b) => a.s.time < b.s.time ? -1 : 1);
  $("#list").innerHTML = L.slice(0, S.show).map(r => {
    const b = r.b, kanalK = r.s.iddia != null ? "TP1" : r.k.sonuc;
    return `<button class="row" data-id="${r.s.id}" aria-label="${r.s.ticker} sinyalinin grafiğini aç">
      <div><div class="tk">${r.s.ticker}</div><div class="tm">${r.s.tarih} · ${r.s.saat_tr}</div></div>
      <div class="cmp"><span class="mut">Kanal:</span>${badge(kanalK)}<span class="ar">→</span><span class="mut">Gerçek:</span>${badge(b.durum === "alindi" ? b.sonuc : b.durum)}</div>
      <div class="res ${b.durum === "alindi" ? cls(b.ret) : "mut"}">${b.durum === "alindi" ? fmtPct(b.ret) : "–"}</div><span class="chev">›</span></button>`;
  }).join("") || `<div style="padding:20px;color:var(--t3)">Bu filtrede sinyal yok.</div>`;
  $$("#list .row").forEach(el => el.onclick = () => openModal(+el.dataset.id));
  $("#more").innerHTML = L.length > S.show ? `<button class="btn" id="moreBtn">${L.length - S.show} sinyal daha</button>` : "";
  if ($("#moreBtn")) $("#moreBtn").onclick = () => { S.show += 20; list(); };
}

/* ---------- kanit ---------- */
let lastFocus = null;
function openModal(id){
  const r = R.rows.find(x => x.s.id === id); if (!r) return;
  lastFocus = document.activeElement;
  const b = r.b, s = r.s, g = r.g;
  $("#mSub").textContent = `${s.tarih} · ${s.saat_tr} Türkiye (${s.saat} New York)`;
  $("#mTitle").textContent = s.ticker;
  const kanal = s.iddia != null ? `Kanal bu sinyali özetinde <b>${fmtPct(s.iddia)} kâr</b> diye yazmış.` : `Kanalın usulüyle: <b>${(SON[r.k.sonuc] || [r.k.sonuc])[0]}</b>.`;
  const dk = m => m < 1 ? "1 dakika içinde" : m < 60 ? `${m} dakika sonra` : `${Math.floor(m / 60)} saat ${m % 60} dakika sonra`;
  let ger;
  if (b.durum === "alindi"){
    const nasil = b.sonuc === "STOP" ? `fiyat zarar kes seviyesine ($${fmtP(g.stop)}) düştü ve zararla satıldı` : (b.sonuc || "").startsWith("TP") ? `fiyat hedefe çıktı ve kârla satıldı` : b.sonuc === "basabas_stop" ? `yarısı kârla satıldı, kalanı alış fiyatına geri dönünce satıldı` : `gün sonuna kadar sonuçlanmadı, son fiyattan satıldı`;
    ger = `Gerçekte: $${fmtP(b.alis)} fiyatından alındı, ${dk(b.sure)} ${nasil}. Sonuç: <b class="${cls(b.ret)}">${fmtPct(b.ret)}</b> (ücret ve kayma dahil).`;
  } else if (b.durum === "kacti") ger = `Gerçekte: Mesaj geldiğinde fiyat alış seviyesinin çok üstündeydi ($${fmtP(g.entry)} yerine daha yukarıda). O fiyattan almak mantıksız olduğu için <b>girilemedi</b>.`;
  else if (b.durum === "kirilim_olmadi") ger = `Gerçekte: Mesajdan sonraki ${A.giris_dk} dakikada fiyat alış seviyesine ($${fmtP(g.entry)}) <b>hiç gelmedi</b>, girilemedi. (Veri eksikliğinden de olabilir; grafiğe bak.)`;
  else ger = `Bu sinyal için fiyat verisi bulunamadı.`;
  $("#mStory").innerHTML = kanal + "<br>" + ger + (s.stop_tahmin ? ` <span class="mut">Zarar kes seviyesi tahmindir (%${String(S.stop).replace(".", ",")}).</span>` : "");
  $("#mMsg").textContent = (s.raw || "").replace(/^\[HAFTALIK ÖZETTEN[^\]]*\]\s*/, "") || "(mesaj metni yok)";
  candles(r);
  $("#modal").classList.add("open"); document.body.classList.add("modal-open"); $("#modal .icon-btn").focus();
}
function closeModal(){ $("#modal").classList.remove("open"); document.body.classList.remove("modal-open"); lastFocus?.focus(); }
$$("#modal [data-close]").forEach(el => el.onclick = closeModal);
addEventListener("keydown", e => { if (e.key === "Escape" && $("#modal").classList.contains("open")) closeModal(); });

function candles(r){
  const box = $("#mChart"), B = r.s.B, P = r.s.P, g = r.g, b = r.b;
  if (!B || !B.n){ box.innerHTML = `<div style="padding:40px;text-align:center;color:var(--t3)">Fiyat verisi yok.</div>`; return; }
  const pre = P ? P.n : 0, endA = Math.min(B.n, Math.max(40, (b.ci ?? b.gi ?? 0) + 12));
  const bars = [];
  for (let i = 0; i < pre; i++) bars.push({o: P.o[i], h: P.h[i], l: P.l[i], c: P.c[i], t: P.t[i], pre: true});
  for (let i = 0; i < endA; i++) bars.push({o: B.o[i], h: B.h[i], l: B.l[i], c: B.c[i], t: B.t[i]});
  const W = Math.max(520, box.clientWidth - 20 || 560), H = 300, p = {l: 6, r: 92, t: 10, b: 22};
  const lv = [g.stop, g.entry, g.tp1, g.tp2].filter(x => x);
  const lo = Math.min(...bars.map(x => x.l), ...lv), hi = Math.max(...bars.map(x => x.h), ...lv), pad = (hi - lo) * .06;
  const Y = v => p.t + (1 - (v - (lo - pad)) / ((hi - lo + 2 * pad) || 1)) * (H - p.t - p.b);
  const bw = (W - p.l - p.r) / bars.length, X = k => p.l + k * bw + bw / 2;
  const tm = t => new Date(t * 60000).toLocaleTimeString("tr-TR", {hour: "2-digit", minute: "2-digit", timeZone: "Europe/Istanbul"});
  let s = "";
  const hl = (v, c, t) => { s += `<line x1="${p.l}" x2="${W - p.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="${c}" stroke-width="1.2" stroke-dasharray="4 3"/><text x="${W - p.r + 6}" y="${Y(v) + 4}" style="fill:${c}">${t} ${fmtP(v)}</text>`; };
  hl(g.entry, "var(--t1)", "AL"); hl(g.stop, "var(--bad)", "STOP"); hl(g.tp1, "var(--good)", "HEDEF"); if (g.tp2) hl(g.tp2, "var(--good)", "HEDEF2");
  if (pre) s += `<line x1="${p.l + pre * bw}" x2="${p.l + pre * bw}" y1="${p.t}" y2="${H - p.b}" stroke="var(--accent)" stroke-width="1.5"/><text x="${p.l + pre * bw + 4}" y="${p.t + 10}" style="fill:var(--accent)">mesaj</text>`;
  bars.forEach((x, k) => {
    const col = x.c >= x.o ? "var(--up)" : "var(--down)", c = X(k), op = x.pre ? .4 : 1;
    s += `<line x1="${c}" x2="${c}" y1="${Y(x.h)}" y2="${Y(x.l)}" stroke="${col}" opacity="${op}"/>`;
    const a = Y(Math.max(x.o, x.c)), z = Y(Math.min(x.o, x.c));
    s += `<rect x="${c - Math.max(1, bw * .32)}" y="${a}" width="${Math.max(2, bw * .64)}" height="${Math.max(1, z - a)}" fill="${col}" opacity="${op}"><title>${tm(x.t)} · açılış ${fmtP(x.o)}, en yüksek ${fmtP(x.h)}, en düşük ${fmtP(x.l)}, kapanış ${fmtP(x.c)}</title></rect>`;
  });
  if (b.durum === "alindi"){
    s += `<path d="M${X(pre + b.gi)},${Y(b.alis) + 6}l-6,10h12z" fill="var(--accent)"/>`;
    if (pre + b.ci < bars.length) s += `<path d="M${X(pre + b.ci)},${Y(b.alis * (1 + b.ret)) - 6}l-6,-10h12z" fill="${b.ret > 0 ? "var(--good)" : "var(--bad)"}"/>`;
  }
  [0, Math.floor(bars.length / 2), bars.length - 1].forEach((k, j) => s += `<text x="${X(k)}" y="${H - 6}" text-anchor="${["start", "middle", "end"][j]}">${tm(bars[k].t)}</text>`);
  box.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="${r.s.ticker} dakikalık fiyat grafiği">${s}</svg>`;
}

/* ---------- girisler ---------- */
$("#inCap").addEventListener("change", e => { const v = +String(e.target.value).replace(/[^\d]/g, ""); if (v >= 1){ S.cap = v; render(); } else e.target.value = Math.round(S.cap).toLocaleString("tr-TR"); });
$("#inCap").addEventListener("keydown", e => { if (e.key === "Enter") e.target.blur(); });
$("#inStop").addEventListener("input", e => { S.stop = +e.target.value; render(); });
$("#resetBtn").onclick = () => { Object.assign(S, DEF); render(); };
$("#rules").innerHTML = [
  `<b>Gerçek fiyatlar:</b> Her sinyalden sonraki dakikalara Yahoo Finance'in 1 dakikalık fiyatlarıyla bakıldı (piyasa öncesi dahil).`,
  `<b>Sanal hesap:</b> Her sinyale kasanın %${Math.round(POZ * 100)}'u konuldu. Gerçek para kullanılmadı.`,
  `<b>Ücret ve kayma:</b> Alışta ve satışta fiyat %${A.kayma * 100} daha kötü sayıldı, her işlemde %${(A.komisyon * 100).toFixed(1)} ücret düşüldü.`,
  `<b>Yetişememe:</b> Mesaj geldiğinde fiyat alış seviyesinin %${A.maks_kovalama * 100}'ünden fazla üstündeyse alım yapılmadı. ${A.giris_dk} dakika içinde fiyat gelmezse sinyal iptal sayıldı.`,
  `<b>Belirsiz anlar:</b> Aynı dakikada hem hedef hem zarar kes görüldüyse zarar sayıldı (dakikanın içindeki sırayı bilemeyiz).`,
  SIG.some(s => s.stop_tahmin) ? `<b>Tahmin:</b> Kanalın özetinde zarar kes seviyesi yazmadığı için %7,5 varsayıldı. "Farklı varsayımlarla dene" bölümünden değiştirebilirsin.` : "",
  `<b>Verinin sınırları:</b> Küçük hisselerde bazı dakikalarda hiç işlem olmaz ve veri eksik olabilir. "Fiyat gelmedi" görünen bir sinyal bundan da kaynaklanabilir.`,
  `<b>Örneklem:</b> ${SIG.length} sinyal. ${SIG.length < 50 ? "Kesin hüküm için az; en az 50-100 sinyal gerekir." : "Daha fazla sinyal sonucu daha güvenilir yapar."}`,
  `<b>Bu bir yargı değil:</b> Sayfa kanalın niyetini bilemez. Sadece aynı sinyallerin gerçek fiyatlarla nasıl sonuçlanacağını gösterir.`
].filter(Boolean).map(x => `<li>${x}</li>`).join("");
$("#gloss").innerHTML = [["Alış seviyesi", "Kanalın \"fiyat buraya gelince al\" dediği fiyat."], ["Zarar kes (stop)", "\"Buraya düşerse sat, daha fazla kaybetme\" denen fiyat."],
  ["Hedef", "Kâr al seviyesi. Fiyat buraya çıkınca satılır."], ["Kayma", "Gerçekte tam istenen fiyattan değil, biraz kötüsünden alınıp satılır."],
  ["Yetişilemedi", "Mesaj gelene kadar fiyat çok yükselmiş, girilemedi."], ["Başa baş", "Kazancın kaybı tam karşıladığı nokta."]]
  .map(([b, p]) => `<div><b>${b}</b><p>${p}</p></div>`).join("");
$("#foot").textContent = `Sinyal Karnesi · üretildi ${V.meta.uretim} · Sanal hesaptır, gerçek işlem yapılmadı. Yatırım tavsiyesi değildir.`;

/* ---------- tema, kar ---------- */
let THEME = store.get("sk-tema") || "dark";
function setTheme(t){ THEME = t; document.documentElement.dataset.theme = t; $("#i-moon").style.display = t === "dark" ? "" : "none"; $("#i-sun").style.display = t === "light" ? "" : "none"; store.set("sk-tema", t); }
$("#themeBtn").onclick = () => setTheme(THEME === "dark" ? "light" : "dark");
(() => {
  const red = matchMedia("(prefers-reduced-motion: reduce)").matches, cv = $("#snow"), c = cv.getContext("2d"); let W, H, dpr, fl = [];
  const size = () => { dpr = Math.min(devicePixelRatio || 1, 2); W = cv.width = innerWidth * dpr; H = cv.height = innerHeight * dpr; cv.style.width = innerWidth + "px"; cv.style.height = innerHeight + "px"; };
  size(); addEventListener("resize", size);
  for (let i = 0; i < (red ? 0 : 40); i++) fl.push({x: Math.random(), y: Math.random(), r: Math.random() * 1.4 + .5, s: Math.random() * .25 + .12, w: Math.random() * 7, o: Math.random() * .3 + .12});
  (function f(){ c.clearRect(0, 0, W, H); const col = getComputedStyle(document.documentElement).getPropertyValue("--snow").trim();
    for (const q of fl){ q.y += q.s * .0016; q.w += .01; q.x += Math.sin(q.w) * .0003; if (q.y > 1.02){ q.y = -.02; q.x = Math.random(); } c.beginPath(); c.arc(q.x * W, q.y * H, q.r * dpr, 0, 7); c.fillStyle = `rgba(${col},${q.o})`; c.fill(); }
    requestAnimationFrame(f); })();
})();
let rz; addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(equity, 120); });
setTheme(THEME);
render();
window.__SK = {hesapla, S};
</script>
</body>
</html>
"""
