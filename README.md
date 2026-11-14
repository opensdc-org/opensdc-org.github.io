# opensdc-org.github.io

Source of the OpenSDC website: https://opensdc-org.github.io

Plain static HTML — no build step. Edit `index.html` and push to `main`; GitHub Pages redeploys in about a minute.

## Adding a project

Edit the `PROJECTS` array near the bottom of `index.html`:

```js
{ name:"MyZip", group:"domain",            // "general" or "domain"
  domain:"Climate", domainZh:"气象气候",     // domain-specific only
  repo:"https://github.com/opensdc-org/MyZip",
  en:"One-line English description.",
  zh:"一句话中文简介。",
  pub:"SC '26", pubUrl:"https://doi.org/..." }
```

## Bilingual pages

- `index.html` — English (default): https://opensdc-org.github.io/
- `zh.html` — 中文: https://opensdc-org.github.io/zh.html

The two files are identical except for `<html lang="en|zh">`, the `<title>` / description, and the language link in the nav.
Every visible string has both versions, `<span data-en>...</span><span data-zh>...</span>`, and the page's `lang` decides which one shows.
When you change content, apply the same edit to both files.

## Local preview

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Benchmark entry points

OpenSDC-Bench is featured in the navigation, hero, dedicated `#benchmark` section, and roadmap in both language pages.

- Published benchmark: https://opensdc-org.github.io/benchmark/
- Evaluation code: https://github.com/opensdc-org/OpenSDC-Bench
- Benchmark website source: https://github.com/opensdc-org/benchmark

Keep these links and the English/Chinese descriptions consistent when editing either page. The `/benchmark/` site is deployed separately; this repository links to it.

## Data Compression Survey

- Page: https://opensdc-org.github.io/survey/
- Source: [survey/index.html](survey/index.html)

The survey is a standalone Chinese-language HTML page. It uses the main site's
existing GitHub Pages deployment and has links from both homepages. Keep the
route stable when updating the catalogue. Update the rendered paper cards and
embedded paper data together, and retain source links and the search cutoff
date.
