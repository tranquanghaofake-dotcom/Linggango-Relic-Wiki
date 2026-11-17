# Tier list Equipment: tổng hợp logic, cách đo và trạng thái

Cập nhật 2026-11-17. Tài liệu này gom mọi thứ về cách trang Equipment xếp hạng vũ khí, giáp và curio: nguyên tắc, công thức, cách đo trong game, các sự thật đã kiểm trong jar, trạng thái hiện tại và các bước còn lại. Mã nằm ở `build/src/gear.js`; cách đo ở `build/pack_audit/kubejs/server_scripts/lgw_measure.js` và `build/pack_audit/measure/`; nhật ký từng phiên ở `docs/NOTES.md`.

## 0. Tóm tắt

- **Nguyên tắc**: một món chỉ được xếp hạng khi có con số lấy từ game. Act chỉ quyết định món có mặt trong danh sách nào. Món chưa có số đứng ở hàng "?" kèm lý do riêng.
- **Trạng thái**: site (nhánh `main`, commit `cdf5407`) đã có Ranged từ số đo phát bắn và curio chia theo lối chơi. Nhánh `claude/exciting-lamport-9cwni5` có thêm số đo lại toàn bộ và mã cho Summon cùng bảng "Own attack" của Mage, nhưng chưa lên site. Mục 6 và 7 ghi chi tiết.
- **Việc tiếp theo** (mục 7): sửa lỗi bài đo minion, nhập lượt đo cuối, kiểm tra, rồi đưa lên site.

## 1. Nguyên tắc

1. **Thứ tự nguồn số liệu** (theo `CLAUDE.md`): số đo hoặc bản xuất từ game đang chạy → file của pack → đọc jar. Wiki bên ngoài chỉ để tham khảo. Số ước tính phải ghi là ước tính.
2. **Act chỉ là điều kiện**: Act quyết định món có mặt trong danh sách của Act nào, không bao giờ quyết định thứ hạng.
3. **Không có số thì không xếp**: món đó vào hàng "?", và trang của nó ghi lý do cụ thể đã đo được (ví dụ "bắn thử không gây sát thương", "chưa đo được tốc độ bắn", "súng bắn bằng phím riêng").
4. **Mỗi lỗi số liệu tìm ra phải thành một invariant** trong `build/checks/` (`gear.js`, `curio_class.js`). Invariant phải được thử đỏ (cài lại lỗi cũ thì báo lỗi) rồi mới xanh.

## 2. Điểm của từng loại

| Loại | Điểm | Nguồn số |
|---|---|---|
| Vũ khí Melee | DPS = nhát chém × tốc độ đánh × chí mạng × hút máu × tầm với, cộng sát thương theo thời gian | 3 nhát chém đo trong game |
| Vũ khí Ranged | sát thương mỗi phát × số phát mỗi giây | 3 phát bắn đo trong game |
| Vũ khí Mage, bảng chính | mức vũ khí nhân sức mạnh phép (chia tier theo phần tăng) | thuộc tính đọc trong game |
| Vũ khí Mage, bảng "Own attack" | sát thương mỗi giây của đòn riêng | bắn thử trong game (mã đã có, chưa có số) |
| Vũ khí Summon | sát thương minion mỗi giây | đo minion trong game (mã đã có, lần chạy bị lỗi) |
| Bộ giáp | hệ số sức mạnh theo lối chơi × máu hiệu dụng^k | mặc thử và nhận đòn trong game |
| Curio | hệ số sức mạnh × (máu hiệu dụng có/không đeo)^k | đeo thử trong game |

### 2.1 Melee (`gMelee`)
- **Nhát chém**: trung vị 3 nhát chém đầy lực vào lợn 100.000 máu, không giáp.
- **Vũ khí theo % máu mục tiêu** (`pct`, ví dụ Nightfall): được chém thêm vào lợn 1.000, 10.000 và 100.000 máu để khớp ra công thức "nền + % máu". Điểm lấy giá trị ở mục tiêu 1.000 máu.
- **Hai loại chí mạng tung riêng, cộng dồn trên cùng nhát** (`gCritME`):
  - Apothic: cơ bản ×1.5, cộng `crit_damage`.
  - Brutality: tỉ lệ = thuộc tính − 1; cơ bản ×1.4, cộng `critical_strike_damage`; cần lực đánh trên 90%.
- **Better Combat** xoá thời gian bất tử sau đòn, nên DPS không bị giới hạn ở 2 nhát mỗi giây.

### 2.2 Ranged (`gRng`)
- **Sát thương mỗi phát**: trung vị 3 phát vào lợn 1.000 máu (cùng chuẩn với cận chiến), mũi tên thường ở tay phụ, kéo căng hết cỡ.
- **Số tick mỗi phát**, tuỳ loại:
  - cung: số tick ít nhất để mũi tên đạt 97% tốc độ tối đa;
  - nỏ: số tick để nạp tên;
  - vũ khí dùng bằng chuột phải: thời gian hồi của item.
- **Món gây sát thương theo % máu**: nếu phát bắn ở 10.000 máu luôn cao hơn ở 1.000 máu và gấp hơn 1.5 lần, giữ thêm số 10k để ghi chú.

### 2.3 Mage
- **Bảng chính** (`GOFF.MA`): lấy giá trị lớn hơn giữa Iron's và Ars, rồi nhân với hệ số "mọi sát thương", hệ số "tầm xa" và chí mạng Apothic.
  - Iron's = (1 + spell power + trường phái tốt nhất) ÷ (1 − giảm hồi chiêu) × thời gian niệm × mana × hồi mana.
  - Ars = sát thương phép phẳng so với nhát chém điển hình của Act.
  - Tier tính theo **phần tăng** (điểm − 1).
- **Bảng "Own attack"** (tiếng Việt: "Đòn riêng"; pool `x`): mọi vũ khí Mage có đòn riêng đo được, xếp theo sát thương mỗi giây, tách hẳn khỏi bảng chính. Bạn đã chọn "một bảng riêng với tên gọi hợp lý".

### 2.4 Summon (`gMn`)
Người thử dùng vũ khí một lần. Một con zombie không AI có 1.000 máu đứng cách 4 khối, và mọi sinh vật mới xuất hiện quanh người thử bị ép nhắm vào nó. Sau 200 tick, lượng máu zombie mất đi chia cho 10 giây là điểm.

### 2.5 Bộ giáp (`gSetScore`, `gEHP`)
- **Điểm** = hệ số sức mạnh của lối chơi (`GOFF`) × máu hiệu dụng^k.
- **Hệ số k**: Melee 1, Ranged 0.7, Mage và Summon 0.6.
- **Máu hiệu dụng** đo theo đòn của Keeper kết thúc Act đó (`GHIT`: Act 0 là 10, Act XII là 50), trên nền 20 + 4 máu mỗi Act.
  - Công thức giáp của Apothic: phần nhận vào = a ÷ (a + giáp), với a = 10 khi đòn dưới 20, a = 10 + (đòn − 20) ÷ 2 khi đòn từ 20 trở lên. Độ cứng (toughness) chỉ giảm tác dụng xuyên giáp.
  - Không bao giờ dưới 13% đòn (sàn của pack) và không bao giờ quá nửa máu (trần của pack).
  - Tính thêm né tránh, kháng đẩy lùi, và phần giảm sát thương **đo được** ngoài giáp (`evr`, ví dụ Resonarium chuyển sát thương thành độ bền mất đi).

### 2.6 Curio (`gCurioScore`)
- **Điểm** = `GOFF` của lối chơi trên các thay đổi đo được × (máu hiệu dụng khi đeo ÷ khi không đeo)^k, trên bộ giáp trung vị của Act.
- **Ba bảng cho mỗi lối chơi**, mỗi bảng tự chia tier trong chính nó, và đều xếp theo điểm gộp (sức mạnh × độ bền, nên cái giá cũng được tính):
  - riêng (`gOwn`): nâng đúng một lối chơi từ 2% trở lên;
  - dùng chung (`gShared`): nâng từ hai lối chơi trở lên;
  - sống sót (`v`): các curio còn lại.
- **Các quy tắc đọc số đo của người thử 20 máu**:
  - `gHitKind`: phần thay đổi nhát chém kiếm được phân loại là cận chiến, mọi sát thương (`dmg_all`), tầm xa > 3 m (`dmg_far`), chỉ tầm xa, hoặc không tính.
    - Cận chiến: curio có thuộc tính chỉ dành cho cận chiến, mô tả nói melee damage, hoặc nói tầm gần dưới 3 m.
    - Mọi sát thương: chỉ lethality, xuyên giáp hoặc chí mạng Apothic giải thích được thay đổi, hoặc mô tả nói "damage dealt". Áp cho cận chiến, đòn bắn và phép, không áp cho minion.
    - Tầm xa > 3 m: mô tả ràng buộc theo khoảng cách. Chỉ tầm xa: mô tả chỉ nói ranged damage.
    - Không tính: không có gì giải thích.
    - Ngoại lệ có dẫn nguồn (`GHITBUFF`): Charged Redstone Piece là buff Amped cho cận chiến.
  - `GHPCT`: phạt máu viết theo % (ví dụ "−99% max health") được áp đúng tỉ lệ đó vào build thật.
  - `gTk`: số đo sát thương nhận vào bị trần nửa máu cắt (10 trên 8) thì bỏ, hoặc lấy theo các loại đòn khác nếu chúng tăng vượt trần.
  - `gAsKind`: tốc độ đánh theo % thì quy về 4.1 (tay không của người thử); cộng thẳng thì so với tốc độ của vũ khí đầu bảng; ±0.1 mà mô tả không nhắc tới tốc độ đánh là nhiễu, bỏ.
  - `GCTX`: curio phụ thuộc điều kiện mà người thử hoặc con lợn tự thoả được hiện nhưng không xếp tier. Gồm điều kiện của người thử (không giáp, đứng yên, dưới Y 0, ban ngày, đầy máu hoặc ít máu) và của mục tiêu (lợn đầy máu, không hostile, có mob khác gần, combo, đang rơi, số đọc dao động).

## 3. Cắt tier (`gTiers`)
- **Mốc so sánh**: món thứ 5 của danh sách ở Act đó; danh sách dưới 5 món thì lấy món mạnh nhất.
- **Điểm dạng hệ số nhân** (vũ khí Mage): so theo phần tăng, tức điểm − 1.
- **Ngưỡng**: S ≥ 85%, A ≥ 70%, B ≥ 55%, C ≥ 40%, còn lại là D. Dưới 25% thì rời danh sách (tìm kiếm vẫn ra).
- **Hạng Power trên trang Curios** (`curio_tiers.json`): hạng tốt nhất của curio đó trên bảng gộp `c`, ở chính Act của nó.

## 4. Sự thật đã kiểm trong jar (6.6.6hf/cf)

| Mod / hiệu ứng | Điều kiện trong code | Wiki tính |
|---|---|---|
| "Damage dealt" (Terramity, Meet Your Fight, More Artifacts, Odd Accessories) | `DamageSource.getEntity()` là người đeo | mọi đòn của người chơi |
| "Melee damage" (Terramity) | `DamageTypes.PLAYER_ATTACK` | cận chiến |
| Chthonic Shell Casing | khoảng cách tới mục tiêu > 3 m | đòn bắn và phép |
| Proximity Badge | khoảng cách < 3 m | cận chiến |
| Chí mạng Apothic | `LivingHurtEvent`, người tấn công là nguồn | cận chiến, đòn bắn, phép |
| Chí mạng Brutality | `CriticalHitEvent` (nhát chém), mặc định 1, sát thương ×1.4 | cận chiến |
| Lethality, xuyên giáp Brutality | mixin `getDamageAfterArmorAbsorb`, người chơi là nguồn | mọi đòn (phép của Iron's không bỏ qua giáp) |
| Amped (Lethality) | thực thể trực tiếp gây đòn là người chơi | cận chiến |
| Resonarium (Deeper and Darker) | mỗi mảnh trừ 1/4 sát thương, chuyển thành độ bền mất đi; độ bền 30 × (11/16/15/13) | `evr` đo được (giữ nguyên) |
| Difficulty Enhancement | huỷ mọi đòn vào người chơi cho tới khi chọn xong độ khó (`SetupGuard`) | bài đo tự chọn độ khó, không modifier |
| 6.6.6cf so với hf | chỉ khác Linggango Fixes (thêm mixin sửa rò bộ nhớ), Punchy! (client) và 5 `defaultconfigs` mặc định | số liệu giữ nguyên |

## 5. Đo trong game

### 5.1 Server
- **Server pack 6.6.6cf** từ link Drive của chủ wiki (387 jar), giải nén ở `/home/user/pack/server` (ngoài repo, mất khi container bị thu hồi). Forge 47.4.20, Java 21, `-Xmx8G`.
- **Chạy**: `cd /home/user/pack/server && tail -n0 -f console.txt | bash run.sh nogui > server.log`. Lệnh được gửi bằng cách ghi thêm dòng vào `console.txt`.
- **`server.properties`**: thế giới phẳng, offline, không sinh quái, `max-tick-time=-1`, `gamemode=survival`.
- **Sau mỗi lần khởi động** chạy `forceload add -48 -48 48 48`: không có người chơi thật thì sau 300 tick vanilla ngừng cập nhật vật thể.

### 5.2 Các lượt đo
| Lệnh (`kubejs custom_command …`) | Kế hoạch (`prep.py`) | Kết quả | Nhập bằng |
|---|---|---|---|
| `lgw_measure` | `prep.py kubejs/lgw_items.json` | thuộc tính, chém, giáp | `import.py` |
| `lgw_measure_extra` | `--extra` | vũ khí theo mục tiêu, đeo thử curio | `import.py` (đối số thứ 3), `import_curios.py` |
| `lgw_measure_third` | `--third [--guns] [--only-missed] [--mage] [--minions] [--rhp 1000]` | bắn thử, đòn riêng Mage, minion, curio chặn đòn, vũ khí quay mặt | `import_third.py LẦN_10K [LẦN_1K]` |
| `lgw_measure_test` | file tay, ví dụ `{"hurtTrace": true}` | dò từng listener của event | đọc tay |

**Thứ tự nhập**: `import.py` → `import_curios.py` → `import_third.py`. Lý do: `import.py` viết lại `gear_measure.json` từ đầu, nên phải nhập lại phát bắn sau nó.

### 5.3 Lỗi của bài đo đã sửa (mọi số trước 2026-11-17 đều mắc)
1. **Người thử rơi**: người thử đứng cao 3 khối và rơi trong lúc chờ. Nhát chém lúc đang rơi thành chí mạng ×1.5, còn mũi tên bay lọt dưới con lợn. Sửa: tắt trọng lực.
2. **Thế giới ngừng cập nhật**: vật thể không di chuyển sau 15 giây. Sửa: `forceload`.
3. **Chế độ sáng tạo**: người thử ở creative thì chặn mọi đòn. Sửa: script đặt survival.
4. **Khoá bảo vệ của Difficulty Enhancement**: người thử miễn sát thương vì chưa chọn độ khó. Sửa: script chọn độ khó, không modifier.
5. **Chí mạng của kẻ đánh thử**: con lợn có 5% chí mạng Apothic; 8 thành 12 rồi bị trần 10 cắt, cho ra 69–84 số đo "nhận thêm 25%" ngẫu nhiên. Sửa: đặt chí mạng của nó về 0. Số đo bị chặn trần giảm từ 69 xuống 8.

### 5.4 Món chuẩn để hiệu chỉnh (phải ra đúng mới tin lượt đo)
- Bow: 20 tick mỗi phát, 7–9 sát thương (vanilla: 6 cộng chí mạng ngẫu nhiên).
- Crossbow: nạp 25 tick. Trident: 10 tick, 8 sát thương.
- Kiếm kim cương: 15. Người thử không mặc gì nhận 10 trên đòn cận chiến 20 (trần nửa máu) và 20 trên các loại đòn khác.

## 6. Trạng thái hiện tại (Act XII)

| Nhóm | Trên site (`cdf5407`) | Trên nhánh, chưa lên site | Lượt đo cuối, chưa nhập |
|---|---|---|---|
| Melee | 1011 xếp / 1 chưa | đo lại: 977/1010 khớp; 7 món bị thổi ×1.5 do người thử rơi | — |
| Ranged | 71 / 73 | — | thêm 11 món có sát thương (74 món đã bắn) |
| Mage | 60 / 41 | mã bảng "Own attack" | 17/102 món có đòn riêng đo được |
| Summon | 0 / 24 | mã chấm điểm | lỗi `arm is not defined`, chưa có số |
| Giáp | 311 / 313 | Hazmat, Scuba của Mekanism được xếp (giáp 0) | — |
| Curio | 253 có hạng Power | số đo lại: 252 có hạng (sau khi sửa phân loại Asteroid Belt, Prismatic Feather, Proximity Badge); số đo bị chặn trần 69 → 8 | số chặn đòn đo lại: Ace of Iron 0/10 (cũ ghi 3/10), Opal Necklace 1/10, Ethereal Eclipse Emblem 1/10, Shinobi Sash 1/10 |

## 7. Các bước còn lại để triển khai (theo thứ tự)
1. **Sửa bài đo minion**: hàm `arm` đang khai báo bên trong `ranged()`; chuyển ra ngoài để `minions()` dùng được. Chạy lại phần minion: `prep.py --third --minions`, bỏ trống `ranged`, `grows`, `blocks`.
2. **Nhập lượt cuối**:
   - gộp phần `ranged` của lượt cuối vào hai file lượt cũ (10k và 1k): món mới chỉ có số ở 1.000 máu;
   - lấy `blocks` và `minions` từ lượt cuối và lượt minion;
   - chạy `import_third.py`.
3. **Dựng và kiểm**: `bash build/patches/apply_all.sh`; xem ảnh `#gear/12/RA/w`, `#gear/12/MA/w/attack`, `#gear/12/SU/w`, `#gear/12/a` ở 1440 và 375 px; chạy `bash build/check.sh`.
4. **Đưa lên site**: ghi NOTES, commit, đẩy lên `main`, kiểm workflow `site` xanh và `/build.txt`.
5. **Món còn chưa đo được** sau bước 2: súng bắn bằng gói phím riêng, đồ ném nổ ngoài tầm hai con lợn thấp, món cần điều kiện riêng. Mỗi nhóm cần một cách bắn riêng; trang của từng món ghi lý do.

## 8. Giới hạn và câu hỏi còn mở
- **Combo của Better Combat**: mỗi nhát trong chuỗi combo có hệ số riêng (Laser Blade: 15, 22.5, 22.5). Trung vị 3 nhát phụ thuộc vào vị trí trong chuỗi; đo đủ một vòng combo sẽ đúng hơn.
- **Hệ số k của giáp**: là số đặt tay. Với mô hình tích, tần suất trúng đòn chỉ là hằng số nên không đổi thứ hạng; k < 1 chỉ đứng được nếu độ bền có lợi ích giảm dần.
- **Lethality**: chỉ đo trên lợn 0 giáp. Hiệu quả thật phụ thuộc giáp của mục tiêu.
- **Kỹ năng chủ động của vũ khí cận chiến**: chưa tính.
- **Summonity**: `minion_damage` đo được bằng nửa con số trong tooltip; chưa đọc code để biết bên nào đúng.
- **Phù phép, reforge (Tiered), hiệu ứng bộ viết trong code**: không tính (hiệu ứng bộ được đo khi chúng chạy qua event).
