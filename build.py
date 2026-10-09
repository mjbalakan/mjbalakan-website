#!/usr/bin/env python3
"""Builds mjbalakan.com from data/*.json.

Edit data/papers.json or data/site.json, then run:  python3 build.py
Outputs: index.html, papers/<slug>.html, sitemap.xml, robots.txt, 404.html
"""
import json, html, os, re, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SITE = json.loads((ROOT / "data/site.json").read_text())
PAPERS = json.loads((ROOT / "data/papers.json").read_text())
BASE = SITE["url"].rstrip("/")
TODAY = datetime.date.today().isoformat()
E = html.escape

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,500..800'
         '&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">')

CSS = r"""
/* Layout: one 1120px column; hero = text + portrait over a live flux-oscillation field; sections stack with mono "readout" labels */
:root{
  --bg:#0a0e1a; --surface:#111729; --raise:#18203a; --line:#25304d;
  --fg:#e9edf6; --muted:#9aa6bf; --accent:#f6a33c; --accent-2:#d2457a;
  --f-display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --field-opacity:.42; color-scheme:dark;
}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]){
  --bg:#f5f6fa; --surface:#ffffff; --raise:#eef0f6; --line:#d8dce8;
  --fg:#111629; --muted:#4f5a73; --accent:#b4530a; --accent-2:#a3245e; --field-opacity:.2; color-scheme:light}}
:root[data-theme="light"]{
  --bg:#f5f6fa; --surface:#ffffff; --raise:#eef0f6; --line:#d8dce8;
  --fg:#111629; --muted:#4f5a73; --accent:#b4530a; --accent-2:#a3245e; --field-opacity:.2; color-scheme:light}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--fg);font:400 17px/1.6 var(--f-body);-webkit-font-smoothing:antialiased}
img{max-width:100%;height:auto;display:block}
a{color:inherit;text-decoration-color:color-mix(in srgb,var(--accent) 60%,transparent);text-underline-offset:3px}
a:hover{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
.wrap{max-width:1120px;margin:0 auto;padding-inline:clamp(16px,4vw,40px)}
h1,h2,h3{font-family:var(--f-display);font-stretch:112%;line-height:1.08;margin:0;text-wrap:balance;letter-spacing:-.01em}
h2{font-size:clamp(1.6rem,3.2vw,2.2rem);font-weight:700}
h3{font-size:1.15rem;font-weight:650;font-stretch:105%}
p{margin:0}
.mono{font-family:var(--f-mono);font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.mono b{color:var(--accent);font-weight:500}

/* nav */
.nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:color-mix(in srgb,var(--bg) 82%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:58px}
.brand{white-space:nowrap;font-family:var(--f-display);font-weight:750;font-stretch:118%;text-decoration:none;letter-spacing:.01em}
.brand span{color:var(--accent)}
.nav ul{display:flex;gap:clamp(10px,2.4vw,26px);list-style:none;margin:0;padding:0;font-size:.92rem;flex-wrap:wrap;justify-content:flex-end}
.nav a{text-decoration:none;color:var(--muted)}
.nav a:hover{color:var(--fg)}
@media (max-width:640px){.nav .hide-s{display:none}.nav ul{gap:14px;font-size:.88rem}}

/* hero */
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line)}
.hero canvas{position:absolute;inset:0;width:100%;height:100%;opacity:var(--field-opacity);pointer-events:none;
  -webkit-mask-image:linear-gradient(100deg,transparent 18%,#000 72%);mask-image:linear-gradient(100deg,transparent 18%,#000 72%)}
.hero .wrap{position:relative;display:grid;grid-template-columns:minmax(0,1.45fr) minmax(0,.75fr);gap:clamp(28px,5vw,64px);align-items:center;padding-block:clamp(48px,8vw,96px) clamp(36px,6vw,64px)}
.hero h1{font-family:var(--f-body);font-stretch:100%;font-size:clamp(2rem,4.4vw,3.2rem);font-weight:600;letter-spacing:-.015em;line-height:1.1;margin-block:14px 16px}
.hero h1 .alt{display:block;font-size:.5em;font-weight:500;color:var(--muted);margin-top:.45em;letter-spacing:0}
.lead{font-size:clamp(1.02rem,1.6vw,1.14rem);max-width:62ch;color:var(--fg)}
.lead strong{font-weight:600;color:var(--accent)}
.now{margin-top:18px;color:var(--muted);max-width:60ch}
.cta{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:8px;border:1px solid var(--line);background:var(--surface);text-decoration:none;font-weight:500;font-size:.95rem}
.btn:hover{border-color:var(--accent);color:var(--fg)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#120c02}
.btn.primary:hover{filter:brightness(1.08);color:#120c02}
.portrait{position:relative;justify-self:end;width:min(100%,330px)}
.portrait img{border-radius:14px;border:1px solid var(--line);aspect-ratio:1;object-fit:cover;width:100%}
.portrait figcaption{margin-top:10px;text-align:right}
.readout{display:flex;flex-wrap:wrap;gap:6px 22px;margin-top:34px;padding-top:16px;border-top:1px dashed var(--line)}
@media (max-width:820px){.hero .wrap{grid-template-columns:1fr}.portrait{justify-self:start;width:min(62%,240px);order:-1}.portrait figcaption{text-align:left}
  .hero canvas{-webkit-mask-image:linear-gradient(180deg,#000 0%,transparent 70%);mask-image:linear-gradient(180deg,#000 0%,transparent 70%)}}

/* sections */
section{padding-block:clamp(48px,7vw,84px)}
section+section{border-top:1px solid var(--line)}
.sec-head{display:flex;flex-direction:column;gap:10px;margin-bottom:32px;max-width:70ch}
.sec-head p{color:var(--muted)}

/* highlights */
.hl{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.hl > div{background:var(--surface);padding:22px 22px 24px;display:flex;flex-direction:column;gap:8px;min-width:0}
.hl .big{font-family:var(--f-display);font-size:1.25rem;font-weight:700;font-stretch:108%;line-height:1.2}
.hl .sub{color:var(--muted);font-size:.93rem}
.stats{display:flex;flex-wrap:wrap;gap:8px 28px;margin-top:22px;font-variant-numeric:tabular-nums}
.stats div{display:flex;align-items:baseline;gap:10px}
.stats strong{font-family:var(--f-body);font-size:1.25rem;font-weight:600}
.stats a{color:var(--muted);font-size:.9rem}

/* research */
.theme{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,4vw,56px);align-items:start;padding-block:36px}
.theme+.theme{border-top:1px dashed var(--line)}
.theme .txt{display:flex;flex-direction:column;gap:14px;min-width:0}
.theme .txt p{color:var(--fg)}
.theme ul{margin:0;padding-left:1.1em;color:var(--muted);font-size:.95rem;display:grid;gap:6px}
.theme ul a{color:var(--fg)}
.figs{display:grid;gap:12px;min-width:0}
.figs.two{grid-template-columns:.9fr 1.1fr;align-items:end}
.fig{margin:0;background:#fff;border-radius:10px;padding:8px;border:1px solid var(--line)}
.fig img{border-radius:4px;margin:0 auto}
.fig.dark{background:#000}
.cap{margin-top:8px}
@media (max-width:820px){.theme{grid-template-columns:1fr}.theme .figs{order:2}}
@media (max-width:480px){.figs.two{grid-template-columns:1fr}}

/* publications */
.pubs{list-style:none;margin:0;padding:0;display:grid;gap:0}
.pub{display:grid;grid-template-columns:4.2rem minmax(0,1fr);gap:18px;padding-block:16px;border-top:1px solid var(--line)}
.pub .yr{font-family:var(--f-mono);color:var(--muted);font-size:.85rem;padding-top:3px;font-variant-numeric:tabular-nums}
.pub h3{font-family:var(--f-body);font-stretch:100%;font-weight:600;font-size:1.02rem;line-height:1.4;letter-spacing:0}
.pub h3 a{text-decoration:none}
.pub h3 a:hover{text-decoration:underline}
.pub .au{color:var(--muted);font-size:.92rem;margin-top:2px}
.pub .au b{color:var(--fg);font-weight:600}
.pub .ve{font-size:.92rem;margin-top:2px;font-style:italic}
.links{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:6px;font-size:.86rem}
.links a{color:var(--muted)}
.badge{display:inline-block;font-family:var(--f-mono);font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;font-style:normal;color:var(--accent);border:1px solid color-mix(in srgb,var(--accent) 55%,transparent);border-radius:999px;padding:1px 8px;margin-left:8px;vertical-align:2px}
details.all{margin-top:28px}
details.all summary{cursor:pointer;font-weight:600;padding:12px 0;color:var(--accent);list-style:none}
details.all summary::-webkit-details-marker{display:none}
details.all summary::before{content:"+ ";font-family:var(--f-mono)}
details.all[open] summary::before{content:"− "}

/* news + cv */
.two-col{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(32px,5vw,64px)}
@media (max-width:820px){.two-col{grid-template-columns:1fr}}
.tl{list-style:none;margin:0;padding:0;display:grid}
.tl li{display:grid;grid-template-columns:4.2rem minmax(0,1fr);gap:16px;padding-block:12px;border-top:1px solid var(--line)}
.tl .when{font-family:var(--f-mono);font-size:.85rem;color:var(--muted);padding-top:2px;font-variant-numeric:tabular-nums}
.tl .what b{font-weight:600}
.tl .what span{display:block;color:var(--muted);font-size:.93rem}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips span{font-size:.86rem;padding:5px 11px;border:1px solid var(--line);border-radius:999px;background:var(--surface)}
.skillgroup{display:grid;gap:10px;margin-bottom:22px}

/* contact */
.contact{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:32px;align-items:start}
@media (max-width:820px){.contact{grid-template-columns:1fr}}
.email{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:18px}
.email code{font-family:var(--f-mono);font-size:1.05rem;padding:10px 14px;border:1px solid var(--line);border-radius:8px;background:var(--surface);user-select:all}
.plist{list-style:none;margin:0;padding:0;display:grid;gap:0}
.plist a{display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-top:1px solid var(--line);text-decoration:none}
.plist a span:last-child{color:var(--muted);font-family:var(--f-mono);font-size:.8rem}
footer{border-top:1px solid var(--line);padding-block:28px;color:var(--muted);font-size:.88rem}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px}


/* research spotlight */
.spot{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:clamp(28px,5vw,64px);align-items:center}
.spot .txt{display:flex;flex-direction:column;gap:16px;min-width:0}
.spot h2{font-size:clamp(1.8rem,3.6vw,2.6rem)}
.results{list-style:none;margin:8px 0 0;padding:0;display:grid}
.results a{display:grid;grid-template-columns:5.2rem minmax(0,1fr);gap:16px;align-items:baseline;padding:14px 0;border-top:1px solid var(--line);text-decoration:none}
.results a:hover .t{color:var(--accent)}
.results .k,.fact .k{font-family:var(--f-display);font-weight:750;font-stretch:110%;font-size:1.35rem;color:var(--accent);white-space:nowrap}
.results .t{color:var(--fg)}
.visual{display:grid;grid-template-columns:1fr;gap:14px;min-width:0}
.visual figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
.visual img{width:100%;aspect-ratio:1.25;object-fit:cover;border-radius:10px;border:1px solid var(--line)}
.visual figure:first-child img{aspect-ratio:1.6}.visual figure:last-child img{aspect-ratio:2.3}
.visual figcaption{text-transform:none;letter-spacing:.02em}
.lab{margin:clamp(40px,6vw,72px) 0 0;display:grid;gap:10px}
.lab img{width:100%;aspect-ratio:2.2;object-fit:cover;object-position:50% 38%;border-radius:14px;border:1px solid var(--line)}
.lab figcaption{color:var(--muted);font-size:.84rem}
@media (min-width:900px){.lab figcaption{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.earlier{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(24px,4vw,56px);margin-top:clamp(40px,6vw,72px);padding-top:clamp(28px,4vw,40px);border-top:1px solid var(--line);align-items:start}
.earlier .txt{display:flex;flex-direction:column;gap:12px;min-width:0}
.earlier .txt p{color:var(--muted)}
.facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.fact{background:var(--surface);padding:18px;display:flex;flex-direction:column;gap:6px;text-decoration:none;min-width:0}
.fact .t{color:var(--muted);font-size:.93rem}
.fact:hover .t{color:var(--fg)}
.tag{display:block;font-family:var(--f-mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-bottom:2px}
.tl .what a{text-decoration:none}
.tl .what a:hover b{color:var(--accent)}
.honors{margin:0;padding-left:1.1em;display:grid;gap:6px;font-size:.95rem}
.honors span{color:var(--muted)}
.hero .stats{margin-top:30px;padding-top:18px;border-top:1px dashed var(--line)}
@media (max-width:820px){.spot,.earlier{grid-template-columns:1fr}.lab img{aspect-ratio:1.5}}
@media (max-width:480px){.facts{grid-template-columns:1fr}.visual{grid-template-columns:1fr}.results a{grid-template-columns:4.4rem minmax(0,1fr)}}

.statline{margin-top:26px;padding-top:14px;border-top:1px dashed var(--line);color:var(--muted);font-size:.86rem;font-variant-numeric:tabular-nums}
.lead .ai{font-weight:inherit;font-size:1.15em}
/* paper page */
.paper{padding-block:clamp(36px,6vw,72px)}
.paper .crumb{margin-bottom:22px}
.paper .crumb a{color:var(--muted)}
.paper h1{font-size:clamp(1.7rem,3.8vw,2.6rem);font-weight:750;max-width:30ch}
.paper .meta{margin-top:16px;display:grid;gap:4px;color:var(--muted)}
.paper .meta .au b{color:var(--fg)}
.paper .body{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:clamp(28px,5vw,56px);margin-top:36px;align-items:start}
@media (max-width:820px){.paper .body{grid-template-columns:1fr}}
.paper .body > div{display:flex;flex-direction:column;gap:18px;min-width:0}
.paper .summary{font-size:1.12rem}
.paper ul.find{margin:0;padding-left:1.1em;display:grid;gap:8px}
.cite{font-family:var(--f-mono);font-size:.82rem;line-height:1.55;padding:14px;border:1px solid var(--line);border-radius:8px;background:var(--surface);overflow-x:auto;white-space:pre-wrap}
.copy{font:inherit;font-size:.86rem;cursor:pointer;background:none;border:1px solid var(--line);color:var(--fg);border-radius:6px;padding:6px 12px}
.copy:hover{border-color:var(--accent)}
.more{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px;margin-top:12px}
.more a{display:block;padding:14px 16px;border:1px solid var(--line);border-radius:10px;text-decoration:none;background:var(--surface)}
.more a span{display:block;color:var(--muted);font-size:.85rem;margin-top:4px}
"""

FIELD_JS = r"""
(function(){
  const c=document.getElementById('field'); if(!c) return;
  const x=c.getContext('2d');
  // inferno-like colormap, the palette used in the Fe(Te,Se) magnetoresistance maps
  const stops=[[0,0,4],[66,10,104],[147,38,103],[221,81,58],[252,165,10],[252,255,164]];
  const lut=[];for(let i=0;i<256;i++){const t=i/255*(stops.length-1),k=Math.min(Math.floor(t),stops.length-2),f=t-k;
    lut.push(stops[k].map((v,j)=>Math.round(v+(stops[k+1][j]-v)*f)));}
  const W=180,H=110; c.width=W; c.height=H;
  const img=x.createImageData(W,H); const noise=new Float32Array(W*H).map(()=>Math.random()-.5);
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  function draw(t){
    for(let j=0;j<H;j++){const I=(j/H-.5)*24;           // bias current, µA
      const slip=Math.abs(I)>5?Math.sign(I)*.5:0;          // phase slip beyond the flip current
      for(let i=0;i<W;i++){const n=(i/W-.5)*20;           // winding number
        const v=.5+.5*Math.cos(2*Math.PI*(n/2+.035*I*Math.abs(I)/6+slip+t))*(.75+.25*Math.cos(I*.9))+noise[j*W+i]*.35;
        const p=lut[Math.max(0,Math.min(255,(v*255)|0))],o=(j*W+i)*4;
        img.data[o]=p[0];img.data[o+1]=p[1];img.data[o+2]=p[2];img.data[o+3]=255;}}
    x.putImageData(img,0,0);
  }
  if(reduce){draw(0);return;}
  let t0=null;function loop(ts){if(t0===null)t0=ts;draw((ts-t0)/16000);requestAnimationFrame(loop);}requestAnimationFrame(loop);
})();
"""

COPY_JS = r"""
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>{
  const el=document.getElementById(b.dataset.copy); const txt=el.innerText.trim();
  const done=()=>{const o=b.textContent;b.textContent='Copied';setTimeout(()=>b.textContent=o,1600)};
  (navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(done).catch(()=>{
    const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);});
}));
"""

def bold_me(authors):
    a = E(authors)
    return re.sub(r"(M\. J\. Balakan|M\. Javadi)", r"<b>\1</b>", a)

def links_of(p, depth="./"):
    out = []
    if p.get("doi"): out.append(f'<a href="https://doi.org/{E(p["doi"])}" target="_blank" rel="noopener">Journal</a>')
    if p.get("arxiv"): out.append(f'<a href="https://arxiv.org/abs/{E(p["arxiv"])}" target="_blank" rel="noopener">arXiv:{E(p["arxiv"])}</a>')
    return out

def head(title, desc, path, depth, jsonld, og_type="website", og_image="img/mj-balakan.jpg"):
    url = BASE + "/" + path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(url)}">
<meta name="author" content="{E(SITE['name'])}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{E(url)}">
<meta property="og:image" content="{E(BASE + '/' + og_image)}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0a0e1a">
<link rel="icon" href="{depth}img/favicon.svg" type="image/svg+xml">
{FONTS}
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
"""

def nav(depth):
    h = "" if depth == "./" else depth
    return f"""<nav class="nav" aria-label="Main"><div class="wrap">
<a class="brand" href="{depth}">MJ <span>Balakan</span></a>
<ul><li><a href="{h}#research">Research</a></li><li class="hide-s"><a href="{h}#publications">Publications</a></li>
<li class="hide-s"><a href="{h}#news">News</a></li><li class="hide-s"><a href="{h}#experience">Experience</a></li><li><a href="{depth}files/MJBalakan_CV.pdf">CV</a></li><li><a href="{h}#contact">Contact</a></li></ul>
</div></nav>"""

def footer():
    return f"""<footer><div class="wrap"><span>© {datetime.date.today().year} {E(SITE['name'])}</span>
<span>Updated {datetime.date.today().strftime('%B %Y')}</span></div></footer>"""

def person_ld():
    return {
        "@context": "https://schema.org", "@type": "Person",
        "name": SITE["name"], "alternateName": SITE["alternate_names"],
        "givenName": "Mohammad", "familyName": "Javadi Balakan",
        "jobTitle": SITE["job_title"], "url": BASE + "/",
        "image": BASE + "/img/mj-balakan.jpg",
        "email": "mailto:" + SITE["email"],
        "address": {"@type": "PostalAddress", "addressLocality": "San Jose", "addressRegion": "CA", "addressCountry": "US"},
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "University of Tehran"},
                     {"@type": "CollegeOrUniversity", "name": "Urmia University"}],
        "affiliation": {"@type": "CollegeOrUniversity", "name": "State University of New York at Albany"},
        "knowsAbout": SITE["knows_about"],
        "sameAs": [p["url"] for p in SITE["profiles"]],
    }

def pub_item(p, depth="./"):
    badge = f'<span class="badge">{E(p["badge"])}</span>' if p.get("badge") else ""
    ls = [f'<a href="{depth}papers/{p["slug"]}.html">Summary</a>'] + links_of(p)
    return f"""<li class="pub"><div class="yr">{p['year']}</div><div>
<h3><a href="{depth}papers/{p['slug']}.html">{E(p['title'])}</a></h3>
<div class="au">{bold_me(p['authors'])}</div>
<div class="ve">{E(p['venue'])}{badge}</div>
<div class="links">{' · '.join(ls)}</div></div></li>"""

def paper_ref(slug):
    return next(p for p in PAPERS if p["slug"] == slug)

def build_index():
    s = SITE
    by = {p["slug"]: p for p in PAPERS}
    sp, ea, lab = s["spotlight"], s["earlier"], s["lab"]

    results = "".join(
        f'<li><a href="papers/{r["slug"]}.html"><span class="k">{r["k"]}</span><span class="t">{E(r["t"])}</span></a></li>'
        for r in sp["results"])
    facts = "".join(
        f'<a class="fact" href="papers/{f["slug"]}.html"><span class="k">{E(f["k"])}</span><span class="t">{E(f["t"])}</span></a>'
        for f in ea["facts"])
    tl = "".join(
        f'<li><span class="when">{E(n["when"])}</span><span class="what"><span class="tag">{E(n["tag"])}</span>'
        + (f'<a href="papers/{n["slug"]}.html"><b>{E(n["title"])}</b></a>' if n.get("slug") else f'<b>{E(n["title"])}</b>')
        + f'<span>{E(n["detail"])}</span></span></li>' for n in s["timeline"])
    cv = "".join(f'<li><span class="when">{E(n["when"])}</span><span class="what"><b>{E(n["title"])}</b><span>{E(n["detail"])}</span></span></li>' for n in s["career"])
    skills = "".join(f'<div class="skillgroup"><span class="mono">{E(g["group"])}</span><div class="chips">{"".join(f"<span>{E(x)}</span>" for x in g["items"])}</div></div>' for g in s["skills"])
    awards = "".join(f'<li>{E(a["title"])} <span>· {E(a["detail"])}, {E(a["when"])}</span></li>' for a in s["awards"] if a["when"] != "Review")
    review = next((a for a in s["awards"] if a["when"] == "Review"), None)
    profiles = "".join(f'<li><a href="{E(p["url"])}" target="_blank" rel="noopener"><span>{E(p["name"])}</span><span>{E(p["handle"])}</span></a></li>' for p in s["profiles"])
    featured = [p for p in PAPERS if p.get("featured")]
    rest = [p for p in PAPERS if not p.get("featured")]
    st = s["stats"]

    title = "Mohammad Javadi (MJ) Balakan · Physicist, Quantum Devices"
    page = head(title, s["meta_description"], "", "./", person_ld()) + nav("./") + f"""
<header class="hero"><canvas id="field" aria-hidden="true"></canvas><div class="wrap">
<div>
<span class="mono">Experimental physicist · <b>Quantum devices</b></span>
<h1>Mohammad Javadi Balakan<span class="alt">MJ Balakan</span></h1>
<p class="lead">{s['lead']}</p>
<p class="now">{E(s['now'])}</p>
<div class="cta">
<a class="btn primary" href="files/MJBalakan_CV.pdf">Download CV</a>
<a class="btn" href="{E(s['profiles'][0]['url'])}" target="_blank" rel="noopener">Google Scholar</a>
<a class="btn" href="{E(s['profiles'][1]['url'])}" target="_blank" rel="noopener">LinkedIn</a>
<a class="btn" href="#contact">Email</a>
</div>
<p class="statline">{st['papers']} papers & preprints · {st['citations']} citations · h-index {st['h_index']}</p>
</div>
<figure class="portrait" style="margin:0"><img src="img/mj-balakan.jpg" alt="Portrait of Mohammad Javadi Balakan" width="800" height="800"></figure>
</div></header>

<main>
<section id="research"><div class="wrap">
<div class="spot">
<div class="txt">
<span class="mono">Research · {E(sp['span'])}</span>
<h2>{E(sp['title'])}</h2>
<p>{E(sp['text'])}</p>
<ul class="results">{results}</ul>
</div>
<div class="visual">
<figure><img src="img/{E(sp['device']['src'])}" alt="{E(sp['device']['alt'])}" width="471" height="358"><figcaption class="mono">{E(sp['device']['cap'])}</figcaption></figure>
<figure><img src="img/{E(sp['data']['src'])}" alt="{E(sp['data']['alt'])}" width="722" height="578" loading="lazy"><figcaption class="mono">{E(sp['data']['cap'])}</figcaption></figure>
</div>
</div>
<figure class="lab"><img src="img/{E(lab['src'])}" alt="{E(lab['alt'])}" width="1600" height="1112" loading="lazy"><figcaption>{E(lab['cap'])}</figcaption></figure>
<div class="earlier">
<div class="txt"><span class="mono">{E(ea['span'])}</span><h3>{E(ea['title'])}</h3><p>{E(ea['text'])}</p></div>
<div class="facts">{facts}</div>
</div>
</div></section>

<section id="news"><div class="wrap">
<div class="sec-head"><span class="mono">Recognition & news</span><h2>Recent</h2></div>
<ul class="tl">{tl}</ul>
</div></section>

<section id="publications"><div class="wrap">
<div class="sec-head"><span class="mono">Publications</span><h2>Selected papers</h2>
<p>Each title opens a one-page summary with the key result, figure and links.</p></div>
<ul class="pubs">{''.join(pub_item(p) for p in featured)}</ul>
<details class="all"><summary>All {len(PAPERS)} papers and preprints</summary>
<ul class="pubs">{''.join(pub_item(p) for p in rest)}</ul></details>
</div></section>

<section id="experience"><div class="wrap two-col">
<div><div class="sec-head"><span class="mono">Experience</span><h2>Career & education</h2></div><ul class="tl">{cv}</ul>
<p style="margin-top:18px"><a href="files/MJBalakan_CV.pdf">Full CV (PDF)</a></p></div>
<div><div class="sec-head"><span class="mono">Toolkit</span><h2>Hands-on skills</h2></div>{skills}
<div class="skillgroup"><span class="mono">Honors</span><ul class="honors">{awards}</ul></div>
{f'<p class="mono" style="text-transform:none;letter-spacing:0">Reviewer for {E(review["detail"])}</p>' if review else ''}
</div>
</div></section>

<section id="contact"><div class="wrap contact">
<div><div class="sec-head"><span class="mono">Contact</span><h2>Get in touch</h2>
<p>For research collaborations, talks, or roles in quantum and semiconductor device development.</p></div>
<div class="email"><code id="em">{E(s['email'])}</code><button class="copy" type="button" data-copy="em">Copy email</button>
<a class="btn" href="mailto:{E(s['email'])}">Write an email</a></div></div>
<div><span class="mono">Profiles</span><ul class="plist" style="margin-top:10px">{profiles}</ul></div>
</div></section>
</main>
{footer()}
<script>{FIELD_JS}{COPY_JS}</script>
</body></html>"""
    return page


def citation(p):
    v = p["venue"]
    tail = f" https://doi.org/{p['doi']}" if p.get("doi") else (f" arXiv:{p['arxiv']}" if p.get("arxiv") else "")
    return f"{p['authors']}, \"{p['title']},\" {v} ({p['year']}).{tail}"

def build_paper(p):
    depth = "../"
    desc = p["summary"][:300]
    ld = {"@context": "https://schema.org", "@type": "ScholarlyArticle", "headline": p["title"],
          "author": [{"@type": "Person", "name": a.strip()} for a in p["authors"].split(",")],
          "datePublished": str(p["year"]), "abstract": p["summary"],
          "isPartOf": p["venue"], "url": f"{BASE}/papers/{p['slug']}.html"}
    if p.get("doi"): ld["sameAs"] = f"https://doi.org/{p['doi']}"
    elif p.get("arxiv"): ld["sameAs"] = f"https://arxiv.org/abs/{p['arxiv']}"
    title = f"{p['title']} · MJ Balakan"
    badge = f'<span class="badge">{E(p["badge"])}</span>' if p.get("badge") else ""
    fig = ""
    if p.get("figure"):
        fig = f'<figure class="fig" style="margin:0"><img src="../img/{E(p["figure"])}" alt="{E(p.get("figure_alt",""))}"></figure><p class="mono cap">{E(p.get("figure_credit",""))}</p>'
    finds = "".join(f"<li>{E(f)}</li>" for f in p["findings"])
    finds_html = f'<span class="mono">Key results</span><ul class="find">{finds}</ul>' if finds else ""
    lks = links_of(p)
    lk_html = "".join(l.replace('<a ', '<a class="btn" ', 1) for l in lks)
    same = [q for q in PAPERS if q["theme"] == p["theme"] and q["slug"] != p["slug"]][:3]
    more = "".join(f'<a href="{q["slug"]}.html">{E(q["title"])}<span>{E(q["venue"])}, {q["year"]}</span></a>' for q in same)
    page = head(title, desc, f"papers/{p['slug']}.html", depth, ld, "article",
                f"img/{p['figure']}" if p.get("figure") else "img/mj-balakan.jpg") + nav(depth) + f"""
<main class="paper"><div class="wrap">
<div class="crumb mono"><a href="../#publications">← All publications</a></div>
<span class="mono">{p['year']} · {E(p['venue'])}</span>{badge}
<h1 style="margin-top:12px">{E(p['title'])}</h1>
<div class="meta"><div class="au">{bold_me(p['authors'])}</div></div>
<div class="cta">{lk_html}</div>
<div class="body">
<div><span class="mono">In brief</span><p class="summary">{E(p['summary'])}</p>{finds_html}
<span class="mono">Cite</span><div class="cite" id="cite">{E(citation(p))}</div>
<div><button class="copy" type="button" data-copy="cite">Copy citation</button></div></div>
<div>{fig}</div>
</div>
{f'<div style="margin-top:48px"><span class="mono">Related work</span><div class="more">{more}</div></div>' if more else ''}
</div></main>
{footer()}
<script>{COPY_JS}</script>
</body></html>"""
    return page

def main():
    out = ROOT
    (out / "papers").mkdir(exist_ok=True)
    (out / "index.html").write_text(build_index())
    for p in PAPERS:
        (out / "papers" / f"{p['slug']}.html").write_text(build_paper(p))
    urls = [BASE + "/"] + [f"{BASE}/papers/{p['slug']}.html" for p in PAPERS]
    sm = "\n".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    nf = head("Page not found · MJ Balakan", "Page not found.", "404.html", "/", {"@context": "https://schema.org", "@type": "WebPage"}) + nav("/") + \
        '<main class="paper"><div class="wrap"><h1>Page not found</h1><p style="margin-top:16px"><a href="/">Go to the homepage</a></p></div></main>' + footer() + "</body></html>"
    (out / "404.html").write_text(nf)
    print(f"Built index + {len(PAPERS)} paper pages")

if __name__ == "__main__":
    main()
