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

### Clip: công thức đã chạy (bản 2, 14/11; bản 1 qua vai đã thay, lý do ở NOTES "tiếp 4" và "tiếp 7")
Chạy được trong container: client Minecraft thật, vẽ bằng CPU, quay màn hình, H.264. `build/pack_audit/spell_clips.py` làm các bước 4–6.
1. `pip install portablemc python-xlib pillow jawa numpy`; `portablemc --main-dir M start forge:1.20.1 --mc-dir W --dry` cài Forge 47.4.29 (Java 21). Máy chủ: `forge-1.20.1-47.4.29-installer.jar --installServer` trong thư mục riêng; phẳng, `online-mode=false`, `difficulty=peaceful`, stdin là FIFO (`tail -f cmd.fifo | java ... nogui > server.log`).
2. Mod ở cả hai phía: Iron's Spells 3.15.6 (+ geckolib, curios, playeranimator, irons_lib), các addon spell và phụ thuộc lấy từ server pack, **Target Dummy** (`dummmmmmy` + Moonlight Lib) làm mục tiêu, **Damage Numbers 1.4.0**, và **CMDCam 2.2.1 + CreativeCore 2.12.42** (Modrinth, LGPL-2.1): camera điều khiển bằng lệnh máy chủ `/cam-server`. Chỉ client: Embeddium 0.3.31, Oculus 1.8.0 với shader Potato Lite v5.1. Bỏ Shoulder Surfing (camera giờ là CMDCam).
3. Client: `Xvfb :99 -screen 0 1280x720x24`, `LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_GL_VERSION_OVERRIDE=4.6 MESA_GLSL_VERSION_OVERRIDE=460 LP_NUM_THREADS=4`, `portablemc ... start forge:1.20.1 --mc-dir W --resolution 960x540 --join-server localhost -u RenderBot` (cửa sổ nằm ở +160,90), F1 ẩn HUD.
4. Sân khấu mỗi spell (cách nhau 100 khối theo z, `forceload` trước khi đặt sàn): sàn polished deepslate, giờ 12300, không sinh mob; người niệm ở x−3.5, Target Dummy ở x+3.5, cột **barrier** (vô hình) ngay sau dummy; người niệm nhắm vào **ngực** dummy (`facing <x> -58.9 <z>`), mặc áo choàng đúng hệ phép và cầm gậy, mọi spell power được kéo về giá trị gốc bằng một modifier `multiply` cho từng thuộc tính.
5. Camera CMDCam chế độ `outside`: nhìn ngang từ 6.5 khối, cao 1.4 khối, cúi 5°, FOV 50, trượt chậm 0.8 khối trong suốt clip (`/cam-server create`, `get <tên> add <x y z> <yaw pitch> <roll> <fov>`, `start <tên> RenderBot`).
6. `/cast RenderBot <spell> <cấp tối đa>`, ffmpeg x11grab 30 fps, H.264 960×540 CRF 24; poster là khung khác khung đầu nhiều nhất. Dài: tức thì 6 s; niệm lâu và liên tục = thời gian niệm + 6 s, tối đa 11 s.

Đo được (14/11, 8 spell, đếm khung khác nhau bằng `mpdecimate`): cửa sổ 1280×720 vẽ 18–24 khung/giây, 960×540 vẽ 42–50 khung/giây, nên clip 30 fps không lặp khung. Tắt shader chỉ nhanh hơn khoảng 25% (26 so với 20 khung/giây ở 720p) mà ảnh phẳng và xanh, nên giữ shader. Đổi render distance không đổi tốc độ. Dung lượng: 0,5–3,7 MB một clip (Fire Breath nặng nhất), trung bình khoảng 1,1 MB; AV1 cùng cỡ bằng khoảng 55% (SSIM 0,986 so với 0,983) nhưng iPhone và Mac đời cũ không phát được.

Đã thử và bỏ: **Tickrate API 6.0.5** (quay chậm ×2 rồi tua lại: gấp đôi khung hình, nhưng thời gian niệm của Iron's chạy theo máy chủ nên Fireball niệm còn khoảng 1 s thay vì 2 s: sai thông tin); **Madgique's Tickrate Changer** (máy chủ không khởi động); **ReplayMod / ReForgedPlay** (ReplayMod bản Forge dừng ở 1.12.2; ReForgedPlay trên GitHub là NeoForge 1.20.4+); shader **Complementary Reimagined** (khoảng 1 khung/giây). Black Hole trông như đĩa đen với tia hồng tím cả khi tắt shader: đó là hình thật của spell, không phải lỗi.

## Còn mở
- Clip: chưa quay cả loạt theo bản 2 (chủ wiki yêu cầu duyệt chất lượng trước); chưa có clip nào được duyệt (`build/clips/approved.json` rỗng). Chỗ chứa khoảng 300 clip (khoảng 330 MB H.264) chưa quyết: không nên đưa vào nhánh `main`.
- Tài khoản Minecraft: chạy client cần bản quyền game của chủ wiki hoặc tài khoản offline cho CI; chủ wiki quyết.
