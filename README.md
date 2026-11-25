[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/dilandagempa25-design/news-image-20261124-lanzking/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/dilandagempa25-design/news-image-20261124-lanzking/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# 24 November 2026 — The World in One Image (Poster Edition)

A bold breaking-news poster that sums up Tuesday 24 November 2026 in a
single 1024×1024 image, generated entirely by a Python standard-library
program — no Pillow, no fonts, no network at run time. Glyph bitmaps are
pre-rendered at build time into `glyphs.bin` (see `make_glyphs.py`) and
blitted by `main.py` onto its own pixel buffer; every panel, icon and the
tanker-in-the-strait illustration is drawn with hand-rolled raster code,
and the PNG is encoded with `zlib` deterministically.

## The edition

- **Lead — Hormuz:** Iran's Revolutionary Guard says three oil tankers hit
  mines in the Strait of Hormuz despite a US escort (unconfirmed by US
  Central Command); the US sanctioned 24+ Iranian exchange houses over
  "shadow banking" and Tehran ruled out talks until its seven conditions
  are met.
- **Nvidia** reinstated Jensen Huang as CEO less than a week after he said
  he would retire, reportedly after President Trump intervened; shares
  jumped about 31%.
- **Shenzhou-24** carried two Chinese astronauts and Pakistani astronaut
  Zeeshan Ali — the first foreign astronaut aboard China's Tiangong station.
- A **Houthi strike** hit Riyadh's tallest tower for the second time in a
  week, injuring 11; the coalition denounced a terrorist attack.
- The **European Commission** proposed a 22nd sanctions package against
  Russia — about 60 more banks and crypto networks, pending all 27 states.
- **North Korea** demanded closure of Switzerland's new Pyongyang office
  and ordered the senior Swiss diplomat to leave.
- A **5.6-magnitude earthquake** struck Nepal's Koshi province, near China.
- **Fourteen countries** affirmed the ICJ decision establishing Myanmar's
  genocide of the Rohingya; Malaysia will return 6,500+ Rohingya refugees.
- **Markets at the close:** S&P 500 7,237.17 (+4.73%), Nasdaq 24,089.56
  (+6.51%), DAX 25,337.27 (+2.15%), FTSE 100 10,480.82 (+1.30%),
  Brent $86.7 (−2.99%), Gold $3,620.4 (−0.85%).

## How to run

```sh
python3 main.py
```

Stdlib only. Writes `entry.png` (1024×1024) to `$MAKEFUN_OUTPUT_DIR`
(default `/output`), falling back to the script's own directory.
To regenerate the glyph data on a build machine with Pillow:
`python3 make_glyphs.py`.
