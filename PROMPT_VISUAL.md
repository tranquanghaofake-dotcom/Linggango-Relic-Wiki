# Prompt: Visual pass cho Linggango Relic Wiki (taste-skill + ui-ux-pro-max)

> Prompt này giao cho một AI agent có quyền đọc/ghi repo, chạy Python/Node 22, Chromium (playwright) và mạng tới GitHub.
> Chỗ `[ … ]` là chỗ thay khi tái sử dụng. Đọc hết trước khi làm; mục 3 và mục 6 là phần dễ làm sai nhất.

---

## 1. Vai trò

Bạn là **product designer kiêm front-end engineer** cho một wiki game tĩnh (HTML/CSS/JS thuần, không framework). Bạn làm việc như người **phục chế**, không như người **thiết kế lại**: bản sắc Minecraft GUI của wiki là quyết định của chủ dự án, không phải "lỗi thẩm mỹ" cần sửa. Việc của bạn là làm cho bản sắc đó **rõ hơn, đọc nhanh hơn, ít lỗi hơn**, dùng hai skill làm **công cụ đo và quy trình**, không làm nguồn phong cách.

## 2. Ngữ cảnh

**Repo:** `tranquanghaofake-dotcom/Linggango-Relic-Wiki`. Đọc trước, theo thứ tự: `CLAUDE.md`, `build/README.md`, `build/ARCHITECTURE.md`, rồi `NOTES.md` trên nhánh `workspace` (ít nhất v26 → v33).

- Site tĩnh: `build/build.py` dựng `index.html` + `static/*.js|css` (hash) + `dist/Linggango_Relic_Wiki.html` (offline, một file).
- **Chỉ sửa nguồn:** `build/src/v5.css`, `build/style.game.css`, `build/src/app.js`, `build/src/gear.js`, `build/src/ux.js`, `build/src/template.html`, `build/src/scenes.js`. Không bao giờ sửa tay `index.html`, `static/`, `dist/`.
- Route: `#` (hub), `#home` (The Path), `#act/N`, `#iN` (curio), `#gear`, `#gN` / `#gsN` (gear, set), `#build`, `#bosses`, `#boss/K`, `#side/K`, `#mechanics`, `#mods`, `#slot/X`.
- Kiểm tra: `bash build/check.sh` (`NODE_PATH=$(npm root -g)`), phải xanh trước mọi push.

**Lịch sử thiết kế (bắt buộc tôn trọng):**
- **v30:** một lượt "calmer UI" xoá bevel, shadow, glow và animation lặp → **v31 bị revert theo yêu cầu chủ dự án** ("trông trơn, không phải sạch", mất cảm giác Minecraft). `CLAUDE.md`: *không được làm phẳng; mọi thay đổi về tổng thể giao diện cần chủ dự án duyệt trước.*
- **v32:** hướng đã chốt: ba ngôn ngữ thị giác theo chức năng, không trộn trong một khối:
  - *quest book* cho tiến trình (bản đồ The Path, Bosses, trang boss): khung lục giác, đường nối trắng/xám, tick xanh, Act hiện tại màu xanh dương, tint theo Act;
  - *inventory* cho đồ vật (curio, Equipment, Builder, Mechanics): ô slot lõm, tooltip vanilla;
  - *ornate metal/gold* chỉ cho rarity: Epic sắt, Legendary bạc + crest, Mythic vàng + crest đá, Must-Have vàng + crest sao.
- The Path chỉ mở một Act (Act "I'm here", nếu không thì Act 0–I); Act đóng chỉ dựng tile khi mở. Không dựng thứ người đọc chưa thấy.
- Ưu tiên desktop/laptop; phone phải dùng được, không cần đẹp ngang desktop.
- Chữ trên wiki là tiếng Anh. Báo cáo cho chủ dự án bằng tiếng Việt.

## 3. Hai skill: lấy gì, bỏ gì

Cài vào thư mục skill của agent (không commit vào `main`; nếu muốn lưu thì đưa vào `.claude/skills/` trên nhánh `workspace` và ghi vào `skills-lock.json`, như 9 skill Vercel đã có):

| Skill | Nguồn | Ghi chú |
|---|---|---|
| **taste-skill** (`design-taste-frontend` v2) | `github.com/Leonxlnx/taste-skill`, thư mục `skills/taste-skill/` | Cần Node 22+ và Chromium. Script: `draw.mjs`, `inspect.mjs`, `lint.mjs`. |
| **ui-ux-pro-max** | `github.com/nextlevelbuilder/ui-ux-pro-max-skill`, thư mục `.claude/skills/ui-ux-pro-max/` | Python 3, không phụ thuộc. Script: `scripts/search.py`. |

Chạy script của skill có thể cần quyền chạy code ngoài; nếu bị chặn, đọc thẳng `references/*.md` và `data/*.csv` thay vì chạy, và ghi rõ trong báo cáo là công cụ không chạy được.

### 3.1 Xung đột phải biết trước

Cả hai skill, nếu áp nguyên văn, sẽ **lặp lại đúng lượt v30 đã bị revert**:

- taste-skill house rules cấm: gradient, shadow trên vật đứng yên, glow, viền 1px / hairline, nhãn chữ hoa nhỏ giãn cách, đánh số thứ tự, hàng card giống nhau, icon trong ô vuông.
- ui-ux-pro-max (`products.csv`, dòng *Wiki / Encyclopedia*) khuyên **Minimalism & Swiss + Flat Design**.

Trong khi đó, bevel, shadow, gradient thanh máu boss, ô slot lõm, hàng tile item, khung rarity là **chính bản sắc** của wiki.

**Quy tắc giải xung đột:** `CLAUDE.md` và mục 2 thắng mọi luật của skill. taste-skill có sẵn lối cho đúng trường hợp này (mục *Special cases → An existing brand or design system*): giữ tài sản thương hiệu, nói rõ trong báo cáo, và cho phép đúng các luật đó trong inspector. Không được dùng lối này để bỏ qua các luật khác.

### 3.2 Lấy gì từ taste-skill

- **Phân loại trang:** chỉ hub `#` là *page* (đi theo "the run"). Mọi trang còn lại (The Path, Equipment, Builder, Bosses, curio, gear, Mechanics) là **app screen**: đọc trọn `references/app-screens.md` và dùng `--app` cho `draw.mjs`, `lint.mjs`, `inspect.mjs`.
- **Không deal hướng mới.** Nếu chạy `draw.mjs`, luôn `--keep palette,type`, chỉ để tham khảo bố cục; không áp palette/typeface được deal.
- **Inventory → câu ý tưởng:** viết inventory 8–12 thứ chỉ Linggango có (Keepers, Acts, Seven Curses, relic levels, boss souls, Hardmode ×2.1, Terraria-inspired…), rồi câu: *"On this screen, [thứ của Linggango] becomes [device]."* Áp competitor test: thay tên bằng một wiki modpack khác mà câu vẫn đúng → ý tưởng chưa đủ.
- **"Câu hỏi duy nhất" của mỗi screen** (`app-screens.md` §2.2): viết một dòng cho từng route chính, ví dụ The Path: *"What can I get at the Act I'm in, and what is worth getting first?"*. Khối lớn nhất trên screen phải trả lời câu đó.
- **Inspector làm thước đo:** `inspect.mjs <file> --app --widths 1440,1024,390 --out .taste-skill/before|after` (bỏ `--app` cho hub). Danh sách `--allow` được phép, **chỉ** những luật thuộc bản sắc:
  `gradient,shadow,heavy-shadow,text-shadow,heavy-borders,outlined-box,palette-purple,icon-tiles,card-rows`
  (icon-tiles/card-rows: lưới ô item là inventory của game). Mọi FAIL khác (contrast, overflow, side-scroll, covered-text, clipped-text, small-text, late-title, tabular, measure, untitled-section…) phải sửa, hoặc giải thích từng cái trong một câu.
- **Critique** theo `references/critique.md`: 14 lượt nhìn, điểm Awwwards (design 40 / usability 30 / creativity 20 / content 10), caps, format `ROUND n`. Bỏ qua cap liên quan tới gradient/shadow/hairline (đã được allow); giữ mọi cap khác. Tối đa 3 vòng.
- **Motion** (`references/motion.md`): chỉ `transform`/`opacity`, ease-out mạnh, hover 200–300 ms, reveal 600–1000 ms, có fallback `prefers-reduced-motion`; tiêu đề trang đọc được trong 1,2 s.

### 3.3 Lấy gì từ ui-ux-pro-max

- **Bảng ưu tiên 1→10** làm thứ tự audit: Accessibility → Touch & Interaction → Performance → Style consistency → Layout & Responsive → Typography & Color → Animation → Forms & Feedback → Navigation → Charts.
- Style tham chiếu gần nhất là **Pixel Art** (`styles.csv` #52) và **Skeuomorphism** (#13), không phải Swiss/Flat. Dùng để kiểm tra nhất quán, không để đổi phong cách.
- Truy vấn `--domain ux` theo từng kết quả quan sát được, một ý mỗi truy vấn, ví dụ: `"focus not obscured"`, `"badge chip label wraps"`, `"orphan heading line balance"`, `"live badge count screen reader"`, `"horizontal scroll nav affordance"`. Stack: `html-tailwind` là gần nhất nhưng site **không** dùng Tailwind; chỉ lấy ý, không lấy cú pháp.
- **Không** chạy `--design-system --persist` (sẽ sinh `MASTER.md` mâu thuẫn với hướng v32). Nếu cần token, viết vào `build/ARCHITECTURE.md` hoặc ghi chú trên `workspace`.

## 4. Quy trình

### Pha A: Ghi nhận hiện trạng (không sửa gì)
1. Build, chạy `check.sh`.
2. Chụp màn hình mọi route ở mục 2 ở 1440, 1024, 390; chạy `inspect.mjs` vào `.taste-skill/before`; `lint.mjs --app build/src`.
3. Kiểm chứng từng mục ở **mục 5** (đúng / sai / không tái hiện được), kèm ảnh.

### Pha B: Review và đề xuất, rồi **DỪNG chờ duyệt**
Xuất một báo cáo tiếng Việt gồm:
- inventory, câu ý tưởng, "câu hỏi duy nhất" của từng screen;
- critique ROUND 0 cho hub, The Path, curio, Equipment, Bosses, Builder;
- danh sách đề xuất chia 3 nhóm:
  - **(1) Sửa lỗi**: không đổi giao diện tổng thể (va chạm chữ, overflow, contrast, nội dung cũ, tiêu đề hiện chậm, focus). Được làm ngay sau khi chủ dự án đồng ý danh sách.
  - **(2) Tinh chỉnh trong bản sắc**: phân cấp, khoảng cách, mật độ, cỡ chữ, trạng thái hover/focus/empty, nhất quán ba ngôn ngữ v32. Mỗi mục kèm ảnh trước/sau (mock bằng CSS trong một nhánh nháp hoặc ảnh chú thích).
  - **(3) Thay đổi tổng thể**: bất cứ thứ gì đụng tới bevel, shadow, palette, typeface, animation chính, bố cục khung trang. Chỉ đề xuất, không làm, trừ khi được duyệt từng mục.
- 3 thay đổi có tác động lớn nhất (theo `critique.md` §5: ý tưởng → phân cấp → bố cục → chữ → hình → màu → chi tiết → motion).

**Không code nhóm (2) và (3) trước khi chủ dự án trả lời.**

### Pha C: Thực hiện phần được duyệt
- Thứ tự: nhóm (1) → (2) → (3) đã duyệt. Mỗi nhóm là một commit riêng, mô tả rõ.
- Sau mỗi nhóm: build, `check.sh`, `inspect.mjs` vào `.taste-skill/after`, mở **mọi** ảnh chụp (không chỉ màn đầu), critique ROUND n.
- Tôn trọng "không dựng thứ người đọc chưa thấy": không thêm DOM/ảnh cho Act đang đóng, không tăng số tile dựng ở lần xem đầu (hiện ~615).

### Pha D: Báo cáo cuối
Tiếng Việt, ngắn: giả định sai của người yêu cầu (nếu có); bảng đo trước/sau từ inspector; điểm critique các vòng; các luật đã `--allow` và lý do từng luật; những gì không làm được và vì sao; ảnh trước/sau của 6 screen chính.

## 5. Vấn đề đã quan sát (2026-10-27, bản `main` hiện tại; kiểm chứng lại, đừng tin mù quáng)

| # | Screen | Quan sát | Nhóm |
|---|---|---|---|
| 1 | Hub `#` | Góc hero ghi **"Linggango V6.6.5b4"** trong khi footer và dữ liệu đã là 6.6.6hf. Chuỗi cứng ở `build/src/app.js:625`. | 1 |
| 2 | Bosses | Số thứ tự ở góc card **đè lên tên boss** dài ("Eldorath the Ancient**4**", "Newborn **of13**", "Fallen **10**"). | 1 |
| 3 | Curio `#iN` | 2,5 s sau khi điều hướng, `h1` và ảnh lớn **vẫn chưa hiện** (khoảng trống phía trên); vượt ngưỡng 1,2 s. | 1 |
| 4 | Curio `#iN` | Một thẻ thông tin có ba khái niệm rarity cạnh nhau: *In-game rarity: Rare*, *Wiki tier: Must-Have ★ · base Epic*. Người đọc không biết tin cái nào. | 2 |
| 5 | Equipment | Gần như **mọi** item ở Act 0–I mang nhãn **NEW**; nhãn mất nghĩa. Hàng tier S/A/B chỉ có 1–2 item, phần lớn chiều ngang trống. | 2 |
| 6 | The Path | Màn đầu bị chiếm bởi 5 chip chú giải, khối filter và sidebar trước khi thấy curio; cột thông tin Act bên trái hẹp, chữ nhỏ. | 2 |
| 7 | Curio / The Path | Sidebar filter (Role, Rarity, Mechanic…) vẫn chiếm ~300 px ở trang chi tiết một curio, nơi nó không có tác dụng trực tiếp. | 2/3 |
| 8 | Phone 390 | Nav trên cùng bị cắt ("Mechanics") mà không có dấu hiệu cuộn ngang; ở `#home` có một thanh rỗng ngay dưới nav. | 1 |
| 9 | Hub `#` | Năm nút lớn trong hero lặp lại đúng năm mục của nav trên cùng. | 2 |
| 10 | Toàn site | Nhãn mục chữ hoa nhỏ ("ROLE", "RARITY", "WHERE IT DROPS") dùng pixel face; kiểm tra contrast và cỡ chữ theo ui-ux-pro-max §1, §6. Giữ phong cách, chỉ sửa nếu không đạt. | 1/2 |

## 6. Ràng buộc

- **Không làm phẳng.** Không xoá bevel, shadow, glow, gradient, animation hiện có, trừ khi chủ dự án duyệt từng mục. Một lượt "minimal" sẽ bị revert như v30.
- **Không trộn ngôn ngữ thị giác** v32 trong một khối (quest book / inventory / ornate rarity).
- **Không đổi số liệu**, không đổi nội dung game. Sửa chữ chỉ khi là lỗi (ví dụ phiên bản cũ) và nói rõ.
- **Không phá:** route, hash, `localStorage` (`lgw-here`, `lgw2`…), search, filter, view transition, Previous/Next, `check.sh` invariants.
- **Tài sản:** chỉ dùng thứ đã có trong repo hoặc texture vanilla 1.20.1 qua pipeline hiện có (`build/pack_audit/scenes.py`). Không nhúng tài sản "All Rights Reserved" của resource pack trong pack. Không dùng ảnh từ open collections của taste-skill (không hợp chủ đề).
- **Accessibility:** contrast chữ ≥ 4.5:1 (chữ lớn ≥ 3:1), focus ring thấy được, điều khiển dùng được bằng bàn phím, `prefers-reduced-motion` tắt mọi chuyển động trang trí.
- **Hiệu năng:** animation chỉ `transform`/`opacity`; không thêm thư viện (không GSAP, không font mới) nếu chưa được duyệt; kích thước `static/*.css|js` không tăng quá ~5%.
- **Git:** theo `CLAUDE.md` (hoặc nhánh được chỉ định trong phiên). Commit `index.html`, `static/`, `dist/` cùng lúc (`git add -A static`). Ghi một mục ngắn vào `NOTES.md` trên `workspace`.

## 7. Tiêu chí nghiệm thu

- `check.sh` xanh; 0 lỗi console trên mọi route ở mục 2.
- `inspect.mjs` (với đúng danh sách `--allow` ở 3.2): **0 FAIL** ở 1440 và 1024; ở 390 không còn `overflow`, `side-scroll`, `covered-text`, `clipped-text`.
- Mười mục ở mục 5: mỗi mục có kết luận (đã sửa / đề xuất chờ duyệt / không tái hiện) kèm ảnh.
- Tiêu đề mọi trang đọc được trong 1,2 s; không còn chữ đè chữ ở bất kỳ độ rộng nào.
- Đặt ảnh trước/sau cạnh nhau: vẫn nhận ra ngay là Minecraft GUI (bevel, ô slot, tooltip vanilla, khung rarity còn nguyên).
- Điểm critique vòng cuối được ghi lại; nếu dưới 7.5, nói thẳng và liệt kê vấn đề còn lại.
