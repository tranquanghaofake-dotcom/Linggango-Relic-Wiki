# Pixel tools

## In this library (own code, `tools/`)
| Script | What it does |
|---|---|
| `tools/fxgen.py` + `palettes.py` | draws effects on the 16 px grid with a 4–5 step ramp, hard alpha, light from the top left: slash (8 frames), magic circle (8), shockwave (6), sparkle (4), burst (6), beam (4), orb (6), embers (8), 16 runes; 12 themes (nether, soul, sculk, end, gold, meadow, cave, arcane, blood, epic, frost, poison). Deterministic. Output in `lib/lgw-fxgen/`, preview `lib/lgw-fxgen/contact_sheet.png` |
| `tools/pixelfix.py` | puts any image on a true pixel grid: auto-detects the block size from the edge-energy period (tested: an 8×8 vanilla flame blown up ×12 and blurred comes back as the same 8×8 alpha mask), downscales by dominant colour (no in-between colours), hard alpha, palette from a theme ramp / a reference PNG / median cut, removes stray pixels. `--soft` maps glows and smoke (alpha × brightness) onto a ramp. For AI output, upscaled art and soft particles |

## Reputable open-source tools (checked 2026-10-27; not vendored, reference only)
| Tool | Licence | Use |
|---|---|---|
| [proper-pixel-art](https://github.com/KennethJAllen/proper-pixel-art) @4de0dda | MIT | clean AI pixel art to true resolution (Python, PyPI) |
| [unfake.js](https://github.com/jenissimo/unfake.js) @6636868 / [unfake.py](https://github.com/painebenjamin/unfake.py) @942cd1f | MIT | scale detection, palette quantisation, jaggy cleanup (browser / Python + Rust) |
| [spritegrid](https://github.com/marksverdhei/spritegrid) @64ab6f3 | MIT | grid detection and resampling, ComfyUI node |
| [restore-pixel-art](https://github.com/elle-trudgett/restore-pixel-art) @40963c5 | MIT | grid by autocorrelation, palette extraction |
| [Sprite Fusion pixel-snapper](https://github.com/Hugo-Dz/spritefusion-pixel-snapper) @02f9315 | MIT | snap to grid with a fixed palette |
| [PixelRefiner](https://github.com/HappyOnigiri/PixelRefiner) @c32659f | MIT | browser batch cleanup, background removal |
| [PixelOE](https://github.com/KohakuBlueleaf/PixelOE) @7ce444b | Apache-2.0 | pixelise photos/paintings with outline expansion |
| [pyxelate](https://github.com/sedthh/pyxelate) @f4a046b | MIT | image → pixel art with dithering and palette transfer |
| [pixel-sprite-generator](https://github.com/zfedoran/pixel-sprite-generator) @8c2cee7 | MIT | procedural sprites from masks |
| [Pixelorama](https://github.com/Orama-Interactive/Pixelorama) @6caa670 | MIT | full pixel editor with animation (Godot) |
| [LibreSprite](https://github.com/LibreSprite/LibreSprite) @20bd251 | GPL-2.0 | Aseprite-like editor (fork of the last GPL Aseprite) |
| theamusing/perfectPixel @72096de | no licence file | reference only (no licence = all rights reserved) |

Tool licences cover the tools, not what you make with them: output drawn by the owner (or by `fxgen.py`) is the owner's.

## AI-generated art (allowed by the owner)
1. Generate at 1024 px with a prompt that names the effect, the frame count, "pixel art, 16x16 grid per frame, hard edges, no anti-aliasing, transparent background, limited palette", and **never** the name of a living artist, a resource pack or a mod (style imitation of a named source is where AI art gets close to copying).
2. `python3 -I tools/pixelfix.py in.png out.png --ramp <theme>` (or `--size 16` when the grid is not detected).
3. Check by eye at ×1 and ×4 next to a vanilla particle; redraw stray pixels by hand.
4. Catalog row: `source` = model name, `license` = "AI-generated (no copyright claimed)", `note` = the prompt. Purely machine-made images may not be protected by copyright (US Copyright Office, 2025 report), so the wiki can use them but cannot claim them.
The session that built this library had Figma's `generate_image` available, but it spends the owner's Figma AI credits, so it was not run without asking.
