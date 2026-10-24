# Báo cáo: 20261024_rules_v0_baseline_test

Model `keyword-baseline-v0` · prompt `v0_baseline` · tập **test** · dữ liệu v1.0 · 128 mẫu

## Nhãn scam / legit

| Chỉ số | Giá trị |
|---|---|
| Recall scam (bắt được bao nhiêu % lừa đảo) | 50.0% (95% CI 38.1%–62.3%) |
| Precision scam (cảnh báo đúng bao nhiêu %) | 81.0% (95% CI 67.6%–91.1%) |
| F1 | 61.8% (95% CI 50.5%–71.7%) |
| Báo nhầm trên legit (FPR) | 13.3% (95% CI 6.2%–22.0%) |
| … trên legit thường (11 mẫu) | 9.1% |
| … trên hard negative (49 mẫu) | 14.3% |
| Accuracy | 67.2% |
| ROC-AUC / PR-AUC theo confidence | 0.701 / 0.753 |
| Ma trận | TP 34 · FN 34 · FP 8 · TN 52 |

Theo loại nguồn:

| source_type | n | recall | FPR |
|---|---|---|---|
| chat | 4 | 50.0% | – |
| document | 11 | 12.5% | 0.0% |
| email | 3 | 33.3% | – |
| job_post | 19 | 33.3% | 23.1% |
| sms | 91 | 59.6% | 11.4% |

## Dấu hiệu S01–S14

Micro: P 44.5% · R 39.5% · F1 41.8% · Macro F1 43.8% (trên 13 dấu hiệu có ≥3 mẫu, bỏ S08) · Khớp đúng cả bộ: 13.3%

| Dấu hiệu | Số mẫu vàng | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| S01 | 17 | 66.7% | 11.8% | 20.0% | 1 | 15 |
| S02 | 22 | 27.6% | 36.4% | 31.4% | 21 | 14 |
| S03 | 8 | 50.0% | 75.0% | 60.0% | 6 | 2 |
| S04 | 7 | 46.2% | 85.7% | 60.0% | 7 | 1 |
| S05 | 32 | 29.4% | 15.6% | 20.4% | 12 | 27 |
| S06 | 5 | 100.0% | 60.0% | 75.0% | 0 | 2 |
| S07 | 9 | 20.8% | 55.6% | 30.3% | 19 | 4 |
| S08 (ít mẫu) | 1 | 100.0% | 100.0% | 100.0% | 0 | 0 |
| S09 | 26 | 50.0% | 19.2% | 27.8% | 5 | 21 |
| S10 | 4 | 28.6% | 50.0% | 36.4% | 5 | 2 |
| S11 | 18 | 70.6% | 66.7% | 68.6% | 5 | 6 |
| S12 | 30 | 100.0% | 50.0% | 66.7% | 0 | 15 |
| S13 | 6 | 28.6% | 66.7% | 40.0% | 10 | 2 |
| S14 | 10 | 37.5% | 30.0% | 33.3% | 5 | 7 |

## Định dạng, bằng chứng, chi phí

- Đầu ra hợp lệ theo schema: 128/128 (100.0%); lỗi API: 0
- Nhãn mâu thuẫn với confidence: 17
- Bằng chứng có thật trong tin: 100.0% (173 bằng chứng)
- Token: {'input_tokens': 0, 'output_tokens': 0, 'cache_read_tokens': 0, 'cache_write_tokens': 0}
- Chi phí lượt này: $0.0000 · ước tính /1.000 tin: $0.000
- Thời gian mỗi tin: trung bình 0.00s · p95 0.00s

## Phân tích lỗi (tập test: ẩn nội dung tin)

### Bỏ sót lừa đảo (FN): 34

### SMS003 (sms) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S05', 'S07', 'S09', 'S12', 'S14'] · dự đoán: ['S11'] · **thiếu** ['S05', 'S07', 'S09', 'S12', 'S14'] · **thừa** ['S11']

### SMS009 (sms) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S02'] · dự đoán: – · **thiếu** ['S02']

### SMS011 (sms) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S04', 'S09', 'S12'] · dự đoán: ['S04', 'S07'] · **thiếu** ['S09', 'S12'] · **thừa** ['S07']

### SMS020 (sms) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S05', 'S09', 'S11'] · dự đoán: – · **thiếu** ['S05', 'S09', 'S11']

### SMS024 (sms) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S02', 'S05', 'S12'] · dự đoán: ['S05'] · **thiếu** ['S02', 'S12']

### SMS030 (sms) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S02', 'S12'] · dự đoán: – · **thiếu** ['S02', 'S12']

### SMS050 (sms) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S02', 'S12'] · dự đoán: ['S02', 'S11'] · **thiếu** ['S12'] · **thừa** ['S11']

### SMS053 (sms) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S05', 'S12', 'S14'] · dự đoán: ['S09'] · **thiếu** ['S05', 'S12', 'S14'] · **thừa** ['S09']

### SMS054 (sms) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S12', 'S13', 'S14'] · dự đoán: ['S13', 'S14'] · **thiếu** ['S12']

### SMS074 (sms) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S02', 'S11', 'S14'] · dự đoán: ['S11'] · **thiếu** ['S02', 'S14']

### DOC002 (document) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S01'] · dự đoán: – · **thiếu** ['S01']

### DOC008 (document) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S01', 'S02', 'S09'] · dự đoán: – · **thiếu** ['S01', 'S02', 'S09']

### DOC009 (document) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S01', 'S02', 'S09'] · dự đoán: ['S07'] · **thiếu** ['S01', 'S02', 'S09'] · **thừa** ['S07']

### DOC010 (document) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S01', 'S02', 'S09'] · dự đoán: ['S07'] · **thiếu** ['S01', 'S02', 'S09'] · **thừa** ['S07']

### SMS092 (sms) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S06', 'S11'] · dự đoán: ['S09', 'S11'] · **thiếu** ['S06'] · **thừa** ['S09']

### SMS104 (sms) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S01', 'S06', 'S10'] · dự đoán: – · **thiếu** ['S01', 'S06', 'S10']

### SMS108 (sms) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S02', 'S07', 'S10', 'S11'] · dự đoán: – · **thiếu** ['S02', 'S07', 'S10', 'S11']

### CHAT001 (chat) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S05'] · dự đoán: ['S02', 'S13'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### JOB023 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S02', 'S11'] · **thiếu** ['S05'] · **thừa** ['S02']

### EMAIL001 (email) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S11'] · **thiếu** ['S05']

### JOB024 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S13'] · dự đoán: ['S13']

### SMS146 (sms) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S09', 'S11'] · dự đoán: – · **thiếu** ['S09', 'S11']

### SMS147 (sms) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S01', 'S05', 'S09', 'S11'] · dự đoán: ['S09'] · **thiếu** ['S01', 'S05', 'S11']

### SMS148 (sms) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S01'] · dự đoán: – · **thiếu** ['S01']

### SMS149 (sms) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S07', 'S09', 'S12'] · dự đoán: ['S07', 'S11'] · **thiếu** ['S09', 'S12'] · **thừa** ['S11']

### SMS152 (sms) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S05', 'S11'] · dự đoán: ['S11', 'S13'] · **thiếu** ['S05'] · **thừa** ['S13']

### SMS153 (sms) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S04'] · dự đoán: ['S04']

### CHAT007 (chat) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S02', 'S05', 'S11'] · dự đoán: ['S02', 'S11'] · **thiếu** ['S05']

### JOB029 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S02', 'S05'] · dự đoán: – · **thiếu** ['S02', 'S05']

### JOB030 (job_post) – vàng **scam**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S05'] · dự đoán: ['S04', 'S14'] · **thiếu** ['S05'] · **thừa** ['S04', 'S14']

### EMAIL002 (email) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S05', 'S11', 'S12'] · dự đoán: ['S07'] · **thiếu** ['S05', 'S11', 'S12'] · **thừa** ['S07']

### DOC018 (document) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S01', 'S02'] · dự đoán: – · **thiếu** ['S01', 'S02']

### DOC019 (document) – vàng **scam**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S03'] · dự đoán: – · **thiếu** ['S03']

### DOC020 (document) – vàng **scam**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S04'] · **thiếu** ['S05', 'S12'] · **thừa** ['S04']


### Báo nhầm (FP): 8

### SMS040 (sms) – vàng **legit**, dự đoán **scam** (conf 0.85) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S05', 'S10'] · **thừa** ['S05', 'S10']

### SMS087 (sms) – vàng **legit**, dự đoán **scam** (conf 0.65) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S01'] · **thừa** ['S01']

### SMS098 (sms) – vàng **legit**, dự đoán **scam** (conf 0.65) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S03'] · **thừa** ['S03']

### SMS099 (sms) – vàng **legit**, dự đoán **scam** (conf 0.85) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S03', 'S05'] · **thừa** ['S03', 'S05']

### SMS133 (sms) – vàng **legit**, dự đoán **scam** (conf 0.65) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S10'] · **thừa** ['S10']

### JOB002 (job_post) – vàng **legit**, dự đoán **scam** (conf 1.00) · hard negative
- Dấu hiệu vàng: – · dự đoán: ['S03', 'S07', 'S14'] · **thừa** ['S03', 'S07', 'S14']

### JOB010 (job_post) – vàng **legit**, dự đoán **scam** (conf 0.65) · legit thường
- Dấu hiệu vàng: – · dự đoán: ['S10'] · **thừa** ['S10']

### JOB019 (job_post) – vàng **legit**, dự đoán **scam** (conf 1.00) · hard negative
- Dấu hiệu vàng: ['S05', 'S09'] · dự đoán: ['S02', 'S03', 'S04'] · **thiếu** ['S05', 'S09'] · **thừa** ['S02', 'S03', 'S04']


### Đúng nhãn nhưng sai dấu hiệu: 71

### SMS002 (sms) – vàng **legit**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: – · dự đoán: ['S05', 'S09'] · **thừa** ['S05', 'S09']

### SMS005 (sms) – vàng **scam**, dự đoán **scam** (conf 0.65)
- Dấu hiệu vàng: ['S04', 'S07', 'S12'] · dự đoán: ['S12'] · **thiếu** ['S04', 'S07']

### SMS007 (sms) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S03', 'S05', 'S12', 'S13'] · **thừa** ['S03', 'S13']

### SMS008 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S11'] · **thừa** ['S11']

### SMS014 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S05'] · **thừa** ['S05']

### SMS016 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S05'] · **thừa** ['S05']

### SMS021 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S05'] · **thừa** ['S05']

### SMS023 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S02', 'S05', 'S07', 'S12'] · dự đoán: ['S07', 'S12'] · **thiếu** ['S02', 'S05']

### SMS025 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S02', 'S05', 'S12'] · dự đoán: ['S07', 'S12'] · **thiếu** ['S02', 'S05'] · **thừa** ['S07']

### SMS026 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S09', 'S12'] · dự đoán: ['S05', 'S12'] · **thiếu** ['S09'] · **thừa** ['S05']

### SMS027 (sms) – vàng **scam**, dự đoán **scam** (conf 0.75)
- Dấu hiệu vàng: ['S01', 'S09', 'S12', 'S14'] · dự đoán: ['S05', 'S09', 'S11'] · **thiếu** ['S01', 'S12', 'S14'] · **thừa** ['S05', 'S11']

### SMS029 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S07'] · **thừa** ['S07']

### SMS032 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S05', 'S07', 'S09', 'S12', 'S14'] · dự đoán: ['S07', 'S12'] · **thiếu** ['S05', 'S09', 'S14']

### SMS035 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS044 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S01', 'S04', 'S09', 'S12'] · dự đoán: ['S04', 'S12'] · **thiếu** ['S01', 'S09']

### SMS045 (sms) – vàng **legit**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S14'] · **thừa** ['S02', 'S14']

### SMS049 (sms) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S02', 'S11', 'S13'] · dự đoán: ['S03', 'S11', 'S13'] · **thiếu** ['S02'] · **thừa** ['S03']

### SMS051 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS055 (sms) – vàng **scam**, dự đoán **scam** (conf 0.65)
- Dấu hiệu vàng: ['S05', 'S12', 'S13', 'S14'] · dự đoán: ['S12'] · **thiếu** ['S05', 'S13', 'S14']

### SMS063 (sms) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S01', 'S02', 'S05', 'S07', 'S12'] · dự đoán: ['S01', 'S02', 'S12'] · **thiếu** ['S05', 'S07']

### SMS064 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS065 (sms) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S05', 'S09', 'S12'] · dự đoán: ['S02', 'S05', 'S12'] · **thiếu** ['S09'] · **thừa** ['S02']

### SMS066 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S07'] · **thừa** ['S07']

### SMS069 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S07'] · **thừa** ['S07']

### SMS075 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S03', 'S12'] · dự đoán: ['S03', 'S14'] · **thiếu** ['S12'] · **thừa** ['S14']

### SMS080 (sms) – vàng **scam**, dự đoán **scam** (conf 0.75)
- Dấu hiệu vàng: ['S02', 'S05', 'S09', 'S12'] · dự đoán: ['S02', 'S05', 'S09'] · **thiếu** ['S12']

### SMS081 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS082 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS084 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S07'] · **thừa** ['S07']

### SMS085 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S05', 'S09', 'S12', 'S14'] · dự đoán: ['S07', 'S12'] · **thiếu** ['S05', 'S09', 'S14'] · **thừa** ['S07']

### SMS093 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S03'] · dự đoán: ['S03', 'S13'] · **thừa** ['S13']

### SMS095 (sms) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S03', 'S05', 'S12', 'S14'] · dự đoán: ['S02', 'S03', 'S13', 'S14'] · **thiếu** ['S05', 'S12'] · **thừa** ['S02', 'S13']

### SMS100 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S05'] · **thừa** ['S05']

### DOC012 (document) – vàng **legit**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S09'] · dự đoán: – · **thiếu** ['S09']

### DOC013 (document) – vàng **legit**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S09'] · dự đoán: – · **thiếu** ['S09']

### DOC014 (document) – vàng **legit**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S09'] · dự đoán: – · **thiếu** ['S09']

### SMS102 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S01', 'S06', 'S10'] · dự đoán: ['S06', 'S10'] · **thiếu** ['S01']

### SMS103 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S04', 'S09', 'S10', 'S11'] · dự đoán: ['S04', 'S10'] · **thiếu** ['S09', 'S11']

### SMS105 (sms) – vàng **scam**, dự đoán **scam** (conf 0.65)
- Dấu hiệu vàng: ['S01', 'S06'] · dự đoán: ['S06'] · **thiếu** ['S01']

### SMS106 (sms) – vàng **scam**, dự đoán **scam** (conf 0.65)
- Dấu hiệu vàng: ['S01', 'S06'] · dự đoán: ['S06'] · **thiếu** ['S01']

### SMS110 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S04', 'S09'] · dự đoán: ['S04'] · **thiếu** ['S09']

### SMS112 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S07'] · **thừa** ['S07']

### SMS114 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S07'] · **thừa** ['S07']

### SMS115 (sms) – vàng **legit**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: – · dự đoán: ['S05', 'S07'] · **thừa** ['S05', 'S07']

### SMS116 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S07'] · **thừa** ['S07']

### SMS117 (sms) – vàng **legit**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: – · dự đoán: ['S07', 'S09'] · **thừa** ['S07', 'S09']

### SMS118 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: ['S02', 'S09'] · dự đoán: ['S05'] · **thiếu** ['S02', 'S09'] · **thừa** ['S05']

### SMS123 (sms) – vàng **legit**, dự đoán **legit** (conf 0.15)
- Dấu hiệu vàng: ['S01', 'S09'] · dự đoán: – · **thiếu** ['S01', 'S09']

### SMS124 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS125 (sms) – vàng **legit**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: – · dự đoán: ['S02', 'S14'] · **thừa** ['S02', 'S14']

### SMS130 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S13'] · **thừa** ['S13']

### SMS131 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS134 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### SMS138 (sms) – vàng **legit**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: ['S02'] · dự đoán: ['S02', 'S07'] · **thừa** ['S07']

### SMS142 (sms) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### JOB001 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.55)
- Dấu hiệu vàng: – · dự đoán: ['S07', 'S13'] · **thừa** ['S07', 'S13']

### JOB004 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S04'] · **thừa** ['S04']

### JOB005 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S04'] · **thừa** ['S04']

### JOB006 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S04'] · **thừa** ['S04']

### JOB015 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### JOB020 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S02'] · **thừa** ['S02']

### JOB022 (job_post) – vàng **legit**, dự đoán **legit** (conf 0.35)
- Dấu hiệu vàng: – · dự đoán: ['S04'] · **thừa** ['S04']

### SMS143 (sms) – vàng **scam**, dự đoán **scam** (conf 0.75)
- Dấu hiệu vàng: ['S02', 'S11', 'S13'] · dự đoán: ['S02', 'S05', 'S11'] · **thiếu** ['S13'] · **thừa** ['S05']

### JOB025 (job_post) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S03', 'S13'] · **thiếu** ['S05'] · **thừa** ['S02', 'S13']

### CHAT002 (chat) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S03', 'S05'] · dự đoán: ['S02', 'S03'] · **thiếu** ['S05'] · **thừa** ['S02']

### CHAT003 (chat) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S01', 'S03'] · dự đoán: ['S02', 'S03'] · **thiếu** ['S01'] · **thừa** ['S02']

### SMS150 (sms) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S05', 'S07', 'S09', 'S12', 'S14'] · dự đoán: ['S07', 'S09', 'S12', 'S14'] · **thiếu** ['S05']

### SMS155 (sms) – vàng **scam**, dự đoán **scam** (conf 0.85)
- Dấu hiệu vàng: ['S05', 'S12'] · dự đoán: ['S12', 'S13'] · **thiếu** ['S05'] · **thừa** ['S13']

### JOB032 (job_post) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S02', 'S11', 'S13'] · dự đoán: ['S02', 'S10', 'S11', 'S13'] · **thừa** ['S10']

### EMAIL005 (email) – vàng **scam**, dự đoán **scam** (conf 1.00)
- Dấu hiệu vàng: ['S05', 'S09', 'S11', 'S12'] · dự đoán: ['S07', 'S09', 'S10', 'S11'] · **thiếu** ['S05', 'S12'] · **thừa** ['S07', 'S10']

### SMS157 (sms) – vàng **scam**, dự đoán **scam** (conf 0.75)
- Dấu hiệu vàng: ['S03', 'S05', 'S11'] · dự đoán: ['S09', 'S11', 'S13'] · **thiếu** ['S03', 'S05'] · **thừa** ['S09', 'S13']

