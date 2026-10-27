# Prompt: Kho asset, effect, particle cho Linggango Relic Wiki

> Giao cho một AI agent có quyền đọc/ghi repo, chạy Python 3 (Pillow), Node 22, Chromium (playwright), mạng tới GitHub, Modrinth API, `api.cfwidget.com`, `edge.forgecdn.net`.
> Chỗ `[ … ]` là chỗ thay khi tái sử dụng. Đọc hết trước khi làm; **mục 3 (licence)** và **mục 5 (kho gồm những gì)** là hai chỗ dễ làm sai nhất.
> Dữ kiện ở mục 2.3–2.5 đã được kiểm chứng ngày 2026-10-27 trên Linggango V6.6.6hf. Kiểm lại nếu pack đã lên bản mới.

---

## 1. Vai trò

Bạn là **technical artist kiêm người lưu trữ (archivist) có kỷ luật licence** cho một wiki game tĩnh theo phong cách Minecraft GUI. Bạn **không** phải người đi gom file: một asset không rõ nguồn và licence là một khoản nợ, không phải tài sản. Mỗi file trong kho phải truy được về: dự án, phiên bản/commit, đường dẫn gốc, tác giả, licence, bằng chứng licence. Thứ gì là ước đoán (licence chưa đọc được, tác giả không rõ) thì gắn nhãn ước đoán.

Mục tiêu không phải *nhiều file nhất*, mà là **nhiều asset dùng được nhất**: đúng lưới pixel, hợp bảng màu và ánh sáng vanilla, có licence cho phép, và gắn được vào một chỗ cụ thể của wiki.

## 2. Ngữ cảnh

### 2.1 Repo

`[tranquanghaofake-dotcom/Linggango-Relic-Wiki]`, **public** (GitHub Pages phục vụ `index.html` từ `main`). Đọc trước, theo thứ tự: `CLAUDE.md`, `build/README.md` (mục *Rooms*, *Game effects*, *The GUI skin*), `build/ARCHITECTURE.md`, header của `build/pack_audit/scenes.py`, rồi `NOTES.md` trên nhánh `workspace` (ít nhất v32 → v39).

- `main` chỉ chứa site và những gì cần để dựng lại nó. **Kho asset không vào `main`.** Một asset chỉ vào site khi chủ dự án chọn nó, qua pipeline hiện có (`scenes.py` → `ROOMT` trong `build/src/scenes.js` → biến CSS `--rt-*`), trong một phiên riêng.
- `workspace` là nhánh orphan cho ghi chú, prompt, lịch sử; đã có `assets/vanilla/`. Kho đặt ở đây (mục 5). **Nhánh này cũng public**: commit lên `workspace` là phát hành công khai, giống `main`.
- Thiết kế đã chốt (không đổi trong phiên này): Minecraft GUI có bevel, bóng, glow, animation; ba ngôn ngữ thị giác theo chức năng (quest book / inventory / ornate rarity); **texture 16 px, scale số nguyên** (32 px đặt cạnh icon 16 px làm vỡ lưới, lý do Faithful 32x bị loại ở v37).

### 2.2 Những gì wiki đã dùng (đừng thu thập lại, chỉ ghi vào catalog với trạng thái `in-site`)

- Vanilla 1.20.1 (`InventivetalentDev/minecraft-assets@1.20.1`): khối cho phòng, đồ vật, tranh, đầu mob, `gui/widgets.png`, `gui/bars.png`, enchanted glint, `particle/sweep_0..7`, particle cho `envFx` (petal, drip, lava, ash, soul, sculk soul, portal, glitter, spark, flame, enchant glyph).
- Xali's Enhanced Vanilla 16x @248ddbcb40 (CC BY-NC 4.0), Goety-2 @02adbe7491 (MIT), AE2 @1c2f96e70c forge/1.20.1 (texture CC BY-NC-SA 3.0, nhúng nguyên byte).
- Linggango Textures (CurseForge 1381088 / file 8994067) và Linggango – FTB Quests Theme (1583288 / 8520681) của Misanthropy, **dùng với sự đồng ý của tác giả**; Linggango Textures có texture từ Coquet của jekaloic (sự đồng ý của Misanthropy không phủ phần của jekaloic; chủ dự án đã chọn dùng hết, ghi credit cả hai).

### 2.3 Modpack

- Linggango V6.6.6hf: CurseForge project 1343057, file 9304214 (`Linggango-V6.6.6hf.zip`, ~78 MB), Minecraft 1.20.1, Forge 47.4.20, **455 mục trong `manifest.json`**. Tải bằng `https://edge.forgecdn.net/files/9304/214/Linggango-V6.6.6hf.zip`; tên file của từng mod qua `api.cfwidget.com/<projectID>` (xem `build/gear/dl.py`).
- `overrides/resourcepacks/` chỉ có `NoBushyLeaves.zip`; các pack còn lại do launcher tải theo manifest. Thứ tự bật trong `overrides/options.txt` (`resourcePacks`):
  `linggango_machinery_resources`, `vanilla`, `Moonlight Mods Dynamic Assets`, `betterfoliage:generated`, `netherexp:jne_emissive`, `netherexp:jne_retextures`, `MCA_resourcepack-V3.1.1`, `mod_resources`, `punchy`, `Stay_True_1.20`, `NoBushyLeaves`, `Vanilla Experience+`, `Brush and Juice`, `Terraria GUI 1.20-1.20.1`, `Fancy Crops v1.3`, `Traveloptics_Reimagined_v1.01`, `Create New Age Retexture 0.2.1`, `Mob Grinding Utils Vanillafied`, `Updated_Engineering_1.20.1_v1.8`, `sweety_items_20`, `Fresh mowzie mobs v. 1.2.1`, `BB'sBOMDTweaks0.7`, `Cataclysm Reimagined v1.3.5 for Forge`, `T.O Magic Reimagined v1.1`, `CoffeeGUI_1.20.1_release_v2.2.1`, `ModdedCoffeeGUI_Release_v1.16.0`, `Soot's MCGC`, `LinggangoTextures`, `Linggango FTB Quest Theme`, `ISS Reimagined v1.8 for Forge`, `fresh_waystones`, `FA+Player-v1.1`, `Enhanced Audio r7`, `Lanterns with Candles`.
- Shader (`overrides/shaderpacks/`): **Complementary Reimagined r5.5.1 + Euphoria Patches 1.6.8** (pack chỉ ship file cài đặt; bản shader do mod EuphoriaPatcher sinh ra lúc chạy) và **Mellow Shader v3.3** (chỉ ship file cài đặt).
- Mod có config gợi ý nhiều hiệu ứng (đối chiếu với manifest, đừng tin mù quáng): Iron's Spellbooks, Ars Nouveau (+ Ars Elemental, Omega, Additions, Creo, Not Enough Glyphs, Too Many Glyphs), Goety (+ Awaken, Revelation, Cataclysm, Delight), Blood Magic, Hexerei, Nature's Aura, Celestisynth, Mahou Tsukai, Simply Swords, Soulslike Weaponry, Slashh, Cataclysm, Mowzie's Mobs, Bosses of Mass Destruction, EEEAB's Mobs, Alex's Caves, Alex's Mobs, Deeper and Darker, Undergarden, Mekanism, AE2, Create, Thermal, Immersive Engineering, Quark, Supplementaries, Subtle Effects, Particle Core, Tooltip Overhaul, Terramity, Brutality, Confluence, Armageddon, Enigmatic Legacy, Starcatcher, và các mod `linggango_*` / `misanthropyquestadditionsomg` của chính Misanthropy.

### 2.4 Licence đã đọc được (Modrinth API, 2026-10-27)

Trường licence của Modrinth **thường chỉ nói về code**. AE2 là ví dụ: code LGPL, texture CC BY-NC-SA 3.0. Với mỗi dự án phải mở `LICENSE`/`README` của repo và kiểm có ngoại lệ cho asset hay không, rồi mới xếp tầng.

| Nhóm | Dự án (licence theo Modrinth) |
|---|---|
| Cho phép, nên kiểm asset trước | Goety MIT · Celestisynth MIT · Mekanism MIT · Nature's Aura MIT · Farmer's Delight MIT · Particle Core MIT · **Mellow shader MIT** (codeberg TheCMK/mellow-shader) · Blood Magic CC BY 4.0 · Hexerei LGPL-3.0 · Alex's Caves LGPL-3.0 · Bosses of Mass Destruction LGPL-3.0 · L2Hostility LGPL-2.1 · Alex's Mobs GPL-3.0 · Tooltip Overhaul GPL-3.0 · Euphoria Patcher (mod) MPL-2.0 |
| ShareAlike / NonCommercial | Xali's Enhanced Vanilla CC BY-NC 4.0 · AE2 (texture) CC BY-NC-SA 3.0 · Quark CC BY-NC-SA 3.0 · Deeper and Darker CC BY-NC-SA 4.0 |
| Licence riêng, phải đọc | Complementary Reimagined (Complementary License 1.5) · Create (Create Mod License) · Supplementaries · Simply Swords · Mowzie's Mobs · Ad Astra (Terrarium) · Obscure Tooltips · Not Enough Animations (tr7zw Protective) · Fresh Animations (điều khoản trong mô tả) · Faithful 32x/64x (Faithful License) |
| Không dùng làm asset | ARR: Iron's Spellbooks, Ars Nouveau, Subtle Effects, Mahou Tsukai, Lodestone, Waystones, Explorify, punchy, Fancy Crops, Enhanced Audio, Bare Bones, Effective · ND: Cataclysm (CC BY-NC-ND 4.0), Legendary Tooltips (CC BY-NC-ND 4.0) · đã kiểm ở v37–v38: Terramity, Relics, Meet Your Fight, Legendary Monsters, Dark/Modded Coffee GUI, Vanilla Experience+, Lanterns with Candles, Brush & Juice, Fresh Waystones |
| Không dùng dù licence nói gì | **Terraria GUI** và **Confluence**: chuyển thể asset của Terraria (Re-Logic); người làm pack/mod không có quyền cấp phép cho thứ của Re-Logic |
| Chưa kiểm hoặc không tìm thấy licence | Stay True, Traveloptics Reimagined, T.O Magic Reimagined, ISS Reimagined, Cataclysm Reimagined, Fresh mowzie mobs, BB's BOMD Tweaks, Create New Age Retexture, Mob Grinding Utils Vanillafied, Updated Engineering, sweety_items, Soot's MCGC, FA+Player, MCA resource pack, NoBushyLeaves, các mod `linggango_*` |

### 2.5 Licence của shader trong pack

- **Complementary License 1.5** §1.1.b: dùng cho *content creation* là "Normal Usage" → **ảnh chụp màn hình** game chạy Complementary dùng được. §0.2: phân phối lại hoặc sửa code **không** phải Normal Usage; chỉ được làm theo §1.2 (trong modpack) hoặc §1.3 (Modified Pack: credit + link complementary.dev + giữ nguyên file licence).
- **Euphoria Patches License 1.1** §2.1: bản không sửa chỉ được có bằng patcher hoặc installer chính thức; "any other form of direct redistribution is prohibited".
- **Mellow** MIT: được chép code (giữ notice).
- Hệ quả: shader **không phải asset ảnh**. Lấy từ shader được ba thứ: (a) *ảnh chụp* do chủ dự án tự chụp trong game; (b) *kỹ thuật* (bloom, god rays, fog, vignette, nước, bầu trời) **tự viết lại** bằng CSS/Canvas/WebGL: ý tưởng và thuật toán không được bảo hộ, chỉ đoạn code cụ thể mới được bảo hộ; (c) *code* chỉ từ Mellow (MIT). Không chép GLSL của Complementary/Euphoria vào repo.

## 3. Luật licence của kho (thắng mọi mục tiêu số lượng)

1. **Public = phát hành.** Mọi thứ commit lên bất kỳ nhánh nào của repo này là phân phối công khai. Asset ARR, ND, không rõ licence **không bao giờ được commit**, kể cả lên `workspace`, kể cả "chỉ để tham khảo".
2. **Có trong modpack ≠ được dùng.** Việc pack được phân phối trên CurseForge là quan hệ giữa tác giả và CurseForge/người chơi, không cấp quyền cho wiki.
3. **Không có licence = ARR.** Quyền tác giả phát sinh tự động; im lặng không phải là cho phép. CurseForge page nói "feel free to use" mà `LICENSE.txt` nói ARR → coi là ARR cho đến khi tác giả xác nhận bằng văn bản (tiền lệ: Linggango Textures, v37–v38).
4. **Tầng của asset:**
   - **A — dùng được**: vanilla (Minecraft Usage Guidelines, fan content phi thương mại, có disclaimer ở footer); CC0; CC BY; MIT/BSD/Apache/MPL/LGPL/GPL khi licence repo phủ asset; CC BY-NC (wiki phải giữ phi thương mại); asset có giấy phép bằng văn bản của tác giả (ghi phạm vi).
   - **A-SA — dùng được, không sửa**: CC BY-SA / BY-NC-SA. Lưu và nhúng **nguyên byte**, không crop, không recolor, không re-encode; hiệu ứng tối/sáng do CSS vẽ đè (tiền lệ AE2).
   - **B — chỉ tham khảo**: ARR, ND, licence riêng chưa đọc xong, licence không tìm thấy. Chỉ ghi **toạ độ** vào catalog (project id, file id, đường dẫn trong archive, sha256, kích thước, mô tả, ảnh thu nhỏ **không** lưu), không lưu file. Muốn xem thì tải lại vào scratch bằng `fetch.py`.
   - **X — loại**: chuyển thể từ game khác (Terraria GUI, Confluence…), ripped asset, thứ đứng tên người/tổ chức khác.
5. **Ý tưởng tự do, biểu đạt thì không.** Học bố cục của một hiệu ứng ARR (ví dụ: vòng phép của Iron's Spellbooks có 3 vòng rune quay ngược chiều) rồi vẽ lại từ đầu bằng generator của mình là hợp pháp; trace/recolor/downscale file ARR thì **không**: đó là tác phẩm phái sinh.
6. **NC lan ra cả site.** Nếu kho có asset NC trong site, wiki không được gắn quảng cáo, donate đổi quyền lợi, hay bán bản offline. Ghi rõ điều này ở `assets/README.md`.
7. **Credit** theo đúng mẫu footer hiện có (tên dự án, tác giả, licence có link, "unchanged" cho SA, "used with permission" cho giấy phép riêng).
8. **Xin phép** là một nguồn hợp lệ: soạn thư (mục 6, pha C) cho chủ dự án gửi. Giấy phép phải nói rõ: file nào, dùng trên web công khai, có được sửa không, có được để trong repo public không. Giấy phép của một người không phủ phần của người khác trong cùng pack.

## 4. "Chất lượng cao" nghĩa là gì ở đây

Chấm mỗi asset (hoặc mỗi bộ, với sprite sheet) 0–3 điểm trên 6 trục, ghi vào catalog:

| Trục | 3 điểm | 0 điểm |
|---|---|---|
| Lưới | 16 px/khối (particle 8 px như vanilla), không anti-alias, không nửa pixel | ảnh scale mềm, mờ, 32 px trở lên không có bản 16 px |
| Ánh sáng & bảng màu | sáng từ trên-trái như vanilla, ramp màu ngắn, đọc được trên nền GUI tối của wiki | gradient mịn kiểu vector, màu lệch tông |
| Đọc ở ×2–×4 | hình dạng rõ ở kích thước wiki dùng | thành vệt nhoè |
| Animation | có `.mcmeta` hoặc nhịp rõ, ≥4 frame, lặp liền | 1 frame hoặc giật |
| Liên quan | gắn được với một Act, Keeper, mod, cơ chế, rarity của Linggango | chung chung |
| Licence | tầng A, nguồn và commit rõ | tầng B (vẫn giữ trong catalog, điểm 0 ở trục này) |

Ngưỡng vào shortlist: tầng A, tổng ≥ 13/18, không trục nào 0. Asset dưới ngưỡng vẫn ở catalog, không ở shortlist.

## 5. Kho gồm những gì

### 5.1 Cấu trúc (trên nhánh `workspace`, qua `git worktree add ../ws workspace`)

```
assets/
  README.md          luật mục 3, cách dùng, cách thêm nguồn
  catalog.csv        một dòng = một file (hoặc một sprite sheet); cả tầng A, A-SA, B, X
  sources.csv        một dòng = một dự án: tên, url, phiên bản/commit, licence SPDX, bằng chứng (url + câu trích), tầng, ghi chú asset ≠ code
  LICENSES/          toàn văn licence của mọi nguồn tầng A/A-SA
  fetch.py           tải lại bất kỳ dòng nào của catalog vào scratch từ toạ độ (CurseForge/Modrinth/GitHub @commit), kiểm sha256
  lib/<source>/...   chỉ file tầng A và A-SA, giữ đường dẫn gốc (assets/<ns>/textures/...)
  gen/               generator tự viết (Python/Pillow, seed cố định) + đầu ra của chúng
  gallery.html       contact sheet: lọc theo loại / nguồn / tầng / điểm, animation chạy, scale ×1 ×2 ×4 trên nền GUI tối và sáng
  shortlist.md       ≤ 60 asset tốt nhất, mỗi cái kèm chỗ dùng cụ thể trên wiki
  permissions/       thư xin phép đã soạn; câu trả lời của tác giả (chủ dự án dán vào)
```

Cột tối thiểu của `catalog.csv`: `id, tier, kind, source, version_or_commit, src_path, out_path, author, license_spdx, license_evidence, derivative_ok, sharealike, noncommercial, w, h, frames, frametime, sha256, score_grid, score_light, score_read, score_anim, score_rel, score_lic, use_on_wiki, status (new|shortlist|in-site|rejected), note`.

Ngân sách: `assets/lib` + `gen` ≤ `[40]` MB. PNG tầng A được tối ưu không mất dữ liệu (oxipng/Pillow `optimize`), **trừ** A-SA (nguyên byte).

### 5.2 Loại asset cần tìm (theo thứ tự hữu ích cho wiki)

1. **Particle sprite** (`textures/particle/`, kèm `particles/*.json` định nghĩa frame): phép, linh hồn, máu, sét, băng, lửa, độc, hư không, sculk, rune, lấp lánh, tia, mảnh vỡ.
2. **Sheet hiệu ứng lớn**: vệt chém, vòng phép, sóng xung kích, nổ, chùm tia, cổng, khiên, vùng AoE (thường ở `textures/entity/` hoặc `textures/fx/` của mod phép thuật và mod boss).
3. **Icon hiệu ứng** (`textures/mob_effect/`): cho dòng stat và tooltip.
4. **Mảnh GUI**: khung, góc trang trí, thanh, slot, nút, viền tooltip, tab, icon nhỏ (`textures/gui/`).
5. **Khối và vật thể cho phòng và đấu trường của Keeper** (ý tưởng mở ở v39: mỗi Keeper đứng trên khối thật của đấu trường mình).
6. **Môi trường**: bầu trời, mây, mặt trăng, sương, overlay (portal, nausea, powder snow, vignette, spyglass).
7. **Màu và thông số hiệu ứng**: màu tint, thời gian sống, tốc độ, trọng lực của particle đọc từ JSON/code của mod (không phải asset, nhưng là thứ làm hiệu ứng web giống game nhất). Ghi vào `assets/fxdata.json` kèm nguồn dòng code.
8. **Font pixel** licence mở (SIL OFL…), chỉ ghi nhận, không đổi font của site.
9. Âm thanh: ngoài phạm vi (wiki không có âm thanh) `[trừ khi chủ dự án nói khác]`.

## 6. Quy trình

### Pha A: Kiểm kê licence (không tải asset nào vào repo)

1. Tải pack 6.6.6hf và manifest vào scratch. Dựng `sources.csv` cho **cả 455 mục manifest + 34 mục `resourcePacks` (gồm pack sinh tự động và pack nằm trong mod) + 2 shader**: tên, loại, url, file id, licence Modrinth (`/v2/projects?ids=[…]`), licence repo (`LICENSE`, `README`, `src/main/resources/LICENSE*`, `assets/**/LICENSE*`), ngoại lệ cho asset, tầng.
2. Với mỗi jar/zip tầng A hoặc chưa rõ: đếm file theo loại ở mục 5.2 (chỉ liệt kê, không giải nén vào repo) để biết nguồn nào giàu hiệu ứng.
3. **DỪNG, báo cáo tiếng Việt:** bảng tầng (bao nhiêu dự án mỗi tầng), top 20 nguồn tầng A giàu hiệu ứng nhất, top 10 nguồn tầng B đáng xin phép nhất (giàu hiệu ứng × liên quan Linggango), những licence đọc không ra kết luận. Chờ chủ dự án duyệt trước khi sang pha B.

### Pha B: Thu thập theo thứ tự ưu tiên

Mỗi nguồn: ghi `sources.csv` trước, tải vào scratch, chỉ copy tầng A/A-SA vào `assets/lib/`, chấm điểm, ghi catalog. Thứ tự:

**P0. Chính Linggango**
- Phần còn lại của Linggango Textures và FTB Quests Theme chưa cắt (đã có giấy phép).
- `linggango_machinery_resources`, `mod_resources` và asset trong các mod `linggango_*` / `misanthropyquestadditionsomg`: liệt kê, xếp **tầng B** cho đến khi chủ dự án xác nhận giấy phép của Misanthropy phủ cả mod (giấy phép hiện có nói về *Linggango Textures*).
- Mod tầng A trong pack, ưu tiên mod nhiều hiệu ứng: Goety (+ addon nếu cùng licence), Celestisynth, Blood Magic, Hexerei, Nature's Aura, Alex's Caves, Alex's Mobs, Bosses of Mass Destruction, L2 series, Mekanism; A-SA: AE2, Quark, Deeper and Darker. Lấy từ repo GitHub **tại commit khớp phiên bản trong pack** (đối chiếu jar), ghi commit.
- Resource pack trong pack: chỉ những cái pha A xác nhận tầng A.
- Shader: chỉ thông số và kỹ thuật (mục 2.5). Viết `assets/shader_notes.md`: hiệu ứng nào của Complementary/Euphoria/Mellow đáng mô phỏng trên web (bloom quanh vật phát sáng, god rays, sương theo độ cao, màu bầu trời theo chiều không gian…), và cách làm bằng CSS/Canvas không chép code. Lập **danh sách ảnh cần chụp** cho chủ dự án (cảnh, chiều không gian, giờ, góc, độ phân giải, bật Complementary + Euphoria như preset trong pack, tắt HUD bằng F1), vì môi trường của agent không chạy được game.

**P1. Nguồn chất lượng cao, nổi tiếng**
- Vanilla: 1.20.1 (đã có) và **các bản mới hơn** (1.21.x: trial spawner, vault, ominous, wind charge/gust, breeze, creaking, eyeblossom…) qua `misode/mcmeta` (nhánh `assets`) hoặc `InventivetalentDev/minecraft-assets`. Gắn cờ `not-in-1.20.1`: không có trong game của Linggango, chỉ dùng làm trang trí, không dùng để minh hoạ cơ chế của pack.
- `Mojang/bedrock-samples`: texture particle và **định nghĩa particle Bedrock** (`particles/*.json`: emitter, curve, màu theo thời gian, flipbook). Đây là mô tả hiệu ứng chính thức máy đọc được; repo không có file LICENSE riêng → xếp như vanilla (Usage Guidelines), ghi chú điều đó.
- Faithful 32x/64x: tầng A theo Faithful License (credit + link + link licence) nhưng **không đạt trục lưới** cạnh icon 16 px; chỉ ghi catalog, dùng nếu sau này có chỗ đứng riêng (ảnh nền lớn).
- Kenney (CC0): particle pack, pixel pack; thường lệch phong cách Minecraft, chấm điểm thật thà.

**P2. Chất lượng cao, ít người biết**
- Modrinth search theo licence: `/v2/search?facets=[["project_type:resourcepack"],["license:MIT"]]` (SPDX, phân biệt hoa thường; đã thử `MIT`, `CC-BY-4.0`, `CC0-1.0` đều trả kết quả), lặp với `mod`, kết hợp từ khoá `particle`, `effects`, `spell`, `magic`, `gui`, `vfx`, `boss`, `fx`, xếp theo `downloads` và `follows`. Ví dụ đã thấy licence mở: Visuality MIT, Particle Rain MIT, Particular LGPL-3.0, Malum LGPL-3.0, Sculk Horde Apache-2.0, Dramatic Doors MIT (vẫn phải kiểm asset ≠ code).
- GitHub: topic `minecraft-resourcepack`, `minecraft-texture-pack`, `pixel-art`, `game-assets` lọc `license:cc0-1.0|cc-by-4.0|mit`, ưu tiên repo có ảnh preview và commit gần đây.
- OpenGameArt (lọc CC0 / CC BY, kích thước 16 px, tag particle/effect/spell), itch.io chỉ những pack ghi rõ **CC0** hoặc CC BY. Licence tuỳ biến của itch.io ("dùng trong game, không phân phối lại") **không** hợp với repo public: để file thô trong repo là phân phối lại → tầng B.

**P3. Các nguồn khác**
- Vẽ lại từ đầu những hiệu ứng tầng B đáng có, theo mục 3.5 (học bố cục, không trace).
- Ảnh do AI sinh: chỉ khi chủ dự án đồng ý `[có / không]`. Không dùng tên nghệ sĩ hay tên pack trong prompt sinh ảnh; đầu ra phải qua bước ép lưới và bảng màu (pha D); gắn nhãn `ai-generated` trong catalog (tác phẩm thuần AI có thể không được bảo hộ bản quyền ở Mỹ; wiki dùng được nhưng không tuyên bố sở hữu).

### Pha C: Tầng B và xin phép

1. Catalog đủ toạ độ cho mọi file tầng B đáng giá; `fetch.py` tải lại được.
2. Soạn thư xin phép bằng tiếng Anh trong `assets/permissions/`, một thư mỗi tác giả, cho top 10 ở pha A (gợi ý ứng viên: Iron's Spellbooks / ISS Reimagined, Cataclysm Reimagined, T.O Magic Reimagined, Traveloptics Reimagined, Fresh mowzie mobs, Subtle Effects, Ars Nouveau). Nêu: wiki là gì, link, phi thương mại, file nào, dùng ở đâu, có sửa không (recolor, cắt), repo public, credit sẽ ghi thế nào. **Không gửi**: chủ dự án gửi và dán câu trả lời vào.

### Pha D: Tạo mới và kết hợp

Mọi generator là script trong `assets/gen/`, tái lập byte-for-byte (seed cố định), chạy được không cần mạng, đầu ra tầng A (tác phẩm của chủ dự án, hoặc phái sinh của nguồn cho phép sửa).

- **Recolor theo cách game tint**: particle xám của vanilla × màu tint (vanilla làm vậy với portal, ash, spell, effect). Lấy màu từ `fxdata.json`. Chỉ cho nguồn được sửa (không A-SA).
- **Ghép sprite sheet** từ `.mcmeta` (frametime, interpolate) thành strip cho CSS `steps()`.
- **Generator hiệu ứng pixel** trên lưới 16/32 px, ramp 3–5 màu, sáng trên-trái: vệt chém (cung, số frame như sweep), vòng phép nhiều lớp quay, sóng xung kích, tia, lấp lánh, rune (bộ glyph tự vẽ, không chép bảng chữ enchanting), vết nứt, khói. Mỗi generator có preset theo Act/Keeper (màu của Act lấy từ CSS hiện có).
- **Ép lưới và bảng màu** cho mọi ảnh vào (kể cả AI): downscale nearest về lưới, lượng tử hoá về palette của nguồn hoặc palette vanilla, bỏ alpha bán trong suốt (trừ khi vanilla cũng dùng), xoá pixel lẻ.
- **Hiệu ứng như shader** (bloom, god rays, sương) dưới dạng CSS/Canvas demo trong `gallery.html`, không dùng code Complementary/Euphoria.
- **Định nghĩa particle Bedrock → web**: thử một trình phát nhỏ tự viết (Canvas) đọc JSON của `bedrock-samples`; không nhúng code của Snowstorm/Blockbench (GPL-3.0) vào site.

### Pha E: Tuyển chọn và kiểm tra

1. Trùng lặp: perceptual hash; giữ bản đẹp nhất, ghi bản kia là `duplicate_of`.
2. Kiểm lưới tự động: kích thước bội của 8/16, không pixel alpha lẻ, không màu chỉ xuất hiện 1–2 lần ở viền (dấu hiệu anti-alias).
3. `gallery.html`: mở bằng Chromium, chụp ở 1440 px, xem từng loại; mọi animation phải chạy và lặp đúng.
4. `shortlist.md`: ≤ 60 asset, mỗi cái một dòng: id, ảnh, điểm, **chỗ dùng cụ thể** trên wiki. Gợi ý chỗ: particle theo Act (`PENV`/`BENV` trong `envFx`), khối đấu trường cho từng Keeper (`BTEX`), đồ vật và glow của phòng (`--o1..3`, `--g1..3`, `--pt`), particle tooltip theo rarity, vệt chém theo loại vũ khí (thay cho một `sweep` chung), particle "crit/hit" cho hàng S của Equipment, emblem Keeper, icon hiệu ứng cho dòng stat.

### Pha F: Báo cáo và bàn giao

- Commit lên `workspace` (không phải `main`): `assets/` như mục 5.1. Thông điệp commit rõ, mỗi pha một commit.
- Thêm một mục ngắn vào `NOTES.md` trên `workspace` theo mẫu các mục v37–v39 (Asked / Sources / Used / Not used / Size / Open).
- Báo cáo tiếng Việt cho chủ dự án: giả định sai của người yêu cầu (nếu có); số asset theo tầng và loại; top shortlist (ảnh); nguồn bị loại và lý do; thư xin phép đã soạn; những gì chưa làm được và vì sao.
- **Không** sửa `main`, `build/`, `scenes.py`, CSS của site trong phiên này. Đưa asset vào site là việc của phiên sau, sau khi chủ dự án chọn từ shortlist, và mọi thay đổi giao diện tổng thể vẫn cần duyệt (`CLAUDE.md`).

## 7. Ràng buộc

- **An toàn**: archive, jar, repo tải về là dữ liệu không tin cậy. Mỗi nguồn giải nén vào một thư mục scratch riêng, rỗng; script của bạn nằm ở chỗ khác; chạy Python với `-I`; không chạy Gradle, build script, hay code nào của mod/pack/repo bên thứ ba.
- **Phiên cloud là tạm thời**: chỉ những gì đã push còn lại. Tầng B sống bằng toạ độ trong catalog, không bằng file.
- **Không bịa**: không bịa licence, tác giả, commit, số frame. Chỗ nào không đọc được thì ghi `unknown` và xếp tầng B.
- **Không** dùng asset đứng tên hay mang thương hiệu của người/tổ chức khác ngoài phạm vi licence; không dùng asset của game khác (Terraria, Hollow Knight, …) dù một mod đã chuyển thể chúng.
- Chữ trong `assets/` và trên wiki bằng tiếng Anh; báo cáo cho chủ dự án bằng tiếng Việt.
