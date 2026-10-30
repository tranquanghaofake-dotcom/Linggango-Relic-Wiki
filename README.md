# Linggango Relic Wiki

An unofficial wiki for the Linggango Minecraft modpack: curios, gear tiers by Act, bosses, a build planner and the pack's mechanics, with numbers read from the pack itself.

- Live site: https://tranquanghaofake-dotcom.github.io/Linggango-Relic-Wiki/
- Offline single file: https://tranquanghaofake-dotcom.github.io/Linggango-Relic-Wiki/dist/Linggango_Relic_Wiki.html

## Build

Needs Python 3.12+, Node 22 and Playwright with Chromium (`npm install -g playwright && npx playwright install chromium`).

```bash
bash build/patches/apply_all.sh   # build: data patches, site, offline file (about 10 s)
bash build/check.sh               # the checks CI runs before deploying (about 5 min)
```

How it works: `build/README.md`. Every push to `main` is built, checked and deployed by `.github/workflows/site.yml`; build outputs are not committed.

Fan content, not affiliated with Mojang, Microsoft or the pack's authors. Texture credits are in the site's footer.
