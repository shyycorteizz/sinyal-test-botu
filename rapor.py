"""Analiz sonucunu tek dosyalik, internetsiz calisan bir HTML paneline cevirir."""
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
    """NaN -> None (JSON'da gecersiz)."""
    if isinstance(x, dict):
        return {k: _temiz(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_temiz(v) for v in x]
    if isinstance(x, float) and x != x:
        return None
    return x


def html_yaz(sonuc: dict, yol: Path):
    veri = json.dumps(_temiz(sonuc), default=_json_default, ensure_ascii=False)
    veri = veri.replace("</", "<\\/")
    fontlar = Path(__file__).with_name("fonts.css")
    css = fontlar.read_text(encoding="utf-8") if fontlar.exists() else ""
    Path(yol).write_text(SABLON.replace("/*__FONTS__*/", css).replace("/*__VERI__*/null", veri), encoding="utf-8")


SABLON = r"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sinyal Karnesi</title>
<style>
/*__FONTS__*/
:root{--font:'Geist',Inter,system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'Geist Mono',ui-monospace,Menlo,monospace;--serif:'Instrument Serif',Georgia,serif;
  --ease:cubic-bezier(.22,.8,.24,1);--spring:cubic-bezier(.3,1.5,.5,1)}
:root,[data-theme="dark"]{
  color-scheme:dark;
  --bg:#040405; --surface-1:rgba(255,255,255,.022); --surface-solid:#0c0c10; --surface-2:#131318; --line:rgba(255,255,255,.06); --line-2:rgba(255,255,255,.12);
  --text-primary:#f3f4f8; --text-secondary:#c4c7d4; --text-muted:#8a8ea0; --faint:#5d6174;
  --series-1:#8b9bff; --series-2:#d95926; --series-3:#5ee6c8; --accent:#b8c4ff; --accent-2:#8ee6d4; --accent-3:#f6b8d8;
  --good:#3ddc84; --critical:#ff6b6b; --warning:#fab219; --serious:#ec835a; --grid:rgba(255,255,255,.06);
  --aur-1:rgba(110,125,255,.09); --aur-2:rgba(94,234,212,.04); --aur-3:rgba(200,140,252,.04);
  --btn:#f3f4f8; --btn-ink:#040405; --shadow:0 30px 80px -30px rgba(0,0,0,.9); --snow:220,225,255;
}
[data-theme="light"]{
  color-scheme:light;
  --bg:#f6f7fb; --surface-1:rgba(255,255,255,.75); --surface-solid:#ffffff; --surface-2:#eef0f7; --line:rgba(20,24,48,.08); --line-2:rgba(20,24,48,.16);
  --text-primary:#12131a; --text-secondary:#3c3f50; --text-muted:#646879; --faint:#9497a6;
  --series-1:#4f5bd5; --accent:#4f5bd5; --accent-2:#0e9f84; --accent-3:#d9468f;
  --good:#0b8a3e; --critical:#d03b3b; --grid:rgba(20,24,48,.07);
  --aur-1:rgba(129,140,248,.24); --aur-2:rgba(45,212,191,.15); --aur-3:rgba(244,114,182,.12);
  --btn:#12131a; --btn-ink:#ffffff; --shadow:0 30px 70px -34px rgba(40,50,110,.35); --snow:150,165,220;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text-primary);font:14.5px/1.55 var(--font);-webkit-font-smoothing:antialiased;overflow-x:hidden;transition:background .5s var(--ease),color .5s var(--ease)}
::selection{background:var(--accent);color:var(--bg)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:8px}
.aurora{position:fixed;inset:-20vh -10vw auto;height:110vh;z-index:-1;pointer-events:none;overflow:hidden}
.aurora i{position:absolute;border-radius:50%;filter:blur(70px)}
.aurora i:nth-child(1){width:52vw;height:42vh;left:40%;top:4%;background:var(--aur-1);animation:d1 22s ease-in-out infinite}
.aurora i:nth-child(2){width:40vw;height:36vh;left:64%;top:28%;background:var(--aur-2);animation:d2 26s ease-in-out infinite}
.aurora i:nth-child(3){width:34vw;height:30vh;left:14%;top:-6%;background:var(--aur-3);animation:d3 30s ease-in-out infinite}
@keyframes d1{50%{transform:translate(-8vw,6vh) scale(1.12)}}@keyframes d2{50%{transform:translate(-10vw,-4vh) scale(.9)}}@keyframes d3{50%{transform:translate(10vw,8vh) scale(1.15)}}
.grain{position:fixed;inset:0;z-index:-1;pointer-events:none;opacity:.035;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
#snow{position:fixed;inset:0;z-index:0;pointer-events:none}
.wrap{position:relative;z-index:1;max-width:1180px;margin:0 auto;padding:0 28px 60px}
.mono{font-family:var(--mono)}
.serif{font-family:var(--serif);font-style:italic;font-weight:400;letter-spacing:-.02em;background:linear-gradient(100deg,var(--text-primary) 0%,var(--accent) 55%,var(--accent-2) 110%);-webkit-background-clip:text;background-clip:text;color:transparent;padding-right:.08em}
h1,h2{margin:0;font-weight:600;letter-spacing:-.04em;color:var(--text-primary)}
h2{font-size:17px;letter-spacing:-.02em}
.sub{color:var(--text-secondary);font-size:13px}
.muted{color:var(--text-muted)}
.pos{color:var(--good)} .neg{color:var(--critical)}

/* top bar */
.top{position:sticky;top:0;z-index:20;margin:0 -28px;padding:0 28px;transition:background .3s,border-color .3s;border-bottom:1px solid transparent}
.top.scrolled{background:color-mix(in srgb,var(--bg) 72%,transparent);backdrop-filter:blur(18px) saturate(1.4);-webkit-backdrop-filter:blur(18px) saturate(1.4);border-bottom-color:var(--line)}
.top-in{height:68px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:19px;letter-spacing:-.045em}
.logo-ic{width:30px;height:30px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent-2));display:grid;place-items:center;color:#fff}
.top-r{display:flex;align-items:center;gap:10px}
.badge-live{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 12px;border-radius:999px;border:1px solid var(--line);background:var(--surface-1);font:400 11.5px var(--mono);color:var(--text-secondary)}
.dot{width:7px;height:7px;border-radius:50%;background:#5ee6a8;animation:ping 2.4s infinite}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(94,230,168,.45)}70%,100%{box-shadow:0 0 0 7px rgba(94,230,168,0)}}
.icon-btn{width:36px;height:36px;border-radius:50%;border:1px solid var(--line);background:var(--surface-1);display:grid;place-items:center;cursor:pointer;color:var(--text-primary);transition:transform .3s var(--spring)}
.icon-btn:hover{transform:rotate(-14deg) scale(1.06)}

/* hero */
.hero{display:grid;grid-template-columns:1.25fr .75fr;gap:24px;align-items:center;padding:52px 0 30px}
.eyebrow{display:inline-flex;align-items:center;gap:9px;padding:6px 13px 6px 11px;border-radius:999px;border:1px solid var(--line);background:var(--surface-1);font:400 12px var(--mono);color:var(--text-secondary)}
.hero h1{margin-top:22px;font-size:clamp(44px,5.8vw,78px);line-height:.98;letter-spacing:-.06em}
.hero h1 .serif{font-size:1.06em}
.hero .lead{margin-top:20px;max-width:520px;color:var(--text-muted);font-size:16px}
.rl{display:block;overflow:hidden}.rl>span{display:inline-block;animation:rise 1s var(--ease) both}.rl:nth-child(2)>span{animation-delay:.12s}
@keyframes rise{from{transform:translateY(105%)}to{transform:none}}
.fi{animation:fu .9s var(--ease) both}@keyframes fu{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.verdict{padding:24px 26px;align-self:stretch;display:flex;flex-direction:column;justify-content:center}
.v-lbl{font:500 11px var(--mono);letter-spacing:.04em;color:var(--text-muted)}
.v-row{display:flex;align-items:center;gap:12px;margin-top:14px}
.v-ic{width:36px;height:36px;border-radius:50%;border:1.5px solid;display:grid;place-items:center;flex:none}
.v-d{font-size:26px;font-weight:600;letter-spacing:-.04em}
.v-a{margin:8px 0 16px;font-size:13px;color:var(--text-secondary)}
.v-kv{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-top:1px solid var(--line);font-size:13px;color:var(--text-muted)}
.v-kv b{font:600 13px var(--mono);color:var(--text-primary)}
.v-bar{margin-top:10px;height:4px;border-radius:2px;background:var(--surface-2);overflow:hidden}
.v-bar i{display:block;height:100%;border-radius:2px}
/* cards */
.card{background:var(--surface-1);border:1px solid var(--line);border-radius:24px;padding:22px 24px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:border-color .25s}
.grid{display:grid;gap:14px}
.k4{grid-template-columns:repeat(4,1fr)}
.k2{grid-template-columns:1.6fr 1fr}
.rv{opacity:0;transform:translateY(22px);transition:opacity .8s var(--ease),transform .8s var(--ease)}
.rv.in{opacity:1;transform:none}
.sec-h{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:56px 0 18px}
.sec-h h3{margin:0;font-size:clamp(28px,3.2vw,40px);font-weight:600;letter-spacing:-.05em;line-height:1}
.sec-h h3 .serif{font-size:1.06em}
.sec-h p{margin:0;max-width:380px;color:var(--text-muted);font-size:14px}

/* vs */
.vs{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.vs>div{position:relative;overflow:hidden;padding:26px 28px;border-radius:24px;border:1px solid var(--line);background:var(--surface-1);backdrop-filter:blur(12px)}
.vs>div::before{content:"";position:absolute;width:260px;height:260px;right:-80px;top:-120px;border-radius:50%;filter:blur(40px);opacity:.45}
.vs>div:first-child::before{background:var(--aur-3)}.vs>div:last-child::before{background:var(--aur-1)}
.vs .t{position:relative;font-size:13px;color:var(--text-secondary)}
.vs .lbl{position:relative;display:inline-flex;align-items:center;gap:8px;font:500 11.5px var(--mono);color:var(--text-muted);margin-bottom:14px}
.vs .big{position:relative;font-size:clamp(40px,5vw,60px);font-weight:600;letter-spacing:-.055em;line-height:1.05;font-variant-numeric:tabular-nums;margin:4px 0 10px}
.note{margin-top:14px;padding:16px 20px;border-radius:18px;background:var(--surface-1);border:1px solid var(--line);color:var(--text-secondary);font-size:14px;line-height:1.7;backdrop-filter:blur(12px)}
.note b{color:var(--text-primary)}

/* controls */
.controls{position:sticky;top:76px;z-index:15;display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:28px 0 14px;padding:8px;border-radius:999px;width:max-content;max-width:100%;background:color-mix(in srgb,var(--bg) 70%,transparent);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid var(--line)}
.controls .sub{padding-left:10px}
.seg{display:inline-flex;background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:3px}
.seg button{all:unset;cursor:pointer;padding:6px 13px;border-radius:999px;color:var(--text-muted);font-size:13px;transition:background .2s,color .2s}
.seg button:hover{color:var(--text-primary)}
.seg button[aria-pressed="true"]{background:var(--text-primary);color:var(--bg)}
.seg button:focus-visible{outline:2px solid var(--accent)}

.tile{transition:transform .35s var(--spring),border-color .25s}
.tile:hover{transform:translateY(-3px);border-color:var(--line-2)}
.tile .lbl{color:var(--text-muted);font:500 11.5px var(--mono)}
.tile .val{font-size:34px;font-weight:600;letter-spacing:-.05em;margin-top:8px;font-variant-numeric:tabular-nums}
.tile .foot{color:var(--text-muted);font-size:12.5px;margin-top:4px}

svg text{fill:var(--text-muted);font-size:11px;font-family:var(--mono)}
.chartbox{position:relative;margin-top:6px}
.tip{position:absolute;pointer-events:none;background:var(--surface-solid);border:1px solid var(--line);border-radius:12px;padding:8px 12px;font-size:12.5px;white-space:nowrap;opacity:0;transition:opacity .1s;z-index:3;box-shadow:var(--shadow)}
.bars .row{display:grid;grid-template-columns:130px 1fr 40px;gap:12px;align-items:center;margin:10px 0;font-size:13px}
.bars .track{height:10px;background:var(--surface-2);border-radius:6px;overflow:hidden}
.bars .fill{height:100%;border-radius:6px;transition:width .8s var(--ease)}
.bars .n{text-align:right;font:500 13px var(--mono);color:var(--text-secondary)}

table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}
th{font:500 11px var(--mono);letter-spacing:.02em;color:var(--text-muted);text-align:right;padding:10px 12px;border-bottom:1px solid var(--line);cursor:pointer;user-select:none;white-space:nowrap}
th:first-child,td:first-child,th.l,td.l{text-align:left}
td{padding:10px 12px;text-align:right;border-bottom:1px solid var(--grid);white-space:nowrap}
tbody tr{transition:background .15s}
tbody tr:hover td{background:var(--surface-2)}
tbody tr:last-child td{border-bottom:0}
.badge{display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;border:1px solid var(--line);background:var(--surface-1);color:var(--text-primary)}
.badge i{width:7px;height:7px;border-radius:50%;display:inline-block}
.scroll{overflow-x:auto;margin-top:8px}
.matrix tr.sel td{background:var(--surface-2)}
.matrix tr.sel td:first-child{box-shadow:inset 3px 0 0 var(--accent)}
.flag{font-size:11.5px;color:var(--serious)}
footer{margin-top:34px;padding-top:20px;border-top:1px solid var(--line);color:var(--faint);font-size:12px}
.q{display:inline-grid;place-items:center;width:16px;height:16px;margin-left:5px;border-radius:50%;border:1px solid var(--line-2);font:600 10px/1 var(--font);color:var(--text-muted);cursor:help;position:relative;vertical-align:1px;font-style:normal;letter-spacing:0;text-transform:none}
.q:hover,.q:focus{color:var(--text-primary);border-color:var(--text-muted);outline:none}
.q::after{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 8px);transform:translateX(-50%) translateY(4px);width:max-content;max-width:260px;padding:10px 12px;border-radius:12px;background:var(--surface-solid);border:1px solid var(--line-2);color:var(--text-secondary);font:400 12.5px/1.5 var(--font);white-space:normal;text-align:left;box-shadow:var(--shadow);opacity:0;pointer-events:none;transition:opacity .15s,transform .2s;z-index:40}
.q:hover::after,.q:focus::after{opacity:1;transform:translateX(-50%)}
th .q::after{bottom:auto;top:calc(100% + 8px)}
.scroll{padding-bottom:4px}
.plain{margin-top:6px;padding:26px 30px;border-radius:24px;border:1px solid var(--line);background:var(--surface-1);backdrop-filter:blur(12px)}
.plain .k{font:500 11px var(--mono);letter-spacing:.04em;color:var(--text-muted)}
.plain .s{margin-top:10px;font-size:clamp(20px,2.3vw,27px);line-height:1.4;letter-spacing:-.025em;font-weight:500;color:var(--text-secondary)}
.plain .s b{color:var(--text-primary);font-weight:600}
.plain .steps{margin-top:18px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.plain .steps div{padding:14px 16px;border-radius:16px;background:var(--surface-2);font-size:13px;color:var(--text-secondary)}
.plain .steps b{display:block;font:600 11px var(--mono);color:var(--text-muted);margin-bottom:4px}
.gloss{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.gloss div{padding:18px 20px;border-radius:18px;border:1px solid var(--line);background:var(--surface-1)}
.gloss b{display:block;font-size:15px;letter-spacing:-.02em}
.gloss i{font-style:normal;font:400 11px var(--mono);color:var(--text-muted)}
.gloss p{margin:6px 0 0;font-size:13.5px;color:var(--text-secondary)}
@media(max-width:900px){.gloss,.plain .steps{grid-template-columns:1fr}}
.tbar{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
@media(max-width:900px){.hero{grid-template-columns:1fr}.k4{grid-template-columns:repeat(2,1fr)}.k2,.vs{grid-template-columns:1fr}.controls{position:static;border-radius:20px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important}.rv{opacity:1;transform:none}}
</style>
</head>
<body>
<div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="grain" aria-hidden="true"></div>
<canvas id="snow" aria-hidden="true"></canvas>
<div class="wrap">
  <div class="top" id="top">
    <div class="top-in">
      <div class="logo"><span class="logo-ic"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8M15 7h6v6"/></svg></span>sinyal karnesi</div>
      <div class="top-r">
        <span class="badge-live"><span class="dot"></span><span id="aralik"></span></span>
        <button class="icon-btn" id="themeBtn" aria-label="tema">
          <svg id="i-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
          <svg id="i-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
        </button>
      </div>
    </div>
  </div>

  <section class="hero" id="hero">
    <div>
      <div class="eyebrow fi"><span class="dot"></span><span id="kanalAd"></span></div>
      <h1><span class="rl"><span>kanal ne diyor,</span></span><span class="rl"><span class="serif">gerçekte ne oldu?</span></span></h1>
      <p class="lead fi" style="animation-delay:.25s">Kanal "şu hisseyi şu fiyattan al" diyor. Bu sayfa, o mesajlara gerçekten uysaydın <b>paranın ne olacağını</b> hesaplıyor. Gerçek para kullanılmadı; her şey sanal.</p>
    </div>
    <div class="verdict card fi" style="animation-delay:.2s" id="verdict"></div>
  </section>

  <section class="plain rv" id="ozet"></section>

  <div class="sec-h rv"><h3>iki farklı <span class="serif">hesap</span></h3><p>Kanal sadece kazandıran sinyalleri sayıyor. Biz kaybettirenleri de, geç kalmayı da sayıyoruz.</p></div>
  <section class="vs rv">
    <div>
      <div class="lbl">KANALIN GÖSTERDİĞİ</div>
      <div class="t">Sadece kazandıran sinyallerin yüzdeleri toplanmış hâli</div>
      <div class="big" id="kanalIddia"></div>
      <div class="t" id="kanalIddiaAlt"></div>
    </div>
    <div>
      <div class="lbl">GERÇEKTE OLACAK OLAN</div>
      <div class="t">Sanal hesabının toplam kâr / zararı</div>
      <div class="big" id="botGercek"></div>
      <div class="t" id="botGercekAlt"></div>
    </div>
  </section>
  <div class="note rv" id="yorum"></div>

  <div class="controls">
    <span class="sub">ya şöyle olsaydı?</span>
    <div class="seg" id="segGecikme" role="group" aria-label="Gecikme"></div>
    <div class="seg" id="segMod" role="group" aria-label="Satış modu"></div>
  </div>

  <section class="grid k4 rv" id="tiles"></section>

  <div class="sec-h rv"><h3>paran <span class="serif">nasıl değişti?</span></h3><p>Çizgi yukarı gidiyorsa para artıyor, aşağı gidiyorsa azalıyor. Kesikli çizgi başladığın para. Üstünde gezinince her sinyal tek tek görünür.</p></div>
  <section class="grid k2 rv">
    <div class="card">
      <h2>Sanal hesabın</h2>
      <div class="sub" id="egriAlt"></div>
      <div class="chartbox" id="egriBox"><div class="tip" id="tip"></div></div>
    </div>
    <div class="card">
      <h2>Sinyallerin sonu ne oldu?</h2>
      <div class="sub">Yeşil = kâr, kırmızı = zarar, gri = alınamadı</div>
      <div class="bars" id="dagilim" style="margin-top:14px"></div>
    </div>
  </section>

  <div class="sec-h rv"><h3>hızlı olmak <span class="serif">ne kadar önemli?</span></h3><p>Aynı sinyaller, farklı hızlarda. Sinyale geç kalınca sonuç nasıl değişiyor, buradan bak. Bir satıra tıklarsan bütün sayfa o duruma göre hesaplanır.</p></div>
  <section class="card rv">
    <div class="scroll"><table class="matrix" id="matrix"></table></div>
  </section>

  <div class="sec-h rv"><h3>tek tek <span class="serif">sinyaller</span></h3><p>Kanalın attığı her sinyal ve başına gelen. Saatler Türkiye (TR) ve Amerika (NY) saatiyle. Sütun başlığına tıklarsan sıralanır.</p></div>
  <section class="card rv">
    <div class="tbar"><div class="sub">Filtre</div><div class="seg" id="segFiltre" role="group" aria-label="Filtre"></div></div>
    <div class="scroll"><table id="tablo"></table></div>
  </section>

  <div class="sec-h rv"><h3>terimler <span class="serif">sözlüğü</span></h3><p>Sayfada ya da kanalda gördüğün kelimelerin anlamı. Hepsini bilmek zorunda değilsin.</p></div>
  <section class="gloss rv" id="sozluk"></section>

  <footer id="foot"></footer>
</div>

<script>
const V = /*__VERI__*/null;
const $ = s => document.querySelector(s);
const pct = (x, s = true, d = 2) => x == null ? "–" : (x < 0 ? "−" : s && x > 0 ? "+" : "") + "%" + Math.abs(100 * x).toFixed(d).replace(".", ",");
const usd = x => "$" + Math.round(x).toLocaleString("tr-TR");
const cls = x => x == null ? "" : x > 0 ? "pos" : x < 0 ? "neg" : "";
let G = "g0", M = "tp1", F = "hepsi", sortKey = "time", sortDir = 1;

// --- tema
const savedTheme = (() => { try { return localStorage.getItem("sk-tema"); } catch (e) { return null; } })();
let THEME = "dark";
function setTheme(t) {
  THEME = t;
  document.documentElement.dataset.theme = t;
  $("#i-moon").style.display = t === "dark" ? "" : "none";
  $("#i-sun").style.display = t === "light" ? "" : "none";
  try { localStorage.setItem("sk-tema", t); } catch (e) {}
  render();
}
$("#themeBtn").onclick = () => setTheme(THEME === "dark" ? "light" : "dark");

// --- sozluk + aciklama baloncuklari
const GL = {
  sinyal: ["Sinyal", "Kanalın attığı \"şu hisseyi şu fiyattan al\" mesajı."],
  kirilim: ["Kırılım (alış seviyesi)", "Kanalın \"fiyat buraya gelince al\" dediği fiyat."],
  stop: ["Stop (zarar kes)", "İşler ters giderse \"buraya düşerse sat, daha fazla kaybetme\" denen fiyat. Stop olmak = zararla çıkmak."],
  tp1: ["TP1 (1. hedef)", "TP = Take Profit, yani kâr al. Fiyat buraya çıkınca satıp kârı cebe koyuyorsun."],
  tp2: ["TP2 (2. hedef)", "Daha yukarıdaki ikinci kâr alma fiyatı. Daha fazla kazandırır ama oraya her zaman çıkmaz."],
  kayma: ["Kayma", "Gerçekte tam istediğin fiyattan alıp satamazsın, biraz daha kötü fiyattan olur. Hesapta bunu %1 saydık."],
  komisyon: ["Komisyon", "Aracı kurumun (Midas vb.) her alım-satımda aldığı küçük ücret."],
  kacti: ["Kaçtı / alınamadı", "Sinyal gelene kadar fiyat çok yükselmiş. O fiyattan almak mantıksız, bot almadı. Kanal ise bunu \"kâr\" sayıyor."],
  basabas: ["Başa baş (kâra geçme eşiği)", "Kazandığın ile kaybettiğinin eşitlendiği nokta. Sinyallerin bu orandan fazlası tutarsa kâr edersin."],
  beklenti: ["Ortalama sonuç (beklenti)", "Bir sinyale uyunca ortalama ne kazanıp ne kaybettiğin. Artıysa uzun vadede kazandırır, eksiyse kaybettirir."],
  dusus: ["En kötü dönem (düşüş)", "Hesabın en yüksek noktasından sonra en fazla ne kadar eridiği. Psikolojik olarak dayanman gereken kayıp."],
  sanal: ["Sanal hesap", "Gerçek para yok. \"10.000 dolarım olsaydı ve her sinyale 1.000 dolar koysaydım\" diye hesaplanıyor."],
  gecikme: ["Gecikme", "Sinyal geldikten sonra kaç dakikada alım yaptığın. Telefondan elle almak birkaç dakika sürer; bot saniyeler içinde alır."],
  ornek: ["Örneklem", "Kaç sinyale bakıldığı. 10-20 sinyal şans olabilir; 50-100 sinyal gerçeği daha iyi gösterir."],
  silinen: ["Silinen sinyal", "Kanalın attığı ama sonradan sildiği sinyal. Genelde kaybettirenler silinir. Bot ilk hâlini sakladı."],
};
const q = k => `<span class="q" tabindex="0" data-tip="${GL[k][1].replace(/"/g, "&quot;")}">?</span>`;

const SONUC = {
  "TP1": ["Kâr (1. hedef)", "var(--good)"], "TP1+TP2": ["Kâr (2 hedef de)", "var(--good)"],
  "TP1+gun_sonu": ["Kâr (gün sonu kapandı)", "var(--good)"], "basabas_stop": ["Kâr aldı, kalanı 0'da çıktı", "var(--warning)"],
  "STOP": ["Zarar (stop oldu)", "var(--critical)"], "gun_sonu": ["Gün bitti, kapatıldı", "var(--warning)"],
  "kacti": ["Yetişemedi, alınmadı", "var(--text-muted)"], "iptal_once_stop": ["İptal", "var(--text-muted)"],
  "kirilim_olmadi": ["Fiyat gelmedi, alınmadı", "var(--text-muted)"], "veri_yok": ["Fiyat verisi yok", "var(--text-muted)"],
  "acik_kaldi": ["Sonuçlanmadı", "var(--warning)"],
};
const badge = k => { const [t, c] = SONUC[k] || [k, "var(--text-muted)"]; return `<span class="badge"><i style="background:${c}"></i>${t}</span>`; };

function seg(el, items, cur, on) {
  el.innerHTML = items.map(([k, t]) => `<button data-k="${k}" aria-pressed="${k === cur}">${t}</button>`).join("");
  el.querySelectorAll("button").forEach(b => b.onclick = () => on(b.dataset.k));
}

function render() {
  const S = V.senaryolar[`${G}_${M}`], O = S.ozet, K = V.kanal;
  $("#kanalAd").textContent = V.meta.kanal;
  $("#aralik").textContent = `${V.meta.aralik} · ${V.sinyaller.length} sinyal`;

  seg($("#segGecikme"), [["g0", "Bot anında alsa"], ["g1", "1 dk geç kalsa"], ["g3", "Elle alsan (3 dk)"]], G, k => { G = k; render(); });
  seg($("#segMod"), [["tp1", "1. hedefte sat"], ["kademeli", "Yarısını 1., yarısını 2. hedefte sat"]], M, k => { M = k; render(); });

  // --- kisacasi
  const fark = O.son_sermaye - V.meta.sermaye, kisi = Math.round(V.meta.sermaye * V.meta.poz);
  const sonucCumle = !O.alinan ? `Henüz alınabilen sinyal yok, biraz daha veri birikmesi lazım.`
    : fark >= 0 ? `Bu kanalın sinyallerine uysaydın <b>${usd(V.meta.sermaye)}</b>'ın <b class="pos">${usd(O.son_sermaye)}</b> olurdu. Yani <b class="pos">${usd(fark)} kâr</b>. Kanal ise bunu <b>${pct(K.basit_toplam_sadece_tp)}</b> diye gösteriyor.`
    : `Bu kanalın sinyallerine uysaydın <b>${usd(V.meta.sermaye)}</b>'ın <b class="neg">${usd(O.son_sermaye)}</b>'a düşerdi. Yani <b class="neg">${usd(-fark)} zarar</b>. Kanal ise bunu <b>${pct(K.basit_toplam_sadece_tp)}</b> kâr diye gösteriyor.`;
  $("#ozet").innerHTML = `<div class="k">KISACASI</div><div class="s">${sonucCumle}</div>
    <div class="steps">
      <div><b>1 · NE VARSAYDIK?</b>Elinde ${usd(V.meta.sermaye)} var, her sinyale ${usd(kisi)} koyuyorsun.</div>
      <div><b>2 · NASIL HESAPLADIK?</b>Her sinyalden sonra hissenin gerçek fiyatına baktık: önce kâr hedefine mi çıktı, zarar kes seviyesine mi düştü?</div>
      <div><b>3 · NEYE DİKKAT?</b>${O.sinyal < 50 ? `Daha ${O.sinyal} sinyal var. 50-100 sinyal olmadan kesin karar verme.` : `${O.sinyal} sinyal var, sonuç artık daha güvenilir.`}</div>
    </div>`;

  // --- kanal vs gercek
  $("#kanalIddia").innerHTML = `<span class="${cls(K.basit_toplam_sadece_tp)}">${pct(K.basit_toplam_sadece_tp)}</span>`;
  $("#kanalIddiaAlt").innerHTML = `${K.girilen} sinyalden ${K.tp} tanesi kâr hedefine ulaştı. Zararla bitenler de eklenince bu rakam <b>${pct(K.basit_toplam_dogru)}</b>'e iniyor. Gecikme ve ücretler de hesaba katılınca ise sağdaki gerçek sonuç çıkıyor.`;
  $("#botGercek").innerHTML = `<span class="${cls(O.toplam_getiri)}">${pct(O.toplam_getiri)}</span>`;
  $("#botGercekAlt").innerHTML = `${usd(V.meta.sermaye)} → <b>${usd(O.son_sermaye)}</b>. Durum: ${S.ad.toLowerCase()}, ${S.mod}. ${q("sanal")}`;

  let y = [];
  if (O.alinan && O.basabas_orani != null) {
    const fark = O.kazanma - O.basabas_orani;
    const on = Math.round(O.basabas_orani * 10), tut = Math.round(O.kazanma * 10);
    y.push(`<b>Neden önemli?</b> Kazandığında az (ortalama ${pct(O.ort_kaz)}), kaybettiğinde çok (ortalama ${pct(O.ort_kay)}) gidiyor. Bu yüzden kâra geçmek için <b>her 10 sinyalden en az ${on} tanesinin tutması</b> lazım. Gerçekte <b>10'da ${tut}</b> tutuyor ` +
      (fark >= 0 ? `→ <b class="pos">şimdilik yetiyor</b>.` : `→ <b class="neg">yetmiyor, uzun vadede para kaybettirir</b>.`) + ` ${q("basabas")}`);
  }
  if (O.kacti) y.push(`<b>${O.kacti} sinyale yetişilemedi:</b> mesaj gelene kadar fiyat çoktan yükselmişti. Kanal bunları "kâr" sayıyor ama takip eden biri o fiyattan alamazdı. ${q("kacti")}`);
  if (K.silinen) y.push(`<b>Kanal ${K.silinen} sinyali sonradan sildi.</b> Silinenler genelde kaybettirenlerdir. Bot ilk hâllerini sakladı ve hesaba kattı. ${q("silinen")}`);
  $("#yorum").innerHTML = y.join("<br><br>") || "Henüz yorum için yeterli işlem yok.";

  // --- tiles
  const tiles = [
    ["Kaç sinyal kâr ettirdi?", `${O.kazanc_say ?? 0}/${O.alinan}`, `yani ${pct(O.kazanma, false, 0)} · kâra geçmek için gereken ${pct(O.basabas_orani, false, 0)}`, "", "basabas"],
    ["Sinyal başına ortalama", pct(O.beklenti), `kazanınca ort. ${pct(O.ort_kaz)} · kaybedince ort. ${pct(O.ort_kay)}`, cls(O.beklenti), "beklenti"],
    ["En kötü dönemde kayıp", pct(O.maks_dd ? -O.maks_dd : 0), "paranın en tepeden en fazla eridiği oran", O.maks_dd > 0 ? "neg" : "", "dusus"],
    ["Kaç sinyale girilebildi?", `${O.alinan}/${O.sinyal}`, `${O.kacti} tanesine yetişilemedi · ${O.kirilim_yok} tanesinde fiyat gelmedi`, "", "kacti"],
  ];
  $("#tiles").innerHTML = tiles.map(([l, v, f, c, g]) =>
    `<div class="card tile"><div class="lbl">${l}${q(g)}</div><div class="val ${c}">${v}</div><div class="foot">${f}</div></div>`).join("");

  egriCiz(O);
  karar();
  dagilimCiz(S);
  matrixCiz();
  tabloCiz(S);
  $("#foot").innerHTML = `Hesap kuralları: her alım ve satışta fiyat %${V.meta.ayar.kayma * 100} daha kötü sayıldı (kayma) ve %${(V.meta.ayar.komisyon * 100).toFixed(1)} ücret düşüldü. ` +
    `Fiyat alış seviyesinin %${V.meta.ayar.maks_kovalama * 100}'ünden fazla üstündeyse alınmadı. Aynı dakikada hem kâr hem zarar seviyesi görüldüyse zarar sayıldı (en kötü ihtimal). ` +
    `${V.meta.ayar.giris_dk} dakika içinde fiyat gelmezse sinyal iptal edildi. Bu bir sanal hesaptır, gerçek işlem yapılmamıştır. Yatırım tavsiyesi değildir.`;
  $("#sozluk").innerHTML = Object.values(GL).map(([b, p]) => `<div><b>${b}</b><p>${p}</p></div>`).join("");
}

function egriCiz(O) {
  const box = $("#egriBox"), tip = $("#tip");
  box.querySelectorAll("svg").forEach(s => s.remove());
  const pts = O.egri, W = box.clientWidth || 640, H = 260, p = {l: 58, r: 14, t: 14, b: 26};
  const vs = pts.map(d => d.v), lo = Math.min(...vs), hi = Math.max(...vs);
  const pad = (hi - lo) * 0.12 || hi * 0.02;
  const y0 = lo - pad, y1 = hi + pad;
  const X = i => p.l + (pts.length > 1 ? i / (pts.length - 1) : 0) * (W - p.l - p.r);
  const Y = v => p.t + (1 - (v - y0) / (y1 - y0)) * (H - p.t - p.b);
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("width", "100%"); svg.setAttribute("height", H);
  svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "Sanal hesap bakiyesi, işlem işlem");
  let g = "";
  const ticks = 4;
  for (let k = 0; k <= ticks; k++) {
    const v = y0 + (y1 - y0) * k / ticks;
    g += `<line x1="${p.l}" x2="${W - p.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--grid)" stroke-width="1"/>`;
    g += `<text x="${p.l - 8}" y="${Y(v) + 4}" text-anchor="end">${usd(v)}</text>`;
  }
  const base = V.meta.sermaye;
  if (base >= y0 && base <= y1)
    g += `<line x1="${p.l}" x2="${W - p.r}" y1="${Y(base)}" y2="${Y(base)}" stroke="var(--text-muted)" stroke-dasharray="3 4" stroke-width="1"/>` +
         `<text x="${W - p.r}" y="${Y(base) - 5}" text-anchor="end">başlangıç</text>`;
  const n = pts.length - 1;
  [0, Math.round(n / 2), n].filter((v, i, a) => a.indexOf(v) === i && v >= 0).forEach(i =>
    g += `<text x="${X(i)}" y="${H - 6}" text-anchor="${i === 0 ? "start" : i === n ? "end" : "middle"}">${i}. işlem</text>`);
  const path = pts.map((d, i) => (i ? "L" : "M") + X(i).toFixed(1) + "," + Y(d.v).toFixed(1)).join("");
  const area = path + `L${X(n).toFixed(1)},${H - p.b}L${X(0).toFixed(1)},${H - p.b}Z`;
  g += `<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--series-1)" stop-opacity=".28"/><stop offset="1" stop-color="var(--series-1)" stop-opacity="0"/></linearGradient></defs>`;
  g += `<path d="${area}" fill="url(#ag)"/>`;
  g += `<path d="${path}" fill="none" stroke="var(--series-1)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`;
  const last = pts[n];
  g += `<circle cx="${X(n)}" cy="${Y(last.v)}" r="4" fill="var(--series-1)" stroke="var(--surface-solid)" stroke-width="2"/>`;
  g += `<line id="cross" y1="${p.t}" y2="${H - p.b}" stroke="var(--text-muted)" stroke-width="1" opacity="0"/>`;
  g += `<circle id="dot" r="5" fill="var(--series-1)" stroke="var(--surface-solid)" stroke-width="2" opacity="0"/>`;
  g += `<rect x="${p.l}" y="0" width="${W - p.l - p.r}" height="${H}" fill="transparent" id="hit"/>`;
  svg.innerHTML = g;
  box.appendChild(svg);
  $("#egriAlt").textContent = `${O.alinan} işlem · son: ${usd(O.son_sermaye)} (${pct(O.toplam_getiri)})`;
  const hit = svg.querySelector("#hit"), cross = svg.querySelector("#cross"), dot = svg.querySelector("#dot");
  const move = ev => {
    const r = svg.getBoundingClientRect(), x = (ev.clientX - r.left) * W / r.width;
    const i = Math.max(0, Math.min(n, Math.round((x - p.l) / (W - p.l - p.r) * n)));
    const d = pts[i];
    cross.setAttribute("x1", X(i)); cross.setAttribute("x2", X(i)); cross.setAttribute("opacity", 1);
    dot.setAttribute("cx", X(i)); dot.setAttribute("cy", Y(d.v)); dot.setAttribute("opacity", 1);
    tip.innerHTML = i === 0 ? `<b>Başlangıç</b><br>${usd(d.v)}` :
      `<b>${i}. işlem · ${d.tk}</b> <span class="muted">${(d.t || "").slice(5, 10).split("-").reverse().join(".")} ${(d.t || "").slice(11, 16)}</span><br>` +
      `İşlem: <span class="${cls(d.g)}">${pct(d.g)}</span> · Hesap: ${usd(d.v)}`;
    const px = X(i) * r.width / W;
    tip.style.left = Math.min(px + 12, r.width - tip.offsetWidth - 4) + "px";
    tip.style.top = Math.max(0, Y(d.v) * r.height / H - 52) + "px";
    tip.style.opacity = 1;
  };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerleave", () => { tip.style.opacity = 0; cross.setAttribute("opacity", 0); dot.setAttribute("opacity", 0); });
}

function dagilimCiz(S) {
  const say = {};
  S.islemler.forEach(r => { const k = r.durum === "alindi" ? r.sonuc : r.durum; say[k] = (say[k] || 0) + 1; });
  const sira = ["TP1+TP2", "TP1", "TP1+gun_sonu", "basabas_stop", "gun_sonu", "STOP", "kacti", "iptal_once_stop", "kirilim_olmadi", "veri_yok"];
  const mx = Math.max(1, ...Object.values(say));
  $("#dagilim").innerHTML = sira.filter(k => say[k]).map(k => {
    const [t, c] = SONUC[k];
    return `<div class="row"><div>${t}</div><div class="track"><div class="fill" style="width:${100 * say[k] / mx}%;background:${c}"></div></div><div class="n">${say[k]}</div></div>`;
  }).join("") || `<div class="muted">Veri yok</div>`;
}

function matrixCiz() {
  const rows = [];
  for (const [g, ga] of [["g0", "Bot anında alsa"], ["g1", "Bot 1 dk geç kalsa"], ["g3", "Elle alsan (3 dk)"]])
    for (const [m, ma] of [["tp1", "1. hedefte sat"], ["kademeli", "Yarı 1., yarı 2. hedef"]]) {
      const O = V.senaryolar[`${g}_${m}`].ozet;
      rows.push(`<tr data-g="${g}" data-m="${m}" class="${g === G && m === M ? "sel" : ""}" style="cursor:pointer">
        <td>${ga}</td><td class="l">${ma}</td><td>${O.alinan}/${O.sinyal}</td><td>${pct(O.kazanma, false, 0)}</td>
        <td>${pct(O.basabas_orani, false, 0)}</td><td class="${cls(O.beklenti)}">${pct(O.beklenti)}</td>
        <td class="${cls(O.toplam_getiri)}">${pct(O.toplam_getiri)}</td><td class="neg">${pct(O.maks_dd ? -O.maks_dd : 0)}</td></tr>`);
    }
  $("#matrix").innerHTML = `<thead><tr><th>Ne kadar hızlı?</th><th class="l">Ne zaman satılır?</th><th>Girilen sinyal</th><th>Tutan</th><th>Kâr için gereken</th>
    <th>Sinyal başı ort.</th><th>Hesabın sonucu</th><th>En kötü dönem</th></tr></thead><tbody>${rows.join("")}</tbody>`;
  $("#matrix").querySelectorAll("tbody tr").forEach(tr => tr.onclick = () => { G = tr.dataset.g; M = tr.dataset.m; render(); window.scrollTo({top: 0, behavior: "smooth"}); });
}

function tabloCiz(S) {
  seg($("#segFiltre"), [["hepsi", "Hepsi"], ["kar", "Kâr ettirenler"], ["zarar", "Zarar ettirenler"], ["alinamadi", "Alınamayanlar"], ["fark", "Kanalın yanıldığı"]], F, k => { F = k; tabloCiz(S); });
  const bot = Object.fromEntries(S.islemler.map(r => [r.id, r]));
  let rows = V.sinyaller.map(s => ({...s, b: bot[s.id]}));
  const kanalKar = s => (s.kanal_sonuc || "").startsWith("TP");
  const botKar = s => s.b.durum === "alindi" && s.b.getiri > 0;
  rows = rows.filter(s => F === "hepsi" ? true : F === "kar" ? botKar(s) : F === "zarar" ? (s.b.durum === "alindi" && s.b.getiri <= 0)
    : F === "alinamadi" ? s.b.durum !== "alindi" : kanalKar(s) !== botKar(s));
  const val = (s, k) => k === "getiri" ? (s.b.durum === "alindi" ? s.b.getiri : -9) : k === "mae" ? (s.b.mae ?? 9) : s[k];
  rows.sort((a, b) => (val(a, sortKey) > val(b, sortKey) ? 1 : val(a, sortKey) < val(b, sortKey) ? -1 : 0) * sortDir);
  const f = x => { if (x == null) return "–"; let t = (+x).toFixed(x < 1 ? 4 : 2); if (x < 1) t = t.replace(/0{1,2}$/, ""); return t.replace(".", ","); };
  const head = [["time", "Tarih / saat", "l"], ["ticker", "Hisse", "l"], [null, "Alış " + q("kirilim")], [null, "Zarar kes " + q("stop")], [null, "1. hedef " + q("tp1")], [null, "2. hedef " + q("tp2")],
    ["kanal_sonuc", "Kanala göre", "l"], [null, "Gerçekte", "l"], ["getiri", "Sonuç"], ["mae", "En dipte"], [null, "", "l"]];
  $("#tablo").innerHTML = `<thead><tr>${head.map(([k, t, c]) => `<th class="${c || ""}" ${k ? `data-k="${k}"` : ""}>${t}${k === sortKey ? (sortDir > 0 ? " ↑" : " ↓") : ""}</th>`).join("")}</tr></thead>
  <tbody>${rows.map(s => {
    const b = s.b, ok = b.durum === "alindi";
    const botTxt = ok ? `${badge(b.sonuc)} <span class="muted">${b.giris_saat}→${b.cikis_saat}</span>` : badge(b.durum);
    const flags = [s.silindi ? "kanal sildi" : "", s.duzenlendi ? "kanal değiştirdi" : "", b.uyari ? "az alıcı vardı" : ""].filter(Boolean).join(" · ");
    return `<tr><td class="l">${s.tarih} <span class="muted">${s.saat} NY · ${s.saat_tr} TR</span></td><td class="l"><b>${s.ticker}</b></td>
      <td>${f(s.entry)}</td><td>${f(s.stop)}</td><td>${f(s.tp1)}</td><td>${f(s.tp2)}</td>
      <td class="l">${badge(s.kanal_sonuc)}</td><td class="l">${botTxt}</td>
      <td class="${ok ? cls(b.getiri) : "muted"}">${ok ? pct(b.getiri) : "–"}</td>
      <td class="${ok && b.mae < 0 ? "neg" : "muted"}">${ok ? pct(b.mae) : "–"}</td>
      <td class="l flag">${flags}</td></tr>`;
  }).join("") || `<tr><td colspan="11" class="muted l">Bu filtrede sinyal yok</td></tr>`}</tbody>`;
  $("#tablo").querySelectorAll("th[data-k]").forEach(th => th.onclick = () => {
    sortDir = sortKey === th.dataset.k ? -sortDir : 1; sortKey = th.dataset.k; tabloCiz(S);
  });
}


// --- karar karti
function karar(){
  const S = V.senaryolar[`${G}_${M}`], O = S.ozet;
  let durum, renk, ikon, aciklama;
  if (!O.alinan) { durum = "Veri yetersiz"; renk = "var(--text-muted)"; ikon = '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>'; aciklama = "Henüz alınabilen işlem yok."; }
  else if (O.beklenti > 0 && (O.basabas_orani == null || O.kazanma >= O.basabas_orani)) { durum = "Şimdilik kâr ettiriyor"; renk = "var(--good)"; ikon = '<path d="M20 6L9 17l-5-5"/>'; aciklama = "Bu sinyallere uyan biri şu ana kadar para kazanırdı."; }
  else { durum = "Zarar ettiriyor"; renk = "var(--critical)"; ikon = '<path d="M18 6L6 18M6 6l12 12"/>'; aciklama = "Bu sinyallere uyan biri şu ana kadar para kaybederdi."; }
  const n = O.sinyal, guven = n >= 100 ? ["Yeterli", "var(--good)"] : n >= 50 ? ["Orta", "var(--warning)"] : ["Düşük", "var(--critical)"];
  const bar = Math.min(100, n);
  $("#verdict").innerHTML = `
    <div class="v-lbl">SONUÇ</div>
    <div class="v-row"><span class="v-ic" style="color:${renk};border-color:${renk}"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${ikon}</svg></span><span class="v-d">${durum}</span></div>
    <div class="v-a">${aciklama}</div>
    <div class="v-kv"><span>Tutan sinyal</span><b>10'da ${O.alinan ? Math.round(O.kazanma * 10) : "–"}</b></div>
    <div class="v-kv"><span>Kâr için gereken ${q("basabas")}</span><b>10'da ${O.basabas_orani != null ? Math.round(O.basabas_orani * 10) : "–"}</b></div>
    <div class="v-kv"><span>Sinyal başına ortalama ${q("beklenti")}</span><b class="${cls(O.beklenti)}">${pct(O.beklenti)}</b></div>
    <div class="v-kv"><span>Sonuca ne kadar güvenebilirsin? ${q("ornek")}</span><b style="color:${guven[1]}">${guven[0]} · ${n}/100 sinyal</b></div>
    <div class="v-bar"><i style="width:${bar}%;background:${guven[1]}"></i></div>`;
}
addEventListener("scroll", () => $("#top").classList.toggle("scrolled", scrollY > 8), {passive: true});
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), {threshold: .08});
document.querySelectorAll(".rv").forEach(el => io.observe(el));
const Snow = (() => {
  const red = matchMedia("(prefers-reduced-motion: reduce)").matches, cv = $("#snow"), c = cv.getContext("2d"); let W, H, dpr, fl = [];
  function size(){ dpr = Math.min(devicePixelRatio || 1, 2); W = cv.width = innerWidth * dpr; H = cv.height = innerHeight * dpr; cv.style.width = innerWidth + "px"; cv.style.height = innerHeight + "px"; }
  size(); addEventListener("resize", size);
  for (let i = 0; i < (red ? 0 : 45); i++) fl.push({x: Math.random(), y: Math.random(), r: Math.random() * 1.5 + .5, s: Math.random() * .25 + .12, w: Math.random() * 7, o: Math.random() * .4 + .2});
  (function f(){ c.clearRect(0, 0, W, H); const col = getComputedStyle(document.documentElement).getPropertyValue("--snow").trim();
    for (const p of fl){ p.y += p.s * .0016; p.w += .01; p.x += Math.sin(p.w) * .0003; if (p.y > 1.02){ p.y = -.02; p.x = Math.random(); } c.beginPath(); c.arc(p.x * W, p.y * H, p.r * dpr, 0, 7); c.fillStyle = `rgba(${col},${p.o})`; c.fill(); }
    requestAnimationFrame(f); })();
})();
addEventListener("resize", () => egriCiz(V.senaryolar[`${G}_${M}`].ozet));
setTheme(savedTheme || "dark");
</script>
</body>
</html>
"""
