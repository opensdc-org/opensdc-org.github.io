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

## Bilingual text

Every visible string has an English and a Chinese version:
`<span data-en>...</span><span data-zh>...</span>`. The toggle in the nav switches between them.

## Local preview

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```
