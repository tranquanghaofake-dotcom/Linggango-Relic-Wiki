# Đa ngôn ngữ, đợt 2: dịch hết (trừ danh từ riêng), nâng chất lượng, cấu trúc dễ cập nhật (2026-11-11)

Tiếp theo `2026-11-08-multilingual.md` (§13.x là nhật ký). Bạn giao 4 việc: (1) làm tiếp, (2) dịch tất cả chỉ chừa danh từ riêng, (3) nâng độ hay và độ chính xác của mọi bản dịch, (4) bố cục để các lần cập nhật sau dễ. Đây là kế hoạch + khảo sát; chưa sửa code.

## 1. Hiện trạng đã đo (ngày 2026-11-11, bản build của `24739e7`)
- Mỗi ngôn ngữ có khoảng 5.650 câu trong `build/i18n/tm/<lang>.json` (≈1 MB mỗi file, một khối, khóa là hash của câu Anh) + bản dịch chính thức của game/mod (`official/`: ru 1.732 tên + 3.495 câu, es 807 + 1.895, pt 713 + 1.663, vi 327 + 663).
- Chữ giao diện, văn xuôi dữ liệu (fx, src, boss, sách, gear, 1.658 dòng tooltip, relic) đã dịch; quét ru trên các trang chính chỉ còn tên riêng.
- **Còn tiếng Anh theo quyết định cũ (D3 và "giữ tên")**, đây là phần việc (2):
  - 1.014 dòng tooltip kiểu "Tên: giá trị" (791 nhãn khác nhau, 280 giá trị khác nhau; 156 giá trị không phải số, ví dụ "no", "(game-rule default)", "Cooldown 16 seconds ~ 12 seconds (at relic level 0; grows as the relic levels up)").
  - Tên vật phẩm: 1.304 curio + 2.150 gear = 3.454 tên. Đã dịch (do bản chính thức): ru 1.731 (50%), es 824 (24%), pt 719 (21%), vi 336 (10%).
  - 95 tên ability của relic, ≈98 tiêu đề trong tooltip, tên địa điểm trong danh sách, tên boss (tên boss là danh từ riêng, giữ).
- Cấu trúc hiện tại làm cập nhật khó: file một khối, diff khó đọc; không có công cụ trong repo để **liệt kê chữ mới chưa dịch** (tôi dùng script nằm ngoài repo, mất khi hết phiên); không có kiểm thuật ngữ; một câu Anh chỉ có một bản dịch bất kể ngữ cảnh; không phân biệt bản dịch "máy / chính thức / người đã duyệt".

## 2. Khảo sát (nguồn mở, đọc ngày 2026-11-11)
| Nguồn | Điều đọc được | Dùng vào |
|---|---|---|
| Weblate, docs `user/glossary` và `user/checks` (đã đọc đoạn về cờ; **chưa đọc hết** danh sách check) | Glossary có cờ `read-only` (không dịch), `forbidden` (cấm bản dịch này), `terminology`; check `Placeholders` nhận regex | `glossary.json` v2 với 3 loại đó; `qa.py` có check đặt tên theo Weblate |
| GEMBA-MQM (Kocmi & Federmann 2023) và MQM-APE (github `coldmist-lu/mqm_ape`) | LLM tự gán lỗi theo loại + mức nặng, không cần bản mẫu; MQM-APE lọc lỗi "không ảnh hưởng" bằng cách tự sửa rồi so | Quy trình duyệt của tôi (B3): chấm Accuracy / Terminology / Fluency / Style, mức Minor / Major / Critical; chỉ sửa khi Major trở lên hoặc lỗi thuật ngữ |
| Minecraft Wiki `Minecraft_Wiki:Translations` | Chỉ quy ước đặt tên trang bản dịch; **không có quy tắc về dịch tên vật phẩm** (đọc, không thấy) | Không có tiền lệ để bám: quyết định tên là của bạn (mục 4) |
| gettext (msgctxt, msgmerge/fuzzy), i18next, Fluent: kiến thức chung, **chưa mở tài liệu trong phiên này** | Bối cảnh đi kèm khóa; khi câu nguồn đổi thì bản dịch cũ chuyển thành "cần xem lại" thay vì mất | `ctx` tùy chọn và cờ `needs-review` trong TM; xuất/nhập `.po` cho người duyệt (B5) |
| Spike mạng (đo bằng curl/pip) | Tải được mô hình từ Hugging Face (206 khi lấy một phần), PyPI, chỉ mục torch CPU và `ctranslate2` đều thông; máy 4 CPU, 29 GB trống, chưa có torch/transformers/sacrebleu | Dịch ngược cục bộ bằng opus-mt để xếp hạng rủi ro (B2); **chưa chạy thử**, có điều kiện go/no-go ở dưới |

Không dùng được hoặc chưa kiểm: DeepL/Google (không có khóa), COMET-QE (mô hình ≈2 GB, CPU quá chậm cho 22 nghìn câu; chưa thử), LanguageTool (cần Java server; Java có sẵn, bản ngữ pháp ru/pt/es chưa thử; để B2 làm kênh phụ nếu thời gian cho phép).

## 3. Công việc
Thứ tự: **A (nền) → B1, B6 (đo rẻ) → C1 (cơ học) → B2, B3 (duyệt) → C2–C4 (theo quyết định) → tài liệu**. Mỗi gói là một commit có mục NOTES, `check.sh` xanh trước khi push; tiếng Anh phải giống hệt (dump so với bản đã commit, như các đợt trước).

### A. Bố cục dễ cập nhật (việc 4, kèm việc 1: `docs/I18N.md`)
- A1. Đưa công cụ vào repo `build/i18n/tools/`: `todo.js` (đọc `dist/` và liệt kê mọi chữ hiển thị chưa có bản dịch, theo miền và ngôn ngữ), `merge.py` (nhận lô `idx|vi|ru|pt|es`, kiểm số/placeholder, ghi TM), `status.py` (phủ theo miền/ngôn ngữ; câu mồ côi trong TM; câu Anh đổi so với lần trước), `qa.py` (B1). Hôm nay các script này nằm ngoài repo.
- A2. Tách TM theo miền: `tm/<lang>/<miền>.json` với miền = `ui`, `names`, `fx`, `src`, `st`, `boss`, `gear`, `guide`, `relic`, `cfg`. Mỗi mục có `s` (`llm` / `official` / `human`), `r` (`ok` / `needs-review`), `c` (ghi chú ngữ cảnh, tùy chọn); ghi sắp xếp ổn định để diff đọc được. **Bằng chứng**: gói `window.I18N` sinh ra trước và sau di chuyển giống từng byte.
- A3. (hoãn, không làm: chỉ gộp file, không đổi gì trên trang; quy tắc "refactor công cụ chờ một sửa chữa thấy được" trong CLAUDE.md) `glossary.json` v2: gộp `keep.json` vào (`names`: không dịch; `terms`: theo ngôn ngữ; `forbidden`: biến thể cấm). Build đọc một nơi.
- A4. `docs/I18N.md`: vòng 5 lệnh khi gói mod cập nhật (build → `todo` → dịch lô → `merge` → `status` + check), cách thêm ngôn ngữ, cách sửa một bản dịch, cách người bản ngữ duyệt.
- A5. (xong dạng CSV thay vì .po: `tools/review.py export/import`, người duyệt dùng Excel hoặc Google Sheets; xem NOTES 2026-11-11) Xuất/nhập `.po` theo miền (thư viện `polib` hoặc tự viết): người duyệt mở bằng Poedit/Weblate, nhập lại gắn `s:"human"`. Round-trip không đổi gì là bằng chứng.

### B. Độ hay và chính xác (việc 3)
Nguyên tắc: **đo trước, sửa sau; duyệt có mẫu**, không đọc lại 22 nghìn câu một cách mù quáng.
- B1. `qa.py` (xác định, không tốn token): placeholder/số/thẻ (đã có trong build), thuật ngữ glossary và biến thể cấm, cùng câu mẫu mà dịch khác nhau ("Reduces soul cost of X spells by …%"), chữ Latin lẫn trong câu ru, từ tiếng Anh sót trong vi/pt/es ngoài danh sách tên, tỷ lệ độ dài lệch, dấu cách trước `%` (es), dấu thập phân, ngoặc kép theo ngôn ngữ, khoảng trắng đôi, chữ hoa đầu câu. Mỗi lỗi thật tìm ra thành bất biến trong `build/checks/i18n.js`.
- B6. So bản của tôi với bản chính thức khi **cùng câu Anh** có cả hai (TM luôn thắng `official/` hiện nay): mọi chỗ khác nhau là dấu hiệu mạnh nhất vì bản chính thức đã qua cộng đồng. Làm sớm, rẻ, danh sách cụ thể.
- B2. (đã chạy thử, no-go: opus-mt-ru-en dịch ngược kém hơn bản dịch được kiểm (120 chuỗi trong 12 s, 25 chuỗi điểm thấp nhất không có lỗi thật, một chuỗi chỉ là câu tiếng Anh mơ hồ); xem NOTES) Dịch ngược bằng opus-mt chạy cục bộ rồi so với câu Anh (chrF) để xếp hạng rủi ro. **Go/no-go trong 45 phút**: nếu không cài/ tải được, hoặc điểm không tách được câu sai đã biết (lấy 40 lỗi đã sửa trong phiên trước làm mẫu thử) thì bỏ, dùng B1+B3.
- B3. Tôi duyệt theo MQM-lite các nhóm: toàn bộ `ui` (1.157 câu × 4), mọi chuỗi ≤3 từ (hay mơ hồ và dùng lại nhiều nơi), mọi mục B1/B2/B6 gắn cờ, và **mẫu ngẫu nhiên 5% mỗi miền mỗi ngôn ngữ** để ước tỷ lệ lỗi; miền nào quá 5% lỗi Major thì duyệt hết miền đó. Ước lượng (chưa đo): ≈5.000 mục ×4 ≈ 1,5 triệu token, chia nhiều cửa sổ 5 giờ.
- B4. Kiểm mơ hồ ngữ cảnh: chuỗi ngắn giống nhau nhưng nghĩa khác (Speed thuộc tính / hiệu ứng, Charm vật phẩm / ô, Block…). Chỉ thêm cơ chế `ctx` nếu thật sự tìm thấy ≥10 chỗ sai; nếu không thì thôi (đổi `T()` ở nhiều nơi là rủi ro).
- B5. Đường duyệt của người bản ngữ (A5) và nhãn trạng thái ngôn ngữ ("đã duyệt" / "dịch máy") trong menu: **thay đổi giao diện nhỏ, cần bạn duyệt**.

### C. Dịch hết, chừa danh từ riêng (việc 2)
- C0. Bảng quy tắc "danh từ riêng" (vào glossary `names`): tên mod/pack, tên boss, tên NPC/nhân vật, tên Act riêng, tên vật phẩm **duy nhất có tên riêng**. Còn lại là danh từ chung và được dịch. Cần bạn chốt phần tên vật phẩm (mục 4).
- C1. 1.014 dòng "Tên: giá trị": từ điển nhãn (791) + giá trị (≈60 mẫu: yes/no, "(game-rule default)", "N seconds", "(at relic level 0; grows as the relic levels up)"), ghép bằng một hàm `cfgT` như `gAL`. Cơ học, xong trong một phiên.
- C2. 95 tên ability relic + ≈98 tiêu đề tooltip.
- C3 (xong 2026-11-11, xem NOTES). Tên vật phẩm/gear/địa điểm chưa có bản chính thức: còn lại 1.723 (ru), 2.630 (es), 2.735 (pt), 3.118 (vi) tên cần dịch (3.454 trừ số đã có bản chính thức ở mục 1), dịch theo glossary (từ như Charm, Ring, Belt đã có), bản chính thức luôn thắng.
- C4. vi: dùng `vi_vn` chính thức của game khi có (hiện có 327 tên), dịch phần còn lại.
- **Tiêu chí xong**: quét `leftover.js` (đưa vào `tools/`) trên mọi loại trang cho từng ngôn ngữ chỉ còn tên trong `glossary.names`; tìm kiếm bằng tên Anh và tên dịch đều ra cùng một trang; tiếng Anh giống hệt.

## 4. Chỗ tôi không đồng ý hoặc cần bạn chốt
1. **Dịch cả tên vật phẩm làm người chơi client tiếng Anh khó tra** (họ thấy "Wrinkled Dollar" trong game, wiki viết bản dịch). Đây là lý do D3 cũ giữ tên Anh. Đề xuất: dịch tên là danh từ chung, nhưng **luôn hiện tên Anh bên cạnh (một dòng phụ dưới tiêu đề trang và trong tooltip) và luôn tìm được bằng tên Anh**. Dòng phụ là một thay đổi nhỏ của giao diện nên cần bạn đồng ý.
2. "Danh từ riêng" cần ranh giới: "Wrinkled Dollar" là tên riêng hay cụm danh từ? Tôi đề xuất coi tên độc nhất của vật phẩm mod là tên riêng nếu bản chính thức của mod không dịch nó, và chỉ dịch tên có nghĩa chung ("Iron Sword", "Leather Belt").
3. Chất lượng không thể hứa là "bản ngữ" nếu không có người bản ngữ duyệt. B3 đo và giảm lỗi, không thay được người đọc thật.
4. Tên đã dịch bằng máy cho vật phẩm mod rất dễ nghe gượng hơn tên chính thức; vì vậy bản chính thức luôn thắng và mỗi tên máy dịch gắn `s:"llm"` để lọc và duyệt sau.

## 5. Rủi ro và cách giảm
- Di chuyển TM sai làm mất chữ: bằng chứng gói trước/sau giống từng byte (A2).
- Dịch hàng nghìn tên làm tràn layout ở 375 px (ru dài): chụp `shot.js --width 375` các trang danh sách mỗi ngôn ngữ.
- Tên máy dịch sai nghĩa mod: gắn cờ, duyệt mẫu 5%, người dùng báo lỗi qua đường B5.
- `check.sh` ≈ 6 phút và máy 4 CPU: không chạy song song với dịch ngược (B2).
- Ngân sách: giới hạn 5 giờ của tài khoản; mỗi lô ghi TM ngay nên dừng giữa chừng vẫn chạy tiếp được.

## 6. Cách làm việc
Không subagent/workflow (bạn chưa yêu cầu). Một nhóm tệp một commit; NOTES mỗi phiên; lỗi thật thành bất biến. Không đụng tệp ngoài phạm vi; thấy gì khác chỉ ghi lại.
