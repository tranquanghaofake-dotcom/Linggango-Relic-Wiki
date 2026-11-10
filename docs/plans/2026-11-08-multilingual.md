# 2026-11-08: Đa ngôn ngữ cho toàn bộ wiki (Tiếng Việt, Русский, Português, Español)

Spec và plan trong một file (CLAUDE.md, Process: việc kiến trúc). **Trạng thái: chủ dự án đã duyệt ("làm", 2026-11-08; D1–D4 dùng mặc định). Phase 0 đã đo xong, kết quả ở mục 13; các chỗ bị số đo làm sai đã sửa tại chỗ và ghi "(đã đo)".**
Lập từ main `b0c2c0e`; mọi con số đo trên bản build của commit đó (`apply_all.sh` chạy sạch, `git status` không đổi).
Chữ của wiki vẫn là tiếng Anh gốc (nguồn sự thật). File này viết bằng tiếng Việt vì người duyệt là chủ dự án.

## 1. Người đọc sẽ thấy gì (value first)
Một menu ngôn ngữ ở đầu trang. Chọn xong, giao diện, trang vật phẩm / boss / trang bị và sách hướng dẫn đổi sang ngôn ngữ đó;
tên vật phẩm khớp với tên người chơi thấy trong game; link chia sẻ cũ (`#i5`, `#build/…`) vẫn mở đúng. Người đọc tiếng Anh
không thấy gì đổi và không tải thêm gói dịch nào.

## 2. Hiểu của tôi về yêu cầu (sửa nếu sai)
- Phạm vi: **toàn bộ** wiki: giao diện, trang chi tiết, dữ liệu hiển thị, trang Mechanics, file offline.
- Bốn ngôn ngữ: vi, ru, pt, es. Tiếng Anh vẫn là bản gốc; không ngôn ngữ nào thay thế nó.
- "Đúng, chuẩn": số liệu không đổi; thuật ngữ trùng với game. "Hay, hợp ngữ cảnh": đọc như người chơi viết, không như máy dịch.
- "Đỡ token": dùng cái đã có (bản dịch chính thức của game, mẫu câu lặp, bộ nhớ dịch) trước khi gọi AI.
- Không đổi look Minecraft (CLAUDE.md, Design). Chỗ nào buộc phải đổi (font, mục 3.3) thì chờ bạn duyệt ảnh.

## 3. Đã đo trong repo (và những giả định cần sửa)
| # | Phát hiện | Hệ quả |
|---|---|---|
| 3.1 | **Không có cơ chế i18n nào.** Chữ giao diện nằm lẫn trong template literal của `app.js`: ≈535 text node, ≈235 chuỗi trong JS, 77 template có văn xuôi (≈110–140k ký tự; hai cách đếm chồng nhau), thêm `gear.js` (35 chuỗi), `ux.js` (6) và `template.html` (nav, skip link, footer; chưa đếm chính xác). | Phải tách chữ khỏi code, từng nhóm trang một. Đây là phần tốn công nhất, không phải phần dịch. |
| 3.2 | **Code đọc ngược chữ tiếng Anh trong dữ liệu**: `RCV=/^(Craft\|Combine\|Infuse…)\b/` (`app.js:1527`), `/^Key requirement: locked behind/i` (`app.js:1267`), và `fmt()` (`app.js:784`) gắn icon bằng regex từ khóa tiếng Anh (`AIRG`, `app.js:778`). | Dịch dữ liệu tại chỗ sẽ làm hỏng logic và mất icon. Giữ tiếng Anh làm khóa (msgid), dịch ở bước cuối trước khi in. **(đã đo, sửa)**: vì `tr()` chỉ áp ở bước in cuối, `RCV` và `Key requirement` vẫn đọc tiếng Anh nên **không phải sửa**; chỉ `fmt()` / `AIRG` bị ảnh hưởng (mục 13.3). |
| 3.3 | **Font nhúng chỉ có Latin cơ bản** (`build/fonts/README.md`: subset U+0020–00FF). Đo bằng fontTools: Russian thiếu **66/66** chữ cái ở cả 3 font; Vietnamese thiếu **54–55/74** ký tự có dấu; Português và Español đủ. | ru và vi sẽ rơi về font hệ thống ở tiêu đề / nút, vỡ phong cách pixel. Cần quyết định về look. |
| 3.4 | Dữ liệu có ≈18,2k chuỗi duy nhất, ≈770k ký tự (đã loại id và số; trong đó ≈24k là tên class Java `GE.cls`, không cần dịch). Nhưng phần lớn chỉ là **mẫu câu khác tên**: `src` 1.483 chuỗi → 272 mẫu; `src0` 1.182 → 300; `why` 252 → 111 (đếm bằng cách thay tên riêng và số bằng ký hiệu). | Dịch mẫu một lần, sinh chuỗi bằng chương trình (mục 6, L2). |
| 3.5 | Tên vật phẩm (1.302 curio + 2.150 gear), tooltip (`fx`, `GE.tip`) và sách Patchouli (`GUIDE`, 424 chuỗi) là chữ **của mod**; game có bản dịch chính thức. Vanilla có `vi_vn`, `ru_ru`, `pt_br`, `pt_pt`, `es_es`; mẫu 1 mod (Ars Nouveau) có đủ cả năm. | Lấy từ file `lang`, không dịch bằng AI: 0 token và đúng thuật ngữ game. **(đã đo, sửa mạnh)**: độ phủ thật thấp hơn tôi kỳ vọng, đặc biệt ngoài tiếng Nga, và tooltip curio (`fx`) hầu như **không** phải chữ nguyên văn của mod (mục 13.2). |
| 3.6 | `build/pack_audit/` đã có sẵn code đọc lang (`name_icons.py`, `tips.py`, `guides.py`, `goety.py`, `summons.py`). | Mở rộng cái có sẵn thay vì viết mới. |
| 3.7 | Không bước Python nào của build hiện **ghi** câu `src` của curio (đã grep `patches/*.py`: chỉ đọc hoặc sửa chỗ khác); `data.js` là source, câu là chữ đã đóng băng từ lần migrate một lần. | Không có "chỗ sinh câu" để thay bằng mẫu; phải khai thác mẫu ngược từ chuỗi có sẵn (L2). |

Hai giả định cần nói thẳng:
- "Dịch hết bằng AI cho nhanh" **không rẻ nhất và không đúng nhất**: tên và tooltip của mod có bản chính thức; AI chỉ nên đụng phần còn lại.
- "Portugal" và "Español" chưa đủ để chọn file lang và từ vựng: `pt_br` khác `pt_pt` khá nhiều; `es_es` khác `es_mx`. Xem D1, D2.

## 4. Bốn quyết định cần bạn chốt (mỗi cái có mặc định của tôi)
| | Câu hỏi | Mặc định | Vì sao |
|---|---|---|---|
| D1 | Bồ Đào Nha: **pt-BR** (Brazil) hay pt-PT? | pt-BR | Nhận định của tôi (chưa đo): người chơi Bồ Đào Nha ngữ chủ yếu ở Brazil. Hai bản khác nhau đủ nhiều để không trộn; DeepL cũng tách PT-BR / PT-PT. |
| D2 | Tây Ban Nha: **es trung tính (Mỹ Latinh)** hay es-ES? | es trung tính; tên lấy từ `es_mx` rồi `es_es`; tránh từ địa phương | Nhận định của tôi (chưa đo): người chơi Mỹ Latinh đông hơn; nhưng nhiều mod chỉ ship `es_es` nên vẫn là nguồn tên chính. Đo ở bước 0.2 rồi chỉnh. |
| D3 | Tên vật phẩm / mob / boss trong **tiếng Việt**: dịch hay giữ tiếng Anh? | **Giữ tiếng Anh**, dịch phần văn xuôi. Chỉ ghi thêm tên vi chính thức (nếu có) ở infobox. Không tự bịa tên vật phẩm tiếng Việt. | Mod ít khi có `vi_vn` đầy đủ; người chơi Việt thường chơi bản tiếng Anh và tìm đồ theo tên Anh. (Giả định này bạn biết rõ hơn tôi.) Với ru / pt / es: tên theo lang chính thức, thiếu thì giữ tiếng Anh; **tên tiếng Anh luôn hiện trong infobox và luôn tìm kiếm được**. |
| D4 | Dịch bằng gì, trả bằng gì? | Claude (Sonnet) chạy trong phiên, theo lô nhỏ, tính vào usage limit; DeepL Free (500.000 ký tự/tháng, hỗ trợ cả 4 ngôn ngữ, có glossary) là phương án thứ hai cho văn xuôi dài của mod, quyết bằng pilot (Phase 1) | Không cần API key; tiến độ lưu theo lô nên dừng vì hết giới hạn thì chạy tiếp, không làm lại. |

Tên riêng của pack (Keeper, tên boss Armageddon, tên Act "Warden Act"…) **giữ tiếng Anh ở mọi ngôn ngữ**; chỉ từ chung được dịch ("Act" theo glossary, mục 6 L3). Mod Armageddon không có bản dịch chính thức để dựa vào.

## 5. Kiến trúc: ba phương án
| | Phương án | Kết luận |
|---|---|---|
| A | Một bản build cho mỗi ngôn ngữ (5 site, 5 file offline) | Loại. 5 × 14 MB, đổi dữ liệu là build ×5, đổi ngôn ngữ phải tải lại trang. |
| **B** | **Gói ngôn ngữ chạy lúc đọc**: tiếng Anh vẫn nằm trong code và dữ liệu (làm khóa); mỗi ngôn ngữ một gói JSON nạp lười; `t()` cho chữ giao diện, `tr()` cho chữ dữ liệu | **Chọn.** Giữ routes `#…` nguyên, đổi ngôn ngữ không tải lại trang, người đọc tiếng Anh không trả giá. Đã có tiền lệ nạp muộn: `wiki_pics.js` (`LATE` trong `build.py`, `loadPics` trong `app.js`). |
| C | Dịch DOM sau khi vẽ (duyệt text node, thay theo từ điển) | Loại. Hỏng với câu ghép từ nhiều mảnh, số nhiều, và nhấp nháy tiếng Anh. Nhanh để có demo nhưng không kiểm tra được. |
| D | Để trình duyệt tự dịch (Google Translate) | Hiện tại nhiều người đã làm vậy; sai thuật ngữ game, vỡ tên riêng. Không phải giải pháp. |

Thư viện i18n (i18next, Fluent, FormatJS) **không dùng**: trình duyệt đã có `Intl.PluralRules` (ru có 4 dạng số nhiều, vi chỉ 1), `Intl.NumberFormat`, `Intl.ListFormat`, `Intl.Collator`; repo cố ý "không framework" (`ARCHITECTURE.md`). Xem lại nếu ngữ pháp ru (biến cách) lấn quá nhiều.

Quy tắc chạy:
- Chọn ngôn ngữ: `?lang=vi` → `localStorage` → `navigator.languages` → `en`. Routes `#…` không chứa ngôn ngữ nên link cũ còn nguyên. `<html lang>` đổi theo.
- Thiếu bản dịch → **tiếng Anh** (không bao giờ trống, không hiện khóa). Chế độ dev tô màu chuỗi chưa dịch.
- `tr(en)` tra theo hash 53-bit của chuỗi Anh (tính khi chạy, có nhớ); build **thất bại** nếu hai chuỗi trùng hash. Với `en`, `tr` là hàm đồng nhất: không tốn gì.
- Hai gói mỗi ngôn ngữ: `ui` (cần cho lần vẽ đầu, ước ≈100 KB) và `data` (nạp khi mở trang chi tiết, như `wiki_pics.js`). File offline `dist/` nhúng cả bốn ngôn ngữ (ước +3–4 MB trên 13,8 MB; ước lượng).
- Tìm kiếm khớp cả tên Anh lẫn tên bản địa; sắp xếp dùng `Intl.Collator(lang)`; `toLocaleString()` truyền ngôn ngữ rõ ràng (hiện đang theo locale trình duyệt).

## 6. Thang tiết kiệm token (đi từ rẻ đến đắt; chỉ xuống bậc dưới cho phần bậc trên không phủ được)
| Bậc | Việc | Token |
|---|---|---|
| L0 | **Không dịch**: id, số, công thức, tên class Java, tên mod, tên riêng của pack | 0 |
| L1 | **Thu hoạch bản dịch chính thức** từ vanilla + jar (`build/i18n/harvest.py`, mở rộng `pack_audit/*`): tên, hiệu ứng, tooltip, Patchouli. Chuỗi trong wiki là bản sao nguyên văn lang `en_us` ("lang templates are stored verbatim", `app.js:779`) nên tra ngược English → khóa → bản `ru_ru` / `pt_br` / `es_es` / `vi_vn`. Một câu Anh ứng nhiều khóa mà bản dịch khác nhau thì **bỏ qua** (đã làm: bỏ 22–115 chuỗi mỗi ngôn ngữ), không đoán. Thiếu bản dịch thì **giữ tiếng Anh**: đúng cái người chơi thấy trong game (key thiếu thì game rơi về `en_us`). **(đã đo)** tên: ru 49%, es 23%, pt 20%, vi 9%; câu nguyên văn: ru 53%, es 29%, pt 25%, vi 10% (mục 13.2) | 0 |
| L2 | **Mẫu câu**: khai thác mẫu (`N at a N from N, N.`), dịch ≈600 mẫu, sinh ra mọi chuỗi cụ thể bằng chương trình (`build/i18n/expand.py`) với tên lấy từ L1. Kiểm bằng cách: sinh lại câu **Anh** từ mẫu phải ra đúng từng ký tự, nếu không thì chuỗi đó rớt xuống L5 | ≈ 1/10 so với dịch thẳng |
| L3 | **Glossary** (`build/i18n/glossary.json`, ≈300–500 mục: Act, Keeper, Curio, Relic, The Path, Hardmode, S/A/B/C/D, DPS, EHP, các từ cơ chế). Mỗi lô chỉ gửi những mục xuất hiện trong lô đó. Mẫu định dạng: `doNotTranslate` + `terms{en→{vi,ru,pt,es}}` (như `ory/elements`). Bạn duyệt bản vi; ru / pt / es dựa lang chính thức và Minecraft Wiki bản ngôn ngữ làm tham chiếu | thấp |
| L4 | **Bộ nhớ dịch** (`build/i18n/tm/<lang>.json`: `hash → {en, t, s, r}`; `s` = official / tpl / llm / mt / human; `r` = đã soát). Chạy lại chỉ dịch chuỗi mới hoặc đổi; sửa chữ Anh thì chuỗi cũ thành "stale" và công cụ báo, không dịch lại âm thầm | 0 khi lặp |
| L5 | **AI dịch phần còn lại**: chữ giao diện, chữ riêng của pack (boss, Mechanics, ghi chú), tooltip mod chưa có bản chính thức. Lô ≤60 chuỗi, glossary + hướng dẫn văn phong cố định đầu lô (hưởng prompt caching), trả JSON, ghi vào TM **sau mỗi lô** (dừng giữa chừng không mất) | phần chính |
| L6 | **QA tự động** (`build/i18n/qa.py` và `build/checks/i18n.js`): giữ nguyên `%s` `%d` `{x}` thẻ HTML và số; đủ thuật ngữ glossary; không sót tiếng Anh (tỷ lệ chữ Cyrillic cho ru…); độ dài hợp lý; cùng tập icon với bản Anh. Chuỗi rớt thì chạy lại riêng, không soát tay cả kho | 0 |
| L7 | **Soát người**: vi do bạn; ru / pt / es qua cộng đồng (Phase 5). Chưa soát thì menu ghi "bản dịch hỗ trợ máy" | — |

**Ước lượng token** (thô, sai số ±50%, đo lại ở pilot Phase 1): ≈750k ký tự ≈190k token Anh. Dịch thẳng mọi thứ cho 4 ngôn ngữ ≈ 1,0–1,6 triệu token output (ru tốn khoảng gấp đôi, vi ≈1,5×, pt/es ≈1,3×). **Sửa sau khi đo L1**: bản dịch chính thức phủ ít hơn dự kiến (tooltip curio hầu như không có), nên phần cần AI cho mỗi ngôn ngữ ≈ 490k ký tự (giao diện ≈125k, `fx` 82k, `st` ≈100k, mẫu `src` ≈40k, boss / sách / ghi chú ≈90k, `tip` ≈30k, `why` 24k), không phải 360k. Qua thang L0–L6 ước **≈0,7–0,9 triệu token output cho cả bốn** (trước đây ghi 0,5–0,7). Vẫn là ước lượng; thay bằng số đo thật sau pilot, trước khi cam kết Phase 3–4.

Nguồn mở đã xem làm tham chiếu (chưa đọc mã, chưa kiểm giấy phép; chỉ lấy thiết kế, tự viết ≈150–300 dòng Python vì khóa của ta là hash của chuỗi Anh và dữ liệu là JS, không phải file i18n chuẩn):
- `taahamahdi/i18n-ai-translate`: dịch theo diff, glossary giữ nguyên / ép dịch theo ngôn ngữ, cache (TM) theo nguồn + ngôn ngữ + ngữ cảnh.
- `i18n-actions/ai-i18n`: băm nội dung để chỉ dịch chuỗi mới, xử lý số nhiều kiểu CLDR / ICU.
- `ory/elements` (`locales/README.md`): mẫu glossary `doNotTranslate` / `terms` và test so file locale với `en.json` (tham số khớp, không còn bản sao tiếng Anh): ta chép ý này vào `checks/i18n.js`.
- Bản dịch chính thức của game (asset index của Mojang, lang trong jar mod, Crowdin của mod): nguồn thuật ngữ số một.
- Minecraft Wiki bản ru / pt / es và trang `Minecraft_Wiki:Translations`: chỉ để đối chiếu thuật ngữ; không chép văn bản (giấy phép của wiki đó khác với repo này, cần kiểm trước khi chép bất cứ thứ gì ngoài tên gọi).
- DeepL API: VI, RU, PT-BR / PT-PT, ES / ES-419 đều có, có glossary và giữ thẻ; Free 500k ký tự/tháng (đọc từ tài liệu DeepL hôm nay).
- Mô hình mở chạy máy (NLLB-200, MADLAD-400, Opus-MT): loại, cần GPU, chất lượng với chuỗi ngắn có tham số kém LLM (nhận định từ kiến thức sẵn có, chưa thử).

## 7. Các phần mới trong repo
```
build/src/i18n.js            t(), tn() (số nhiều), trạng thái ngôn ngữ, nạp gói, menu (đã làm); tr() cho chữ dữ liệu: Phase 3
build/i18n/ui.json           chữ giao diện: {khóa: {en, vi, ru, pt, es}}; build.py tách thành gói từng ngôn ngữ và kiểm với trang (đã làm, Phase 1)
build/i18n/glossary.json     L3
build/i18n/tm/<lang>.json    L4 (commit; có `en` để xem diff dịch được)
build/i18n/official/<l>.json L1 (commit; kết quả harvest, nhỏ)
build/i18n/{harvest,extract,expand,translate,qa}.py   công cụ; translate.py in lô ra / nhận lô vào, không giữ khóa API
build/checks/i18n.js         bất biến (nạp bởi check.js như các file khác trong checks/)
build/shot.js                thêm --lang (shot nhiều ngôn ngữ)
docs/I18N.md                 cách thêm ngôn ngữ, sửa một bản dịch, chạy lại một lô
```
Gói gửi lên site chỉ chứa `hash → bản dịch` (bỏ `en`).

## 8. Các phase
Mỗi phase đi hết CLAUDE.md bước 2–6 và ship riêng; mỗi nhóm trang một invariant. Số phiên là ước lượng.

### Phase 0: nền (người đọc chưa thấy gì; ≈2 phiên)
- **0.1 Font. (xong, mục 13.5.)** Monocraft gốc có đủ Cyrillic nên ru dùng chính Monocraft (không đổi look). Không font pixel OFL nào có đủ cả Cyrillic lẫn tiếng Việt; **bạn đã chọn V2 cho tiếng Việt**: VT323 cho tiêu đề và nhãn khi `html[lang=vi]`, thân bài vẫn Be Vietnam Pro.
- **0.2 Đo độ phủ lang chính thức. (xong.)** `build/i18n/harvest.py` (`fetch`, `vanilla`, `build`) tải từng jar của manifest CurseForge, giữ chỉ file lang + Patchouli, xóa jar (454/455 file, 56 MB, chạy được ngay trong phiên cloud, chưa đầy 3 phút); `build` ra `build/i18n/official/<lang>.json` (đã commit) và báo cáo. Kết quả ở mục 13.2.
- **0.3 Icon trong câu dịch. (đã đo; thiết kế chốt.)** Không cần gỡ `RCV` / `Key requirement` (xem 3.2). Chỉ `fmt()` cần đổi: **tập icon lấy từ câu tiếng Anh gốc; bảng từ khóa của từng ngôn ngữ chỉ để tìm vị trí đặt icon trong bản dịch, không tìm thấy thì đặt đầu dòng** (mục 13.3). Làm khi viết `i18n.js` (Phase 1), kèm bảng ru / es / pt / vi (đã có bản nháp ru, es).
- **0.4** Bạn chốt D1–D4.

### Phase 1: động cơ + vỏ giao diện, tiếng Việt (≈2 phiên)
**Đã làm (mục 13.4): menu ngôn ngữ + vỏ trang (header, nav, thanh lọc, footer) ở cả 4 ngôn ngữ; trang hub dời sang Phase 2(a).** Dự kiến ban đầu: menu ngôn ngữ; đầu trang, nav, footer, hub bằng tiếng Việt. Làm: `i18n.js`, gói ui, `build.py` (gói + bản offline), `shot.js --lang`, `site_check.js` (gói tải được, mất gói → vẫn tiếng Anh), `checks/i18n.js`. **Pilot đo token**: dịch hub + một trang curio hết đường L1→L6, ghi token / 1.000 ký tự, so DeepL với Claude trên 40 chuỗi mỗi ngôn ngữ (bạn chấm bản vi). Cập nhật mục 6 bằng số thật rồi mới sang Phase 2.

### Phase 2: toàn bộ chữ giao diện, tiếng Việt (≈3 phiên, ship từng nhóm)
(a) hub + Act + The Path; (b) Curios; (c) Equipment + Build planner; (d) Bosses + trang Keeper / side boss; (e) Mechanics + Changes. Mỗi nhóm: tách chữ ra `t()`, dịch, shot 1440 px và 375 px, bạn xem. Chuỗi có số nhiều dùng `tn()`.

### Phase 3: dữ liệu, tiếng Việt (≈2 phiên)
Curio (`fx`, `src`, `st`, `why`…), gear (`tip`), Keeper / side boss (`BINFO`, `SIDEB`, `SSTAT`), sách (`GUIDE`), Goety / AE2 / summons. Có ≈100–200 chỗ in chữ dữ liệu (grep thô đếm được ≈57 chỗ cho riêng `fx` / `src` / `st` của curio) phải bọc `tr()`. L1 + L2 + L5.

### Phase 4: ru, pt-BR, es (≈1 phiên mỗi ngôn ngữ, ru nặng nhất)
Mỗi ngôn ngữ: glossary → harvest → TM → QA → shot 1440 / 375 (tràn layout; ru thường dài hơn en khoảng 20–30%, **ước lượng, chưa đo trên wiki**). Làm ru ngay sau vi vì nó thử động cơ khó nhất (4 dạng số nhiều, Cyrillic, biến cách). pt và es gần như chỉ là chạy lại quy trình.

### Phase 5: soát cộng đồng + tài liệu (≈1 phiên)
Nút "Đề xuất bản dịch tốt hơn" mở issue / PR sửa `tm/<lang>.json`; menu ghi trạng thái từng ngôn ngữ ("đã soát" / "hỗ trợ máy"); `docs/I18N.md`. Weblate hoặc Crowdin chỉ khi có cộng đồng thật sự đến sửa (chưa kiểm gói miễn phí hiện hành).

## 9. Tiêu chí "xong" và cách kiểm
- Mỗi ngôn ngữ: 100% khóa có bản dịch hoặc nằm trong danh sách "giữ tiếng Anh" có chủ đích; `qa.py` 0 lỗi; thuật ngữ trùng glossary.
- Quét các route của mọi loại trang: không còn chữ Anh nhìn thấy ngoài danh sách tên riêng cho phép (script đếm text node chỉ chứa từ tiếng Anh).
- `check.sh` xanh ở tiếng Anh (đủ 3.918 trang chi tiết); với vi / ru / pt / es chạy **mẫu**: mọi trang danh sách + ≈150 trang chi tiết đại diện + kiểm tràn ở 375 px (chạy đủ ×5 sẽ ≈30 phút mỗi lần).
- Bạn đọc xong bản vi của hub, một curio, một gear, một Keeper và Mechanics.
- Tiếng Anh: `shot.js --diff` 0% pixel đổi so với trước khi làm; thời gian tải trang đầu không tăng quá ngưỡng đo được ở `perf.js`.

## 10. Rủi ro đã biết
- **Biến cách tiếng Nga** (và mạo từ giống / số ở es / pt) khi ghép tên vào câu mẫu: "Скрафтите из {item}" cần đúng cách. Cách giảm: viết mẫu để tên đứng ở danh sách sau dấu hai chấm hoặc trong « », không chia cách; vẫn cần người bản ngữ soát.
- **Không bản ngữ ru / pt / es trong tay** ⇒ QA tự động và thuật ngữ chính thức bắt được lỗi hệ thống, không bắt được câu "gượng". Đó là lý do có nhãn "hỗ trợ máy" và Phase 5. Không hứa chất lượng bản ngữ khi chưa có người soát.
- **Giấy phép chữ của mod**: wiki đã trích tooltip và sách bằng tiếng Anh; dùng bản dịch chính thức của chính các chuỗi đó có cùng cơ sở. Quy tắc README hiện chỉ nói về **texture**; chữ từ mod "All Rights Reserved" chưa có quy tắc. Đề xuất: dùng bản dịch chính thức cho tên và các chuỗi mà wiki đã trích sẵn, không thêm văn bản mới của mod. Cần bạn xác nhận.
- Chuỗi tham số `%s`, `%1$s`, `[]` của mod (`gameTx`, `app.js:779`) phải còn nguyên sau dịch (L6 kiểm).
- Link chia sẻ build (`#build/…`) giữ nguyên vì không chứa ngôn ngữ; ngôn ngữ đi kèm bằng `?lang=` nếu người gửi muốn.
- `check.js` đã 6 phút; không nhân ×5 (xem mục 9).
- Hash trùng ⇒ build thất bại (đã tính ở mục 5), không đoán.

## 11. Cách làm việc và ngân sách (CLAUDE.md, Budget)
Không subagent, không workflow song song (bạn chưa yêu cầu). Opus cho glossary, hướng dẫn văn phong và chuỗi QA bắt lỗi; Sonnet cho các lô L5 và sửa nhỏ. Mỗi lô ghi TM ngay nên dừng vì usage limit rồi chạy tiếp được. Mỗi phiên thêm một mục vào `docs/NOTES.md`; mỗi lỗi tìm thấy trong bản dịch thành một bất biến trong `build/checks/i18n.js`.

## 12. Chưa kiểm chứng (đừng coi là sự thật)
- Giấy phép và chất lượng của `i18n-ai-translate`, `ai-i18n`; gói miễn phí Weblate / Crowdin; giá API hiện hành.
- Tỷ lệ token thật cho ru / vi (mục 6 là ước lượng).
- Mức nở layout của ru trên wiki.
- Độ phủ bản dịch của sách Patchouli (`GUIDE`): file đã nằm trong cache thu hoạch nhưng `harvest.py build` chưa ghép (mới ghép tên theo id và câu nguyên văn).
- Chất lượng bảng vị trí icon ngoài hai bản nháp ru / es; chưa thử pt, vi.
- Độ chính xác của "câu nguyên văn": một câu ứng một khóa duy nhất thì chắc; còn lại là bỏ qua khi mơ hồ, nhưng chưa ai đọc từng cặp.

## 13. Kết quả Phase 0 (đo ngày 2026-11-08 trên bản build của `b0c2c0e`)
### 13.1 Font (đã đo bằng fontTools; ảnh so sánh đã gửi bạn)
| Font | Cyrillic thiếu | Tiếng Việt thiếu |
|---|---|---|
| Monocraft đang nhúng (subset) | 66/66 | 55/74 |
| Monocraft gốc (v4.2.1, 1.475 glyph) | **0/66** | 48/74 (không có combining mark) |
| Jersey 15 (cả họ Jersey) | 66/66 | 50/74 |
| Pixelify Sans / Press Start 2P | 2 / 0 của 66 | 48 / 49 của 74 |
| VT323 | 66/66 | **0/74** |
| Be Vietnam Pro (thân bài hiện tại) | 66/66 | 0/74 |
- **ru**: Jersey 15 → Monocraft gốc cho đủ chữ, cùng phong cách (ảnh R1 đẹp). Không phải xin duyệt look vì không đổi gì ở tiếng Anh.
- **vi**, ba cách (ảnh): **V1** Monocraft + VT323 chen từng glyph: chữ nhỏ to lẫn lộn trong một từ ("đồ", "Kẻ"), **không nên**. **V2** VT323 cho cả dòng: đồng nhất, vẫn pixel, thanh mảnh và cao hơn Monocraft. **V3** Be Vietnam Pro đậm: sạch nhất, không còn pixel. Tôi khuyên **V2** cho tiêu đề và nhãn khi `lang=vi`, thân bài giữ Be Vietnam Pro. *Chờ bạn chọn.*

### 13.2 Độ phủ bản dịch chính thức (`harvest.py`, 306 mod có lang)
Số mod ship từng file: `ru_ru` 170, `pt_br` 114, `es_es` 91, `es_mx` 70, `vi_vn` 36; `pt_pt` chỉ thêm đúng 1 mod không có `pt_br` (ủng hộ D1); 124 mod không có ngôn ngữ nào trong bốn.
| | ru | pt (pt_br) | es (es_mx → es_es) | vi |
|---|---|---|---|---|
| Tên theo id (3.519 curio + gear) | 49% | 20% | 23% | 9% |
| Chuỗi nguyên văn trong `en_us` (6.604 chuỗi duy nhất của dữ liệu) | 53% | 25% | 29% | 10% |
| Chuỗi bỏ qua vì mơ hồ | 115 | 60 | 114 | 22 |
- Chỉ **6.604 / 24.909** chuỗi duy nhất (≥8 ký tự) của dữ liệu là chữ nguyên văn của game. Phần còn lại do wiki tự soạn.
- Tooltip curio (`fx`): chỉ **1%** nguyên văn (13 / 2.213): đó là câu tóm tắt do wiki ghép từ nhiều dòng và thuộc tính. Tooltip gear (`tip`): **87%** nguyên văn, nhưng có bản dịch chỉ ru 44%, es 43%, pt 8%, vi 5%. Dòng `st` của curio: 33% nguyên văn, ru 14%.
- Hệ quả: L1 cho **tên** (đúng thuật ngữ game, 0 token) và một phần tooltip gear; phần văn xuôi do wiki soạn vẫn cần L2 / L5. Ước lượng token ở mục 6 đã sửa theo đó.
- Lỗi dữ liệu nguồn đã gặp và xử lý: một số file lang của mod kết thúc giá trị bằng dấu phẩy thừa ("Pergamino de Historia,"); `build` bỏ dấu phẩy nếu câu Anh không có.
- Kết quả đã commit: `build/i18n/official/{ru,pt,es,vi}.json` (≈370 / 124 / 160 / 52 KB). Chỉ chứa tên và các chuỗi mà wiki đã trích sẵn (xem rủi ro giấy phép, mục 10).

### 13.3 Icon trong câu dịch (spike trên 301 / 279 cặp dịch chính thức không mơ hồ)
- Cách "chạy lại bảng từ khóa trên bản dịch" cho tập icon khác bản Anh nhiều (cùng tập: ru 27%, es 48%) vì bảng từ khóa vốn đã mờ ngay cả ở tiếng Anh và nhiều cặp dịch không sát nghĩa.
- Cách chọn: **tập icon từ câu Anh (100% giống bản Anh theo cách xây)**, bảng ngôn ngữ chỉ tìm vị trí. Bản nháp chưa chỉnh tìm được vị trí cho ru 61% (66/109 icon), es 84% (78/93); phần còn lại đặt đầu dòng. Chỉnh bảng bằng glossary khi làm Phase 1.

### 13.4 Lát cắt Phase 1: động cơ + vỏ trang (làm ngày 2026-11-08, nhánh `claude/busy-ride-88rgef`)
- **Có gì:** `build/src/i18n.js` (`t`, `tn`, `shell`, `setLang`, menu), `build/i18n/ui.json` (34 khóa × 5 ngôn ngữ), `build/i18n/glossary.json` (12 thuật ngữ khởi đầu), `build.py` (kiểm bảng chuỗi rồi tách gói: nhúng sẵn trong file offline, mỗi ngôn ngữ một file `static/lang-xx.<hash>.js` trên site, chỉ tải khi chọn), `shot.js --lang`, `site_check.js` (gói tải được; gói bị chặn thì vẫn tiếng Anh), `checks/i18n.js`.
- **Cách chọn ngôn ngữ:** `?lang=xx` → lựa chọn lần trước (`localStorage`) → tiếng Anh. Chưa đoán theo trình duyệt vì bản dịch chưa được soát (Phase 5).
- **Phần cố ý để nguyên tiếng Anh:** đoạn "Art" của footer (ghi công và giấy phép: chữ pháp lý giữ nguyên để không sai lệch); chữ do JS sinh ra (Phase 2 và 3).
- **Lỗi đã bắt được nhờ kiểm bằng so `outerHTML`:** `app.js` đã dùng sẵn `data-i` cho nút Act của The Path; bản đầu của tôi cũng dùng `data-i` nên `shell()` ghi đè các nút đó. Đổi sang `data-lg` / `data-lgh` / `data-lga` (đã kiểm không ai dùng). Bài học: kiểm "đi vòng các ngôn ngữ rồi về tiếng Anh phải y nguyên" là phép kiểm cần có.
- **Điểm ảnh:** so với bản build trước (`b0c2c0e`, cả hai chụp tắt motion, 6 route ở 1440 px): chỉ vùng header đổi (menu mới, ô tìm kiếm co lại), thân trang giữ nguyên.
- **Giao diện cần bạn duyệt:** menu ngôn ngữ là một nút đá (kiểu `select` của wiki) nằm **trong đầu phải của ô tìm kiếm** (như cổng wikipedia.org): đóng thì hiện mã `EN` / `VI` / `RU` / `PT` / `ES`, mở ra thì hiện mã và tên. Ru hiện còn dùng font hệ thống cho chữ Cyrillic cho đến khi làm bước font (13.1).
- **Sửa lại sau `check.sh` đầu tiên (đã đẩy ở `e53d039`, lỗi trong bản đó):** bản đầu đặt menu thành phần tử thứ tư của hàng header. `style_check` báo "768px #mechanics: tiêu đề AE2 nằm dưới header (-28 px)" (bản cũ qua); đo thêm thấy ở 1000–1100 px menu rơi **ra ngoài** header 64 px, và ở 768 / 900 px header cao thêm một hàng (212 so với 164 px). Gốc: hàng header đã chật sẵn (ở 1000 px ô tìm kiếm của bản cũ chỉ còn 70 px). Cách sửa: đưa menu vào trong ô tìm kiếm (không thêm chiều rộng hay hàng nào), cho header xuống hai hàng sớm hơn (≤1180 px thay vì ≤900 px, vì dưới 1180 ô tìm kiếm bị ép dưới 250 px) và riêng ru / pt ở ≤1320 px (nav của ru 767 px, pt 754 px so với en 640 px). Sau sửa: hình học header giống hệt bản cũ ở 768 / 900 px, ô gõ còn ≥135 px ở mọi độ rộng đã đo, `style_check` qua, và so với bản cũ chỉ **0,148%** điểm ảnh đổi (đúng chỗ nút menu). Thay đổi cho người đọc tiếng Anh ngoài nút menu: ở 901–1180 px header giờ xuống hai hàng (ô tìm kiếm một hàng riêng) thay vì ô tìm kiếm 70–170 px.
- **Chưa làm:** chữ do JS sinh, `tr()` cho dữ liệu, bảng vị trí icon, gói `data`. (Font ru / vi: xong, mục 13.5.)

### 13.5 Font cho ru và vi (làm ngày 2026-11-08, theo lựa chọn V2 của bạn)
- **ru:** `Monocraft-Cyrillic.woff2` và `Monocraft-Bold-Cyrillic.woff2` (subset U+0401, 0410-044F, 0451, 2116 từ bản phát hành v4.2.1; mỗi file ≈3 KB), khai báo cùng họ `Monocraft` với `unicode-range`, nên nhãn và tiêu đề tiếng Nga vẽ bằng Monocraft thật (tiêu đề rơi từ Jersey 15, không có Cyrillic, về Monocraft). Thân bài tiếng Nga vẫn là font hệ thống vì Be Vietnam Pro không có Cyrillic (chưa quyết định đổi).
- **vi (V2):** `VT323-Vietnamese.woff2` (≈20 KB; VT323 của Peter Hull, SIL OFL 1.1; đủ cả 1EA0-1EF9 và ă â đ ê ô ơ ư), họ `VT323 vi`, `size-adjust:127%` (ảnh bạn chọn dùng 19 px cho 15 px của Monocraft), dải đậm 400-900 để trình duyệt không bôi đậm giả lên chữ pixel. Quy tắc: `html[lang=vi]{--disp:…;--title:…}` ở cuối `style.game.css`. Ghi công đã thêm vào đoạn "Art" của footer.
- **Không tốn gì cho người đọc tiếng Anh:** file offline nhúng base64 (+≈33 KB); trên site là file `woff2` riêng, trình duyệt chỉ tải khi chữ cần tới (`unicode-range` cho Cyrillic, chính họ font cho VT323). Đã kiểm: tiếng Anh vẫn chỉ lệch 0,148% điểm ảnh so với bản trước khi làm i18n (nút menu).
- **Kiểm:** `checks/i18n.js` (phải có face Cyrillic thường và đậm đã tải, face VT323 đã tải, trang vi dùng VT323 cho nhãn và tiêu đề, VT323 không rò sang en / ru; thử cố ý xóa các face thì báo đúng lỗi); `site_check.js` (trên bản site thật, file font tải được, 0 yêu cầu thất bại). Phép đo "độ rộng so với font mặc định" tôi thử trước **không đáng tin** (Chromium chọn font hệ thống riêng cho từng glyph thiếu, báo xanh giả), nên bỏ.

### 13.6 Phase 2, nhóm (a): hub, trang Act, The Path, thanh điều hướng (làm ngày 2026-11-08)
- **Đổi cách cho chữ viết trong JS:** thay vì đặt khóa bằng tay (như `ui.json` cho `template.html`), **chính câu tiếng Anh là khóa**: `T("Opens when {boss} falls.",{boss})`, `TN(n,"{n} curio","{n} curios")`. Khóa là băm của câu Anh (`hsh` trong `i18n.js`, cùng thuật toán trong `i18n/tmlib.py`; đã kiểm hai bên cho cùng kết quả kể cả chữ có dấu, ký tự Cyrillic và rỗng). Lý do: quét tự động được, tiếng Anh nằm ngay tại chỗ dùng, không phải đặt tên ~800 khóa. Bộ nhớ dịch là `i18n/tm/<lang>.json`.
- **Đã chuyển:** `crumb` ("Home"), nhãn Act (`actL`, `actF`), `wikiNav` (thanh điều hướng cuối mọi trang chi tiết), thanh bộ lọc đang bật, các nút của màn hình tiêu đề, bốn thẻ "Start here", The Path (tiêu đề, bảng từng Act, nút "I'm here", dòng "Your run"), các mục của hub (Equipment, Must-Have, Curio slots, Mythic, New in 6.6.6), trang Act (tiêu đề, mô tả, "Opened by beating", "Next boss", "Showing … of …", "Show 60 more", không tìm thấy). **88 câu viết trực tiếp + 29 câu dựng từ biến** (mô tả Act, tên boss trong câu) do `i18n/trlog.js` thu thập.
- **Dịch:** 104 câu × 4 ngôn ngữ (vi, ru, pt-BR, es) vào `tm/`; 13 câu giữ tiếng Anh có chủ đích (`i18n/keep.json`: Keeper, tên riêng Arion / Eldorath / Iron Colossus / Nyxaris / Sanghor / Vaedric / Zoranth…, The Discord, L2 Artifacts, Must-Have, Mythic). Quyết định thuật ngữ mới cần bạn xem: **"The Path" được dịch** (vi "Lộ trình", ru "Путь", pt "O Caminho", es "El Camino"), vì đó là khái niệm của chính wiki chứ không phải tên riêng của pack; **Act** → vi "Act", ru "Акт", pt "Ato", es "Acto" (nhãn dạng "Act 0–I" thành "Акт 0–I"). Tiếng Nga dùng cấu trúc "…после победы над боссом: {boss}" để tên boss đứng ở danh cách (tránh biến cách).
- **Bằng chứng tiếng Anh không đổi:** `innerHTML` của `<main>`, tiêu đề tab và nút màn hình tiêu đề ở **34 trạng thái** (17 route, có và không có "I'm here"): hub, Act 0 / 2 / 5 / 6 / 12 / L2 / Act không tồn tại, một curio, một gear, một bộ giáp, Keeper, Bosses, Mechanics, Changes, Curios) giống bản trước **từng ký tự** (chuẩn hóa blob URL và thứ tự lớp `seen`). Phép so này bắt được một lỗi của tôi (một chuỗi trong dấu nháy đơn không nội suy `${}`).
- **Kiểm:** `build.py` (băm, `{x}`, thẻ, dạng số nhiều; độ phủ 117/117 mỗi ngôn ngữ; thử cố ý sửa `{boss}` thành `{zzz}` bị chặn); `checks/i18n.js` (hub, Act, Act không tồn tại trong 4 ngôn ngữ: không còn `{x}` / `undefined`, và **mọi câu trang yêu cầu đều có bản dịch hoặc nằm trong `keep`**; thử cố ý xóa một bản dịch thì báo đúng câu).
- **Tiêu đề tiếng Nga:** dùng Monocraft trọn vẹn (`html[lang=ru]{--title:Monocraft}`): lúc đầu "АКТ II" ghép chữ Cyrillic từ Monocraft với "II" từ Jersey 15 trông lệch.
- **Còn tiếng Anh trên các trang này (cố ý, nhóm sau):** tên slot (Charm, Ring… có bản dịch chính thức trong mod Curios), thanh lọc và vai trò (nhóm b), chữ dữ liệu của curio, ảnh tiêu đề Act do pack vẽ sẵn (là hình), phần ghi công ở footer.

### 13.7 Phase 2, nhóm (b): trang Curios, cột lọc, thanh lọc, tên slot (làm ngày 2026-11-09)
- **Cột lọc được dựng một lần lúc tải, bằng tiếng Anh** (chip vai trò / độ hiếm / cơ chế / nguyên tố, các ô chọn): đổi ngôn ngữ không dựng lại mà **gắn nhãn lại** (`relabelSide` trong `app.js`, được `useLang` gọi). Khóa lọc vẫn là tiếng Anh, nên bộ lọc đã lưu và link chia sẻ không hỏng. Tìm kiếm hiểu cả tên vai trò bản địa (`role:ближний` ra các curio cận chiến, `role:melee` vẫn chạy).
- **Đã chuyển:** thanh bộ lọc (ô tìm, danh sách trường, nút, đoạn "How it works", mức Relic), nhãn các pill bộ lọc đang bật, trang Curios (tiêu đề, mô tả, chú giải, đầu từng Act, bảng, nút "Show all N curios"), thẻ curio, huy hiệu slot, các slot ở hub, đếm "N / TOTAL curios" và danh sách mục lục. Câu viết trong dấu backtick được quét nhờ mở rộng `tmlib.scan_msgids`.
- **Dịch:** thêm 127 câu → 244 câu mỗi ngôn ngữ, phủ 244/244. **Bản dịch chính thức của game** dùng cho tên slot (mod Curios: Charm → ru Амулет, pt Amuleto, es Amuleto…) và trường phái phép của Iron's Spells (Fire → ru Огонь, pt Fogo, es Fuego…). **vi giữ tiếng Anh cho tên slot và trường phái** (theo D3: người chơi Việt thường chạy game bản tiếng Anh; vi chính thức có "Nhẫn", "Lửa"… nếu bạn muốn đổi, chỉ cần bỏ chúng khỏi `keep.json` mục `vi` và thêm vào `tm/vi.json`). Slot riêng của mod (Spellbook, Anklet, Sacrament…) không có bản dịch chính thức nên giữ tiếng Anh ở mọi ngôn ngữ; tên độ hiếm (Common … Legendary, Mythic, Must-Have) giữ tiếng Anh ở mọi ngôn ngữ (không có bản dịch chính thức; là tên của wiki).
- **Xung đột thuật ngữ đã xử lý:** chính thức ru gọi Evocation là "Призыв" và es là "Invocación", trùng nhãn vai trò Summon; đổi vai trò Summon thành "Призыватель" (ru) và "Invocador" (es) để hai chip trong cùng cột lọc không giống nhau.
- **Tiếng Anh thay đổi đúng một chỗ, có chủ đích:** "1 items" → "1 item" khi một Act (đang lọc) chỉ có một curio. Ngoài ra HTML của 51 trạng thái route (17 route × thường / "I'm here" / bộ lọc bật), gồm cả cột lọc, giống bản trước **từng ký tự**. Phép so này lại bắt được một lỗi nháy đơn của tôi (huy hiệu Must-Have trên thẻ).

### 13.8 Phase 2, nhóm (c1): khung trang chi tiết, tooltip và **tên vật phẩm theo bản dịch chính thức** (2026-11-09)
- **Tên vật phẩm (L1, bắt đầu Phase 3):** `build.py` đưa vào gói của từng ngôn ngữ các tên và câu nguyên văn lấy từ chính game (`i18n/official/<lang>.json`, đã thu hoạch ở Phase 0), khóa theo băm của câu Anh mà trang hiển thị; câu của ta luôn thắng. Thêm `TD(en)` (cùng cách tra nhưng không ghi nhật ký, không điền tham số) và bọc nó quanh **70 chỗ in tên** (`esc(x.n)`) ở `app.js` và `gear.js`, tiêu đề tab của trang curio / gear / bộ giáp, và ô tìm: gõ tên tiếng Nga của một curio cũng ra nó (`d._q` có thêm tên bản địa). Tên chưa có bản dịch chính thức vẫn là tiếng Anh, đúng như người chơi thấy trong game khi bản dịch thiếu. Kết quả: ru có tên Nga cho khoảng một nửa số curio và gear, es ≈23%, pt ≈20%, vi ≈9% (số đã đo ở 13.2).
- **Khung `article()`** (mọi trang chi tiết: 3.918 trang): "On this page", "↑ Back to top", dòng "Checked against…", nút Copy / Copied / Press Ctrl+C, breadcrumb của trang curio.
- **Tooltip:** dòng loại, "Evolves from / into", "Locked until … falls", "Requires the …", "Must-Have: get it as soon as … opens", "with luck from …", "estimate"; `relabelSide` xóa bộ nhớ đệm tooltip khi đổi ngôn ngữ.
- **Dịch:** 13 câu mới → 257 câu mỗi ngôn ngữ, phủ 257/257.
- **Tiếng Anh không đổi:** HTML của 51 trạng thái route giống bản trước (chỉ khác "1 item" đã nêu ở 13.7), và HTML tooltip của 35 curio (thường, bị khóa Keeper, cần nhẫn, Must-Have, tiến hóa, ước lượng, cửa sổ may mắn) giống từng ký tự.
- **Chưa làm (c2):** thân trang curio ("How to get it", "Stats", "Used to craft", các dòng nguồn…), cùng chữ dữ liệu (`fx`, `src`, `st`, `why`) cần dịch thật sự (Phase 3).


### 13.9 Phase 2, nhóm (c2): thân trang curio (2026-11-09)
- **Đã chuyển:** toàn bộ thân trang curio trong `app.js`: các mục (How to get it, Where it drops, From the guide book, Evolution, Relic levels, Stats, Measured in game, Used to craft, Duplicates), banner Must-Have / Scarce, dòng khóa Keeper và nhẫn, thẻ nguồn (Boss drop, Mob drop, treasure bag, chests, Trade…), cửa sổ công thức (Ingredients, "any {tag}", cách đặt nguyên liệu), tab chỉ số (Element, Damage, tên chỉ số có gợi ý), bảng và bảng điều khiển Relic (thanh cấp, điểm, độ sao, Auto-spend), thẻ Duplicates (Stacks / Doesn't stack, bậc thang bộ). Thêm `N("…")`: đánh dấu câu nằm trong bảng hằng (STATH, DMGT, SKL, SKW, STHOW, how-text), in ra bằng `T(x)`; `tmlib.scan_msgids` quét cả `N(`.
- **Dịch:** 131 câu mới (128 + 3 sót do bảng hằng) → 390 câu mỗi ngôn ngữ, phủ 390/390. Thuật ngữ mới cần bạn xem: loại sát thương (vi Chém/Xuyên/Đập/Phép thuật/Đạn bay; ru Рубящий/Колющий/Дробящий/Магический/Снаряд; pt Cortante/Perfurante/Contundente/Mágico/Projétil; es Cortante/Perforante/Contundente/Mágico/Proyectil); "Relic" → ru реликвия, pt relíquia, es reliquia (vi giữ Relic); "Duplicates" → vi Bản sao, ru Дубликаты, pt Duplicatas, es Duplicados; "Roll" giữ nguyên ở vi/pt, ru "бросок", es "tirada" khi nói về lần roll sao.
- **Tiếng Anh không đổi:** HTML `<main>` + cột bên của 51 trạng thái route giống bản trước (chỉ khác "1 item"), tooltip 35 curio giống từng ký tự, và HTML của 50 trang curio (có relic, từng loại cộng dồn, bậc thang, Must-Have, khóa Keeper / nhẫn, tiến hóa, kể cả bảng relic sau khi kéo thanh cấp) giống từng ký tự (`pagedump`, script tạm).
- **`checks/i18n.js`:** ngoài 7 trang cũ, nay vẽ thêm 11 loại trang curio (relic + kéo thanh cấp, không cộng dồn, bậc thang, Scarce, Must-Have, khóa Keeper, cần nhẫn, tiến hóa, Loot) và đòi mọi câu đã được dịch hoặc giữ tiếng Anh. Kiểm tra mới bắt ngay 3 câu sót trong bảng how-text (đã sửa).
- **Chưa làm / thấy khi làm:** số có dấu phân cách (`toLocaleString()` mặc định, ru nên là "2 100"); chữ dữ liệu của curio (`fx`, `src`, `st`, `why`) = Phase 3.

### 13.10 Phase 2, nhóm (d1): Equipment (2026-11-09)
- **Đã chuyển** (`gear.js`): danh sách Equipment (tiêu đề, lede theo Act, thanh Act, Best loadout, ba tab, ô tìm, "Show more", câu "No … unlocked yet", chân trang đếm kết quả với số nhiều đúng, khối "How the tiers are worked out" 5 đoạn), trang vũ khí / giáp (câu dẫn, How to get, Stats, Bonuses, Effects, Measured in game với mọi nhánh: swings, nodmg, nomelee, cond, dull, once, pct, grows, Tier by Act, infobox, navbox), trang bộ giáp, tooltip của vũ khí / bộ giáp, và phần "Measured in game" của trang curio. Bảng `GROLE`, `GKIND`, `GSLOT`, `GMK`, `GWHEN` dùng hàm `gT()` (đọc ra qua `T()`, câu gốc đánh dấu bằng `N()`), nên ~20 chỗ in vai trò không phải sửa.
- **Cố ý để tiếng Anh (Phase 3):** các dòng chỉ số trong tooltip / Bonuses (`+5 Attack Damage`…) vì chúng đi qua `fmt()` đặt icon theo từ tiếng Anh; tên hiệu ứng và thuộc tính (`gAttr`, `gCName`).
- **Dịch:** 187 câu mới (kể cả 10 dạng số nhiều) → 577 câu mỗi ngôn ngữ, phủ 577/577. Tên trạm chế tạo đi qua `TD()` (bản dịch chính thức của game nếu có). Thuật ngữ cần bạn xem: Playstyle (vi Lối chơi, ru Стиль игры, pt Estilo de jogo, es Estilo de juego), Loadout (Bộ trang bị / Набор / Conjunto), Toughness (vi Độ bền bỉ, ru Стойкость, pt Resistência, es Dureza), "tier list" (vi Bảng xếp hạng, ru Тир-лист, pt Lista de tiers, es Lista de tiers).
- **Tiếng Anh không đổi:** 205 mục (8 trạng thái của danh sách Equipment, tìm có / không kết quả, "show all", 76 trang vũ khí và giáp chọn theo từng nhánh của phần đo, 13 trang bộ, 16 trang curio có phần đo, 89 tooltip) giống từng ký tự sau khi bỏ nhiễu thời gian (thuộc tính `data-px`, `style`, canvas của phòng); cộng 51 route, 50 trang curio như cũ.
- **Lỗi thật tìm thấy:** ở ru và pt, danh sách Equipment hiện khung đỏ "Wiki error: ResizeObserver loop completed with undelivered notifications" (chữ dịch dài làm phòng vẽ xong lại đổi chiều cao). Thông báo này vô hại (trình duyệt giao ở khung hình sau) nên `app.js` không hiện nó nữa; `site_check.js` tải mới thẳng vào `#gear/5/ME/w` bằng tiếng Nga và đòi không có khung lỗi (đã thử trên bản chưa sửa: báo hỏng).
- **`checks/i18n.js`:** thêm các trang Equipment (3 tab, tìm có và không có kết quả, vũ khí các loại, bộ giáp, curio có phần đo) và tooltip gear; kiểm tra bắt ngay slot viết thường trong dữ liệu đo ("charm") chưa có bản dịch (đã sửa bằng `gSl`).

### 13.11 Phase 2, nhóm (d2): Build planner và Bosses (2026-11-09)
- **Đã chuyển** (`app.js`): Build planner (tiêu đề, lede theo thiết bị cảm ứng / chuột, thanh tiến độ, build khởi đầu, ô thêm / gỡ, bộ chọn và ô tìm, bảng kiểm tra, các bảng bên phải: tổng chỉ số, cấp relic, hiệu ứng, tiến hóa, thông báo liên kết cũ / mất) và Bosses (danh sách, trang Keeper, ba boss vanilla với các bước triệu hồi, trang boss phụ, bảng chỉ số boss và chú thích Hardmode, nút tiếp / trước). Câu nằm trong bảng hằng (VSUM, cột bảng chỉ số, `kind`) dùng `N()`.
- **Cố ý để tiếng Anh (Phase 3):** mô tả đòn tấn công và chỗ tìm boss phụ (`b.attacks`, `b.find`), quy tắc trong `BST`, `SUM[k].use/info`, cột "Weak to / Looting Charm" của bảng ACTS, tên chỉ số trong tổng build.
- **Dịch:** 155 câu mới (kể cả 4 dạng số nhiều) → 732 câu mỗi ngôn ngữ, phủ 732/732. "Hardmode", "Keeper", "Boss Soul" giữ nguyên ở cả bốn ngôn ngữ; tên vật phẩm vanilla trong các bước triệu hồi viết tên Anh trong ngoặc ở ru/pt/es.
- **Tiếng Anh không đổi:** 106 bản chụp `<main>` (danh sách, 14 trang Keeper + vanilla, 71 trang boss phụ, planner ở 8 build khởi đầu, bộ chọn có / không kết quả, bảng kiểm tra, ô bên, tiêu hao, relic trong build, liên kết mất) giống từng ký tự; 205 bản chụp Equipment, 51 route như cũ.
- **Lỗi thật tìm thấy:** `build.py` ghép bản dịch chính thức của game *sau* danh sách `keep`, nên ở tiếng Việt "Necklace" hiện "Vòng Cổ" trong khi các slot khác giữ tiếng Anh (D3). Nay `build.py` bỏ qua bản dịch chính thức của câu nằm trong `keep`; `checks/i18n.js` đòi mọi câu `keep` không có bản dịch trong gói (đã thử: chèn một bản dịch → báo).
- **Chưa làm / thấy khi làm:** nhãn "Tiến độ" của thanh Progress ngắt thành hai dòng ở tiếng Việt (cột nhãn hẹp); chưa sửa vì là chỉnh giao diện.

### 13.12 Phase 2, nhóm (e): Mechanics, Changes, trang mod, chân trang (2026-11-09)
- **Công cụ mới `mkwrap.py` (script tạm, không giữ trong repo):** bọc chữ tĩnh của các dòng HTML trong `mechPage`, `changesPage`, `modPage` bằng `T("…")` (cả đoạn kể cả thẻ `<b> <code> <a>` bên trong; `${expr}` đơn giản thành `{a}`, `{b}`…), phần còn lại sửa tay. Tên chỉ số in đậm một mình (`<b>Dodge Chance</b>`) cố ý giữ tiếng Anh: đó là tên game và mod in ra. Kết quả: ~370 câu của Mechanics, 45 của Changes, trang mod, chân trang "Art" (`foot.p3`, các liên kết giữ nguyên), nhãn "Back to top" / "Search results" (cập nhật khi đổi ngôn ngữ), tên nguyên liệu nghi thức qua `TD`.
- **Dịch:** 383 câu mới + 19 mô tả hiệu ứng (qua `TD`) → 1.117 câu mỗi ngôn ngữ, phủ 1.117/1.117. `trlog.js` nay đi thêm `#boss/warden`, `#gear`, `#build`, `#mods`, `#mod/Brutality`.
- **Tiếng Anh không đổi:** 68 bản chụp (Mechanics với bộ lọc nghi thức ở 6 trạng thái và "show more", Changes, danh sách mod, cả 56 trang mod, chân trang, hai aria-label) giống từng ký tự, trừ hai chỗ cố ý: `<option value="Craft">` (thêm thuộc tính `value` vì chữ hiển thị đã được dịch, bộ lọc vẫn so với tiếng Anh) và `data-lgh="foot.p3"` ở chân trang; 106 bản chụp Bosses/Build planner, 205 bản chụp Equipment, 51 route như cũ.
- **Chưa làm (Phase 3):** chữ dữ liệu: mô tả hiệu ứng curio (`fx`, `st`, `src`, `why`), mô tả mod `I[2]`, `I[3]`, tên chỉ số, các dòng chỉ số trong tooltip; nội dung Changes giữ nguyên tên mod và tên vật phẩm (không dịch).

### 13.13 Phase 3 (phần): dòng hiệu ứng curio `fx` (2026-11-10)
- `d.fx` (1.256 dòng khác nhau, 82k ký tự) vẫn là tiếng Anh trong dữ liệu (logic, regex, tìm kiếm đọc nó); mọi chỗ hiển thị đi qua `fxT(d)` = `TD(d.fx)`. Tìm kiếm cũng lập chỉ mục dòng đã dịch.
- Dịch tay theo lô ~115 dòng, tệp `idx|vi|ru|pt|es` (script tạm `fx_apply.py` gộp vào `tm/<lang>.json`, kiểm mọi con số của dòng gốc có trong bản dịch; `--dry` để xem trước). Quy ước: giữ số nguyên vẹn (dấu phẩy thập phân ở ru/pt/es), tên hiệu ứng mod, tên vật phẩm, tên trường phái phép (Aqua, Geo…) giữ tiếng Anh; ru/pt/es dùng tên hiệu ứng vanilla chính thức của game; vi giữ tên hiệu ứng tiếng Anh. Thuật ngữ: Summon → Triệu hồi/Призыв/Invocação/Invocación; minion → minion/миньон/lacaio/esbirro; cooldown → hồi/перезарядка/recarga/enfriamiento; lifesteal → hút máu/вампиризм/roubo de vida/robo de vida; trait (đặc tính mob) → đặc tính/черта/característica/rasgo.
- **Chưa làm:** `st` (2.972 dòng chỉ số), `src` (~1.480 dòng nguồn, sinh theo mẫu), `why` (~40 mẫu), tên chỉ số trong tooltip, mô tả mod `I[2]`/`I[3]`, mô tả đòn đánh của boss.

### 13.14 Phase 3 (phần): dòng nguồn `src` (2026-11-10)
- Các dòng nguồn do script vá ghép từ vài mẫu mệnh đề, nối bằng "; ". Thay vì dịch từng dòng cụ thể (607 dòng, 648 mệnh đề), `srcT` khớp từng mệnh đề với ~40 mẫu (`SRCSH`, `SRCSUF`) và nói lại bằng `T("câu có {chỗ trống}")`: tên mob/vật phẩm qua `TD`, tên địa điểm giữ nguyên, "and N more places" là dạng số nhiều (`TN`), phần trăm dùng dấu phẩy thập phân. 83 mệnh đề/dòng không mẫu nào khớp được dịch nguyên câu. Tiếng Anh không đi qua `srcT`.
- Kiểm: vòng đi-về với gói rỗng (589 mệnh đề khớp, 0 sai), `howText`/thẻ loot/dòng nguồn trong tooltip giống từng byte với bản đã commit cho cả 1.321 curio; invariant mới trong `checks/i18n.js`.
- **Chưa làm:** `st` (~2.800 dòng chỉ số ở tooltip khi rê chuột và mục "In-game tooltip"), tên địa điểm trong danh sách vẫn tiếng Anh.

### 13.15 Phase 3 (phần): trang boss (2026-11-10)
- 995 câu (attack, find, drop note, chance, SUM info, rules BST/VBI, bảng Acts) dịch tay, nối vào hiển thị bằng `TD(...)`; dữ liệu giữ tiếng Anh. Tên attack dịch (nhãn của wiki), tên boss/vật phẩm/cấu trúc/mod giữ nguyên.
- Kiểm: quét mọi route boss ở ru (996 nút chữ Anh → 196, toàn tên); 106 bản chụp Bosses/planner tiếng Anh giống từng byte; invariant mới trong `checks/i18n.js`.
- **Chưa làm:** `st` (~2.800 dòng chỉ số), `GUIDE` (sách hướng dẫn trong game, 323 đoạn / 45k ký tự), mô tả mod `I[2]`/`I[3]`, tên chỉ số trong tooltip Equipment.

