# Tier list Equipment: tổng hợp logic, cách đo và trạng thái

Cập nhật 2026-11-17. Tài liệu này gom mọi thứ về cách trang Equipment xếp hạng vũ khí, giáp và curio: nguyên tắc, công thức, cách đo trong game, các sự thật đã kiểm trong jar, trạng thái hiện tại và các bước còn lại. Mã nằm ở `build/src/gear.js`; cách đo ở `build/pack_audit/kubejs/server_scripts/lgw_measure.js` và `build/pack_audit/measure/`; nhật ký từng phiên ở `docs/NOTES.md`.

## 0. Tóm tắt

- **Nguyên tắc**: một món chỉ được xếp hạng khi có con số lấy từ game, hoặc một hằng số đọc trong code khi bài đo không tạo được điều kiện (ghi rõ trên trang). Act chỉ quyết định món có mặt trong danh sách nào. Món chưa có số đứng ở hàng "?" kèm lý do riêng.
- **Trạng thái** (sau đợt 2026-11-17, mục 6):
  - toàn bộ vũ khí, giáp và curio được đo lại trên người thử đã sửa;
  - Ranged có 76 món, Mage có bảng "Own attack", giáp 313/313 bộ được xếp;
  - Summon có số từ đợt "tiếp 7": 12 staff có tier, roi có bảng "Whips" riêng (mục 2.4, 6).
  - Ranged: 49 món mới có số (súng Terramity, đồ ném Brutality, Gatling, Raygun, Meka-Gun...); còn 23 món chưa xếp ở Act XII (mục 6).
- **Việc còn lại**: mục 7.

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
| Vũ khí Mage, bảng "Own attack" | sát thương mỗi giây của đòn riêng | bắn thử trong game |
| Vũ khí Summon | sát thương minion mỗi giây | đo minion trong game |
| Roi Summon, bảng "Whips" | sát thương mỗi giây của chính cây roi | config của pack (Summonity), nhát chém đo trong game (Better Combat) |
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
- **Sát thương mỗi phát**: trung vị 3 phát vào lợn 1.000 máu (cùng chuẩn với cận chiến), kéo căng hết cỡ. Đạn để trong túi từ ô 9 (mũi tên, khoai tây, phi tiêu, đạn Soulslike, thanh thép IE, đá Undergarden, đạn và vỏ đạn Terramity), không ở tay phụ: súng Terramity chỉ bắn khi tay phụ trống.
- **Phát đầu bị phồng**: phát đầu cao hơn 3 lần các phát sau thì bỏ (đạn bắn trễ của lần trước rơi vào). Súng có các phát lệch nhau quá 3 lần, hoặc chỉ trúng 1/3 phát (shotgun tản đạn), không xếp.
- **Số tick mỗi phát**, tuỳ loại:
  - cung: số tick ít nhất để mũi tên đạt 97% tốc độ tối đa;
  - nỏ: số tick để nạp tên;
  - vũ khí dùng bằng chuột phải: thời gian hồi của item;
  - đồ ném Brutality: ném qua hàm xử lý nhát vung (`handleCooldownAndSound`, đúng đường gói tin chuột trái), hồi 20 ÷ tốc độ đánh;
  - vũ khí không có thời gian hồi: dùng lại mỗi 4 tick (nhịp lặp khi giữ chuột phải) trong 40 tick, lấy tổng sát thương;
  - vũ khí giữ chuột mà sát thương tăng mãi (tia, gatling): giữ 10/20/40/60 tick theo thời gian thật, tốc độ = phần tăng từ 20 đến 60 tick; cung thường không bị tính vậy (đòi tăng 1.5 lần rồi 1.3 lần);
  - súng có băng đạn (Terramity): tháo hết đạn, ngồi + chuột phải để nạp, đếm thời gian nạp; số tick mỗi phát = (số viên × hồi + nạp) ÷ số viên. Basic Pistol: 5 viên, nạp 75 tick → 19 sát thương/giây (không phải 72).
- **Món gây sát thương theo % máu**: nếu phát bắn ở 10.000 máu luôn cao hơn ở 1.000 máu và gấp hơn 1.5 lần, giữ thêm số 10k để ghi chú.

### 2.3 Mage
- **Bảng chính** (`GOFF.MA`): lấy giá trị lớn hơn giữa Iron's và Ars, rồi nhân với hệ số "mọi sát thương", hệ số "tầm xa" và chí mạng Apothic.
  - Iron's = (1 + spell power + trường phái tốt nhất) ÷ (1 − giảm hồi chiêu) × thời gian niệm × mana × hồi mana.
  - Ars = sát thương phép phẳng so với nhát chém điển hình của Act.
  - Tier tính theo **phần tăng** (điểm − 1).
- **Bảng "Own attack"** (tiếng Việt: "Đòn riêng"; pool `x`): mọi vũ khí Mage có đòn riêng đo được, xếp theo sát thương mỗi giây, tách hẳn khỏi bảng chính. Bạn đã chọn "một bảng riêng với tên gọi hợp lý".

### 2.4 Summon (`gMn`, `gWh`)
- **Staff**: người thử dùng vũ khí một lần (Summonity triệu hồi khi nhấp vào khối sàn). Một con zombie không AI, 100.000 máu, không giáp, đứng trên sàn đá cách 4 khối, lúc nửa đêm; mọi thực thể mới xuất hiện bị ép nhắm vào nó. Máu của nó được đọc mỗi 10 tick trong 300 tick. Điểm = máu mất từ lần đọc đầu tiên có sát thương tới lần cuối, chia cho số giây đó (không tính lúc minion đi tới).
- **Người thử phải là "chủ" minion**: minion Summonity tìm chủ trong danh sách người chơi của server; script đưa FakePlayer vào map UUID của danh sách đó trong lúc đo.
- **Roi** (bảng "Whips", pool `h`, tách khỏi bảng staff như "Own attack" của Mage): roi không triệu hồi gì; minion vẫn giữ nguyên sát thương khi cầm roi. Roi Summonity: sát thương × 20 ÷ cooldownTicks lấy từ `summonity-common.toml` (đòn quất không đo được: nó tìm chủ bằng `level.getEntity`). Roi Better Combat (Goety Revelation): nhát chém đo được × tốc độ đánh.

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
- **`server.properties`**: thế giới phẳng, offline, không sinh quái, `max-tick-time=-1`, `gamemode=survival`. `spawn-animals=true` và `spawn-npcs=true`: tắt đi thì mỗi tick vanilla xóa mọi động vật và dân làng, kể cả lợn thử (2026-11-18).
- **Sau mỗi lần khởi động** chạy `forceload add -48 -48 48 48`: không có người chơi thật thì sau 300 tick vanilla ngừng cập nhật vật thể.

### 5.2 Các lượt đo
| Lệnh (`kubejs custom_command …`) | Kế hoạch (`prep.py`) | Kết quả | Nhập bằng |
|---|---|---|---|
| `lgw_measure` | `prep.py kubejs/lgw_items.json` | thuộc tính, chém, giáp | `import.py` |
| `lgw_measure_extra` | `--extra` | vũ khí theo mục tiêu, đeo thử curio | `import.py` (đối số thứ 3), `import_curios.py` |
| `lgw_measure_third` | `--third [--guns] [--only-missed] [--mage] [--minions] [--rhp 1000]` | bắn thử, đòn riêng Mage, minion, curio chặn đòn, vũ khí quay mặt | `import_third.py LẦN_10K [LẦN_1K]` |
| `lgw_measure_test` | file tay, ví dụ `{"hurtTrace": true}` | dò từng listener của event | đọc tay |
| `lgw_measure_fx` | `kubejs/lgw_fx_items.json` (`effects`, `fxLevels`, `fxSkip`, `fxSolo`) | hiệu ứng trên lợn thử và người chơi thử, thuốc và đồ ăn cho ra hiệu ứng | `import_fx.py` |

**Thứ tự nhập**: `import.py` → `import_curios.py` → `import_third.py`. Lý do: `import.py` viết lại `gear_measure.json` từ đầu, nên phải nhập lại phát bắn sau nó.

### 5.3 Lỗi của bài đo đã sửa (mọi số trước 2026-11-17 đều mắc)
1. **Người thử rơi**: người thử đứng cao 3 khối và rơi trong lúc chờ. Nhát chém lúc đang rơi thành chí mạng ×1.5, còn mũi tên bay lọt dưới con lợn. Sửa: tắt trọng lực.
2. **Thế giới ngừng cập nhật**: vật thể không di chuyển sau 15 giây. Sửa: `forceload`.
3. **Chế độ sáng tạo**: người thử ở creative thì chặn mọi đòn. Sửa: script đặt survival.
4. **Khoá bảo vệ của Difficulty Enhancement**: người thử miễn sát thương vì chưa chọn độ khó. Sửa: script chọn độ khó, không modifier.
5. **Chí mạng của kẻ đánh thử**: con lợn có 5% chí mạng Apothic; 8 thành 12 rồi bị trần 10 cắt, cho ra 69–84 số đo "nhận thêm 25%" ngẫu nhiên. Sửa: đặt chí mạng của nó về 0. Số đo bị chặn trần giảm từ 69 xuống 8.
6. **Minion tự xoá** (Summonity tìm chủ trong danh sách người chơi của server): đưa FakePlayer vào map UUID của danh sách đó trong lúc đo. Cùng đợt: đếm thực thể theo `getId` (tên `getUUID` không gọi được trên FakePlayer), zombie đứng trên sàn, máu đặt sau khi vào thế giới (pack co 1.000 → 25), giữ nửa đêm (zombie cháy nắng 1,25/giây).
7. **Mũi tên ở tay phụ**: súng Terramity không bắn. Chuyển vào túi; ở ô 0 thì bị vũ khí đè (Bow đọc 0), nên để từ ô 9.
8. **Đường cong kéo cung gọi `use()` 17 lần**: với súng đó là 17 phát thật, rơi trễ vào phát đo đầu (Burst Rifle 493). Nay chỉ vẽ đường cong cho món có thời gian kéo.
9. **Bắn liên tục mỗi tick**: client chỉ lặp chuột phải mỗi 4 tick; nay đo theo nhịp đó.
10. **Đạn 999 viên**: bỏ qua thời gian nạp; nay đo nạp đạn thật cho súng có băng.

### 5.4 Món chuẩn để hiệu chỉnh (phải ra đúng mới tin lượt đo)
- Bow: 20 tick mỗi phát, 7–9 sát thương (vanilla: 6 cộng chí mạng ngẫu nhiên).
- Crossbow: nạp 25 tick. Trident: 10 tick, 8 sát thương.
- Kiếm kim cương: 15. Người thử không mặc gì nhận 10 trên đòn cận chiến 20 (trần nửa máu) và 20 trên các loại đòn khác.

## 6. Trạng thái hiện tại (Act XII, sau đợt 2026-11-17)

| Nhóm | Đã xếp / chưa xếp | Ghi chú |
|---|---|---|
| Melee | 1011 / 1 | Đo lại: 977/1010 khớp lần cũ; 7 món lần cũ bị thổi ×1.5 vì người thử đang rơi |
| Ranged | 121 có số / 23 chưa xếp | 42 món đạt ngưỡng tier ở Act XII. Chưa xếp: cung Animus, Too Many Bows, L2 Archery, Meka-Bow, Infinity Launcher, Matter Cannon, Tesla Cannon, Crankbow, Autoloader, shotgun Nether Expansion, Providence, Rocket Launcher, Sticky Bomb, Beach Ball (không gây sát thương trong bài thử); Blunderbuss, Pump Action Shotgun (không đọc được nạp đạn); Railgun và Sawed Off Shotgun Terramity (các phát lệch nhau) |
| Mage, bảng chính | 60 / 41 | 41 món không cộng gì cho phép |
| Mage, "Own attack" | 7 có tier (9 có số) | 92 món không có đòn riêng gây sát thương, hoặc chưa đo được tốc độ |
| Summon | 12 / 12 | 12 staff có DPS minion; 12 món không gây sát thương: roi (xếp ở bảng "Whips"), Fairy Staff (hỗ trợ), 2 staff Goety (phóng focus), Blood Staff |
| Summon, "Whips" | 7 có tier ở Act XII | Summonity theo config, Goety Revelation theo nhát chém đo được |
| Giáp | 313 / 313 | Hazmat và Scuba của Mekanism được xếp với giáp 0 |
| Curio | 253 có hạng Power | Ba bảng mỗi lối chơi; số đo bị chặn trần 69 → 8 |

Số đo lại của curio đã đổi một số kết luận cũ:
- Chặn đòn: Ace of Iron chặn 0/10 (cũ ghi 3/10); Opal Necklace, Ethereal Eclipse Emblem, Shinobi Sash mỗi món 1/10.
- Lethality đánh vào mục tiêu 0 giáp không tăng gì: Warpslice Scabbard và Portable Quantum Thingamabob mất mức +70%/+100% cũ (số cũ là lỗi của bài đo).
- Chthonic Shell Casing được tính ×1.3 cho đòn từ xa theo hằng số trong code: nhát chém thử cách 1.2 khối, không tạo được khoảng cách trên 3 khối.

## 7. Các bước còn lại
1. **Summon**: xong (mục 2.4). Còn lại: Fairy Staff và staff Goety không có số vì không tự gây sát thương.
2. **Ranged còn 23 món** (mục 6): mỗi món cần cách bắn riêng của mod (ví dụ cung Animus cần "will", Sticky Bomb cần lệnh kích nổ, Too Many Bows và L2 Archery không bắn được với mũi tên thường trong túi). Đã thử 2 cách chung (mũi tên ở tay phụ, rồi ở túi), nên dừng theo quy tắc 2 lần.
3. **Lethality và xuyên giáp**: tính theo giáp của Keeper ở từng Act, dùng đúng công thức đã đọc trong mixin của Brutality, thay cho bài đo trên mục tiêu 0 giáp. Số liệu đã có trong `entitybalance.json`: giáp Keeper 12 (Act II), 18, 50, 100, 120, 130–330 (Act VIII), 340, 400, 450 (Act XII), độ cứng tới 460. Với giáp như vậy lethality phẳng (vài điểm) gần như không đổi gì ở Keeper cuối, còn xuyên giáp bị độ cứng làm yếu (2%/điểm, tối đa 60%). Chưa làm vì cần chọn mô hình (sàn sát thương của pack có áp cho quái không, công thức giáp Apothic với đòn của người chơi): cần chủ wiki duyệt.
4. **Combo của Better Combat**: đo đủ một vòng combo thay vì trung vị 3 nhát. Cần đo lại 1.048 vũ khí cận chiến với chí mạng của người thử tắt; sai số hiện tại tối đa khoảng 10% (Laser Blade: 15, 22.5, 22.5 → trung vị 22.5, trung bình 20). Chưa làm.
5. **Kỹ năng chủ động của vũ khí cận chiến** và **hệ số k của giáp**: mục 8.

## 8. Giới hạn và câu hỏi còn mở
- **Combo của Better Combat**: mỗi nhát trong chuỗi combo có hệ số riêng (Laser Blade: 15, 22.5, 22.5). Trung vị 3 nhát phụ thuộc vào vị trí trong chuỗi; đo đủ một vòng combo sẽ đúng hơn.
- **Hệ số k của giáp**: là số đặt tay. Với mô hình tích, tần suất trúng đòn chỉ là hằng số nên không đổi thứ hạng; k < 1 chỉ đứng được nếu độ bền có lợi ích giảm dần.
- **Lethality**: chỉ đo trên lợn 0 giáp. Hiệu quả thật phụ thuộc giáp của mục tiêu.
- **Kỹ năng chủ động của vũ khí cận chiến**: chưa tính.
- **Summonity**: `minion_damage` đo được bằng nửa con số trong tooltip; chưa đọc code để biết bên nào đúng.
- **Phù phép, reforge (Tiered), hiệu ứng bộ viết trong code**: không tính (hiệu ứng bộ được đo khi chúng chạy qua event).

### 5.4 Lấy mẫu cho curio xác suất (2026-11-18)
- **Vì sao**: bài đo hai nhát chém không thấy được hiệu ứng là một xác suất (xúc xắc, đồng xu, proc trên đòn), nên những curio đó không có tier.
- **Bài đo**: `lgw_measure_chance` (`lgw_measure.js` mục 3b) đọc `kubejs/lgw_chance_items.json` (`{"chance": [id…], "chanceN": 300, "chanceHurt": 300, "chanceAmt": 4, "chanceLuck": ["0", "e1", "e3"]}`) và ghi `kubejs/lgw_chance_measure.json`: đeo curio, N nhát chém kiếm kim cương vào heo mới, M đòn 4 sát thương mỗi loại qua các sự kiện sát thương. Mức Luck: số là thuộc tính Luck, `eN` là hiệu ứng Luck cấp N. Đòn thử là 4 vì pack chặn một đòn ở nửa máu người thử (10): đòn 8 nhân ×1.5 chỉ đọc được 10.
- **Nhập**: `python3 build/pack_audit/measure/import_chance.py chance_main.json chance_luck.json` → `build/patches/curio_chance.json` (`CCH` trong trang): `hs` = trung bình sát thương gây ra so với người thử trần, `tk` = trung bình sát thương nhận vào theo loại, `lk` = các mức Luck hiệu ứng.
- **Điểm**: `gear.js` dùng `hs` và `tk` thay cho một nhát và một đòn, trừ curio mà thuộc tính đo đã giải thích sát thương (`gHsOwned`: crit, sát thương, tốc độ, lifesteal), để không cộng đôi. Trang curio ghi "Sampled in game".
- **Sự thật đo được**: (1) điểm thuộc tính Luck không đổi gì (Lucky Dice 20% ở Luck 0, 5 và 20; người thử trần cùng sát thương); chỉ **hiệu ứng Luck** tăng tỉ lệ: Lucky Dice 20% → 29% (Luck I) → 73% (Luck V), Nullifying Dice 10% → 13,5% → 36,5%, đúng "mỗi cấp" trong text. (2) Fateful Coin: gây ra ×1.25 nhưng nhận vào từ đòn cận chiến ×1.54 (lửa, nổ, phép, rơi ×1.25). (3) Slicer's Dice (text không có số nào) thật ra ×1.18 sát thương, ×1.25 ở Luck I, ×1.48 ở Luck III.
- **Kết quả**: 125 curio được lấy mẫu; 33 đổi sát thương gây ra, 12 đổi sát thương nhận vào, 84 không đo được bằng bài này (điều kiện, kỹ năng chủ động). Curio có tier 282 → 286 (thêm Ace of Iron, Slicer's Dice, Shinobi Sash, Ultra Sniffer Fur).
- **Server**: pack 6.6.6cf giải nén ngoài repo; Forge 47.4.20, Java 21, `-Xmx8G`; chạy cùng build và `check.sh` thì hết RAM (15 GB) và tiến trình bị kill: tắt server trước khi build.

### 5.5 Lấy mẫu theo điều kiện (2026-11-18)
- **Bài đo**: `lgw_measure_cond` (`lgw_measure.js` mục 3c) đọc `kubejs/lgw_cond_items.json` (`{"cond": [id…], "states": ["lowhp", "night", "burning", "sprint", "zombie", "tburn", "tlow"], "condN": 120, "condHurt": 60, "chanceAmt": 4}`) và ghi `kubejs/lgw_cond_measure.json`: mỗi curio và người thử trần (`(none)`) được đo trong từng trạng thái (máu thấp 20%, nửa đêm, đang cháy, chạy nước rút, đánh zombie, mục tiêu đang cháy, mục tiêu còn 20% máu).
- **Nhập**: `python3 build/pack_audit/measure/import_cond.py file1.json file2.json…` → `build/patches/curio_cond.json` (`CCD` trong trang). Mỗi file có đường cơ sở riêng, nên đo theo lô được.
- **Điểm**: kích cỡ hiệu ứng trong một trạng thái là số đo; tỉ lệ thời gian người chơi ở trạng thái đó là **giả định**, đặt ở `patches/effect_uptime.json` ("states": máu thấp 25%, ban đêm 33%, đang cháy 10%, chạy 40%, đánh undead 30%, mục tiêu cháy 15%, mục tiêu máu thấp 25%). Các trạng thái chồng nhau nên tổng bị chặn ở mức lớn nhất của một trạng thái.
- **Điều kiện người thử tự thỏa** (hiệu ứng hiện ở từ 5 trạng thái trở lên) chỉ được hiển thị, không tính (`dfk`), đúng tinh thần `GCTX`: Rage Glove ×4.7 (đòn liên tiếp nên stack đầy ngay), Stillness Scarf ×1.5 (người thử đứng yên), Berserk Charm ×2 (người thử chém ở nửa máu). Nếu tính, các món này lên S sai.
- **Kết quả**: 327 curio có điều kiện được đo, 0 lỗi; 46 đổi sát thương trong ít nhất một trạng thái; 37 là điều kiện thỏa sẵn (chỉ hiển thị); 9 có hiệu ứng điều kiện thật được tính (Tearstone Ring ×1.13, Ruby Ring, Lava Gauntlet, Eye for Violence…). Curio có tier 286 → 288 (Earth Promise, Lava Gauntlet).
- **Server**: một lượt 330 curio làm server hết heap Java (`OutOfMemoryError`) sau khoảng 100 curio và không ghi gì; chạy theo lô nhỏ, mỗi lô một server mới (`run_batches.sh` trong thư mục làm việc, không nằm trong repo) và lưu từng lô. Container bị thu hồi khi lượt làm việc dừng: phải ở lại trong lượt cho tới khi đo xong.
