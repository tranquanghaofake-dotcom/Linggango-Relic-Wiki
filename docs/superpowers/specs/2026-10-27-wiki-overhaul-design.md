# Design: đại cải tạo Linggango Relic Wiki (hướng D)

> Viết theo `superpowers:brainstorming`. Trạng thái: **chờ chủ dự án duyệt**. Sau khi duyệt, tài liệu này là đầu vào cho `superpowers:writing-plans`.
> Hình minh hoạ, prototype và số đo nằm trong `2026-10-27-wiki-overhaul/` (cùng thư mục).

## 1. Mục tiêu

Làm lại **toàn bộ lớp trình bày, bố cục và UX** của wiki để:
- đồng nhất phong cách "pixel Minecraft mod": một lưới pixel, một bộ màu, hai font, cùng một bộ component cho mọi trang;
- bố cục đúng chuẩn wiki game (Minecraft Wiki, Terraria và Calamity trên wiki.gg): tiêu đề, lead, mục lục, infobox, các mục theo thứ tự cố định, navbox;
- UI/UX hợp lý: một ô tìm kiếm, bộ lọc ở đúng chỗ, không còn khoảng trống, chữ bị cắt hay lỗi logic.

**Không đổi:** dữ liệu, số liệu, cách xếp hạng (`gear.js`), route và hash, `localStorage` (`lgw-here`, `lgw2`…), các bất biến trong `check.js`, chữ trên wiki bằng tiếng Anh. Không làm phẳng giao diện: bevel, bóng, hiệu ứng và chuyển động vẫn là bản sắc (bài học v30–v31).

## 2. Hiện trạng đo được (`audit/before.json`, Chromium 1440 px)

| Vấn đề | Số đo |
|---|---|
| Pixel art phóng **không nguyên lần** | có trên mọi trang: ×1.5, ×1.86, ×1.8, ×3.5, ×1.13, ×2.25, ×0.56, ×1.25, ×1.38, ×0.34, ×0.69; nền co giãn `cover`/`contain`/`%`: 24–140 chỗ mỗi trang |
| Màu | 22–50 màu khác nhau mỗi trang, tới 46 cặp gần trùng (lệch dưới 12/255); 567 mã màu viết tay trong CSS |
| Chữ | 3 font được tải (Pixelify Sans, Silkscreen, Be Vietnam Pro); 11–16 tổ hợp font và cỡ mỗi trang; **Pixelify Sans vẽ 2 thành 8** (prototype: "0123" → "0183"), trước đó 5 giống 8 (v13) |
| Kích thước slot | slot 54/40/64 px, icon bên trong 32/24/40 px: 24 và 40 là ×1.5 và ×2.5 |
| CSS | `v5.css` + `style.game.css` = 2.780 dòng, khoảng 25 lớp lịch sử (v3 → v39) đè lên nhau, nhiều `!important` |
| Lỗi thấy ngay | trang curio (`#i76`) **không hiện tiêu đề** (khoảng trống phía trên lead); `#mods` hiển thị y hệt `#home`; hub có hai ô tìm kiếm; bộ lọc 300 px vẫn chiếm chỗ ở trang có ít tác dụng; tier S/A/B xếp ngang so le |

Ảnh trước: `before_*.png`.

## 3. Quyết định thiết kế

### 3.1 Lưới pixel
- **1 texel = 2 px CSS** (`--t: 2px`). Mọi texture 16 px hiện ở 32 px; particle 8 px ở 16 px; khung, bevel, viền đều là bội số của 2 px.
- **Một component, một cỡ texel.** Ngoại lệ duy nhất là ảnh trưng bày trong infobox: ×6 (vật phẩm 96 px trong khung vàng hoặc bạc 144 × 168 px, khung cũng ×6, nên vẫn là một texel trong component đó).
- Icon chen giữa dòng chữ: ×1 (16 px), chỉ khi nằm trong câu.
- Không bao giờ dùng `cover`/`contain`/`%` cho pixel art; texture lặp có kích thước `n × 32px`.
- Khoảng cách: bội số 8 px.

### 3.2 Màu (token, cấm màu viết tay)
- **Trung tính** `n0…n9` (đen tím → kem), lấy từ thang GUI tối hiện có.
- **Rarity** theo màu định dạng của game: Common `#ffffff`, Uncommon `#ffff55`, Rare `#55ffff`, Epic `#ff55ff`, Legendary `#ffaa00`, Mythic `#ff5555`; Must-Have giữ vàng `#ffd21f`.
- **Chức năng:** xp `#55ff55`, liên kết `#ffff55`, boss `#ec3fd0`, cảnh báo `#ff5555`.
- **Màu nhấn theo Act:** 13 màu, lấy từ khối hoặc biểu tượng của Act, khai báo một lần.
- `check.sh` sẽ thất bại nếu CSS có màu nằm ngoài bộ token.

### 3.3 Chữ
- **Display:** Monocraft (SIL OFL 1.1, tự host), chỉ ở 16 / 24 / 32 px. Dùng cho tiêu đề, nút, nhãn, breadcrumb và mục lục.
- **Thân bài:** Be Vietnam Pro 16 px (14 px cho chú thích, 18 px cho lead). Số liệu dùng font thân bài.
- Bỏ Pixelify Sans và Silkscreen. Mỗi trang tối đa 2 font và 6 cỡ chữ.

### 3.4 Component (một bộ cho toàn site, đặc tả ở ×2)
Panel (bevel), slot (40 px, icon 32), nút đá (vanilla `widgets.png`, 9-slice, `repeat` ở ×2), tab, chip, ô nhập liệu, tooltip vanilla, infobox, navbox, bảng, hàng tier, thanh boss, nút quest (lục giác), thẻ boss, ảnh trưng bày. Mỗi component có trạng thái hover, focus, active, disabled, empty.

### 3.5 Khung trang và kiến trúc thông tin
- **Thanh trên** (64 px, dính trên cùng): logo, 5 mục nav (The Path, Equipment, Bosses, Build planner, Mechanics), **một** ô tìm kiếm (phím `/`).
- **Trang chi tiết** (curio, gear, set, Keeper, side boss): breadcrumb → hàng tiêu đề (slot + h1 màu rarity) → lead → chip. Ba cột:
  - mục lục dính bên trái, 200 px, sáng mục đang đọc khi cuộn;
  - bài viết ở giữa, các mục là panel;
  - infobox dính bên phải, 320 px.
  - Dưới 1180 px: mục lục ẩn, infobox chuyển lên sau lead (như hiện nay).
- **Trang danh sách** (The Path, Equipment, Bosses, Mods, Slot):
  - thanh bộ lọc nằm **trên** kết quả, gập được, thay cho cột bên 300 px;
  - kết quả là lưới slot hoặc thẻ;
  - The Path: dải Act (kiểu quest book) ở trên, panel của Act đang chọn ở dưới;
  - Equipment: các hàng S / A / B / C xếp chồng toàn chiều ngang.
- **Hub:** "màn hình tiêu đề" (panorama của pack trong khung GUI; đây là ảnh duy nhất không phải pixel art, như panorama của game), ba hành động chính (Tiếp tục Act N, The Path, Equipment), bản đồ The Path thu gọn, mục mới trong 6.6.6.
- **Room** (cảnh tường, đồ vật, khung vật phẩm) giữ làm đầu mục của các trang danh sách, vẽ lại đúng ×2.
- Tham khảo mẫu bố cục: Minecraft Wiki và wiki.gg (thứ tự mục, infobox, navbox); `jekyll-theme-chirpy` chỉ lấy mẫu khung ba cột và mục lục dính có sáng mục đang đọc, không lấy mã hay phong cách.

### 3.6 Hiệu ứng
- Giữ: glint trên item Mythic và Must-Have, vệt chém khi rê chuột, không khí theo Act, chuyển trang. Tất cả tắt khi người dùng chọn giảm chuyển động.
- Thay hoặc thêm từ `assets/shortlist.md` (giai đoạn 5):
  - lửa Goety cho Act Nether;
  - lửa linh hồn cho soul sand;
  - lửa End;
  - lấp lánh cho rarity;
  - vệt chém theo loại sát thương (fxgen);
  - sóng xung kích trên thẻ Keeper;
  - crit trên hàng S.
- Chỉ dùng asset tầng A, A-SA, A-perm hoặc tự tạo. Tầng B chỉ dùng sau khi giấy phép của tác giả được ghi vào `assets/permissions/`.

### 3.7 Mã nguồn
- Thay `src/v5.css` và `style.game.css` bằng `build/css/` theo lớp: `tokens.css`, `base.css`, `components.css`, `pages/*.css`. `build.py` ghép chúng thành một file như hiện nay.
- Đánh dấu HTML trong `app.js`, `gear.js`, `ux.js` được sửa theo component mới (`article()`, `room()`, thẻ, hàng tier, bộ lọc).
- CSS cũ chỉ bị xoá sau khi trang tương ứng đạt tiêu chí.
- `audit.js` (đo tỉ lệ pixel, màu, font) chuyển vào `build/` và thành một bước của `check.sh`.

## 4. Lỗi logic và UX phải sửa (danh sách đầy đủ lập ở bước đầu của plan)
Tiêu đề trang curio không hiện; `#mods`; hai ô tìm kiếm ở hub; bộ lọc ở trang chi tiết; tier xếp ngang so le; nhãn NEW vẫn có trên 67/105 item ở Act II (v34); nhãn bản đồ The Path 11 px ở ≤1024 px (v34); CSS chết của header gear cũ (`.gph`, `.gcols`, `.gpage`, `.sbhero`); những "Known weak spots" trong `build/README.md`.

## 5. Tiêu chí nghiệm thu (đo được)
- `audit.js` trên mọi route chính và một mẫu trang chi tiết:
  - 0 tỉ lệ pixel không nguyên;
  - tỉ lệ chỉ thuộc {1 (trong dòng chữ), 2, 6 (ảnh trưng bày)};
  - 0 màu ngoài token;
  - tối đa 2 font và 6 cỡ chữ.
- `check.sh` xanh: 3.878 trang chi tiết, không lỗi script, các bất biến giữ nguyên.
- Ảnh trước và sau ở 1440 / 1024 / 390 px.
- Chấm điểm critique của taste-skill không thấp hơn lần trước. Nếu script của taste-skill bị chặn, đọc tài liệu tham khảo của nó và dùng `audit.js`.
- Bundle không tăng quá 10%; tiêu đề hiện trong 1,2 s; vẫn không dựng những gì người đọc chưa thấy (Act đóng).

## 6. Giai đoạn
Làm trên nhánh `claude/determined-dirac-u2c3ca`. Mỗi giai đoạn: một hoặc vài commit, ảnh trước và sau, số đo. Chủ dự án duyệt rồi mới merge vào `main`.

1. Token, font, khung trang (thanh trên, breadcrumb, nền) + `audit.js` vào `check.sh`.
2. Mẫu trang chi tiết (`article()`, infobox ×6, mục lục dính) cho cả 5 loại trang.
3. Trang danh sách và công cụ: The Path, Equipment, Bosses, Build planner, Mechanics, Mods/Slot.
4. Hub.
5. Hiệu ứng từ shortlist.
6. Dọn dẹp: xoá CSS cũ, cập nhật README và ARCHITECTURE, ghi NOTES.

## 7. Rủi ro
- Lặp lại v30 ("trơn, không sạch"): đã chặn bằng mục 1 và bằng ảnh duyệt ở từng giai đoạn.
- Lỗi ở trang ít người xem trong 3.878 trang chi tiết: `check.js` render toàn bộ, `audit.js` lấy mẫu.
- Monocraft là font đơn cách (monospace): tiêu đề dài sẽ rộng hơn; giới hạn 32 px và cho phép xuống dòng.

## 8. Cần chủ dự án quyết
1. Duyệt hướng này cùng prototype (`proto_top.png`, `proto_spec.png`, `proto.html`).
2. Font display: **Monocraft** (đề xuất) hay Silkscreen?
3. Ảnh trưng bày trong infobox ở ×6 (vật phẩm 96 px) có ổn không, hay ×8 (128 px)?

## 9. Bổ sung sau phản hồi "chưa thấy là wiki Minecraft, nhất là Linggango" (prototype v2)

Prototype đầu đúng lưới nhưng trượt **phép thử đối thủ** của taste-skill: thay "Linggango" bằng tên modpack khác mà trang vẫn đúng. Bản sửa làm theo quy trình của skill. Script của skill bị bộ phân loại tự động chặn, nên phần dưới chỉ áp dụng phương pháp từ `SKILL.md` và `references/app-screens.md`.

**Kiểm kê (chỉ Linggango có):**
- logo cam kiểu pixel và splash text ("The Keepers are watching.", "Red means don't parry.", "Hardmode starts after the Dragon.", "Treasure bags for everyone!");
- menu chính kiểu Terraria do Misanthropy làm bằng FancyMenu: chữ `#E6E6E6`, rê chuột chuyển `#FFE14A`, không có khung nút;
- các Keeper khoá từng Act;
- The Path từ Act 0–I tới XII, có Dragon;
- Hardmode ×2.1 sau Dragon;
- treasure bag, reforge, parry;
- Boss Soul;
- khung kim loại của Linggango Textures, nền quest book FTB;
- tooltip curio có màu rarity;
- khẩu hiệu "Terraria-inspired, Minecraft-powered".

**Câu ý tưởng:** *Trên wiki này, hành trình qua các Keeper của bạn trở thành khung của mọi trang.* Câu này qua phép thử đối thủ: modpack khác không có Keeper khoá từng Act.

**Thứ sống:** chọn "I'm here" (đã có sẵn, `lgw-here`). Thanh "Your run" dưới header đánh dấu Act đã qua, Act hiện tại và Act của trang đang xem. Mỗi trang ghi rõ còn cách bạn bao nhiêu Keeper, bằng thanh boss.

**Thay đổi so với mục 3:**
- **Header:** logo thật của pack + splash text nhún nhảy như màn hình tiêu đề Minecraft + menu chữ kiểu Terraria. Nút đá chỉ dùng trong nội dung.
- **Nền:** quest book FTB của pack, thay cho nền tối trơn.
- **Panel:** khung kim loại của Linggango Textures (9-slice ×2), lòng tối.
- **Công thức:** cửa sổ container vanilla xám sáng `#C6C6C6` với slot `#8B8B8B`, đúng như trong game.
- **Infobox = tooltip của chính vật phẩm:** nền `#100010`, viền tím `#5000FF`→`#28007F`, tên màu rarity, dòng chỉ số xanh `#5555FF`, dòng mô tả xám. Ảnh trưng bày ×6 trong khung vàng hoặc bạc.
- **Từ ngữ của trò chơi:** Keeper-gated, Hardmode, Treasure Bag, Boss Soul, Act.

Ảnh: `2026-10-27-wiki-overhaul/proto2_top.png`. Trang: `proto2.html`.
Lỗi mới: trang Keeper cũng mất tiêu đề (`before_keeper.png`). `h1` có trong DOM nhưng không hiện, nên đây là lỗi chung của `article()`.

## 10. Phản hồi về v2: "trông như một bãi rác, quá loạn, tham khảo wiki cũ" → hướng R: phục chế từ wiki hiện tại

- v1 (`proto.html`) và v2 (`proto2.html`) **bị loại**. v2 nhồi quá nhiều thứ đặc trưng vào một màn hình: tím của tooltip, hồng của thanh boss, xám của container, vàng của menu, vân quest book. Đúng kiểu lỗi taste-skill gọi là "a style's move was over-applied".
- **Đính chính hai "lỗi" ở mục 2 và 4:**
  - Tiêu đề trang chi tiết **không mất**: nó hiện sau khoảng 0,65–0,72 s (đo ở `#i76` và `#boss/arion`). Ảnh chụp ở mốc 2 s thấy trống là do cách chụp, như v34 đã ghi.
  - `#mods` → `#home` là **cố ý**: trang Mods đã bị bỏ (`build/README.md`, Known weak spots).
- **Hướng R:** giữ nguyên giao diện hiện tại (room, skin GUI, khung ornate, Pixelify Sans, bố cục `article()`), chỉ sửa chỗ lệch, mỗi chỗ đo được:
  1. **Pixel:** khoảng 15 selector đang ở tỉ lệ lẻ đưa về tỉ lệ nguyên. Danh sách từ `restore/scales.js`:
     - `.gtl img` ×3.5 → ×3;
     - `.rfr img` ×1.86 → ×2;
     - `.emb.sm` ×1.8 → ×2;
     - `.emb.xs` ×1.13 → ×1;
     - `.gc .pic` ×2.25 → ×2;
     - `.slot.sm` ×1.5 → ×2;
     - `.bsum` ×1.25 → ×1;
     - `.nic` ×1.38 → ×1;
     - `.slot.big` (Mechanics) ×2.5 → ×3;
     - `.coin` → 32 px.
     Demo: `restore/restore.css`, ảnh phóng to `restore/zoom_gear.png`.
  2. **Màu:** gộp 567 mã màu thành bộ token **lấy từ chính bảng màu hiện tại**; các sắc gần trùng (lệch dưới 12/255) gộp về một. Mắt thường không thấy đổi.
  3. **CSS:** gộp 25 lớp v3–v39 thành một bộ file có thứ tự. Kiểm bằng so ảnh từng pixel trước và sau trên mọi route chính: chỉ những chỗ cố ý sửa được khác.
  4. **Số:** dùng font thân bài ở mọi nơi (Pixelify vẽ 2 thành 8).
  5. **Hiệu ứng từ kho:** chỉ thay đúng chỗ, mỗi chỗ một lần duyệt.
- Tiêu chí: `audit.js` không còn tỉ lệ lẻ; số màu khác nhau giảm, không còn cặp gần trùng; `check.sh` xanh; ảnh trước/sau.
