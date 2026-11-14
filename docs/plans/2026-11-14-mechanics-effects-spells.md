# 2026-11-14: Mechanics tách trang, Effects đầy đủ, tab Spells

Chủ wiki yêu cầu (14/11): (1) tách các mục của Mechanics thành trang riêng mà không làm đầy thanh tab chính; (2) Effects có mọi hiệu ứng trong game; (3) một tab mới cho mọi spell, có video/hiệu ứng.
Đã duyệt: mục 3 theo phương án A (dữ liệu thật từ jar + ô clip), phạm vi spell = spell đăng ký trong Iron's Spells 'n Spellbooks và addon của nó (đếm từ jar rồi báo), Goety foci và Ars Nouveau glyph để sau. Về bản quyền của clip spell, chủ wiki bảo "không cần lo": đó là ngoại lệ có chủ ý so với quy tắc texture ở `build/README.md` (Licence rules), chỉ áp cho clip spell, ghi ở NOTES.

Ba việc độc lập, làm theo thứ tự, mỗi việc đi hết `CLAUDE.md` bước 2–6 rồi mới sang việc sau.

## Việc 1: Mechanics thành bốn trang
- Thanh chính giữ nguyên một tab Mechanics. Trong trang là thanh phụ (cùng kiểu nút `.mtabs`): Goety rituals · AE2 storage · Effects · Stats.
- Route: `#mechanics/goety`, `#mechanics/ae2`, `#mechanics/effects`, `#mechanics/stats`; `#mechanics` (và `#mechanics/<gì đó lạ>`) mở Goety rituals. Đổi so với bản đã duyệt: không làm trang chọn mục riêng, vì thanh phụ luôn hiện đã là bộ chọn và trang chọn cần thêm câu mô tả phải dịch ra bốn ngôn ngữ. Hai link cũ `#mechanics/effects` và `#mechanics/stats` (trang item, mục Changes) tiếp tục đúng nghĩa, nay mở thẳng trang đó thay vì cuộn.
- Stats giữ một trang với 11 mục nhỏ bên trong.
- Xong khi: mỗi mục là một trang, thanh chính không thêm tab, route cũ còn dùng được, 375 px không tràn, `check.sh` xanh.

## Việc 2: Effects đầy đủ
- Nguồn: đăng ký `MobEffect` trong mọi jar của pack (`gear/classlib.py` đọc bytecode; `pack_audit/gear_fx.py` đã đọc effect của gear), tên và mô tả từ file lang của mod, số từ code/datapack. Chỗ không đọc được thì ghi "chưa xác nhận".
- Icon: effect của mod nào bị `NO_ART` hoặc All Rights Reserved không có icon (quy tắc texture giữ nguyên cho effect).
- Xong khi: số effect trên trang khớp số đọc từ jar (trừ danh sách loại trừ có lý do), mỗi dòng có nguồn.

## Việc 3: tab Spells
- Tab thứ 7 trên thanh chính. Mỗi spell: trường phái, mana, cooldown, thời gian niệm, sát thương/hiệu ứng theo cấp, nguồn lấy (sách, scroll, boss, ritual), mô tả, liên kết sang Effects mà spell gây ra.
- Ô clip cho mỗi spell, chỉ hiện khi có file clip.

### Clip: công cụ tìm được trước khi thử (14/11; bảng dưới là dự kiến, kết quả thật ở mục kế tiếp)
Spell của Iron's phần lớn là code Java (hạt, thực thể, shader), không phải dữ liệu JSON, nên không "trích" ra rồi tự dựng được: muốn video thật phải chạy game rồi quay. Hướng khả thi:

| Công cụ | Dùng để | Trạng thái |
|---|---|---|
| Client Minecraft 1.20.1 + Forge, chỉ nạp Iron's và thư viện của nó (không nạp cả 430 mod) | chạy spell thật | chưa thử |
| Mesa llvmpipe + Xvfb (container có `swrast_dri.so`, `xvfb-run`, `ffmpeg`, Java 21) | vẽ OpenGL bằng CPU, không cần GPU | có sẵn, chưa thử vẽ Minecraft |
| ReplayMod: ghi `.mcpr` rồi render offline ở fps cố định, xuất bằng ffmpeg | video mượt dù máy chậm (quay trực tiếp bằng `x11grab` dưới llvmpipe sẽ giật) | build cho Forge 1.20.1 chưa xác nhận (Modrinth không trả bản nào theo bộ lọc; thử replaymod.com/CurseForge) |
| Mẫu tham khảo: `IceyyDev/Vps-Renderer` (setup.sh + render.sh + mod AutoRender) | cùng quy trình `.mcpr` → llvmpipe → ffmpeg, nhưng cho Fabric 26.1 | đọc README, chưa đọc mã |
| HeadlessMC (`headlesshq/headlessmc`) | khởi chạy client không cửa sổ, có Forge | README nói tài khoản offline chỉ dành cho CI |
| Lệnh `/cast` của Iron's (có trong 1.20.1) | ép từng spell chạy trong thế giới thử | cú pháp chưa đọc: đọc từ class lệnh trong jar |

Cần xác minh trước khi hứa: (a) client chạy được dưới llvmpipe ở đây, (b) fps và thời gian render một clip 3 giây, (c) có ReplayMod chạy trên Forge 1.20.1 không, (d) một mod nhỏ tự động hoá cả chuỗi (vào thế giới, đặt mục tiêu, `/cast`, đặt camera). Bước thử một spell, một clip, đặt giới hạn thời gian; thất bại hai lần cùng một hướng thì dừng và báo.
Server pack `serverpack-slim-6.6.6hf.zip` (Drive, 877,854,222 byte) không có mod client và không có `assets/*/sounds`; client cần thêm 46 mod client-only và resource pack từ bản CurseForge (`Linggango-V6.6.6hf.zip`, `build/README.md`, mục pack_audit).
Clip làm file offline `Linggango_Relic_Wiki.html` phình to: dùng video nhỏ (webm ngắn, vài chục KB mỗi cái), tải riêng như `wiki_pics.js`, và bản offline có thể bỏ clip.

### Clip: công thức đã chạy (14/11, chạy thật trong container này)
Chạy được: client Minecraft thật, vẽ bằng CPU, quay màn hình, mã hoá H.264. Không dùng ReplayMod, Replay Fabric hay shader.
1. `pip install portablemc python-xlib pillow jawa`; `portablemc --main-dir M start forge:1.20.1 --mc-dir W --dry` cài Forge 47.4.29 (JVM hệ thống Java 21 chạy được) và tải thư viện Mojang. Máy chủ: `forge-1.20.1-47.4.29-installer.jar --installServer` trong thư mục riêng (maven.minecraftforge.net).
2. Mod ở cả hai phía: `irons_spellbooks` 3.15.6, `geckolib`, `curios`, `playeranimator`, `irons_lib` (đúng các jar của server pack). Chỉ client: `ShoulderSurfing-Forge-1.20.1-5.3.1` (camera qua vai, người niệm lệch trái, mục tiêu hiện bên phải) và `embeddium-0.3.31+mc1.20.1` (đã bỏ vào nhưng chưa đo có nhanh hơn không).
3. Máy chủ phẳng: `online-mode=false`, `difficulty=peaceful`, `level-type=minecraft\:flat`, stdin là FIFO (`tail -f cmd.fifo | java ... nogui`). Client: `Xvfb :99 -screen 0 854x480x24`, `LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_GL_VERSION_OVERRIDE=4.6 MESA_GLSL_VERSION_OVERRIDE=460 LP_NUM_THREADS=4`, `portablemc ... start forge:1.20.1 --mc-dir W --resolution 854x480 --join-server localhost -u RenderBot`. Đo thật: khoảng 13 khung hình khác nhau mỗi giây ở 854x480 với 4 luồng.
4. `build/pack_audit/spell_clips.py` điều khiển: `/cast RenderBot <spell> <cấp tối đa>` qua FIFO (người chơi niệm nên có thanh niệm và hoạt ảnh), `ffmpeg -f x11grab`, nén H.264 480 px, 15 fps, không tiếng; tự nhận góc nhìn qua vai từ ảnh chụp (F5 qua XTEST đôi khi mất phím; **không** di chuyển con trỏ: game bắt chuột, nhảy con trỏ làm xoay camera) và tự đóng màn hình Ender Chest do spell Pocket Dimension mở.
5. Kết quả: 105 spell của Iron's quay được; 92 clip có chuyển động nhìn thấy (đo bằng số điểm ảnh đổi so với khung đầu); 13 spell không thấy hiệu ứng (chủ yếu spell cần mục tiêu hoặc tác dụng nhỏ: abyssal_shroud, devour, frostbite, gluttony, planar_sight, pocket_dimension, sacrifice, sculk_tentacles, sonic_boom, spectral_hammer, spider_aspect, touch_dig, wololo) chưa có clip. 90 spell của addon (T.O Magic, Geomancy Plus, Refined, Peyro's Scythe, Somake, Deeper and Darker) chưa quay: cần thêm 19 jar và phụ thuộc (Apothic Attributes, Cataclysm, Alex's Caves, Citadel, Placebo, lionfish, gtbcs_spell_lib, deeperdarker…) vào cả hai phía.
6. Không làm: shader (Oculus/Iris dưới llvmpipe dưới 1 khung hình mỗi giây theo README của `icxyy/Vps-Renderer`), ReplayMod (không có bản Forge 1.20.1 trên Modrinth), tickrate (bản Forge cần hai mod phụ thuộc, chưa thử).

## Còn mở
- Clip: 92 của 195 spell có; xem mục "Clip: công thức đã chạy" cho phần còn lại và lý do.
- Tài khoản Minecraft: chạy client cần bản quyền game của chủ wiki hoặc tài khoản offline cho CI; chủ wiki quyết.
