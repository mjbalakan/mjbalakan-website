# mjbalakan.com

Personal research website and CV of Mohammad Javadi (MJ) Balakan, hosted on GitHub Pages.

## One source, two outputs
Everything is generated from three data files:

| File | What it holds | Used by |
|---|---|---|
| `data/papers.json` | Every paper once: title, year, links, website summary, and a `cv` block (author list and journal as printed in the CV) | Website publications + paper pages, CV publications |
| `data/site.json` | Website text: header, research, news, career rows, skills | Website |
| `data/cv.json` | CV-only content: dated header, address, employment, education, awards, skills, service, research experience, teaching, talks, conferences | CV; awards with `"web": true` also show on the website |

Name, email and homepage come from `site.json` and appear in both.

## Updating
1. Edit the data files (adding a paper = one entry in `papers.json`; it appears on the site, gets its own page, and is listed first in the CV).
2. Run `python3 build.py`. It writes `index.html`, `papers/*.html`, `cv.html` + `files/MJBalakan_CV.pdf` (full CV), `resume.html` + `files/MJBalakan_Resume.pdf` (2-page resume), `sitemap.xml`, `robots.txt`, `404.html`.
   The PDF step needs Playwright (`pip install playwright && playwright install chromium`); without it, use `python3 build.py --no-pdf`.
3. Commit and push. GitHub Pages republishes within a minute or two.

Text in `cv.json` may contain simple HTML (`<i>`, `<b>`, `<u>`, `<a>`, `<sub>`).
