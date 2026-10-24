# Kết quả đánh giá (số liệu tổng hợp)

Thư mục `runs/` (có nội dung tin và câu trả lời của model) không được công khai. Ở đây chỉ có số liệu tổng hợp:

- `compare_test.md`: bảng so sánh 4 hệ thống trên tập test v1.0 (128 tin), prompt chốt `v4_rules`.
- `compare_dev.md`: các lượt chạy trên tập dev (85 tin) trong lúc sửa prompt v0 → v4.
- `test/*.scores.json`, `test/*.report.md`: chỉ số chi tiết của từng hệ thống trên test (theo nhãn, theo loại nguồn, theo từng dấu hiệu S01–S14, chi phí, thời gian). Phần phân tích lỗi chỉ ghi mã tin, không có nội dung tin.

Cách tạo lại: `python scripts/score.py runs/<lượt>` rồi `python scripts/compare.py --split test` (cần bộ dữ liệu, không kèm trong repo).
