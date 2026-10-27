# Fonts embedded by build.py

`Monocraft.woff2`, `Monocraft-Bold.woff2`: Monocraft by Idrees Hassan (github.com/IdreesInc/Monocraft @04d8a6f3c0, v4.2.1),
SIL Open Font License 1.1 (`OFL.txt`). Subset to Latin (U+0020-007E, U+00A0-00FF and a few punctuation marks) with
`pyftsubset dist/Monocraft-otf/Monocraft.otf --unicodes=… --flavor=woff2 --layout-features='*'`. The display face of the wiki
(headings, buttons, labels): it draws every letter and digit unambiguously, which Pixelify Sans did not (B like 8, C like O, 2 like 8).
