# 2026-11-08: Đa ngôn ngữ cho toàn bộ wiki (Tiếng Việt, Русский, Português, Español)

Spec và plan trong một file (CLAUDE.md, Process: việc kiến trúc). **Trạng thái: bản nháp chờ chủ dự án duyệt. Chưa sửa dòng code nào.**
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
| 3.2 | **Code đọc ngược chữ tiếng Anh trong dữ liệu**: `RCV=/^(Craft\|Combine\|Infuse…)\b/` (`app.js:1527`), `/^Key requirement: locked behind/i` (`app.js:1267`), và `fmt()` (`app.js:784`) gắn icon bằng regex từ khóa tiếng Anh (`AIRG`, `app.js:778`). | Dịch dữ liệu tại chỗ sẽ làm hỏng logic và mất icon. Giữ tiếng Anh làm khóa (msgid), dịch ở bước cuối trước khi in. |
| 3.3 | **Font nhúng chỉ có Latin cơ bản** (`build/fonts/README.md`: subset U+0020–00FF). Đo bằng fontTools: Russian thiếu **66/66** chữ cái ở cả 3 font; Vietnamese thiếu **54–55/74** ký tự có dấu; Português và Español đủ. | ru và vi sẽ rơi về font hệ thống ở tiêu đề / nút, vỡ phong cách pixel. Cần quyết định về look. |
| 3.4 | Dữ liệu có ≈18,2k chuỗi duy nhất, ≈770k ký tự (đã loại id và số; trong đó ≈24k là tên class Java `GE.cls`, không cần dịch). Nhưng phần lớn chỉ là **mẫu câu khác tên**: `src` 1.483 chuỗi → 272 mẫu; `src0` 1.182 → 300; `why` 252 → 111 (đếm bằng cách thay tên riêng và số bằng ký hiệu). | Dịch mẫu một lần, sinh chuỗi bằng chương trình (mục 6, L2). |
| 3.5 | Tên vật phẩm (1.302 curio + 2.150 gear), tooltip (`fx`, `GE.tip`) và sách Patchouli (`GUIDE`, 424 chuỗi) là chữ **của mod**; game có bản dịch chính thức. Vanilla có `vi_vn`, `ru_ru`, `pt_br`, `pt_pt`, `es_es`; mẫu 1 mod (Ars Nouveau) có đủ cả năm. | Lấy từ file `lang`, không dịch bằng AI: 0 token và đúng thuật ngữ game. **Độ phủ cả 383 jar chưa đo** (bước 0.2). |
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
| L1 | **Thu hoạch bản dịch chính thức** từ vanilla + jar (`build/i18n/harvest.py`, mở rộng `pack_audit/*`): tên, hiệu ứng, tooltip, Patchouli. Chuỗi trong wiki là bản sao nguyên văn lang `en_us` ("lang templates are stored verbatim", `app.js:779`) nên tra ngược English → khóa → bản `ru_ru` / `pt_br` / `es_es` / `vi_vn`. Một câu Anh ứng nhiều khóa khác nghĩa thì ưu tiên khóa cùng namespace với vật phẩm; vẫn mơ hồ thì gắn cờ, không đoán | 0 |
| L2 | **Mẫu câu**: khai thác mẫu (`N at a N from N, N.`), dịch ≈600 mẫu, sinh ra mọi chuỗi cụ thể bằng chương trình (`build/i18n/expand.py`) với tên lấy từ L1. Kiểm bằng cách: sinh lại câu **Anh** từ mẫu phải ra đúng từng ký tự, nếu không thì chuỗi đó rớt xuống L5 | ≈ 1/10 so với dịch thẳng |
| L3 | **Glossary** (`build/i18n/glossary.json`, ≈300–500 mục: Act, Keeper, Curio, Relic, The Path, Hardmode, S/A/B/C/D, DPS, EHP, các từ cơ chế). Mỗi lô chỉ gửi những mục xuất hiện trong lô đó. Mẫu định dạng: `doNotTranslate` + `terms{en→{vi,ru,pt,es}}` (như `ory/elements`). Bạn duyệt bản vi; ru / pt / es dựa lang chính thức và Minecraft Wiki bản ngôn ngữ làm tham chiếu | thấp |
| L4 | **Bộ nhớ dịch** (`build/i18n/tm/<lang>.json`: `hash → {en, t, s, r}`; `s` = official / tpl / llm / mt / human; `r` = đã soát). Chạy lại chỉ dịch chuỗi mới hoặc đổi; sửa chữ Anh thì chuỗi cũ thành "stale" và công cụ báo, không dịch lại âm thầm | 0 khi lặp |
| L5 | **AI dịch phần còn lại**: chữ giao diện, chữ riêng của pack (boss, Mechanics, ghi chú), tooltip mod chưa có bản chính thức. Lô ≤60 chuỗi, glossary + hướng dẫn văn phong cố định đầu lô (hưởng prompt caching), trả JSON, ghi vào TM **sau mỗi lô** (dừng giữa chừng không mất) | phần chính |
| L6 | **QA tự động** (`build/i18n/qa.py` và `build/checks/i18n.js`): giữ nguyên `%s` `%d` `{x}` thẻ HTML và số; đủ thuật ngữ glossary; không sót tiếng Anh (tỷ lệ chữ Cyrillic cho ru…); độ dài hợp lý; cùng tập icon với bản Anh. Chuỗi rớt thì chạy lại riêng, không soát tay cả kho | 0 |
| L7 | **Soát người**: vi do bạn; ru / pt / es qua cộng đồng (Phase 5). Chưa soát thì menu ghi "bản dịch hỗ trợ máy" | — |

**Ước lượng token** (thô, sai số ±50%, đo lại ở pilot Phase 1): ≈750k ký tự ≈190k token Anh. Dịch thẳng mọi thứ cho 4 ngôn ngữ ≈ 1,0–1,6 triệu token output (ru tốn khoảng gấp đôi, vi ≈1,5×, pt/es ≈1,3×). Qua thang L0–L6 chỉ còn ≈360k ký tự cần AI cho mỗi ngôn ngữ, tức ≈0,5–0,7 triệu token output cho cả bốn. Con số này sẽ thay bằng số đo thật sau pilot, trước khi cam kết Phase 3–4.

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
build/src/i18n.js            t(), tn() (số nhiều), tr(), trạng thái ngôn ngữ, nạp gói; thêm vào NAMES của build.py
build/i18n/en.json           khóa giao diện + chuỗi Anh gốc (do extract.py tạo từ code, rồi giữ tay)
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
- **0.1 Font.** Kiểm font gốc Monocraft (README của họ nói "hơn 500 glyph" nhờ ghép dấu; chưa biết có Cyrillic không) và Jersey 15; vá subset hoặc chọn font OFL dự phòng có Cyrillic + dấu Việt. *Cần bạn duyệt ảnh so sánh* (CLAUDE.md: đổi look phải duyệt). Xong khi bạn gật ảnh.
- **0.2 Đo độ phủ lang chính thức.** `harvest.py` đọc vanilla + 383 jar (cần pack: README nói file server pack 877 MB trên Google Drive; phiên cloud này có tải được không **chưa kiểm**, nếu không thì chạy trên máy bạn rồi commit JSON kết quả, nhỏ). Xong khi có báo cáo % tên / tooltip / sách có bản chính thức theo từng ngôn ngữ; đây là con số quyết định khối lượng L5.
- **0.3 Gỡ phụ thuộc chữ Anh trong code.** `RCV`, "Key requirement" → cờ trong dữ liệu; `AIRG` → làm theo ngôn ngữ. Icon trong câu dịch: thử 2 cách trong một spike nhỏ (a: dịch giữ thẻ `{k:fire|…}` và QA kiểm cùng tập icon; b: bảng từ khóa theo ngôn ngữ lấy từ glossary; ru có biến cách nên b dễ sót). Xong khi `shot.js --diff` 0% đổi pixel trên các route chính và `check.sh` xanh (đây là refactor có lý do hiển thị: điều kiện của mọi phase sau).
- **0.4** Bạn chốt D1–D4.

### Phase 1: động cơ + vỏ giao diện, tiếng Việt (≈2 phiên)
Người đọc thấy: menu ngôn ngữ; đầu trang, nav, footer, hub bằng tiếng Việt. Làm: `i18n.js`, gói ui, `build.py` (gói + bản offline), `shot.js --lang`, `site_check.js` (gói tải được, mất gói → vẫn tiếng Anh), `checks/i18n.js`. **Pilot đo token**: dịch hub + một trang curio hết đường L1→L6, ghi token / 1.000 ký tự, so DeepL với Claude trên 40 chuỗi mỗi ngôn ngữ (bạn chấm bản vi). Cập nhật mục 6 bằng số thật rồi mới sang Phase 2.

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
- Độ phủ bản dịch chính thức của cả pack (mới xem 1 mod: Ars Nouveau; thử xem Goety bị 404 do sai nhánh, bỏ).
- Font Monocraft gốc có Cyrillic / dấu Việt không; font OFL dự phòng nào có đủ cả hai.
- Phiên cloud có tải được pack hay không.
- Giấy phép và chất lượng của `i18n-ai-translate`, `ai-i18n`; gói miễn phí Weblate / Crowdin; giá API hiện hành.
- Tỷ lệ token thật cho ru / vi (mục 6 là ước lượng).
- Mức nở layout của ru trên wiki.
