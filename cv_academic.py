"""Full CV from the shared data files.

Writes cv.html and files/MJBalakan_CV.pdf.
"""
import json, re, html, datetime

E = html.escape


def _me(authors):
    return re.sub(r"(M\. J\. Balakan|M\. Javadi)", r"<b>\1</b>", E(authors))


def _ref(ref):
    """Bold the volume number: '14, 064048' -> <b>14</b>, 064048."""
    m = re.match(r"(\d+)(.*)", ref)
    return f"<b>{m.group(1)}</b>{E(m.group(2))}" if m else E(ref)


NOTES = {}


def _links(p):
    out = []
    if p.get("doi"):
        out.append(f'<a href="https://doi.org/{E(p["doi"])}">doi:{E(p["doi"])}</a>')
    if p["slug"] in NOTES:
        out.append(f'<span class="xnote">{E(NOTES[p["slug"]])}</span>')
    elif p.get("arxiv"):
        out.append(f'<a href="https://arxiv.org/abs/{E(p["arxiv"])}">arXiv:{E(p["arxiv"])}</a>')
    return out


def _pub(n, p):
    c = p["cv"]
    title = E(p["title"].replace("⁠", ""))
    badge = f' <span class="badge">{E(c["badge"])}</span>' if c.get("badge") else ""
    if c.get("accepted"):
        a = c["accepted"]
        body = f'{_me(c["authors"])}, “{title},” <i>{E(a["journal"])}</i> {E(a["note"])} ({p["year"]}).'
    elif c.get("journal"):
        body = f'{_me(c["authors"])}, “{title},” <i>{E(c["journal"])}</i> {_ref(c["ref"])} ({p["year"]}).'
    else:
        status = "submitted" if "submitted" in c.get("tail", "") else "preprint"
        body = f'{_me(c["authors"])}, “{title},” {status} ({p["year"]}).'
    tail = [x for x in ([badge.strip()] if badge else []) + _links(p)]
    return f'<li value="{n}"><span>{body} {" · ".join(tail)}</span></li>'


CSS = r"""
@page{size:Letter;margin:0.85in 0.9in 0.8in 0.9in}
:root{--ink:#16181d;--muted:#5a6070;--navy:#1d3461;--rule:#c9cfdb;color-scheme:light}
*{box-sizing:border-box}
html,body{background:#e8eaef}
body{margin:0;color:var(--ink);font:10.4pt/1.42 "TeX Gyre Pagella","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;font-variant-numeric:oldstyle-nums}
.sheet{background:#fff;max-width:8.5in;margin:24px auto;padding:0.85in 0.9in;box-shadow:0 2px 14px rgba(0,0,0,.12)}
.bar{max-width:8.5in;margin:16px auto 0;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding-inline:16px;font:500 14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
.bar a{color:#1b2440;text-decoration:none;padding:8px 14px;border:1px solid #c9ccd6;border-radius:8px;background:#fff}
.seg{display:inline-flex;border:1px solid #1b2440;border-radius:8px;overflow:hidden;background:#fff}.bar .seg a{border:0;border-radius:0;padding:8px 14px}.bar .seg a+a{border-left:1px solid #1b2440}.bar .seg a.on{background:#1b2440;color:#fff}
.bar a.pdf{background:#1b2440;color:#fff;border-color:#1b2440}
@media screen and (max-width:700px){.sheet{padding:28px 18px;margin:12px 8px}.row{grid-template-columns:1fr!important;gap:2px!important}.row .d{color:var(--muted)}}
@media print{html,body{background:#fff}.sheet{box-shadow:none;margin:0;padding:0;max-width:none}.bar{display:none}}
a{color:var(--navy);text-decoration:none}
header{display:grid;gap:4px;margin-bottom:6px}
h1{font-weight:400;font-size:22pt;letter-spacing:.02em;margin:0;font-variant:small-caps;font-variant-numeric:lining-nums}
.pos{font-size:11pt;color:var(--muted)}
.contact{font-size:9.4pt;color:var(--muted);font-variant-numeric:lining-nums}
.contact a{color:var(--navy)}
h2{font-size:11pt;font-weight:700;font-variant:small-caps;letter-spacing:.08em;color:var(--navy);margin:20px 0 8px;padding-bottom:3px;border-bottom:.6pt solid var(--rule);break-after:avoid}
h3{font-size:10.4pt;font-style:italic;font-weight:400;margin:10px 0 4px;color:var(--muted);break-after:avoid}
p{margin:0}
.row{display:grid;grid-template-columns:1.15in 1fr;gap:14px;margin:0 0 8px;break-inside:avoid}
.row .d{font-variant-numeric:lining-nums tabular-nums;white-space:nowrap}
.row .role{font-weight:700}
.row .note{color:var(--muted);font-size:9.8pt}
.row ul{margin:3px 0 0;padding-left:1.05em}
.row li{margin:1px 0;text-align:justify}
.interests{text-align:justify}
ol.pubs{margin:0;padding-left:2.2em;font-variant-numeric:lining-nums}
ol.pubs li{margin:0 0 5px;padding-left:.2em;text-align:justify;break-inside:avoid}
ol.pubs li::marker{color:var(--muted);font-size:9.4pt}
ol.pubs a{font-size:9pt;color:var(--muted)}
.badge{font-size:8.2pt;font-variant:small-caps;letter-spacing:.06em;color:var(--navy);font-weight:700;white-space:nowrap}
.metrics{color:var(--muted);font-size:9.4pt;margin:0 0 6px;font-variant-numeric:lining-nums}
ul.plain{margin:0;padding-left:1.05em}
ul.plain li{margin:0 0 3px;text-align:justify;break-inside:avoid}
.sk p{margin:0 0 3px;text-align:justify}
.row .sub{font-style:italic;color:var(--muted);font-size:9.8pt;margin-top:4px}
.xnote{font-size:9pt;color:var(--muted)}
h2,h3{orphans:3}
ol.pubs,ul.plain{orphans:2;widows:2}
"""


def build(root, site, papers):
    cv = json.loads((root / "data/cv.json").read_text())
    ac = cv["academic"]
    NOTES.clear(); NOTES.update(ac.get("arxiv_notes", {}))
    by = {p["slug"]: p for p in papers}
    order = cv.get("publication_order", [])
    pubs = [p for p in papers if p["slug"] not in order] + [by[s] for s in order if s in by]
    research = cv["research"]

    def bullets(i):
        return "<ul>" + "".join(f"<li>{x}</li>" for x in research[i]["items"]) + "</ul>"

    appts = "".join(
        f'<div class="row"><span class="d">{E(a["when"])}</span><div><p class="role">{E(a["role"])}</p>'
        f'<p>{E(a["org"])}</p>' + (f'<p class="note">{E(a["note"])}</p>' if a.get("note") else "")
        + (bullets(a["research"]) if "research" in a else "")
        + "".join(f'<p class="sub">{research[i]["lab"]}</p>{bullets(i)}' for i in a.get("research_multi", [])) + "</div></div>"
        for a in ac["appointments"])

    def year(s):
        m = re.search(r"\((\d{4})\)", s)
        return m.group(1) if m else ""
    edu = "".join(
        f'<div class="row"><span class="d">{year(e["degree"])}</span><div><p class="role">{E(re.sub(r" \(\d{4}\)$", "", e["degree"]))}</p>'
        + (f'<p class="note">Thesis: <i>{e["thesis"]}</i></p>' if e.get("thesis") else "") + "</div></div>"
        for e in cv["education"])

    peer = [p for p in pubs if p["cv"].get("journal") and not p["cv"].get("accepted")]
    acc = [p for p in pubs if p["cv"].get("accepted")]
    sub = [p for p in pubs if not p["cv"].get("journal") and not p["cv"].get("accepted")]
    n = len(pubs)
    blocks = []
    for label, group in (("Accepted", acc), ("Submitted and preprints", sub), ("Peer-reviewed journal articles", peer)):
        items = []
        for p in group:
            items.append(_pub(n, p)); n -= 1
        blocks.append(f'<h3>{label}</h3><ol class="pubs" reversed>{"".join(items)}</ol>')
    st = site.get("stats", {})
    metrics = (f'<p class="metrics">{len(pubs)} publications and preprints · {st.get("citations")} citations · h-index {st.get("h_index")} '
               f'(<a href="{E(site["profiles"][0]["url"])}">Google Scholar</a>, {E(st.get("as_of", ""))})</p>') if st else ""

    awards = "".join(
        f'<div class="row"><span class="d">{E(a["year"].replace(" - ", "–"))}</span><div>{E(a["title"])}' + (f', {E(a["org"])}' if a.get("org") else "") + "</div></div>"
        for a in cv["awards"])
    talks = "".join(f"<li>{x}</li>" for x in cv["invited_talks"])
    confs = "".join(f"<li>{x}</li>".replace("<u>", "<b>").replace("</u>", "</b>") for x in cv["conferences"])
    service = "".join(f"<li>{x}</li>" for x in cv["service"])
    mentoring = "".join(f"<li>{x}</li>" for x in cv["mentoring"])
    skills = "".join(f'<p><b>{s["label"]}:</b> {s["text"]}</p>' for s in cv["skills"])
    sch = next((p["url"] for p in site["profiles"] if "Scholar" in p["name"]), "")
    orc = next((p for p in site["profiles"] if p["name"] == "ORCID"), None)
    home = site["url"].replace("https://", "")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>CV · {E(site['name'])}</title>
<meta name="description" content="Curriculum vitae of {E(site['name'])}, experimental physicist: appointments, publications, talks and skills.">
<link rel="canonical" href="{E(site['url'])}/cv.html">
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
<style>{CSS}</style></head>
<body>
<nav class="bar"><a href="./">← {E(site['name'])}</a><span class="seg" role="group" aria-label="CV format"><a href="resume.html">2-page resume</a><a href="cv.html" class="on" aria-current="page">Full CV</a></span><a class="pdf" href="files/MJBalakan_CV.pdf">Download PDF</a></nav>
<main class="sheet">
<header>
<h1>{E(site['name'])}</h1>
<p class="pos">{E(ac['position'])} · {E(ac['location'])} · {E(ac['status'])}</p>
<p class="contact"><a href="mailto:{E(site['email'])}">{E(site['email'])}</a> · <a href="{E(site['url'])}">{E(home)}</a> · <a href="{E(sch)}">Google Scholar</a>{f' · ORCID <a href="{E(orc["url"])}">{E(orc["handle"])}</a>' if orc else ''}</p>
</header>

<h2>Research interests</h2><p class="interests">{E(ac['interests'])}</p>
<h2>Appointments</h2>{appts}
<h2>Education</h2>{edu}
<h2>Awards, fellowships and funding</h2>{awards}
<h2 style="break-before:page">Publications</h2>{metrics}<p class="metrics">{E(ac.get('name_note',''))}</p>{''.join(blocks)}
<h2>Invited talks</h2><ul class="plain">{talks}</ul>
<h2>Conference presentations</h2><ul class="plain">{confs}</ul>
<section style="break-inside:avoid"><h2>Teaching and mentoring</h2><p style="margin-bottom:4px">{cv['teaching']}</p><ul class="plain">{mentoring}</ul></section>
<h2>Professional service</h2><ul class="plain">{service}</ul>
<h2>Technical skills</h2><div class="sk">{skills}</div>
<h2>References</h2><p>{E(ac['references'])}</p>
</main></body></html>"""
    (root / "cv.html").write_text(page)


def make_pdf(root, site):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    month = datetime.date.today().strftime("%B %Y")
    f = "font:8pt 'TeX Gyre Pagella','Palatino Linotype',serif;color:#5a6070;width:100%;padding:0 0.9in;display:flex;justify-content:space-between"
    header = f'<div style="{f}"><span>M. J. Balakan · Curriculum Vitae</span><span>Last updated {month}</span></div>'
    footer = f'<div style="{f};justify-content:flex-end"><span>page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content((root / "cv.html").read_text(), wait_until="load")
        pg.pdf(path=str(root / "files/MJBalakan_CV.pdf"), format="Letter", display_header_footer=True,
               header_template=header, footer_template=footer,
               margin={"top": "0.85in", "bottom": "0.8in", "left": "0.9in", "right": "0.9in"})
        b.close()
    return True
