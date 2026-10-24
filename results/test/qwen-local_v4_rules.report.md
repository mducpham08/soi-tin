# Báo cáo: 20261024_qwen-local_v4_rules_test

Model `qwen3.5:9b` · prompt `v4_rules` · tập **test** · dữ liệu v1.0 · 128 mẫu

## Nhãn scam / legit

| Chỉ số | Giá trị |
|---|---|
| Recall scam (bắt được bao nhiêu % lừa đảo) | 89.7% (95% CI 82.5%–96.7%) |
| Precision scam (cảnh báo đúng bao nhiêu %) | 92.4% (95% CI 85.5%–98.3%) |
| F1 | 91.0% (95% CI 85.7%–95.9%) |
| Báo nhầm trên legit (FPR) | 8.3% (95% CI 1.8%–15.8%) |
| … trên legit thường (11 mẫu) | 0.0% |
| … trên hard negative (49 mẫu) | 10.2% |
| Accuracy | 90.6% |
| ROC-AUC / PR-AUC theo confidence | 0.931 / 0.941 |
| Ma trận | TP 61 · FN 7 · FP 5 · TN 55 |

Theo loại nguồn:

| source_type | n | recall | FPR |
|---|---|---|---|
| chat | 4 | 75.0% | – |
| document | 11 | 75.0% | 0.0% |
| email | 3 | 100.0% | – |
| job_post | 19 | 66.7% | 7.7% |
| sms | 91 | 95.7% | 9.1% |

## Dấu hiệu S01–S14

Micro: P 61.6% · R 64.1% · F1 62.8% · Macro F1 63.4% (trên 13 dấu hiệu có ≥3 mẫu, bỏ S08) · Khớp đúng cả bộ: 40.6%

| Dấu hiệu | Số mẫu vàng | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| S01 | 17 | 58.3% | 82.4% | 68.3% | 10 | 3 |
| S02 | 22 | 47.1% | 72.7% | 57.1% | 18 | 6 |
| S03 | 8 | 50.0% | 50.0% | 50.0% | 4 | 4 |
| S04 | 7 | 75.0% | 85.7% | 80.0% | 2 | 1 |
| S05 | 32 | 55.6% | 46.9% | 50.8% | 12 | 17 |
| S06 | 5 | 83.3% | 100.0% | 90.9% | 1 | 0 |
| S07 | 9 | 66.7% | 44.4% | 53.3% | 2 | 5 |
| S08 (ít mẫu) | 1 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S09 | 26 | 53.8% | 53.8% | 53.8% | 12 | 12 |
| S10 | 4 | 50.0% | 50.0% | 50.0% | 2 | 2 |
| S11 | 18 | 88.9% | 44.4% | 59.3% | 1 | 10 |
| S12 | 30 | 82.8% | 80.0% | 81.4% | 5 | 6 |
| S13 | 6 | 41.7% | 83.3% | 55.6% | 7 | 1 |
| S14 | 10 | 77.8% | 70.0% | 73.7% | 2 | 3 |

## Định dạng, bằng chứng, chi phí

- Đầu ra hợp lệ theo schema: 128/128 (100.0%); lỗi API: 0
- Nhãn mâu thuẫn với confidence: 0
- Bằng chứng có thật trong tin: 88.2% (203 bằng chứng)
- Token: {'input_tokens': 726914, 'output_tokens': 25818, 'cache_read_tokens': 0, 'cache_write_tokens': 0}
- Chi phí lượt này: $0.0000 · ước tính /1.000 tin: $0.000
- Thời gian mỗi tin: trung bình 8.80s · p95 13.28s

## Phân tích lỗi (tập test: ẩn nội dung tin)

### Bỏ sót lừa đảo (FN): 7

### SMS009 (sms) – vàng **scam**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S02'] · dự đoán: – · **thiếu** ['S02']

### CHAT001 (chat) – vàng **scam**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S05'] · dự đoán: – · **thiếu** ['S05']

### JOB023 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: – · **thiếu** ['S05', 'S11']

### SMS146 (sms) – vàng **scam**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S09', 'S11'] · dự đoán: – · **thiếu** ['S09', 'S11']

### JOB030 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: ['S05'] · dự đoán: – · **thiếu** ['S05']

### DOC019 (document) – vàng **scam**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S03'] · dự đoán: – · **thiếu** ['S03']

### DOC020 (document) – vàng **scam**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: – · **thiếu** ['S05', 'S12']


### Báo nhầm (FP): 5

### SMS082 (sms) – vàng **legit**, dự đoán **scam** (conf 0.95) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S01', 'S02', 'S11'] · **thừa** ['S01', 'S02', 'S11']

### SMS087 (sms) – vàng **legit**, dự đoán **scam** (conf 0.85) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S12'] · **thừa** ['S02', 'S12']

### SMS098 (sms) – vàng **legit**, dự đoán **scam** (conf 0.85) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S03'] · **thừa** ['S03']

### SMS099 (sms) – vàng **legit**, dự đoán **scam** (conf 0.95) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S12'] · **thừa** ['S02', 'S12']

### JOB001 (job_post) – vàng **legit**, dự đoán **scam** (conf 0.85) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S09', 'S13'] · **thừa** ['S02', 'S09', 'S13']


### Đúng nhãn nhưng sai dấu hiệu: 64

### SMS002 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS003 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S07', 'S09', 'S12', 'S14'] · dự đoán: ['S05', 'S12', 'S14'] · **thiếu** ['S07', 'S09']

### SMS005 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S04', 'S07', 'S12'] · dự đoán: ['S04', 'S05', 'S12'] · **thiếu** ['S07'] · **thừa** ['S05']

### SMS007 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S05', 'S12', 'S13'] · **thừa** ['S13']

### SMS011 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S04', 'S09', 'S12'] · dự đoán: ['S04', 'S05', 'S09'] · **thiếu** ['S12'] · **thừa** ['S05']

### SMS020 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S09', 'S11'] · dự đoán: ['S01', 'S05', 'S09'] · **thiếu** ['S11'] · **thừa** ['S01']

### SMS023 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S05', 'S07', 'S12'] · dự đoán: ['S01', 'S02', 'S05', 'S07', 'S12'] · **thừa** ['S01']

### SMS024 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S05', 'S12'] · dự đoán: ['S02', 'S12'] · **thiếu** ['S05']

### SMS026 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S09', 'S12'] · dự đoán: ['S01', 'S02', 'S05', 'S12'] · **thiếu** ['S09'] · **thừa** ['S01', 'S02', 'S05']

### SMS027 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S09', 'S12', 'S14'] · dự đoán: ['S01', 'S09', 'S12'] · **thiếu** ['S14']

### SMS032 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S07', 'S09', 'S12', 'S14'] · dự đoán: ['S05', 'S07', 'S14'] · **thiếu** ['S09', 'S12']

### SMS040 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S01', 'S02', 'S09'] · **thừa** ['S01', 'S02', 'S09']

### SMS044 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S04', 'S09', 'S12'] · dự đoán: ['S04', 'S05', 'S12'] · **thiếu** ['S01', 'S09'] · **thừa** ['S05']

### SMS050 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S12'] · dự đoán: ['S02', 'S05', 'S12'] · **thừa** ['S05']

### SMS052 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S05'] · **thừa** ['S05']

### SMS053 (sms) – vàng **scam**, dự đoán **scam** (conf 0.90)
- Dấu hiệu vàng: ['S05', 'S12', 'S14'] · dự đoán: ['S09', 'S12', 'S14'] · **thiếu** ['S05'] · **thừa** ['S09']

### SMS054 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S12', 'S13', 'S14'] · dự đoán: ['S03', 'S05', 'S12', 'S14'] · **thiếu** ['S13'] · **thừa** ['S03', 'S05']

### SMS055 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S12', 'S13', 'S14'] · dự đoán: ['S03', 'S12', 'S13', 'S14'] · **thiếu** ['S05'] · **thừa** ['S03']

### SMS063 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S02', 'S05', 'S07', 'S12'] · dự đoán: ['S01'] · **thiếu** ['S02', 'S05', 'S07', 'S12']

### SMS064 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S01', 'S02', 'S09'] · **thừa** ['S01', 'S02', 'S09']

### SMS065 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S09', 'S12'] · dự đoán: ['S09', 'S12'] · **thiếu** ['S05']

### SMS074 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S11', 'S14'] · dự đoán: ['S12', 'S14'] · **thiếu** ['S02', 'S11'] · **thừa** ['S12']

### SMS075 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S03', 'S12'] · dự đoán: ['S02', 'S05', 'S12'] · **thiếu** ['S03'] · **thừa** ['S02', 'S05']

### SMS080 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S05', 'S09', 'S12'] · dự đoán: ['S02', 'S05', 'S12'] · **thiếu** ['S09']

### SMS085 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S09', 'S12', 'S14'] · dự đoán: ['S09', 'S12', 'S14'] · **thiếu** ['S05']

### DOC008 (document) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S02', 'S09'] · dự đoán: ['S01', 'S05', 'S12'] · **thiếu** ['S02', 'S09'] · **thừa** ['S05', 'S12']

### SMS092 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S06', 'S11'] · dự đoán: ['S06', 'S10'] · **thiếu** ['S11'] · **thừa** ['S10']

### SMS093 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S03'] · dự đoán: ['S02', 'S03', 'S12'] · **thừa** ['S02', 'S12']

### SMS095 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S03', 'S05', 'S12', 'S14'] · dự đoán: ['S03', 'S05', 'S12'] · **thiếu** ['S14']

### DOC012 (document) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S09'] · dự đoán: ['S01', 'S09'] · **thừa** ['S01']

### DOC013 (document) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S09'] · dự đoán: – · **thiếu** ['S09']

### DOC014 (document) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S09'] · dự đoán: – · **thiếu** ['S09']

### SMS103 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S04', 'S09', 'S10', 'S11'] · dự đoán: ['S04', 'S09', 'S10'] · **thiếu** ['S11']

### SMS104 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S06', 'S10'] · dự đoán: ['S01', 'S06'] · **thiếu** ['S10']

### SMS108 (sms) – vàng **scam**, dự đoán **scam** (conf 0.98)
- Dấu hiệu vàng: ['S02', 'S07', 'S10', 'S11'] · dự đoán: ['S02', 'S05', 'S07'] · **thiếu** ['S10', 'S11'] · **thừa** ['S05']

### SMS109 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: ['S07'] · dự đoán: ['S01', 'S09'] · **thiếu** ['S07'] · **thừa** ['S01', 'S09']

### SMS110 (sms) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S04', 'S09'] · dự đoán: ['S07', 'S09'] · **thiếu** ['S04'] · **thừa** ['S07']

### SMS118 (sms) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S02', 'S09'] · dự đoán: – · **thiếu** ['S02', 'S09']

### SMS123 (sms) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S01', 'S09'] · dự đoán: – · **thiếu** ['S01', 'S09']

### SMS125 (sms) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S09'] · **thừa** ['S02', 'S09']

### SMS134 (sms) – vàng **legit**, dự đoán **legit** (conf 0.20)
- Dấu hiệu vàng: – · dự đoán: ['S01', 'S09'] · **thừa** ['S01', 'S09']

### SMS138 (sms) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S02'] · dự đoán: – · **thiếu** ['S02']

### JOB006 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S09'] · **thừa** ['S02', 'S09']

### JOB019 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.10)
- Dấu hiệu vàng: ['S05', 'S09'] · dự đoán: – · **thiếu** ['S05', 'S09']

### DOC017 (document) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01'] · dự đoán: ['S01', 'S09'] · **thừa** ['S09']

### JOB024 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S13'] · dự đoán: ['S02', 'S13'] · **thừa** ['S02']

### SMS143 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S11', 'S13'] · dự đoán: ['S02', 'S09', 'S11', 'S13'] · **thừa** ['S09']

### JOB025 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S13'] · **thiếu** ['S03', 'S05'] · **thừa** ['S02', 'S13']

### CHAT002 (chat) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S03', 'S13'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### CHAT003 (chat) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S03'] · dự đoán: ['S01', 'S02', 'S03'] · **thừa** ['S02']

### SMS147 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S05', 'S09', 'S11'] · dự đoán: ['S01', 'S04', 'S09'] · **thiếu** ['S05', 'S11'] · **thừa** ['S04']

### SMS148 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01'] · dự đoán: ['S01', 'S06'] · **thừa** ['S06']

### SMS149 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S07', 'S09', 'S12'] · dự đoán: ['S04', 'S05', 'S07', 'S09'] · **thiếu** ['S12'] · **thừa** ['S04', 'S05']

### SMS150 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S07', 'S09', 'S12', 'S14'] · dự đoán: ['S01', 'S05', 'S09'] · **thiếu** ['S07', 'S12', 'S14'] · **thừa** ['S01']

### SMS152 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S02', 'S05', 'S11', 'S13'] · **thừa** ['S02', 'S13']

### SMS153 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S04'] · dự đoán: ['S04', 'S07', 'S10'] · **thừa** ['S07', 'S10']

### SMS155 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S12', 'S13'] · **thiếu** ['S05'] · **thừa** ['S13']

### CHAT007 (chat) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S05', 'S11'] · dự đoán: ['S02', 'S03', 'S05', 'S11'] · **thừa** ['S03']

### JOB029 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S05'] · dự đoán: ['S02', 'S09'] · **thiếu** ['S05'] · **thừa** ['S09']

### JOB032 (job_post) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S02', 'S11', 'S13'] · dự đoán: ['S02', 'S11', 'S13', 'S14'] · **thừa** ['S14']

### EMAIL002 (email) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S11', 'S12'] · dự đoán: ['S12', 'S14'] · **thiếu** ['S05', 'S11'] · **thừa** ['S14']

### EMAIL005 (email) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S05', 'S09', 'S11', 'S12'] · dự đoán: ['S05', 'S09', 'S12'] · **thiếu** ['S11']

### DOC018 (document) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S01', 'S02'] · dự đoán: ['S02', 'S05', 'S13'] · **thiếu** ['S01'] · **thừa** ['S05', 'S13']

### SMS157 (sms) – vàng **scam**, dự đoán **scam** (conf 0.95)
- Dấu hiệu vàng: ['S03', 'S05', 'S11'] · dự đoán: ['S02', 'S05', 'S09', 'S11'] · **thiếu** ['S03'] · **thừa** ['S02', 'S09']


### Bằng chứng không có trong tin: 24

- SMS002 S02: “…”
- SMS020 S01: “…”
- SMS025 S12: “…”
- SMS025 S02: “…”
- SMS025 S05: “…”
- SMS052 S05: “…”
- SMS087 S12: “…”
- DOC009 S01: “…”
- DOC009 S09: “…”
- DOC010 S01: “…”
- SMS110 S07: “…”
- SMS134 S01: “…”
- JOB006 S02: “…”
- JOB025 S02: “…”
- CHAT002 S02: “…”
- CHAT002 S03: “…”
- SMS150 S01: “…”
- SMS152 S02: “…”
- SMS152 S11: “…”
- JOB029 S02: “…”
- JOB032 S02: “…”
- EMAIL005 S05: “…”
- DOC018 S05: “…”
- SMS157 S02: “…”
