# Profile Maintenance

The README is generated automatically. Edit `data/personal.json` for the bilingual biography, learning directions and vision; use the Actions tab to run **Update profile** afterward.

The workflow refreshes public GitHub data every day at 00:30 UTC (08:30 Asia/Shanghai). GitHub may delay scheduled runs. Public repository schedules may be disabled after 60 days without repository activity; check the Actions tab if updates stop.

Updated content includes the contribution calendar and 3D SVG, statistics, 30-day activity chart, latest 100 public events, public authored PR/issue project list, and up to three non-fork repositories with the highest nonzero star counts. Core Contributor is an owner-provided profile label.

Public PR and issue searches include pagination. Incomplete requests fail without publishing partial output. GitHub search has a 1,000-result limit; if reached, split searches by date before resuming updates. Private activity and other people's PR reviews are not included in the project discovery query.

`GITHUB_TOKEN` is provided automatically by Actions. No personal access token or external chart service is required. Generated SVGs are checked into this repository; GitHub image caching may delay their appearance.

To regenerate locally with public API access:

```sh
python3 scripts/refresh.py
```

The `tools/` generator sources are shared with the local design workspace. GitHub Profile renders the Markdown and SVG version; it does not run the interactive webpage's JavaScript.
