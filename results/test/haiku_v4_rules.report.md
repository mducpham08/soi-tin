# Báo cáo: 20261024_haiku_v4_rules_test

Model `claude-haiku-5-5` · prompt `v4_rules` · tập **test** · dữ liệu v1.0 · 128 mẫu

## Nhãn scam / legit

| Chỉ số | Giá trị |
|---|---|
| Recall scam (bắt được bao nhiêu % lừa đảo) | 92.6% (95% CI 86.1%–98.5%) |
| Precision scam (cảnh báo đúng bao nhiêu %) | 95.5% (95% CI 89.6%–100.0%) |
| F1 | 94.0% (95% CI 89.7%–97.7%) |
| Báo nhầm trên legit (FPR) | 5.0% (95% CI 0.0%–11.3%) |
| … trên legit thường (11 mẫu) | 0.0% |
| … trên hard negative (49 mẫu) | 6.1% |
| Accuracy | 93.8% |
| ROC-AUC / PR-AUC theo confidence | 0.969 / 0.977 |
| Ma trận | TP 63 · FN 5 · FP 3 · TN 57 |

Theo loại nguồn:

| source_type | n | recall | FPR |
|---|---|---|---|
| chat | 4 | 75.0% | – |
| document | 11 | 75.0% | 0.0% |
| email | 3 | 100.0% | – |
| job_post | 19 | 66.7% | 0.0% |
| sms | 91 | 100.0% | 6.8% |

## Dấu hiệu S01–S14

Micro: P 70.1% · R 87.7% · F1 77.9% · Macro F1 79.3% (trên 13 dấu hiệu có ≥3 mẫu, bỏ S08) · Khớp đúng cả bộ: 49.2%

| Dấu hiệu | Số mẫu vàng | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| S01 | 17 | 93.3% | 82.4% | 87.5% | 1 | 3 |
| S02 | 22 | 52.9% | 81.8% | 64.3% | 16 | 4 |
| S03 | 8 | 66.7% | 100.0% | 80.0% | 4 | 0 |
| S04 | 7 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S05 | 32 | 83.3% | 62.5% | 71.4% | 4 | 12 |
| S06 | 5 | 83.3% | 100.0% | 90.9% | 1 | 0 |
| S07 | 9 | 69.2% | 100.0% | 81.8% | 4 | 0 |
| S08 (ít mẫu) | 1 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S09 | 26 | 60.5% | 88.5% | 71.9% | 15 | 3 |
| S10 | 4 | 75.0% | 75.0% | 75.0% | 1 | 1 |
| S11 | 18 | 90.0% | 100.0% | 94.7% | 2 | 0 |
| S12 | 30 | 82.9% | 96.7% | 89.2% | 6 | 1 |
| S13 | 6 | 33.3% | 100.0% | 50.0% | 12 | 0 |
| S14 | 10 | 58.8% | 100.0% | 74.1% | 7 | 0 |

## Định dạng, bằng chứng, chi phí

- Đầu ra hợp lệ theo schema: 127/128 (99.2%); lỗi API: 0
- Nhãn mâu thuẫn với confidence: 0
- Bằng chứng có thật trong tin: 99.6% (244 bằng chứng)
- Token: {'input_tokens': 71631, 'output_tokens': 45935, 'cache_read_tokens': 1446530, 'cache_write_tokens': 11390}
- Chi phí lượt này: $0.0460 · ước tính /1.000 tin: $0.360
- Thời gian mỗi tin: trung bình 2.28s · p95 3.25s

## Phân tích lỗi (tập test: ẩn nội dung tin)

### Bỏ sót lừa đảo (FN): 5

### CHAT001 (chat) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S05'] · dự đoán: – · **thiếu** ['S05']

### DOC017 (document) – vàng **scam**, dự đoán **legit** (conf 0.50)
- Dấu hiệu vàng: ['S01'] · dự đoán: – · **thiếu** ['S01']
- Lỗi: dấu hiệu bị lặp

### JOB023 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.30)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S02', 'S11'] · **thiếu** ['S05'] · **thừa** ['S02']

### JOB030 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: ['S05'] · dự đoán: ['S12'] · **thiếu** ['S05'] · **thừa** ['S12']

### DOC020 (document) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: – · **thiếu** ['S05', 'S12']


### Báo nhầm (FP): 3

### SMS087 (sms) – vàng **legit**, dự đoán **scam** (conf 0.72) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S05', 'S12'] · **thừa** ['S05', 'S12']

### SMS109 (sms) – vàng **legit**, dự đoán **scam** (conf 0.82) · hard negative
- Dấu hiệu vàng: ['S07'] · dự đoán: ['S07', 'S09', 'S12'] · **thừa** ['S09', 'S12']

### SMS110 (sms) – vàng **legit**, dự đoán **scam** (conf 0.85) · hard negative
- Dấu hiệu vàng: ['S04', 'S09'] · dự đoán: ['S04', 'S09']


### Đúng nhãn nhưng sai dấu hiệu: 58

### SMS002 (sms) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS007 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S05', 'S12', 'S13'] · **thừa** ['S13']

### SMS009 (sms) – vàng **scam**, dự đoán **scam** (conf 0.72)
- Dấu hiệu vàng: ['S02'] · dự đoán: ['S02', 'S11', 'S14'] · **thừa** ['S11', 'S14']

### SMS016 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS020 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S05', 'S09', 'S11'] · dự đoán: ['S05', 'S07', 'S09', 'S11'] · **thừa** ['S07']

### SMS023 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S02', 'S05', 'S07', 'S12'] · dự đoán: ['S02', 'S07', 'S12'] · **thiếu** ['S05']

### SMS025 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S02', 'S05', 'S12'] · dự đoán: ['S02', 'S12', 'S14'] · **thiếu** ['S05'] · **thừa** ['S14']

### SMS038 (sms) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S04', 'S12'] · dự đoán: ['S04', 'S09', 'S12'] · **thừa** ['S09']

### SMS040 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS044 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S04', 'S09', 'S12'] · dự đoán: ['S04', 'S09', 'S12'] · **thiếu** ['S01']

### SMS045 (sms) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S14'] · **thừa** ['S14']

### SMS049 (sms) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S02', 'S11', 'S13'] · dự đoán: ['S02', 'S03', 'S11', 'S13'] · **thừa** ['S03']

### SMS050 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S02', 'S12'] · dự đoán: ['S02', 'S12', 'S14'] · **thừa** ['S14']

### SMS052 (sms) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S11'] · **thừa** ['S11']

### SMS054 (sms) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S12', 'S13', 'S14'] · dự đoán: ['S03', 'S12', 'S13', 'S14'] · **thừa** ['S03']

### SMS055 (sms) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S05', 'S12', 'S13', 'S14'] · dự đoán: ['S12', 'S13', 'S14'] · **thiếu** ['S05']

### SMS064 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS074 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S02', 'S11', 'S14'] · dự đoán: ['S11', 'S12', 'S14'] · **thiếu** ['S02'] · **thừa** ['S12']

### SMS075 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S03', 'S12'] · dự đoán: ['S02', 'S03', 'S12', 'S14'] · **thừa** ['S02', 'S14']

### SMS080 (sms) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S02', 'S05', 'S09', 'S12'] · dự đoán: ['S05', 'S09', 'S12'] · **thiếu** ['S02']

### SMS082 (sms) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S14'] · **thừa** ['S14']

### DOC002 (document) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S01'] · dự đoán: ['S01', 'S09'] · **thừa** ['S09']

### DOC009 (document) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S01', 'S02', 'S09'] · dự đoán: ['S01', 'S02', 'S07', 'S09'] · **thừa** ['S07']

### SMS093 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S03'] · dự đoán: ['S02', 'S03', 'S05', 'S12', 'S13'] · **thừa** ['S02', 'S05', 'S12', 'S13']

### SMS095 (sms) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S03', 'S05', 'S12', 'S14'] · dự đoán: ['S02', 'S03', 'S12', 'S13', 'S14'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### SMS098 (sms) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S03'] · **thừa** ['S03']

### SMS099 (sms) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S09', 'S12'] · **thừa** ['S09', 'S12']

### DOC013 (document) – vàng **legit**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S09'] · dự đoán: – · **thiếu** ['S09']

### SMS104 (sms) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S01', 'S06', 'S10'] · dự đoán: ['S01', 'S06'] · **thiếu** ['S10']

### SMS108 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S02', 'S07', 'S10', 'S11'] · dự đoán: ['S02', 'S05', 'S07', 'S10', 'S11'] · **thừa** ['S05']

### SMS118 (sms) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: ['S02', 'S09'] · dự đoán: ['S09'] · **thiếu** ['S02']

### SMS123 (sms) – vàng **legit**, dự đoán **legit** (conf 0.30)
- Dấu hiệu vàng: ['S01', 'S09'] · dự đoán: ['S01'] · **thiếu** ['S09']

### SMS125 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS133 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S14'] · **thừa** ['S14']

### SMS134 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S09'] · **thừa** ['S02', 'S09']

### SMS138 (sms) – vàng **legit**, dự đoán **legit** (conf 0.12)
- Dấu hiệu vàng: ['S02'] · dự đoán: – · **thiếu** ['S02']

### SMS142 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### JOB001 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.30)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### JOB002 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### JOB006 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.25)
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S09'] · **thừa** ['S02', 'S09']

### JOB019 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.30)
- Dấu hiệu vàng: ['S05', 'S09'] · dự đoán: ['S05', 'S13'] · **thiếu** ['S09'] · **thừa** ['S13']

### EMAIL001 (email) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S05', 'S11', 'S13'] · **thừa** ['S13']

### JOB024 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.70)
- Dấu hiệu vàng: ['S13'] · dự đoán: ['S02', 'S13'] · **thừa** ['S02']

### JOB025 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S03', 'S13'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### CHAT002 (chat) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S03', 'S05', 'S13'] · **thừa** ['S02', 'S13']

### CHAT003 (chat) – vàng **scam**, dự đoán **scam** (conf 0.98)
- Dấu hiệu vàng: ['S01', 'S03'] · dự đoán: ['S01', 'S02', 'S03'] · **thừa** ['S02']

### SMS147 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S01', 'S05', 'S09', 'S11'] · dự đoán: ['S09', 'S11'] · **thiếu** ['S01', 'S05']

### SMS148 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S01'] · dự đoán: ['S01', 'S06'] · **thừa** ['S06']

### SMS152 (sms) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S02', 'S05', 'S11', 'S13'] · **thừa** ['S02', 'S13']

### SMS153 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S04'] · dự đoán: ['S04', 'S07'] · **thừa** ['S07']

### SMS155 (sms) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S02', 'S12', 'S13'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### CHAT007 (chat) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S02', 'S05', 'S11'] · dự đoán: ['S02', 'S05', 'S11', 'S13'] · **thừa** ['S13']

### JOB029 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S02', 'S05'] · dự đoán: ['S02', 'S09'] · **thiếu** ['S05'] · **thừa** ['S09']

### JOB032 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S11', 'S13'] · dự đoán: ['S01', 'S02', 'S10', 'S11', 'S13'] · **thừa** ['S01', 'S10']

### EMAIL002 (email) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S05', 'S11', 'S12'] · dự đoán: ['S05', 'S07', 'S09', 'S11', 'S12'] · **thừa** ['S07', 'S09']

### DOC018 (document) – vàng **scam**, dự đoán **scam** (conf 0.92)
- Dấu hiệu vàng: ['S01', 'S02'] · dự đoán: ['S01', 'S02', 'S03', 'S05'] · **thừa** ['S03', 'S05']

### DOC019 (document) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S03'] · dự đoán: ['S02', 'S03', 'S13'] · **thừa** ['S02', 'S13']

### SMS157 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S03', 'S05', 'S11'] · dự đoán: ['S02', 'S03', 'S05', 'S09', 'S11', 'S13'] · **thừa** ['S02', 'S09', 'S13']


### Bằng chứng không có trong tin: 1

- SMS093 S03: “…”
