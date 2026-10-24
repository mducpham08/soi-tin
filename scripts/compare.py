"""So sánh các lượt chạy đã chấm: python scripts/compare.py [--split dev|test]

In bảng Markdown (và ghi runs/compare_<split>.md) từ runs/*/scores.json.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scamdet import RUNS_DIR

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def p(x):
    return "–" if x is None else f"{100 * x:.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    a = ap.parse_args()
    rows = []
    for f in sorted(RUNS_DIR.glob("*/scores.json")):
        s = json.loads(f.read_text(encoding="utf-8"))
        if s["meta"]["split"] != a.split or s["meta"]["model_key"] == "oracle":
            continue
        L = s["label"]
        rows.append(f"| {s['meta']['run_name']} | {s['n']} | {p(L['recall'])} | {p(L['precision'])} | {p(L['f1'])} | "
                    f"{p(L['fpr_hard_negative'])} | {p(L['fpr_normal_legit'])} | {p(s['signals_micro']['f1'])} | "
                    f"{p(s['signals_macro_f1'])} | {p(s['evidence_grounded_rate'])} | {p(s['format_valid_rate'])} | "
                    f"{s['cost_per_1000_msgs_usd'] or 0:.3f} | {s['latency_mean_s'] or 0:.2f} |")
    head = ["| Lượt chạy | n | Recall | Precision | F1 | FPR hard neg | FPR legit thường | Signal micro F1 | Signal macro F1 | Bằng chứng thật | JSON hợp lệ | $/1000 tin | s/tin |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    table = "\n".join(head + rows) + "\n"
    print(table)
    (RUNS_DIR / f"compare_{a.split}.md").write_text(table, encoding="utf-8")


if __name__ == "__main__":
    main()
