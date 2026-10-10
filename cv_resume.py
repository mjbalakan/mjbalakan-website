"""Two-page industry resume from the shared data -> resume.html + files/MJBalakan_Resume.pdf."""
import json, re, html

E = html.escape


def _me(a):
    return re.sub(r"(M\. J\. Balakan|M\. Javadi)", r"<b>\1</b>", E(a))


def _short_authors(a):
    names = [x.strip().removeprefix("and ").strip() for x in a.split(",")]
    if len(names) <= 4:
        return _me(", ".join(names))
    me = next((n for n in names if "Balakan" in n or "Javadi" in n), names[0])
    first = names[0]
    return _me(f"{first}, et al." if first == me else f"{first}, …, {me}, et al.")


CSS = r"""
@page{size:Letter;margin:0.6in 0.65in 0.6in 0.65in}
:root{--ink:#14171f;--muted:#566070;--accent:#1d3461;--rule:#d3d8e2;color-scheme:light}
*{box-sizing:border-box}
html,body{background:#e8eaef}
body{margin:0;color:var(--ink);font:9.8pt/1.4 "Inter","Helvetica Neue",Arial,sans-serif}
.sheet{background:#fff;max-width:8.5in;margin:24px auto;padding:0.6in 0.65in;box-shadow:0 2px 14px rgba(0,0,0,.12)}
.bar{max-width:8.5in;margin:16px auto 0;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding-inline:16px;font:500 14px/1.4 system-ui,sans-serif}
.bar a{color:#1b2440;text-decoration:none;padding:8px 14px;border:1px solid #c9ccd6;border-radius:8px;background:#fff}
.seg{display:inline-flex;border:1px solid #1b2440;border-radius:8px;overflow:hidden;background:#fff}.bar .seg a{border:0;border-radius:0;padding:8px 14px}.bar .seg a+a{border-left:1px solid #1b2440}.bar .seg a.on{background:#1b2440;color:#fff}
.bar a.pdf{background:#1b2440;color:#fff;border-color:#1b2440}
@media screen and (max-width:700px){.sheet{padding:24px 16px;margin:12px 8px}.job .top{flex-direction:column}}
@media print{html,body{background:#fff}.sheet{box-shadow:none;margin:0;padding:0;max-width:none}.bar{display:none}}
a{color:var(--accent);text-decoration:none}
header{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;padding-bottom:8px;border-bottom:2px solid var(--accent)}
h1{font-size:21pt;font-weight:700;letter-spacing:-.01em;margin:0;line-height:1.1}
.head{color:var(--accent);font-weight:600;font-size:10.2pt;margin-top:3px}
.contact{text-align:right;font-size:8.8pt;color:var(--muted);line-height:1.5}
h2{font-size:9pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:14px 0 6px;break-after:avoid}
p{margin:0}
.summary{text-align:justify}
.skills p{margin:0 0 3px;text-align:justify}
.job{margin:0 0 8px;break-inside:avoid}
.job .top{display:flex;justify-content:space-between;gap:12px}
.job .role{font-weight:700}
.job .when{color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
.job .org{color:var(--muted)}
ul{margin:3px 0 0;padding-left:1.1em}
li{margin:0 0 2px}
.pubs li{margin-bottom:4px}
.pubs i{color:var(--ink)}
.badge{font-size:7.8pt;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--accent)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:0 24px}
.line{display:flex;justify-content:space-between;gap:10px;margin-bottom:2px}
.line span:last-child{color:var(--muted);white-space:nowrap}
.note{color:var(--muted);font-size:8.6pt;margin-top:4px}
"""


def build(root, site, papers):
    cv = json.loads((root / "data/cv.json").read_text())
    r = cv["resume"]
    by = {p["slug"]: p for p in papers}
    sch = next((p["url"] for p in site["profiles"] if "Scholar" in p["name"]), "")
    li = next((p["url"] for p in site["profiles"] if p["name"] == "LinkedIn"), "")
    home = site["url"].replace("https://", "")

    jobs = "".join(
        f'<div class="job"><div class="top"><span><span class="role">{E(j["role"])}</span> · <span class="org">{E(j["org"])}</span></span>'
        f'<span class="when">{E(j["when"])}</span></div>'
        + ("<ul>" + "".join(f"<li>{E(b)}</li>" for b in j["bullets"]) + "</ul>" if j["bullets"] else "") + "</div>"
        for j in r["experience"])
    skills = "".join(f'<p><b>{E(s["label"])}:</b> {E(s["text"])}</p>' for s in cv["skills"])

    def pub(p):
        c = p["cv"]
        t = E(p["title"].replace("⁠", ""))
        if c.get("accepted"):
            v = f'<i>{E(c["accepted"]["journal"])}</i> (Letter), accepted {p["year"]}'
        elif c.get("journal"):
            v = f'<i>{E(c["journal"])}</i> {E(c["ref"].split(",")[0])} ({p["year"]})'
        else:
            v = f'submitted ({p["year"]})' + (f', arXiv:{E(p["arxiv"])}' if p.get("arxiv") and p["slug"] != "half-integer-winding-order-parameter" else "")
        b = f' <span class="badge">{E(c["badge"])}</span>' if c.get("badge") else ""
        return f'<li>{_short_authors(c["authors"])}, “{t},” {v}.{b}</li>'
    pubs = "".join(pub(by[s]) for s in r["selected"] if s in by)
    n = len(papers); st = site.get("stats", {})

    edu = "".join(
        f'<div class="line"><span>{E(re.sub(r" \(\d{4}\)$", "", e["degree"]))}</span><span>{re.search(r"\((\d{4})\)", e["degree"]).group(1)}</span></div>'
        for e in cv["education"])
    web_awards = [a for a in cv["awards"] if a.get("web")]
    honors = "".join(f'<div class="line"><span>{E(a["title"])}</span><span>{E(a["year"].replace(" - ", "–"))}</span></div>' for a in web_awards)
    talks = [
        ("Invited talk, Gordon Research Conference (Correlated Electron Systems)", "2026"),
        ("Talk, APS Global Physics Summit", "2026"),
        ("Invited talk, Laboratory for Physical Sciences, College Park, MD", "2025"),
        ("Referee for Physical Review Letters, Applied Physics Letters, 2D Materials, Nanotechnology", ""),
    ]
    talks_html = "".join(f'<div class="line"><span>{E(t)}</span><span>{E(y)}</span></div>' for t, y in talks)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Resume · {E(site['name'])}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap">
<style>{CSS}</style></head>
<body>
<nav class="bar"><a href="./">← {E(site['name'])}</a><span class="seg" role="group" aria-label="CV format"><a href="resume.html" class="on" aria-current="page">2-page resume</a><a href="cv.html">Full CV</a></span><a class="pdf" href="files/MJBalakan_Resume.pdf">Download PDF</a></nav>
<main class="sheet">
<header><div><h1>{E(site['name'])}</h1><p class="head">{E(r['headline'])}</p></div>
<div class="contact">{E(cv['academic']['location'])} · {E(cv['academic']['status'])}<br>
<a href="mailto:{E(site['email'])}">{E(site['email'])}</a> · <a href="{E(site['url'])}">{E(home)}</a><br>
<a href="{E(li)}">linkedin.com/in/mjbalakan</a> · <a href="{E(sch)}">Google Scholar</a></div></header>

<h2>Summary</h2><p class="summary">{E(r['summary'])}</p>
<h2>Core skills</h2><div class="skills">{skills}</div>
<h2>Experience</h2>{jobs}
<h2>Selected publications</h2><ul class="pubs">{pubs}</ul>
<p class="note">{n} publications and preprints · {st.get('citations')} citations · h-index {st.get('h_index')} (Google Scholar). Full list at {E(home)}. Earlier papers under M. Javadi.</p>
<div class="two">
<div><h2>Education</h2>{edu}</div>
<div><h2>Honors</h2>{honors}</div>
</div>
<h2>Talks and service</h2>{talks_html}
</main></body></html>"""
    (root / "resume.html").write_text(page)


def make_pdf(root):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        t = re.sub(r'<link rel="stylesheet" href="https://fonts[^>]+>', "", (root / "resume.html").read_text())
        pg.set_content(t, wait_until="load")
        pg.pdf(path=str(root / "files/MJBalakan_Resume.pdf"), format="Letter",
               margin={"top": "0.6in", "bottom": "0.6in", "left": "0.65in", "right": "0.65in"})
        b.close()
    return True
