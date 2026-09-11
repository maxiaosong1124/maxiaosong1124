# Profile Maintenance

The README is generated automatically. Edit `data/personal.json` for the bilingual biography, learning directions and vision; use the Actions tab to run **Update profile** afterward.

The GitHub profile itself displays dark PNG modules for the bilingual biography, current learning, vision, projects, activity and contact details. Each module has a 480px mobile variant selected by `<picture>`. Project and event images link to their original records; the interactive terminal button remains available. A collapsed text version preserves readable/searchable biography content.

The 3D contribution GIF is rendered daily from the existing Three.js scene using Playwright (64 frames, eight-second loop), then encoded with Pillow. Desktop and mobile versions are generated separately. Font packages provide predictable Chinese glyphs; dependencies are pinned. No chart is fabricated and no client-side JavaScript is required to animate the GIF on GitHub.

The complete interactive terminal is deployed to https://maxiaosong1124.github.io/maxiaosong1124/ using GitHub Pages. The same daily job builds both versions from identical fresh data, uploads `_site/`, and deploys it. `web/` contains the webpage source and local Three.js assets. `tools/build_preview.py` bundles a self-contained HTML page with static fallback content. GitHub itself cannot run the site's JavaScript or custom page CSS.

The workflow refreshes public GitHub data every day at 00:30 UTC (08:30 Asia/Shanghai). GitHub may delay scheduled runs. Public repository schedules may be disabled after 60 days without repository activity; check the Actions tab if updates stop.

Updated content includes the contribution calendar and 3D SVG, statistics, 30-day activity chart, latest 100 public events, public authored PR/issue project list, and up to three non-fork repositories with the highest nonzero star counts. Core Contributor is an owner-provided profile label.

Public PR and issue searches include pagination. Incomplete requests fail without publishing partial output. GitHub search has a 1,000-result limit; if reached, split searches by date before resuming updates. Private activity and other people's PR reviews are not included in the project discovery query.

`GITHUB_TOKEN` is provided automatically by Actions. No personal access token or external chart service is required. Generated SVGs are checked into this repository; GitHub image caching may delay their appearance.

To regenerate locally with public API access:

```sh
python3 scripts/refresh.py
```

The `tools/` generator sources are shared with the local design workspace. GitHub Profile renders the Markdown and SVG version; it does not run the interactive webpage's JavaScript.
