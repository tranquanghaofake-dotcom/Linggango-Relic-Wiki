# Fonts embedded by build.py

`Monocraft.woff2`, `Monocraft-Bold.woff2`: Monocraft by Idrees Hassan (github.com/IdreesInc/Monocraft @04d8a6f3c0, v4.2.1),
SIL Open Font License 1.1 (`OFL.txt`). Subset to Latin (U+0020-007E, U+00A0-00FF and a few punctuation marks) with
`pyftsubset dist/Monocraft-otf/Monocraft.otf --unicodes=… --flavor=woff2 --layout-features='*'`. The display face of the wiki
(headings, buttons, labels): it draws every letter and digit unambiguously, which Pixelify Sans did not (B like 8, C like O, 2 like 8).

`Jersey15.woff2`: Jersey 15 by The Soft Type Project (github.com/scfried/soft-type-jersey), SIL Open Font License 1.1
(`OFL-Jersey15.txt`); the Latin subset Google Fonts serves (fonts.gstatic.com/s/jersey15/v4). The title face: page titles and
section headings, in capitals, the way the game's own logo and menus set big words. Labels, tables and small UI stay in Monocraft.

`Monocraft-Cyrillic.woff2`, `Monocraft-Bold-Cyrillic.woff2`: the same Monocraft (v4.2.1 release, `Monocraft.otf` and `weights/Monocraft-Bold.otf`), subset to
U+0401, U+0410-044F, U+0451, U+2116 (`python -m fontTools.subset … --flavor=woff2 --layout-features='*'`). The Latin faces above stop at Latin-1, so Russian had no
Monocraft; `build.py` `EXTRA` declares these with a `unicode-range`, and the browser fetches them only when Cyrillic text is drawn. Titles in Russian fall
through Jersey 15 (no Cyrillic) to Monocraft.

`VT323-Vietnamese.woff2`: VT323 by Peter Hull, SIL Open Font License 1.1 (`OFL-VT323.txt`), from github.com/google/fonts `ofl/vt323`, subset to Basic Latin, Latin-1, the
Vietnamese letters (U+0102-0103, 0110-0111, 0128-0129, 0168-0169, 01A0-01A1, 01AF-01B0, 1EA0-1EF9) and a few punctuation marks. It is the face of titles and labels
when `html[lang=vi]` (`style.game.css`, last block): Monocraft and Jersey 15 lack 48 of the 74 Vietnamese letters and no pixel font has both Vietnamese and
Cyrillic (measured 2026-11-08). Declared `size-adjust:127%` because VT323 is drawn smaller than Monocraft; the weight range 400-900 keeps the browser from
smearing a fake bold over a pixel face. The body text of every language stays Be Vietnam Pro.

