"""Đọc bộ dữ liệu, taxonomy, schema."""
import json
from . import DATA_DIR, SCHEMA_PATH


def load_split(split):
    """Trả về list mẫu của dev / test / unsure."""
    path = DATA_DIR / f"{split}.jsonl"
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_taxonomy():
    with open(DATA_DIR / "taxonomy.json", encoding="utf-8") as f:
        return json.load(f)


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def model_input(example):
    """Chỉ những gì model được thấy. KHÔNG đưa label, signals, source, label_notes vào prompt."""
    return {"id": example["id"], "source_type": example["source_type"], "text": example["text"]}
