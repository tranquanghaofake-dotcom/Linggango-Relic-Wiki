# Kế hoạch: lấy toàn bộ dữ liệu wiki từ chính game (runtime export)

Viết 2026-10-22, sau v27–v28. Áp dụng cho Linggango 6.6.5b4 và mọi bản cập nhật sau.

## 1. Nguyên tắc

**Thứ bậc nguồn**, cao thắng thấp. Mỗi con số trên wiki mang nhãn nguồn của nó:

| Hạng | Nguồn | Khi nào dùng | Nhãn trên wiki |
|---|---|---|---|
| A | **Runtime export**: script KubeJS chạy trong game hỏi chính game | Mọi con số game tính ra: attribute, máu boss, recipe sau KubeJS, tag, tooltip đã điền số, tỉ lệ rơi | `game` |
| B | **File của pack**: config `.toml`, datapack và script `kubejs/`, quest FTB | Ý đồ thiết kế, giá trị config, quest/thứ tự boss, nghi lễ, guide book | `config` |
| C | **Đọc jar tĩnh** (pipeline hiện tại: `gear/`, `pack_audit/`, mjvm) | Chỉ khi A và B không có: model/texture cho icon, hằng số trong code | `code` |
| D | **Nguồn ngoài**: minecraft-guides.com, wiki mod, saloeater | Gợi ý để biết cần đo cái gì; **không bao giờ** là con số hiển thị | `ref` (chỉ trong ghi chú) |

**Quy tắc vận hành**
1. Mỗi lần xuất (export) ghi kèm meta: phiên bản pack, danh sách mod và phiên bản, thời điểm. Build từ chối trộn hai lần xuất khác phiên bản.
2. Mỗi lần nhập in một **báo cáo khác biệt** (file `build/changes.csv` đã có): item nào đổi, đổi gì, từ nguồn nào sang nguồn nào. Không thay số một cách im lặng.
3. Trước khi dùng một lần xuất, kiểm tra **độ tươi**: đối chiếu với file của pack. Đây là cách đã phát hiện bản `gear_dump.json` trong server pack bị cũ (chỉ có 48/1471 modifier của các file `gear_authored_profiles_*`).
4. `check.js` có thêm bất biến: tỉ lệ dữ liệu hạng A không được giảm; số chỗ "?"/"…" trong curio không được tăng.

## 2. Hiện trạng và lỗ hổng theo từng mảng

| Mảng | Nguồn hiện tại | Lỗ hổng đo được | Đã có runtime? |
|---|---|---|---|
| Vũ khí melee, armor | Dump runtime (v27) + đọc jar | Item mà dump không phủ | ✅ 1760 item |
| Staff, cung, súng, roi summon (attribute) | Đọc jar | ~190 item không có trong dump | ⏳ `dump_gear_all.js` (v28) |
| Sát thương cung/súng/phép, effect | Ước lượng theo Act | Toàn bộ | ⏳ `dmg_logger` + 71 món (v28) |
| Curio: attribute | `data.js` viết tay + đọc jar | Chưa kiểm chứng bằng runtime | ❌ |
| Curio: dòng hiệu ứng | Chuỗi lang chưa điền số | **175/1328 curio còn "?"/"…"** | ❌ |
| Boss: máu, giáp, sát thương | `boss_stats.py` từ `entitybalance.json` + jar | Đòn đặc biệt; phase; hệ số độ khó | ❌ |
| Rơi đồ | Loot table tĩnh (`drops.py`) | Global loot modifier, treasure bag, tỉ lệ thật | ❌ |
| Recipe | Jar + script KubeJS đọc tĩnh | Recipe bị KubeJS sửa/xoá có thể lệch | ❌ (pack có sẵn `dump_recipe_conflicts.js`) |
| Tag, gate theo Act | Đọc file tag tĩnh | Tag lồng nhau, tag do script thêm | ❌ |
| Tên hiển thị | Lang tĩnh + `kubejs/client_scripts/lang.js` | Đã đối chiếu tay (v13) | ❌ |
| Cơ chế (mechanics) | Comment trong `linggango_tweaks-common.toml` | Chưa đo thực tế | ❌ |
| Nghi lễ, guide book, quest | File của pack | Ổn | Hạng B là đủ |
| Icon, ảnh render | Model/texture từ jar | Ổn | Hạng C là đủ |

## 3. Bộ export: một lệnh xuất hết, một lệnh cho client

Tất cả nằm trong `build/pack_audit/kubejs/` (thư mục đã có từ v28). Người chơi chép vào `kubejs/` của instance:
- `/kubejs custom_command lgw_export` (phía server) ghi ra `kubejs/lgw_export/*.json`.
- Script client tự chạy một lần khi vào thế giới, ghi tooltip và tên ra `kubejs/lgw_export/client_*.json`.
- Nén thư mục `kubejs/lgw_export/` gửi lên là xong.

| Script | Chạy ở | Lấy gì | Cách làm | Thay cho |
|---|---|---|---|---|
| `meta` | server | Phiên bản pack, mod và phiên bản, thời điểm | `Platform.mods`, file `manifest.json` của instance | — |
| `gear` (= `dump_gear_all`) | server | Modifier của mọi item theo slot | `ItemStack.getAttributeModifiers(slot)` | Đọc jar |
| `curios` | server | Modifier curio theo slot | `CuriosApi.getAttributeModifiers(slotContext, uuid, stack)` cho từng slot hợp lệ của item | Attribute curio trong `data.js` |
| `tooltips` | **client** | Tooltip đầy đủ, **đã điền số**, cho mọi curio và vũ khí | `stack.getTooltipLines(player, TooltipFlag.ADVANCED)`, giữ mã màu; giả lập Shift nếu mod giấu dòng sau Shift | 175 dòng "?"/"…" |
| `names` | client | Tên hiển thị item và entity | `stack.getHoverName()`, `EntityType.getDescription()` | Lang tĩnh |
| `recipes` | server | Mọi recipe sau KubeJS: loại, nguyên liệu (tag đã giải), kết quả | `server.getRecipeManager().getRecipes()` | Recipe đọc tĩnh |
| `tags` | server | Item tag, gồm `linggango_tweaks:gated/*`, `forge:*_tools` | `ForgeRegistries.ITEMS.tags()` | Tag tĩnh, gate |
| `bosses` | server | Máu, giáp, toughness, attack damage, tốc độ **sau khi spawn** (entitybalance và tweak đã áp) | Spawn từng boss ở vùng thử, đọc `getAttributeValue`, rồi `discard()` | `boss_stats.py` |
| `loot` | server | Tỉ lệ rơi thực nghiệm, gồm global loot modifier và treasure bag | Roll mỗi loot table N = 1000 lần bằng `LootParams` có killer là người chơi; mở treasure bag bằng cách roll loot table của nó | `drops.py` |
| `dmg_logger` (v28) | server | Sát thương thật mỗi đòn của vũ khí; **mở rộng**: sát thương người chơi nhận theo từng boss và kiểu đòn | `LivingDamageEvent` | Ước lượng; `GHIT` lấy từ `entitybalance` |

**Điểm cần thử trước (spike), vì có thể không làm được trọn:**
- **Relics:** chỉ số curio thay đổi theo cấp relic (lưu trong NBT). Cần dump ở cấp 0 và cấp tối đa, bằng cách đặt NBT cấp qua API của Relics. Phải đọc API trước.
- **Tooltip:** một số mod chỉ dựng tooltip khi có màn hình hoặc phím Shift. Kiểm tra trên 5 curio mẫu trước khi chạy hết.
- **Spawn boss:** một số boss dựng đấu trường hoặc kích hoạt sự kiện khi spawn. Chạy trong thế giới superflat riêng, có danh sách loại trừ, và đọc chỉ số trong tick đầu rồi xoá ngay.
- **Loot:** loot table của boss có thể đòi `DamageSource` từ người chơi; GLM có điều kiện riêng (cấp L2 Hostility, độ khó). Ghi lại điều kiện đã dùng cạnh tỉ lệ.
- **Rhino (KubeJS 6):** chỉ dùng `var`/`forEach`/object thường (bài học v28).

## 4. Phía wiki: nhập dữ liệu

1. `build/patches/runtime/`: ảnh chụp các lần xuất, mỗi mảng một file JSON, có `_meta`. Đây là nguồn được commit; `.zip` thô không commit.
2. `patches/runtime_import.py`: đọc `.zip` người dùng gửi, kiểm tra meta và độ tươi, chuẩn hoá về dạng gọn (mỗi item một dòng như `gear_runtime.json`), rồi in báo cáo khác biệt.
3. Mỗi mảng có một stage riêng, đặt **sau** các stage tĩnh và ghi đè theo thứ bậc A > B > C:
   - gear: `gear_runtime` (đã có), mở rộng cho `gear_dump_all` và sát thương đo được (`gEstScore` dùng DPS đo thay cho ước lượng theo Act khi có).
   - curio: `curio_runtime`, điền attribute và dòng tooltip đã có số. `data.js` vẫn là nguồn viết tay cho phần chữ; số lấy từ export.
   - boss: `boss_runtime` thay phần số trong `boss_stats.py`; quest book vẫn quyết thứ tự.
   - loot: `loot_runtime` cho tỉ lệ rơi.
   - recipe và tag: `recipe_runtime`, `tag_runtime`. Gate theo Act đọc tag runtime.
4. Mỗi con số hiển thị kèm nhãn nguồn (`game` / `config` / `code`), dùng lại cơ chế `tg` và nhãn "Read from the mod" đã có.
5. Code đọc jar không xoá ngay: giữ làm phương án dự phòng một phiên bản. Sau đó xoá những đường đã có runtime thay hoàn toàn (`runtime_bonus` trong `gear_data.py`, các overlay trong `gear_stats.json`).

## 5. Lộ trình

| Giai đoạn | Nội dung | Phần việc của anh | Kiểm tra hoàn thành |
|---|---|---|---|
| P0 ✅ | Melee, armor từ `dump_gear` | Xong | 1760 item, 4955/5048 modifier khớp config |
| **P1** | `gear_dump_all` + `curios` + `tooltips` + `meta` | Chép script, 1 lệnh, vào thế giới 1 lần (~10 phút) | Số curio còn "?"/"…" từ 175 về gần 0; ~190 staff/cung có attribute |
| P2 | `recipes` + `tags` + `names` | Cùng lần xuất P1 (gộp vào `lgw_export`) | Báo cáo khác biệt recipe/gate; giải thích được từng chỗ lệch |
| P3 | `bosses` + `dmg_logger` chiều nhận sát thương | Đánh mỗi Keeper boss vài phút (hoặc chỉ đứng chịu đòn) | Trang boss có máu/giáp thật và đòn đặc biệt; `GHIT` lấy từ đo |
| P4 | `loot` | 1 lệnh (chạy lâu: N × số bảng) | Tỉ lệ rơi gồm GLM; so với `drops.py` |
| P5 | Đo vũ khí Ranged/Mage/Summon (71 món, v28) | ~30–40 phút bắn hình nộm | Tier Ranged/Mage/Summon dùng DPS đo được |
| P6 | Dọn dẹp | — | Xoá đường đọc jar đã bị thay; tài liệu cập nhật |

Mỗi lần pack cập nhật: chạy lại `lgw_export` (P1–P4 gộp), gửi file zip; P5 chỉ đo lại những vũ khí bị đổi.

## 6. Nguồn ngoài: minecraft-guides.com (đánh giá 2026-10-22)

- **Độ phủ:** 310 trang mod, trong đó **55/446** mod của pack. Thiếu các mod cốt lõi: Armageddon, Iron's Spellbooks, Cataclysm, Relics, Goety, L2, Brutality.
- **Loại số liệu:** giá trị **mặc định của mod**, không phải của pack. Ví dụ: Cocktail Cutlass trên trang là 7 sát thương; game Linggango áp 12. Slicer's Dice trên trang ghi 17% / +100%, và config của pack cũng đang là 0.1667 / ×2. Lần này trùng là do pack giữ nguyên mặc định, không phải vì trang kia nói đúng về pack.
- **Văn bản:** dòng "tooltip" trên trang là văn bản dựng lại, không phải tooltip thật của game (ví dụ "Craft from 6 Gold Ingots…"); phần mô tả viết theo lối văn xuôi, có chỗ suy diễn.
- **Kết luận:** dùng làm **danh sách gợi ý** (biết item có hiệu ứng gì để đo hoặc tìm trong config), **không** chép số và không chép văn bản (bản quyền nội dung của họ). Mọi con số trên wiki phải đến từ nguồn A hoặc B.

## 7. Rủi ro

| Rủi ro | Ảnh hưởng | Giảm thiểu |
|---|---|---|
| Lần xuất cũ hoặc lệch phiên bản | Số sai hàng loạt (đã xảy ra với dump trong server pack) | Meta + kiểm tra độ tươi bắt buộc khi nhập |
| Script không chạy trên KubeJS 6 | Mất một lượt của anh | Spike 5 item mẫu; script ghi lỗi vào log; tách lệnh theo mảng |
| Chỉ số phụ thuộc NBT (Relics, Blood Magic, Tetra) | Dump mặc định không đại diện | Đánh dấu "phụ thuộc cấp"; dump nhiều mức nếu API cho phép |
| Boss spawn gây sự kiện | Crash hoặc phá thế giới | Thế giới thử riêng, danh sách loại trừ, xoá ngay sau khi đọc |
| Đo tay có sai số (crit ngẫu nhiên, kéo cung chưa căng) | DPS lệch 10–20% | Trung vị trên ≥ 5 phát; ghi số phát; đo lại món bất thường |
| Pack có config phía client khác server | Tooltip lệch | Chạy single player trên đúng instance chơi |
