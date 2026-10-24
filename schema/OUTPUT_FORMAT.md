# Định dạng đầu ra của model (v1)

Với mỗi tin, model trả về **đúng một object JSON**, không kèm chữ nào khác. Schema đầy đủ: `output.schema.json`.

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `label` | `"scam"` \| `"legit"` | Kết luận cuối cùng. Không có "unsure": model buộc phải chọn. |
| `confidence` | số 0–1 | Mức chắc chắn rằng tin **là scam** (0 = chắc chắn legit, 1 = chắc chắn scam). Dùng để vẽ đường precision–recall và chọn ngưỡng cảnh báo. |
| `signals` | mảng | Các dấu hiệu S01–S14 tìm thấy, mỗi phần tử gồm `id` và `evidence`. Có thể rỗng. |
| `signals[].evidence` | chuỗi ≤ 200 ký tự | Trích **nguyên văn** một đoạn trong tin. Script chấm điểm sẽ kiểm tra đoạn này có thật trong tin không (chống bịa). |
| `explanation` | chuỗi ≤ 600 ký tự | 1–3 câu tiếng Việt cho người dùng: vì sao, và nên làm gì. |

## Quy tắc quan trọng (giống quy tắc gán nhãn của bộ dữ liệu)

1. **Dấu hiệu gán theo nội dung, độc lập với nhãn.** Tin legit vẫn có thể có dấu hiệu (ví dụ thông báo học bổng thật có hạn nộp → S09). Đó chính là hard negative: model phải nhận ra dấu hiệu nhưng vẫn kết luận legit khi tổng thể hợp lệ.
2. **Định nghĩa dấu hiệu** lấy từ `data/v1.0/taxonomy.json` (cột "Không gán khi" quan trọng không kém định nghĩa).
3. Các tag ẩn danh như `[MONEY]`, `[SDT]`, `[TEN]`, `[OTP]` là chỗ dữ liệu đã bị che, **không phải bằng chứng**. Ví dụ `[MONEY]/ngày` không đủ để gán S02.

## Ví dụ

Hai tin tự viết (giống các tin mẫu trong app), không lấy từ bộ dữ liệu.

**Tin OTP thật – legit, hard negative** (có OTP, số tiền, thời hạn nhưng không đòi gì)
> Ma OTP cua Quy khach la 482913, dung de xac thuc giao dich chuyen tien 2.000.000 VND, hieu luc trong 3 phut. Tuyet doi KHONG cung cap ma nay cho bat ky ai, ke ca nhan vien ngan hang.

```json
{
  "label": "legit",
  "confidence": 0.1,
  "signals": [],
  "explanation": "Đây là tin ngân hàng gửi mã OTP cho giao dịch của chính bạn và còn nhắc không đưa mã cho ai; tin không đòi gửi lại mã hay bấm link. Nếu bạn không hề thực hiện giao dịch này, hãy gọi ngay tổng đài in sau thẻ."
}
```

**Giả ngân hàng – scam**
> [VCB] Tai khoan cua Quy khach se bi tam khoa trong 24h do chua cap nhat sinh trac hoc theo quy dinh moi. Vui long cap nhat ngay tai: https://vietcombank-xacthuc.top/kyc de tranh gian doan giao dich.

```json
{
  "label": "scam",
  "confidence": 0.95,
  "signals": [
    {
      "id": "S05",
      "evidence": "[VCB] Tai khoan cua Quy khach"
    },
    {
      "id": "S09",
      "evidence": "se bi tam khoa trong 24h"
    },
    {
      "id": "S12",
      "evidence": "https://vietcombank-xacthuc.top/kyc"
    }
  ],
  "explanation": "Tin tự xưng Vietcombank nhưng dẫn tới tên miền vietcombank-xacthuc.top, không phải tên miền của ngân hàng, và doạ khoá tài khoản để ép bạn bấm link. Đừng bấm link; hãy mở ứng dụng ngân hàng hoặc gọi tổng đài in sau thẻ."
}
```

## Cách chấm (`scripts/score.py`)

- **Nhãn:** precision / recall / F1 cho `scam`; tỉ lệ báo nhầm (FPR) tính riêng cho legit thường và legit hard negative. Mẫu `unsure` không dùng.
- **Dấu hiệu:** so `signals[].id` với nhãn vàng, tính precision / recall từng S01–S14 (micro và macro), luôn kèm số mẫu. S08 chỉ có 1 mẫu nên không đánh giá riêng.
- **Bằng chứng:** tỉ lệ `evidence` thực sự xuất hiện trong tin (so khớp sau khi chuẩn hóa khoảng trắng, hoa/thường).
- **Định dạng:** tỉ lệ đầu ra hợp lệ theo schema; đầu ra lỗi được tính là sai.
- `confidence` dùng cho đường PR/ROC; nhãn chính vẫn lấy từ `label`.
