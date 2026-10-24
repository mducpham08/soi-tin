# Báo cáo: 20261024_sonnet_v4_rules_test

Model `claude-sonnet-5-5` · prompt `v4_rules` · tập **test** · dữ liệu v1.0 · 128 mẫu

## Nhãn scam / legit

| Chỉ số | Giá trị |
|---|---|
| Recall scam (bắt được bao nhiêu % lừa đảo) | 94.1% (95% CI 88.2%–98.6%) |
| Precision scam (cảnh báo đúng bao nhiêu %) | 100.0% (95% CI 100.0%–100.0%) |
| F1 | 97.0% (95% CI 93.8%–99.3%) |
| Báo nhầm trên legit (FPR) | 0.0% (95% CI 0.0%–0.0%) |
| … trên legit thường (11 mẫu) | 0.0% |
| … trên hard negative (49 mẫu) | 0.0% |
| Accuracy | 96.9% |
| ROC-AUC / PR-AUC theo confidence | 0.998 / 0.998 |
| Ma trận | TP 64 · FN 4 · FP 0 · TN 60 |

Theo loại nguồn:

| source_type | n | recall | FPR |
|---|---|---|---|
| chat | 4 | 75.0% | – |
| document | 11 | 100.0% | 0.0% |
| email | 3 | 100.0% | – |
| job_post | 19 | 66.7% | 0.0% |
| sms | 91 | 97.9% | 0.0% |

## Dấu hiệu S01–S14

Micro: P 77.4% · R 89.7% · F1 83.1% · Macro F1 85.5% (trên 13 dấu hiệu có ≥3 mẫu, bỏ S08) · Khớp đúng cả bộ: 58.6%

| Dấu hiệu | Số mẫu vàng | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| S01 | 17 | 93.8% | 88.2% | 90.9% | 1 | 2 |
| S02 | 22 | 64.5% | 90.9% | 75.5% | 11 | 2 |
| S03 | 8 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S04 | 7 | 77.8% | 100.0% | 87.5% | 2 | 0 |
| S05 | 32 | 75.0% | 75.0% | 75.0% | 8 | 8 |
| S06 | 5 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S07 | 9 | 66.7% | 88.9% | 76.2% | 4 | 1 |
| S08 (ít mẫu) | 1 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S09 | 26 | 68.6% | 92.3% | 78.7% | 11 | 2 |
| S10 | 4 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S11 | 18 | 100.0% | 83.3% | 90.9% | 0 | 3 |
| S12 | 30 | 93.5% | 96.7% | 95.1% | 2 | 1 |
| S13 | 6 | 35.3% | 100.0% | 52.2% | 11 | 0 |
| S14 | 10 | 90.0% | 90.0% | 90.0% | 1 | 1 |

## Định dạng, bằng chứng, chi phí

- Đầu ra hợp lệ theo schema: 127/128 (99.2%); lỗi API: 0
- Nhãn mâu thuẫn với confidence: 0
- Bằng chứng có thật trong tin: 99.6% (226 bằng chứng)
- Token: {'input_tokens': 47055, 'output_tokens': 35881, 'cache_read_tokens': 1489075, 'cache_write_tokens': 11725}
- Chi phí lượt này: $0.6311 · ước tính /1.000 tin: $4.931
- Thời gian mỗi tin: trung bình 3.25s · p95 4.48s

## Phân tích lỗi (tập test: ẩn nội dung tin)

### Bỏ sót lừa đảo (FN): 4

### SMS027 (sms) – vàng **scam**, dự đoán **legit** (conf 0.50)
- Dấu hiệu vàng: ['S01', 'S09', 'S12', 'S14'] · dự đoán: – · **thiếu** ['S01', 'S09', 'S12', 'S14']
- Lỗi: dấu hiệu bị lặp

### CHAT001 (chat) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S05'] · dự đoán: – · **thiếu** ['S05']

### JOB023 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.30)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S11'] · **thiếu** ['S05']

### JOB030 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.30)
- Dấu hiệu vàng: ['S05'] · dự đoán: ['S07'] · **thiếu** ['S05'] · **thừa** ['S07']


### Báo nhầm (FP): 0


### Đúng nhãn nhưng sai dấu hiệu: 49

### SMS007 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S05', 'S12', 'S14'] · **thừa** ['S14']

### SMS009 (sms) – vàng **scam**, dự đoán **scam** (conf 0.75)
- Dấu hiệu vàng: ['S02'] · dự đoán: ['S02', 'S05'] · **thừa** ['S05']

### SMS020 (sms) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S05', 'S09', 'S11'] · dự đoán: ['S05', 'S07', 'S09', 'S11'] · **thừa** ['S07']

### SMS021 (sms) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS023 (sms) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S02', 'S05', 'S07', 'S12'] · dự đoán: ['S02', 'S07', 'S12'] · **thiếu** ['S05']

### SMS038 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S04', 'S12'] · dự đoán: ['S04', 'S09', 'S12'] · **thừa** ['S09']

### SMS074 (sms) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S02', 'S11', 'S14'] · dự đoán: ['S11', 'S12', 'S14'] · **thiếu** ['S02'] · **thừa** ['S12']

### SMS075 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S03', 'S12'] · dự đoán: ['S03', 'S12', 'S13'] · **thừa** ['S13']

### SMS082 (sms) – vàng **legit**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### DOC002 (document) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S01'] · dự đoán: ['S01', 'S02'] · **thừa** ['S02']

### DOC008 (document) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S01', 'S02', 'S09'] · dự đoán: ['S01', 'S02', 'S05', 'S09'] · **thừa** ['S05']

### DOC009 (document) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S01', 'S02', 'S09'] · dự đoán: ['S01', 'S02', 'S04', 'S09'] · **thừa** ['S04']

### SMS092 (sms) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S06', 'S11'] · dự đoán: ['S06', 'S09', 'S11'] · **thừa** ['S09']

### SMS093 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S03'] · dự đoán: ['S02', 'S03', 'S05'] · **thừa** ['S02', 'S05']

### SMS095 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S03', 'S05', 'S12', 'S14'] · dự đoán: ['S03', 'S05', 'S12', 'S13', 'S14'] · **thừa** ['S13']

### SMS101 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S08', 'S11'] · dự đoán: ['S08', 'S11', 'S13'] · **thừa** ['S13']

### SMS102 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S01', 'S06', 'S10'] · dự đoán: ['S01', 'S06', 'S09', 'S10'] · **thừa** ['S09']

### SMS103 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S04', 'S09', 'S10', 'S11'] · dự đoán: ['S04', 'S09', 'S10'] · **thiếu** ['S11']

### SMS105 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S01', 'S06'] · dự đoán: ['S01', 'S06', 'S09'] · **thừa** ['S09']

### SMS106 (sms) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S01', 'S06'] · dự đoán: ['S01', 'S06', 'S09'] · **thừa** ['S09']

### SMS108 (sms) – vàng **scam**, dự đoán **scam** (conf 0.98)
- Dấu hiệu vàng: ['S02', 'S07', 'S10', 'S11'] · dự đoán: ['S02', 'S05', 'S07', 'S10', 'S12'] · **thiếu** ['S11'] · **thừa** ['S05', 'S12']

### SMS109 (sms) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S07'] · dự đoán: ['S07', 'S09'] · **thừa** ['S09']

### SMS123 (sms) – vàng **legit**, dự đoán **legit** (conf 0.05)
- Dấu hiệu vàng: ['S01', 'S09'] · dự đoán: ['S09'] · **thiếu** ['S01']

### SMS124 (sms) – vàng **legit**, dự đoán **legit** (conf 0.04)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS125 (sms) – vàng **legit**, dự đoán **legit** (conf 0.08)
- Dấu hiệu vàng: – · dự đoán: ['S01'] · **thừa** ['S01']

### SMS134 (sms) – vàng **legit**, dự đoán **legit** (conf 0.07)
- Dấu hiệu vàng: – · dự đoán: ['S09'] · **thừa** ['S09']

### SMS138 (sms) – vàng **legit**, dự đoán **legit** (conf 0.04)
- Dấu hiệu vàng: ['S02'] · dự đoán: – · **thiếu** ['S02']

### JOB019 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: ['S05', 'S09'] · dự đoán: – · **thiếu** ['S05', 'S09']

### DOC017 (document) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S01'] · dự đoán: ['S01', 'S13'] · **thừa** ['S13']

### EMAIL001 (email) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S02', 'S05', 'S11'] · **thừa** ['S02']

### JOB024 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S13'] · dự đoán: ['S02', 'S13'] · **thừa** ['S02']

### JOB025 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S03', 'S13'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### CHAT002 (chat) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S03', 'S13'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### CHAT003 (chat) – vàng **scam**, dự đoán **scam** (conf 0.99)
- Dấu hiệu vàng: ['S01', 'S03'] · dự đoán: ['S01', 'S02', 'S03', 'S13'] · **thừa** ['S02', 'S13']

### SMS146 (sms) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S09', 'S11'] · dự đoán: ['S05', 'S09', 'S11'] · **thừa** ['S05']

### SMS147 (sms) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S01', 'S05', 'S09', 'S11'] · dự đoán: ['S01', 'S05', 'S09'] · **thiếu** ['S11']

### SMS149 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S07', 'S09', 'S12'] · dự đoán: ['S05', 'S07', 'S09', 'S12'] · **thừa** ['S05']

### SMS150 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S05', 'S07', 'S09', 'S12', 'S14'] · dự đoán: ['S05', 'S09', 'S12', 'S14'] · **thiếu** ['S07']

### SMS152 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S02', 'S05', 'S11'] · **thừa** ['S02']

### SMS153 (sms) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S04'] · dự đoán: ['S04', 'S07'] · **thừa** ['S07']

### SMS155 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S05', 'S12', 'S13'] · **thừa** ['S13']

### CHAT007 (chat) – vàng **scam**, dự đoán **scam** (conf 0.93)
- Dấu hiệu vàng: ['S02', 'S05', 'S11'] · dự đoán: ['S02', 'S05', 'S11', 'S13'] · **thừa** ['S13']

### JOB029 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S02', 'S05'] · dự đoán: ['S02', 'S13'] · **thiếu** ['S05'] · **thừa** ['S13']

### EMAIL002 (email) – vàng **scam**, dự đoán **scam** (conf 0.88)
- Dấu hiệu vàng: ['S05', 'S11', 'S12'] · dự đoán: ['S05', 'S09', 'S11', 'S12'] · **thừa** ['S09']

### EMAIL005 (email) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S05', 'S09', 'S11', 'S12'] · dự đoán: ['S05', 'S07', 'S09', 'S11', 'S12'] · **thừa** ['S07']

### DOC018 (document) – vàng **scam**, dự đoán **scam** (conf 0.96)
- Dấu hiệu vàng: ['S01', 'S02'] · dự đoán: ['S01', 'S02', 'S04', 'S05', 'S13'] · **thừa** ['S04', 'S05', 'S13']

### DOC019 (document) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S03'] · dự đoán: ['S03', 'S05'] · **thừa** ['S05']

### DOC020 (document) – vàng **scam**, dự đoán **scam** (conf 0.80)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S02', 'S05', 'S12'] · **thừa** ['S02']

### SMS157 (sms) – vàng **scam**, dự đoán **scam** (conf 0.97)
- Dấu hiệu vàng: ['S03', 'S05', 'S11'] · dự đoán: ['S02', 'S03', 'S05', 'S09', 'S11'] · **thừa** ['S02', 'S09']


### Bằng chứng không có trong tin: 1

- DOC018 S01: “…”
