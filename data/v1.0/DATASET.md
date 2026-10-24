# Bộ dữ liệu đánh giá phát hiện dấu hiệu lừa đảo – v1.0

Bộ dữ liệu nhỏ, gán nhãn thủ công, dùng để **đánh giá** (không phải huấn luyện) một hệ thống LLM phát hiện dấu hiệu lừa đảo trong tin nhắn, tin tuyển dụng, email và văn bản tiếng Việt nhắm vào sinh viên.

- Phiên bản: **1.0** (đóng băng 22/10/2026). Mọi kết quả đo phải ghi rõ "trên v1.0". Sửa nhãn thì tạo phiên bản mới, không sửa đè.
- Người gán nhãn: Minh Đức.
- Tệp nguồn: `scam-detector-dataset-v3.xlsx` (tab Dữ liệu, Taxonomy). Xuất bằng `scripts/export_dataset.py`; kiểm tra toàn vẹn bằng `MANIFEST.sha256`.

> **Trong repo công khai** chỉ có `taxonomy.json`, `MANIFEST.sha256` và tệp mô tả này. Các tệp tin nhắn (`dev.jsonl`, `test.jsonl`, `unsure.jsonl`) và file Excel gốc được giữ riêng, vì có nội dung chép từ báo và mạng xã hội, một phần nguồn chưa rõ giấy phép, và để tập test không lọt vào dữ liệu huấn luyện của các model sau này.

## Tệp

| Tệp | Nội dung |
|---|---|
| `dev.jsonl` | 85 mẫu: dùng để thử prompt, đọc lỗi, chọn ví dụ few-shot |
| `test.jsonl` | 128 mẫu: **chỉ chạy một lần** khi đã chốt prompt; không đọc trong lúc phát triển |
| `unsure.jsonl` | 8 mẫu nhãn không chắc chắn; không dùng khi đo |
| `taxonomy.json` | Định nghĩa 14 dấu hiệu S01–S14: định nghĩa, cụm từ gợi ý, ví dụ, trường hợp không gán |
| `MANIFEST.sha256` | Mã băm SHA-256 của các tệp trên |

Mỗi dòng JSONL gồm: `id`, `text`, `source_type` (sms, job_post, chat, email, document), `language` (vi, en, mixed), `label` (scam, legit, unsure), `signals` (danh sách mã dấu hiệu), `hard_negative` (chỉ cho legit), `split`, `source`, `label_notes` (lý do gán nhãn). Hai trường `source` và `label_notes` **không được đưa vào prompt**.

## Số lượng

| | dev | test | tổng |
|---|---:|---:|---:|
| scam | 45 | 68 | 113 |
| legit | 40 | 60 | 100 |
| trong đó hard negative | 35 | 49 | 84 |
| unsure (không chia) | – | – | 8 |

Theo loại nguồn (scam / legit):

| source_type | dev | test |
|---|---|---|
| sms | 30 / 28 | 47 / 44 |
| job_post | 4 / 9 | 6 / 13 |
| document | 6 / 3 | 8 / 3 |
| chat | 3 / 0 | 4 / 0 |
| email | 2 / 0 | 3 / 0 |

Dấu hiệu trong mẫu scam (dev / test):

| | S01 | S02 | S03 | S04 | S05 | S06 | S07 | S08 | S09 | S10 | S11 | S12 | S13 | S14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev | 10 | 15 | 6 | 4 | 21 | 3 | 6 | 0 | 14 | 1 | 12 | 20 | 3 | 7 |
| test | 16 | 20 | 8 | 6 | 31 | 5 | 8 | 1 | 19 | 4 | 18 | 30 | 6 | 10 |

Dấu hiệu cũng xuất hiện trong mẫu legit (gán theo nội dung): S09 ×11, S02 ×4, S07 ×3, S01 ×2, S04 ×1, S05 ×1.

## Nguồn dữ liệu

| Nguồn | Số mẫu | Ghi chú |
|---|---:|---|
| vietnamese_sms_dataset (train.csv) | 73 scam, 72 legit, 8 unsure | Giấy phép CC BY 4.0. Chỉ lấy từ train.csv, loại tin trùng hoặc gần trùng test.csv của nguồn (trừ 7 tin gần trùng có đánh dấu, bắt buộc nằm trong test của mình). Mỗi khuôn mẫu chỉ lấy 1–2 biến thể. |
| Ảnh chụp trong bài báo (Thanh Niên, Tuổi Trẻ/PLO, VnExpress, SGGP, Thế Giới Di Động, VietnamWorks…) và thông báo cảnh báo của các trường đại học | 24 scam | Tin tuyển dụng, chat, email, văn bản giả được các báo trích làm ví dụ cảnh báo; chép lại từ ảnh. Mỗi dòng ghi link bài báo và chú thích ảnh. |
| Bài cảnh báo trên Facebook của doanh nghiệp/trường (Vinamilk, Vinbus, Tâm Anh, CareerViet…) và ảnh chụp do người gán nhãn thu thập | 14 scam | Không ghi link cá nhân. |
| Cổng Hợp tác doanh nghiệp – ĐH Sài Gòn | 22 legit | Tin tuyển dụng thật, công khai. |
| Phòng Quan hệ đối ngoại – ĐH CNTT (UIT) | 6 legit | Thông báo học bổng/chương trình thật. |
| Smishtank Dataset I (Timko & Rahman, 2024) | 2 scam (tiếng Anh) | Chưa rõ giấy phép: **chỉ dùng nội bộ, không phát hành lại**. |

## Cách gán nhãn

- **label** quyết định theo **nguồn**: tin được nguồn (bộ dữ liệu, bài báo, đơn vị bị giả mạo) xác nhận là lừa đảo → scam; tin từ kênh chính thức → legit; nguồn mâu thuẫn hoặc có thể chỉ là tin rác → unsure. Quảng cáo cờ bạc được xếp unsure (giữ phạm vi hẹp vào lừa đảo).
- **signals** gán theo **nội dung**, kể cả với tin legit, theo định nghĩa trong `taxonomy.json`. Dấu hiệu phải được nói ra trong tin, không suy luận; tag ẩn danh (ví dụ `[MONEY]`) không phải bằng chứng.
- **hard_negative** (chỉ cho legit): tin trông giống lừa đảo bề ngoài (có tiền, link, hạn chót, OTP, "không cần kinh nghiệm", hoa hồng…). 84% mẫu legit là hard negative, vì vậy tỉ lệ báo nhầm đo được sẽ cao hơn so với hộp thư thông thường; báo cáo nên tách riêng hai nhóm.

## Ẩn danh

Thông tin cá nhân đã được thay bằng tag: `[TEN]` tên người, `[SDT]` số điện thoại, `[STK]` số tài khoản, `[EMAIL]` email cá nhân, `[DIA_CHI]` địa chỉ, `[OTP]` mã OTP, `[MAT_KHAU]` mật khẩu, `[NGAY]`, `[NUMBER]`. Các tag `[MONEY]`, `[TIME]`, `[DATE]`, `[POINT]`, `[NAME]`, `[URL]` có sẵn từ bộ dữ liệu nguồn. Giữ nguyên tên miền, email và tài khoản Telegram **của kẻ lừa đảo** vì đó là bằng chứng (S05, S11, S12) và không phải thông tin cá nhân của nạn nhân. Chỗ bị che hoặc mờ trong ảnh ghi là `[…]`.

## Cách chia dev/test

Script `scripts/split_dev_test.py` (seed 42, chạy lại ra cùng kết quả). Mục tiêu khoảng 40% dev / 60% test, với các ràng buộc:

1. Tin cùng nhóm đi nguyên khối vào một tập: cùng hội thoại, cùng chiến dịch giả danh (ví dụ Vinamilk, Mega Market, Tâm Anh), cùng mẫu thư, cùng tiền tố khuôn mẫu `[Tag_Xxx]`, tin gần giống nhau (Jaccard từ ≥ 0,5), tin tuyển dụng cùng công ty. Có 13 nhóm nhiều hơn 1 dòng.
2. 7 tin gần trùng test.csv của nguồn (SMS101–106, SMS143) bắt buộc vào test.
3. Phân tầng: tỉ lệ dev xấp xỉ 40% theo label, loại nguồn, ngôn ngữ, hard negative và từng dấu hiệu (sai lệch nằm trong khoảng 33–50%, trừ các dấu hiệu chỉ có 1–5 mẫu).

## Giới hạn đã biết

- Bộ dữ liệu nhỏ (213 mẫu dùng để đo). Khoảng tin cậy 95% cho recall quanh 90% trên test là khoảng ±7–8 điểm %.
- Dấu hiệu hiếm: S08 (1 mẫu, không đánh giá riêng), S10 (5), S06 (8), S13 (9). Kết quả cho các dấu hiệu này cần ghi kèm số mẫu.
- Lệch theo loại nguồn: chat và email chỉ có mẫu scam; tin tuyển dụng có 10 scam so với 22 legit. Model có thể dựa vào loại nguồn; nên báo cáo kết quả theo từng loại.
- Nhiều SMS scam của nguồn là tin khuôn mẫu, có thể do nguồn tổng hợp, không hẳn là tin thật bị gửi tới người dùng.
- Một số mẫu chép lại từ ảnh mờ hoặc bị gạch chéo; chỗ không chắc đã ghi `[…]` và nêu trong `label_notes`.
- Mỗi mẫu chỉ có một người gán nhãn; chưa đo độ đồng thuận giữa nhiều người gán.
- Nội dung chép từ bài báo và bài đăng mạng xã hội dùng cho mục đích nghiên cứu, có trích nguồn. Không đưa `test.jsonl` công khai lên mạng (để test không bị lọt vào dữ liệu huấn luyện của model và vì lý do bản quyền); nếu công khai repo, chỉ đăng mã nguồn và số liệu tổng hợp.
