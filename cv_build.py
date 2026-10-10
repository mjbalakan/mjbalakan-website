"""CV generator: data/cv.json + data/site.json + data/papers.json  ->  cv.html (+ files/MJBalakan_CV.pdf).

Called from build.py. The PDF step needs Playwright with Chromium; if it is missing the
HTML is still written and the PDF step is skipped with a message.
"""
import json, re, html, pathlib

E = html.escape


def _me(authors):
    """Underline the author's own name, as in the original CV."""
    return re.sub(r"(M\. J\. Balakan|M\. Javadi)", r"<u>\1</u>", E(authors))


def _pub(p):
    c = p["cv"]
    title = E(p["title"].replace("⁠", ""))
    if c.get("journal"):
        body = f'{_me(c["authors"])}, {title}, <i>{E(c["journal"])}</i> {E(c["ref"])}, ({p["year"]})'
    else:
        body = f'{_me(c["authors"])}, {title}, {E(c["tail"])}'
    if c.get("badge"):
        body += f' [<b class="badge">{E(c["badge"])}</b>]'
    return f"<li>{body}.</li>"


CSS = r"""
@page{size:Letter;margin:0.75in 1in 0.85in 1in}
:root{--ink:#111;--grey:#555;--link:#1a55c4;color-scheme:light}
*{box-sizing:border-box}
html{background:#e9eaee}
body{margin:0;background:#e9eaee;color:var(--ink);font:10.6pt/1.5 "Times New Roman","Tinos","TeX Gyre Termes","Liberation Serif",Times,serif}
.sheet{background:#fff;max-width:8.5in;margin:24px auto;padding:0.75in 1in 0.9in;box-shadow:0 2px 14px rgba(0,0,0,.12)}
.bar{max-width:8.5in;margin:16px auto 0;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding-inline:16px;font:500 14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
.bar a{color:#1b2440;text-decoration:none;padding:8px 14px;border:1px solid #c9ccd6;border-radius:8px;background:#fff}
.bar a.pdf{background:#1b2440;color:#fff;border-color:#1b2440}
@media (max-width:700px){.sheet{padding:28px 18px;margin:12px 8px}}
@media print{html,body{background:#fff}.sheet{box-shadow:none;margin:0;padding:0;max-width:none}.bar{display:none}}
a{color:var(--link)}
a.plain{text-decoration:none}
.dated{text-align:right;line-height:1.35;font-size:9.6pt}
h1{font-weight:400;font-size:15.5pt;margin:12px 0 14px}
.loc{margin:0 0 16px}
.addr{color:var(--grey);margin:0 0 16px;font-size:10pt;line-height:1.45}
.contact{margin:0;font-size:10pt;line-height:1.5}
h2{font-size:11pt;font-weight:700;margin:26px 0 12px;break-after:avoid}
.ind{padding-left:0.48in}
.emp{margin-bottom:18px}
.emp p,.edu p{margin:0;line-height:1.6}
.emp .sub{padding-left:0.24in}
.edu{margin-bottom:16px}
.edu .th{padding-left:0.52in;text-indent:-0.3in;line-height:1.5}
ul{margin:0;padding-left:0.48in}
li{margin:0 0 7px;padding-left:0.08in;break-inside:avoid}
.just li,.just p{text-align:justify}
.skills p{margin:0 0 9px;padding-left:0.22in;text-align:justify;line-height:1.5}
.rx{margin-bottom:20px;break-inside:avoid-page}
.rx h3{font-size:10.6pt;font-weight:700;font-style:italic;margin:0 0 8px;line-height:1.45}
.teach{padding-left:0.48in;text-align:justify;margin:0 0 18px}
.badge{color:var(--link)}
.brk{break-before:page}
"""


def build_cv(root, site, papers):
    cv = json.loads((root / "data/cv.json").read_text())
    by = {p["slug"]: p for p in papers}
    order = cv.get("publication_order", [])
    new = [p for p in papers if p["slug"] not in order]          # papers not yet ordered go first
    pubs = new + [by[s] for s in order if s in by]

    emp = "".join(
        '<div class="emp ind">' + "".join(f"<p>{r}</p>" for r in g["roles"])
        + "".join(f'<p class="sub">{l}</p>' for l in g["lines"]) + "</div>" for g in cv["employment"])
    edu = "".join(
        f'<div class="edu ind"><p>{e["degree"]}</p>' + (f'<p class="th">Thesis: {e["thesis"]}</p>' if e.get("thesis") else "") + "</div>"
        for e in cv["education"])
    awards = "".join(f'<li>{", ".join(x for x in (a["title"], a.get("org"), a["year"]) if x)}</li>' for a in cv["awards"])
    skills = "".join(f'<p><b>{s["label"]}:</b> {s["text"]}</p>' for s in cv["skills"])
    service = "".join(f"<li>{x}</li>" for x in cv["service"])
    research = "".join(
        f'<div class="rx"><h3>{r["lab"]}' + (f'<br>{r["topic"]}' if r.get("topic") else "") + '</h3><ul class="just">'
        + "".join(f"<li>{i}</li>" for i in r["items"]) + "</ul></div>" for r in cv["research"])
    mentoring = "".join(f"<li>{x}</li>" for x in cv["mentoring"])
    talks = "".join(f"<li>{x}</li>" for x in cv["invited_talks"])
    confs = "".join(f"<li>{x}</li>" for x in cv["conferences"])
    publist = "".join(_pub(p) for p in pubs)
    home = site["url"].replace("https://", "")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>CV · {E(site['name'])}</title>
<meta name="description" content="Curriculum vitae of {E(site['name'])}: employment, education, awards, skills, research experience and publications.">
<link rel="canonical" href="{E(site['url'])}/cv.html">
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tinos:ital,wght@0,400;0,700;1,400;1,700&display=swap">
<style>{CSS}</style></head>
<body>
<nav class="bar"><a href="./">← {E(site['name'])}</a><a class="pdf" href="files/MJBalakan_CV.pdf">Download PDF</a></nav>
<main class="sheet">
<div class="dated">{E(cv['updated'])}<br>{E(cv['status_note'])}</div>
<h1>{E(site['name'])}</h1>
<p class="loc">Location: {E(cv['location'])}</p>
{('<p class="addr">' + '<br>'.join(E(a) for a in cv['address']) + '</p>') if cv.get('address') else ''}
<p class="contact">{('Phone: ' + E(cv['phone']) + '<br>') if cv.get('phone') else ''}Email: {E(site['email'])}<br>Homepage: <a href="{E(site['url'])}">{E(home)}</a></p>

<h2>Employment History</h2>{emp}
<h2>Education</h2>{edu}

<h2 class="brk">Awards and Honors</h2><ul>{awards}</ul>
<h2>Technical Skills</h2><div class="skills">{skills}</div>
<h2>Professional Service</h2><ul class="just">{service}</ul>
<h2>Research Experience</h2>{research}

<h2 class="brk">Teaching And Mentoring</h2><p class="teach">{cv['teaching']}</p><ul class="just">{mentoring}</ul>
<h2>Invited Talks</h2><ul class="just">{talks}</ul>
<h2>Publications</h2><ul class="just">{publist}</ul>
<h2>Conference Presentations</h2><ul class="just">{confs}</ul>
</main>
</body></html>"""
    (root / "cv.html").write_text(page)
    return cv


def make_pdf(root):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed: skipped PDF (cv.html was still built)")
        return False
    footer = ('<div style="width:100%;font:9pt \'Times New Roman\',\'Liberation Serif\',serif;'
              'text-align:right;padding-right:1in;color:#111"><span class="pageNumber"></span></div>')
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        html_text = (root / "cv.html").read_text()
        # print without the web-font request so it renders offline with local Times-metric fonts
        html_text = re.sub(r'<link rel="stylesheet" href="https://fonts[^>]+>', "", html_text)
        pg.set_content(html_text, wait_until="load")
        (root / "files").mkdir(exist_ok=True)
        pg.pdf(path=str(root / "files/MJBalakan_CV.pdf"), format="Letter", print_background=False,
               display_header_footer=True, header_template="<div></div>", footer_template=footer,
               margin={"top": "0.75in", "bottom": "0.85in", "left": "1in", "right": "1in"})
        b.close()
    return True
