# Kế hoạch: tăng hiệu năng toàn wiki mà không đổi phần nhìn (2026-11-12)

Phân loại (CLAUDE.md "Classify first"): **kiến trúc** (nhiều công cụ, đổi cách dữ liệu được nạp), nên có kế hoạch viết ra. Giai đoạn này chỉ là **nghiên cứu và đo**; chưa sửa gì trong `build/src`. Việc thực hiện chỉ bắt đầu sau khi chủ wiki duyệt danh sách xếp hạng ở bước 3.

## 1. "Không đổi phần nhìn" nghĩa là gì (tiêu chí không thương lượng)
- **Cho phép**: tách tệp, nạp muộn, nạp theo trang, nén **không mất dữ liệu** (cùng từng điểm ảnh sau giải mã), bộ nhớ đệm, thứ tự nạp, cắt việc thừa của CPU, `content-visibility`, tự lưu phông chữ.
- **Cấm**: ảnh nén có mất, đổi phông chữ hay cách hiển thị chữ, bỏ hoặc rút ngắn animation, giảm số khung hình của Keeper, bỏ nền hay chi tiết, bỏ ngôn ngữ, đổi bố cục.
- **Cách chứng minh, mỗi đợt**: (a) `node build/shot.js '#home' '#g12' …` bản trước và bản sau với `--diff`, mọi trang chạm tới phải ra **0 điểm ảnh khác** ở 1440 và 375; (b) với ảnh đổi dạng chứa: so băm RGBA sau `decode()` của bản cũ và bản mới; (c) `bash build/check.sh` xanh; (d) bản offline `dist/Linggango_Relic_Wiki.html` vẫn mở được từ ổ đĩa; (e) bốn ngôn ngữ (vi, es, pt, ru) vẫn nạp.

## 2. Hiện trạng đo được hôm nay (nhánh `claude/fervent-volta-4697s9`, chưa nằm trên `main`)
Cách đo: máy chủ http cục bộ nén gzip mức 6 như GitHub Pages, Chromium của container (dựng hình bằng phần mềm: số tuyệt đối chỉ để so với nhau), giả lập mạng và CPU bằng CDP, một lượt mỗi hồ sơ. **Chưa lặp nhiều lần**; coi là sơ bộ.

| | Máy tính (10 Mbps, trễ 40 ms, CPU 1×) | Điện thoại (1,6 Mbps, trễ 150 ms, CPU 4×) |
|---|---|---|
| Tổng truyền tới khi xong | 11,07 MB | 11,07 MB |
| First contentful paint | 0,4 s | 3,8 s |
| DOMContentLoaded (lúc app chạy) | 7,6 s | 44,3 s |
| Largest contentful paint | 8,6 s | 45,9 s |
| Sự kiện load | 10,5 s | 59,3 s |
| Long task (số, dài nhất) | 7, 360 ms | 12, 1589 ms |
| Total blocking time | 0,96 s | 2,9 s |
| Tính lại style | 464 ms | 3979 ms |
| Heap JS | 37–69 MB | 24–48 MB |

**Cập nhật sau câu trả lời 1 của chủ wiki: "laptop là chính".** Hồ sơ chính thành **laptop trên mạng nhà tốt** (50 Mbps, trễ 20 ms), thêm bản CPU yếu gấp đôi để mô phỏng laptop văn phòng; điện thoại chỉ còn là hồ sơ **không được tệ đi** (375 px không vỡ, số không xấu hơn), không đặt mục tiêu riêng. Một lượt mỗi hồ sơ, cùng cách đo:

| | Laptop 50 Mbps, CPU 1× | Laptop 50 Mbps, CPU 2× |
|---|---|---|
| DOMContentLoaded (lúc app chạy) | 2,2 s | 2,6 s |
| Largest contentful paint | 3,2 s | 4,0 s |
| Sự kiện load | 3,2 s | 4,0 s |
| Long task (số, dài nhất) | 6, 381 ms | 6, 704 ms |
| Total blocking time | 0,94 s | 1,64 s |
| Thời gian script / tính lại style | 884 ms / 344 ms | 1190 ms / 697 ms |

Đọc bảng: trên mạng tốt, thời gian chia khoảng nửa mạng (≈1,6 s chờ `wiki_data.js` về) nửa CPU (khoảng 1 s việc của app sau khi nhận dữ liệu, gồm 6 long task), và **phần CPU tăng gần gấp đôi khi CPU yếu hơn một nửa**, còn mạng thì không. Vì vậy với laptop, hướng B (CPU) và A3 (vẽ màn đầu trước, dữ liệu sau) lên đầu cùng A1/A2; A6 (phông chữ) xuống thấp (A5, Service Worker, đã loại). LCP (3,18 s) trùng gần đúng lúc `wiki_pics.js` về xong (3,0 s) và sự kiện load: có thể phần tử lớn nhất đang đợi `wiki_pics.js`; đây là điều phải xác minh trước (mục "chưa biết").

Những điều đã chắc (đo hoặc đọc được):
1. **Màn đầu đợi toàn bộ dữ liệu.** `index.html` nạp `data.js`, `gear_data.js`, `wiki_data.js` bằng `<script defer>`; script defer chạy theo thứ tự sau khi tải xong, nên `app.js` đợi cả ba (7,7 MB gzip: wiki_data 4,39 MB, gear_data 1,93 MB, data 1,35 MB). Ngoài nền inline, không có gì được vẽ trước đó.
2. **`wiki_pics.js` (2,9 MB gzip) nằm trong sự kiện load** (`loadPics()` sau lần vẽ đầu nhưng vẫn trước `load`).
3. **Nhánh này nặng hơn bản đang chạy**: `wiki_data.js` đang live là 3,13 MB gzip (đo bằng `curl`), bản trên nhánh là 4,39 MB (gzip mức 6; mức 9 cho 4,52 MB). Chênh khoảng 1,3 MB, chủ yếu do dải hình Keeper 24 khung và màu hoàng hôn (đợt 16–20). Tối ưu phải bù lại phần này.
4. **GitHub Pages**: chỉ gzip (xin `br` vẫn trả `gzip`), `cache-control: max-age=600` cố định cho mọi tệp, không đổi được header. Tên tệp đã băm nội dung nhưng trình duyệt vẫn hỏi lại sau 10 phút.
5. **Thành phần các tệp dữ liệu** (kích thước JSON sau khi nạp): `wiki_data` — `BFIG` 3,03 MB (dải hình Keeper trang chủ), `PIMG` 1,61 MB, `SIDEB` 0,64 MB, `SIMG` 0,29 MB, `GOETY` 0,22 MB; `data.js` — `D` (curio) 1,35 MB, `IC` 0,94 MB, `UI` 0,50 MB; `gear_data` — `GE` 1,39 MB trong tệp 4,33 MB.
6. Phông chữ Google đã không giữ chân lần vẽ đầu (a11y-perf-10, giới hạn 1500 ms, đã có trong `a11y_check.js`); `build/perf.js` chỉ đo thời gian khung hình khi cuộn/hover, **chưa đo thời gian tải**.

Chưa biết (phải trả lời bằng đo, không đoán): **phần tử nào là LCP và có đợi `wiki_pics.js` không**; trang chủ thật sự cần dữ liệu nào lúc vẽ đầu; vì sao `gear_data` 4,33 MB mà `GE` chỉ 1,39 MB (phần còn lại là gì); `BFIG` có tách ra tệp ảnh riêng thì tiết kiệm bao nhiêu sau gzip; chi phí phân tích (parse) 20 MB JS trên điện thoại thật; hàm nào gây long task 360 ms; selector nào làm tính lại style 464 ms; bộ nhớ GPU của các dải hình (đợt 16 đã ghi là chưa đo).

## 3. Các hướng cần nghiên cứu
**Thứ tự ưu tiên cho laptop** (sau câu trả lời 1): 1) B2 và A3 (việc CPU của lần vẽ đầu); 2) A1 và A2 (bớt byte và bớt thứ phải phân tích trước khi vẽ); 3) B1 (tính lại style); 4) A4, B3, B4; 5) A7; 6) A6 (chỉ khi còn lợi sau khi xong các mục trên). Danh sách dưới đây giữ nguyên nhóm A/B/C cho dễ tra, không phải thứ tự làm.
**A. Tải ít hơn trước khi vẽ màn đầu** (lợi nhất: thời gian chờ nằm ở mạng)
- A1 Tách dữ liệu theo trang: `gear_data` (Equipment, Build planner, trang gear) và phần lớn `wiki_data` (trang chi tiết) không cần cho trang chủ. Mẫu có sẵn: `loadPics()` và gói ngôn ngữ nạp theo `data-lang-*`. Nghiên cứu: bản đồ "trang nào dùng biến nào" (`D, IC, UI, BFIG, PIMG, SIDEB…`), điểm cắt, cách nạp đồng bộ khi vào thẳng một đường dẫn chia sẻ. Rủi ro nhìn: thấp; rủi ro chức năng: trung bình (trang chờ dữ liệu).
- A2 **(đã đo, xem mục 9: đổi base64 sang tệp nhị phân KHÔNG tiết kiệm byte; hướng đúng là nén lại lossless)** Dải hình Keeper: hiện là base64 trong JS (cộng thêm khoảng 33% so với nhị phân). Thử xuất thành tệp WebP lossless riêng, nạp song song, `decode()` trước khi dùng. Chứng minh bằng băm điểm ảnh. Rủi ro nhìn: thấp nếu lossless.
- A3 Nạp hai pha: vẽ trang chủ chỉ với dữ liệu tối thiểu, phần còn lại khi rảnh (`requestIdleCallback`). Rủi ro: các chỗ đọc `D`, `IC` toàn cục.
- A4 **(đã đo, xem mục 9: `JSON.parse` không nhanh hơn, loại)** Hình dạng dữ liệu: `JSON.parse` so với literal JS (V8 khuyên cho đối tượng lớn), mã hoá cột, bỏ trường không dùng, bỏ trùng lặp chuỗi, xem `IC`/`UI`/`PIMG` có bị lặp không. Đo cả byte gzip và thời gian parse.
- ~~A5~~ **Đã loại (chủ wiki: "chưa cần Service Worker")**; chỉ ghi lại để khỏi bàn lại. Ý cũ: Service Worker (cache-first cho tệp tên băm, kiểm bản mới qua `/build.txt`), để vượt giới hạn `max-age=600`. Lợi lớn cho người quay lại và dùng offline; rủi ro: bản cũ bị kẹt, khó gỡ; phải có cách tự cập nhật và tự gỡ.
- A6 Tự lưu phông chữ (Silkscreen, Pixelify Sans, Be Vietnam Pro là OFL): bỏ vòng hỏi tên miền thứ ba. Chặn: container không với tới Google Fonts; cần nguồn tệp hợp pháp (repo `google/fonts` hay gói phông), và phải giữ nguyên tập con ký tự (đã có Cyrillic, Vietnamese). Rủi ro nhìn: **cao nếu sai tập con hay `font-display`**; chỉ làm nếu A–B xong mà vẫn cần.
- A7 Thứ tự và độ ưu tiên nạp: `preload`, `fetchpriority`, bỏ chờ nhau giữa các script.

**B. Bớt việc của CPU**
- B1 Tính lại style 464 ms với CSS 410 KB (≈126 KB gzip): ghi vết có thống kê selector, tìm selector đắt, thử `content-visibility:auto` + `contain-intrinsic-size` cho phần ngoài màn hình (không đổi hình khi cuộn tới). Đợt 17 đã gỡ một nguồn tính lại style (`--mx/--my` ghi lên tổ tiên); xem còn gì tương tự.
- B2 Long task 360 ms (desktop) và 1589 ms (điện thoại giả lập): lấy hồ sơ CPU, chia nhỏ phần nặng nhất của lần vẽ đầu và `decorate()`.
- B3 Trang chi tiết (3.878 trang sinh từ dữ liệu): đo thời gian mở, số nút DOM (a11y_check giữ trần 5.000 cho Mechanics), thử chỉ dựng phần thấy.
- B4 Ảnh: giải mã không chặn (`decoding=async`), bộ nhớ của dải hình 24 khung (đợt 16: +127 MB chưa đo trên điện thoại thật).
- B5 Bản offline 23,6 MB một tệp: chỉ đo thời gian mở, không đổi cách đóng gói.

**C. Không làm trong kế hoạch này**: tốc độ `check.sh` (6 phút) và CI; đổi giao diện; đổi dữ liệu game.

## 4. Nghiên cứu và tham khảo (mục tiêu: lấy kỹ thuật, không lấy mã nguồn dán vào)
Sẽ đọc và ghi vào mục "Kết quả nghiên cứu" của tệp này, mỗi nguồn kèm điều rút ra và có áp dụng được không. Địa chỉ ghi theo trí nhớ, **phải xác minh bằng đọc thật** trước khi trích:
- Tài liệu: web.dev (tối ưu LCP, `content-visibility`, `fetchpriority`, bfcache), v8.dev (chi phí JavaScript, `JSON.parse` so với literal), MDN (Service Worker, `requestIdleCallback`, `DecompressionStream`).
- Mã nguồn mở trên GitHub: Workbox (chiến lược cache của Service Worker), Pagefind (chỉ mục tìm kiếm chia mảnh nạp khi cần — mẫu cho dữ liệu lớn), `phiresky/sql.js-httpvfs` (nạp theo khoảng byte cho dữ liệu lớn tĩnh), Lighthouse / Lighthouse CI (cách họ tính và đặt ngưỡng), Squoosh (nén lossless).
- Trong repo này: `docs/NOTES.md` mục "Path lazy build" (30 Oct 2026) và các ghi chú hiệu năng cũ để khỏi làm lại; `build/README.md` mục "Motion and speed".
Quy tắc nguồn của CLAUDE.md giữ nguyên: trang đọc qua Firecrawl/Parallel chỉ là tham khảo; số liệu của chúng tôi lấy từ đo trên chính wiki.

## 5. Phương pháp đo (làm trước, để mọi so sánh sau đó có nghĩa)
- Mở rộng `build/perf.js` (không tạo tệp mới) thêm chế độ `--load`: máy chủ cục bộ nén gzip + `cache-control: max-age=600` như GitHub Pages, bốn hồ sơ (laptop 50 Mbps CPU 1× và 2×, mạng nhà chậm 10 Mbps CPU 1×, điện thoại 1,6 Mbps CPU 4× chỉ để canh không tệ đi), **5 lượt lấy trung vị**, đo lượt đầu và lượt vào lại (bộ nhớ đệm ấm, chỉ để biết, không đặt mục tiêu), ghi FCP, LCP, DCL, load, tổng byte, TBT, long task, tính lại style, heap. Tham số mạng/CPU giống bảng ở mục 2.
- Hồ sơ CPU và ghi vết (`Profiler`, `Tracing`) cho B1, B2.
- Thử từng giả thuyết trên bản sao (spike), không cam kết: mỗi spike trả lời bằng một con số trước/sau và kết quả `--diff`.

## 6. Các bước
0. **Công cụ và số gốc** (khoảng 1 giờ): chế độ `--load` của `perf.js`, lưu số gốc 5 lượt vào mục "Kết quả" bên dưới.
1. **Nghiên cứu và spike** (khoảng 2–3 giờ): trả lời các mục "chưa biết" ở mục 2, đọc nguồn ở mục 4, thử A1, A2, A4, B1, B2 trên bản sao.
2. **Báo cáo**: bảng xếp hạng (lợi ích đo được, rủi ro cho phần nhìn, công sức), kèm đề xuất mục tiêu số.
3. **Chủ wiki duyệt** danh sách và mục tiêu. Không làm gì ngoài danh sách đã duyệt.
4. **Thực hiện theo từng đợt nhỏ**, mỗi đợt: sửa nguồn, `apply_all.sh`, `--diff` 0 điểm ảnh, `check.sh`, một commit kèm NOTES. Công việc vượt ngưỡng 1 giờ nói trước bằng một dòng người đọc sẽ thấy gì đổi (CLAUDE.md "Value first").

Tiêu chí xong của **giai đoạn nghiên cứu**: số gốc 5 lượt trong tệp này; mỗi mục "chưa biết" có câu trả lời hoặc ghi rõ vì sao chưa; bảng xếp hạng có số đo của spike; không có thay đổi nào trong `build/src`.

Mục tiêu số **đề xuất** (chờ duyệt, sau khi có số gốc 5 lượt): trang chủ vẽ xong (LCP) ≤ 2 s ở laptop 50 Mbps CPU 2× (hiện 4,0 s) và ≤ 3 s ở mạng 10 Mbps CPU 1× (hiện 8,6 s); không long task nào quá 200 ms ở laptop CPU 2× (hiện dài nhất 704 ms); heap không tăng quá 10%; hồ sơ điện thoại không tệ hơn số gốc.

## 7. Rủi ro
- Tách dữ liệu có thể làm một trang đọc biến chưa nạp: cần bảng "trang dùng biến nào" và invariant `build/checks/` (mọi đường dẫn mở trực tiếp, mọi ngôn ngữ).
- Số đo trong container dựng hình bằng phần mềm không phải số của máy thật: dùng để so sánh, không để hứa con số cho người đọc; nếu có điện thoại thật thì đo thêm một lượt.
- Việc nhỏ về byte nhưng đổi pixel (nén ảnh): chỉ chấp nhận khi băm điểm ảnh sau giải mã trùng.

## 8. Câu hỏi cho chủ wiki (trả lời ngắn là đủ)
1. ~~Người đọc chính: điện thoại hay laptop?~~ **Đã trả lời: laptop là chính** (đã đổi hồ sơ đo, thứ tự ưu tiên và mục tiêu ở trên).
2. ~~Có đồng ý Service Worker không?~~ **Đã trả lời: chưa cần** (A5 loại khỏi phạm vi; lượt vào lại vẫn theo `max-age=600` của GitHub Pages).
3. Có đồng ý ảnh Keeper tách thành tệp `.webp` riêng trong `static/` (thêm tệp, ít byte hơn) thay vì nhúng trong JS không?
4. Bản offline một tệp (`dist/`) giữ nguyên cách đóng gói?

## 9. Kết quả nghiên cứu (2026-11-12, bước 0–2 đã chạy; chưa sửa gì trong `build/src`)
**Công cụ (bước 0)**: `build/perf.js --load` (xem đầu tệp): máy chủ cục bộ gzip mức 6 + `max-age=600`, bốn hồ sơ, 5 lượt lấy trung vị (điện thoại 3 lượt). Các thử nghiệm bên dưới (hồ sơ CPU, vết, vi đo, biến thể bản sao) là tệp bỏ đi, chạy trên bản sao; công thức đủ để làm lại.

**Số gốc, trung vị 5 lượt** (cold load, trang chủ 1440×900; LCP luôn là `h1.lg`, tức dòng tiêu đề):

| Hồ sơ | LCP (khoảng) | DCL | load | TBT | long task dài nhất | script | tính lại style | byte |
|---|---|---|---|---|---|---|---|---|
| Laptop 50 Mbps, CPU 1× | 3,16 s (3,08–3,27) | 2,09 s | 3,11 s | 0,93 s | 323 ms | 918 ms | 324 ms | 11,07 MB |
| Laptop 50 Mbps, CPU 2× | 4,35 s (4,12–4,60) | 2,72 s | 4,31 s | 1,97 s | 793 ms | 1445 ms | 710 ms | 11,07 MB |
| Mạng nhà 10 Mbps, CPU 1× | 8,57 s (8,46–8,61) | 7,51 s | 10,39 s | 0,92 s | 312 ms | 893 ms | 397 ms | 11,07 MB |
| Điện thoại 1,6 Mbps, CPU 4× (3 lượt) | 45,8 s | 44,2 s | 59,3 s | 2,94 s | 1471 ms | 1734 ms | 4034 ms | 11,07 MB |

**Điều đã trả lời**
1. **LCP không đợi `wiki_pics.js`**: phần tử LCP là tiêu đề do JS dựng ngay trong `DOMContentLoaded`. Nhưng `wiki_pics.js` (2,9 MB gzip) vẫn nằm trong sự kiện `load`.
2. **Thời gian sau DCL tới LCP (khoảng 1 s ở CPU 1×, 1,6 s ở CPU 2×) là việc của app**, không phải mạng. Vết chính (laptop 50 Mbps, CPU 2×): chạy script rất rẻ (app.js 106 ms, gear.js 83, data.js 23, gear_data.js 16); `FunctionCall` 1665 ms trong đó bộ xử lý DOMContentLoaded (`render`+`decorate`) 790 ms, rAF 692 ms, timer 399 ms; `UpdateLayoutTree` 871 ms; bố cục 90 ms; vẽ 190 ms; GC 140 ms.
3. **Nền hoàng hôn là phần JS lớn nhất của lần tải đầu**: hồ sơ CPU cho `skyPaint` 906 ms (CPU 2×), nhiều hơn mọi hàm khác. **Nó chạy 3 lần** (ở 778, 1168, 1360 ms): khóa bộ nhớ đệm có hộp chữ làm tròn, mà hộp chữ còn dịch vài điểm ảnh khi bố cục ổn định, nên mỗi lần lệch là một lần vẽ lại cả bức. Biến thể (laptop CPU 2×, 5 lượt): bản gốc LCP 4,06 s, TBT 1,72 s, script 1212 ms; **vẽ một lần**: script 852 ms (−360), TBT 1,40 s (−312), LCP 4,00 s (trong nhiễu); **không vẽ nền**: script 473 ms (−739), TBT 1,00 s (−716), LCP 3,66 s (−0,40 s). Dù bỏ hẳn nền, long task dài nhất vẫn ~750 ms: đó là bộ xử lý DOMContentLoaded.
4. **Trong bộ xử lý đó**: `hubHome` 442 ms, `pathMapWire` 338 ms, trong đó `toph` (đọc `offsetHeight`) 158 ms và `fit` 132 ms là bố cục bị ép đồng bộ (đọc kích thước giữa các lần ghi). Phần ghi biến `--sunb/--sunx` lên `.dsky` thay vì `.climb` chỉ bớt khoảng 38 ms (trong nhiễu): không đáng riêng.
5. **Tính lại style 871 ms (CPU 2×) gồm 208 lần**, nhưng 4 lần tính lại 1.100–1.200 phần tử chiếm khoảng 430 ms (~130 µs mỗi phần tử ở CPU 2×, đắt); sau khi tải xong còn ~25 ms mỗi 250 ms khi trang đứng yên (≈10% CPU) do các animation chạy trên luồng chính. CSS chỉ dùng 13% ở trang chủ (53 KB trên 401 KB), nhưng chưa có bằng chứng bỏ phần thừa làm nhanh hơn.
6. **DOM 4.423 phần tử, trong đó `aside#side` (ẩn, `display:none`) giữ 3.233 (73%)**, gồm `ul#idx` 3.002 nút; dựng lúc tải dù chưa ai thấy (chỉ ~21 ms ở CPU 2× nhưng tốn bộ nhớ và là việc thừa).
7. **Byte**: `wiki_data.js` 6,37 MB có 5,56 MB là ảnh nhúng base64; trang chủ chỉ cần `BFIG` (dải Keeper, 3,03 MB nguồn); `PIMG` 1,61 MB, `SIDEB` 0,64 MB, `SIMG` 0,29 MB, `GOETY`, `BPORT` chỉ dành cho trang boss. Khoảng 2,2 MB gzip của `wiki_data` và cả `gear_data` 1,93 MB gzip không cần cho trang chủ, nhưng **trang chủ hiện không khởi động nếu thiếu `gear_data`** (lỗi `GE is not defined`, `Cannot access 'GTC' before initialization`: `gear.js` đọc `GE` ở cấp cao nhất). Code đã dùng `typeof PIMG!=="undefined"` ở nhiều chỗ nên các phần ảnh của `wiki_data` dễ tách hơn.
8. **Đổi ảnh base64 sang tệp nhị phân không tiết kiệm byte truyền**: `BFIG` gzip ở dạng base64 là 2,18 MB, dạng nhị phân 2,27 MB (WebP không nén thêm được). Giả thuyết "tiết kiệm 33%" của A2 sai; giá trị duy nhất là nạp riêng.
9. **Nén lại lossless có lợi thật**: dùng WebP lossless mức nỗ lực cao nhất (Pillow `method=6`, `exact=True`), **mọi ảnh nhúng bị quét đều giống hệt từng điểm RGBA** (514 ảnh): `wiki_data` WebP 3,48→2,59 MB và PNG 0,70→0,43 MB; `wiki_pics` WebP 2,47→1,77 MB và PNG 0,45→0,29 MB; tổng tiết kiệm khoảng 2,0 MB nhị phân; riêng `BFIG` (trên đường tới trang chủ) 2,27→1,37 MB. Chưa quét: chuỗi base64 trần không có tiền tố `data:` (icon `IC`, `UI` trong `data.js`, `BPORT`).
10. **`JSON.parse` không nhanh hơn**: biên dịch và chạy literal `D` của `data.js` mất 15 ms, `JSON.parse` cùng dữ liệu 14 ms (CPU 2×). Loại A4.

**Bảng xếp hạng đề xuất** (lợi ích: đo = đã có số từ biến thể; ước = tính từ byte và vết, chưa thử):

| # | Hướng | Lợi ích cho laptop | Rủi ro cho phần nhìn | Công sức |
|---|---|---|---|---|
| 1 | **Vẽ nền đúng một lần**: bộ nhớ đệm chỉ vẽ lại khi vị trí cũ (mặt trời, mặt trăng, mây, đảo) va chạm với hộp chữ mới; sau đó cân nhắc vẽ trong Worker | đo: script −360 ms, TBT −312 ms ở CPU 2×; tối đa −739/−716 ms nếu đưa khỏi luồng chính; LCP −0,06 s đến −0,40 s | thấp cho dedupe; **nếu đưa ra Worker, nền hiện sau chữ một nhịp (vài trăm ms)**: cần chủ wiki quyết | nhỏ (dedupe), vừa (Worker) |
| 2 | **Nén lại ảnh nhúng lossless** (đổi bộ mã hoá trong `pack_audit/boss_portraits.js`; bước PNG→WebP có băm) | đo: −2,0 MB nhị phân; trên đường tới trang chủ −0,9 MB; ước: mạng 50 Mbps −0,15 s, 10 Mbps −0,7 s | **không** (băm RGBA giống hệt, kiểm lại mỗi lần chạy) | nhỏ |
| 3 | **Tách dữ liệu ra khỏi đường tới trang chủ**: `gear_data` (cần `gear.js` khởi tạo muộn) và phần ảnh của `wiki_data` (PIMG, SIDEB, SIMG...) nạp khi vào trang cần | ước: 7,7 MB gzip → ≈3,6 MB (≈2,7 MB cùng mục 2); mạng 50 Mbps −0,7 s, 10 Mbps −3,3 s | không; rủi ro chức năng (vào thẳng link chia sẻ, mọi ngôn ngữ) | vừa tới lớn |
| 4 | **Rút long task 790 ms của bộ xử lý DOMContentLoaded**: gỡ bố cục ép đồng bộ (`toph`, `fit` ≈ 290 ms), hoãn dựng `aside#side` (3.233 nút) và các phần dưới màn hình, nhường luồng giữa `render` và `decorate` | ước: long task 790 → dưới 300 ms, LCP −0,3 s; cần đo | thấp | vừa |
| 5 | **Tính lại style và việc lúc rảnh**: thống kê selector, 4 lần tính lại 1.100–1.200 phần tử, animation trên luồng chính (≈10% CPU lúc rảnh) | chưa đo biến thể; mục tiêu: −300 ms style, idle xuống dưới 3% CPU | **trung bình** (đụng animation: mỗi thay đổi phải qua `--diff` và so chuyển động) | vừa |
| 6 | Nạp `wiki_pics.js` (vòng đi của Keeper, 2,9 MB) khi rảnh hoặc khi hover đầu tiên | rút sự kiện `load`, nhường băng thông; không đổi LCP | thấp (vòng đi chỉ cần khi hover) | nhỏ |
| – | **Đã loại bằng đo**: base64→nhị phân (không bớt byte), `JSON.parse` (eval 15 ms), ghi biến lên `.dsky` (−38 ms nhiễu), Service Worker (chủ wiki). **Để sau**: tách CSS theo trang (13% dùng nhưng chưa có bằng chứng lợi), tự lưu phông chữ. | | | |

**Mục tiêu số đề xuất, chỉnh theo số đo**: làm 1+2+3+4 dự kiến đưa LCP laptop CPU 2× từ 4,35 s xuống khoảng 2,2–2,6 s (chưa thử đồng thời; ước, không hứa), mạng 10 Mbps từ 8,6 s xuống khoảng 4–5 s; mục tiêu "≤ 2 s / ≤ 3 s" ở mục 6 là mục tiêu kéo dài, chỉ đạt được nếu mục 5 và việc tải trước dải Keeper cũng chạy. Cần chủ wiki duyệt (i) danh sách và thứ tự, (ii) việc nền hiện sau chữ một nhịp (mục 1, nhánh Worker).
