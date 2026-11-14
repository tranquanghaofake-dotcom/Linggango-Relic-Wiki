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

### Clip: công thức đã chạy (bản 3, 14/11; bản 1 qua vai và bản 2 960×540 đã thay, lý do ở NOTES "tiếp 4", "tiếp 7", "tiếp 8")
Chạy được trong container: client Minecraft thật, vẽ bằng CPU, quay màn hình, H.264. `build/pack_audit/spell_clips.py` làm các bước 5–7.
1. `pip install portablemc python-xlib pillow jawa numpy`; `apt-get install faketime libfaketime`; `portablemc --main-dir M start forge:1.20.1 --mc-dir W --dry` cài Forge 47.4.29 (Java 21). Máy chủ: `forge-1.20.1-47.4.29-installer.jar --installServer` trong thư mục riêng; phẳng, `online-mode=false`, `difficulty=peaceful`.
2. Mod ở cả hai phía: Iron's Spells 3.15.6 (+ geckolib, curios, playeranimator, irons_lib), các addon spell và phụ thuộc lấy từ server pack, **Target Dummy** (`dummmmmmy` + Moonlight Lib) làm mục tiêu, **Damage Numbers 1.4.0**, **CMDCam 2.2.1 + CreativeCore 2.12.42** (Modrinth, LGPL-2.1, camera điều khiển bằng lệnh máy chủ `/cam-server`). Chỉ client: Embeddium 0.3.31, Oculus 1.8.0 với shader Potato Lite v5.1. Không dùng Shoulder Surfing.
3. **Đồng hồ chậm**: máy chủ và client đều chạy dưới libfaketime cùng một tốc độ, `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/faketime/libfaketimeMT.so.1 FAKETIME='+0 x0.25'`. Cả game chạy bằng một phần tư tốc độ (tick, thời gian niệm, hạt, hoạt ảnh, đồng hồ của shader), nên CPU có gấp bốn thời gian để vẽ mỗi khung; ffmpeg ghi màn hình theo giờ thật ở 15 khung/giây rồi đổi về giờ game (`setpts=PTS*0.25`) thành 60 khung/giây. Không đổi tốc độ khi game đang chạy (đồng hồ sẽ nhảy lùi).
   - Máy chủ: `tail -f cmd.fifo | env LD_PRELOAD=... FAKETIME='+0 x0.25' java @user_jvm_args.txt @libraries/.../unix_args.txt nogui > server.log`.
   - Client: `Xvfb :99 -screen 0 1920x1080x24`; `env DISPLAY=:99 LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_GL_VERSION_OVERRIDE=4.6 MESA_GLSL_VERSION_OVERRIDE=460 LP_NUM_THREADS=4 LD_PRELOAD=... FAKETIME='+0 x0.25' portablemc ... start forge:1.20.1 --mc-dir W --resolution 1920x1080 --join-server localhost -u RenderBot`; `options.txt`: `maxFps:260`, `enableVsync:false` (giới hạn khung tính theo giờ game); F1 ẩn HUD.
4. Đo được (14/11): ở ×0.25, cửa sổ 1080p vẽ 12–14 khung mỗi giây thật, tức 49–56 khung khác nhau mỗi giây game trên 60 (Fireball, Fire Breath). Thời gian đúng: Fireball rời gậy ở giây 2,75 cả khi quay thường lẫn khi quay ×0.25. Java dưới libfaketime ×0.5: `Thread.sleep`, `LockSupport.parkNanos`, `Object.wait` và `System.nanoTime` đều chậm đúng một nửa.
5. Sân khấu mỗi spell (cách nhau 100 khối theo z, `forceload` trước khi đặt sàn): sàn polished deepslate, giờ 12300, không sinh mob; người niệm ở x−3.5, Target Dummy ở x+3.5, cột **barrier** (vô hình) ngay sau dummy; người niệm nhắm vào **ngực** dummy, mặc áo choàng đúng hệ phép và cầm gậy, mọi spell power được kéo về 1.0 bằng một modifier `multiply` cho từng thuộc tính (số tính một lần cho mỗi bộ áo).
6. Camera CMDCam chế độ `outside`: nhìn ngang từ 6.5 khối, cao 1.4 khối, cúi 5°, FOV 50, trượt chậm 0.8 khối (`/cam-server create`, `get <tên> add <x y z> <yaw pitch> <roll> <fov>`, `start <tên> RenderBot`).
7. `/cast RenderBot <spell> <cấp tối đa>`; bản gốc 1080p60 thu nhỏ xuống 1280×720 (lanczos, cũng làm mịn cạnh) 60 fps H.264 CRF 23. Poster: khung có nhiều màu của phép nhất (độ "colourfulness" Hasler–Süsstrunk tăng so với khung đầu) mà người niệm (một phần tư bên trái) chưa bị che; phép màu xám (đá, Vex) ra khung sớm, chọn tay khi duyệt. Dài (giờ game): tức thì 6 s; niệm lâu và liên tục = thời gian niệm + 6 s, tối đa 11 s.

Bộ thử 8 spell (14/11): 0,86–2,0 MB một clip, riêng Fire Breath (lửa dày, 11 s) 7,0 MB; 47–57 khung mới mỗi giây trên 60. Không chạy việc nặng nào khác khi đang quay: lúc chạy thử nén video song song, Summon Vex chỉ còn 19 khung mới cả clip. Dung lượng theo cách nén (Fireball 8 s): 720p60 H.264 1,93 MB (SSIM 0,977), 720p30 1,69 MB, 1080p60 3,5 MB, 720p60 AV1 1,60 MB (SSIM 0,986). Một spell mất khoảng 1 phút thật (8 s game ×4 cộng dựng sân khấu), nên 314 spell khoảng 5 giờ.

Đã thử và bỏ: **bản 2** (cửa sổ 960×540 ở tốc độ thường, 42–50 khung/giây: mượt 30 fps nhưng kém nét); **Tickrate API 6.0.5** (chỉ làm chậm thực thể và client, máy chủ vẫn đếm thời gian niệm theo giờ thật: Fireball niệm còn khoảng 1 s); **Madgique's Tickrate Changer** (máy chủ không khởi động); **ReplayMod / ReForgedPlay** (không có bản Forge 1.20.1); shader **Complementary Reimagined** (khoảng 1 khung/giây ở 480p). Black Hole là đĩa đen với tia hồng tím cả khi tắt shader: đó là hình thật. Với phép phun (Fire Breath), số sát thương của dummy bị lửa che; mục tiêu vẫn mất máu như nhau dù có hay không có cột barrier (đo bằng một iron golem 1000 máu).

## Còn mở
- Clip: chưa quay cả loạt theo bản 2 (chủ wiki yêu cầu duyệt chất lượng trước); chưa có clip nào được duyệt (`build/clips/approved.json` rỗng). Chỗ chứa khoảng 300 clip (khoảng 330 MB H.264) chưa quyết: không nên đưa vào nhánh `main`.
- Tài khoản Minecraft: chạy client cần bản quyền game của chủ wiki hoặc tài khoản offline cho CI; chủ wiki quyết.
