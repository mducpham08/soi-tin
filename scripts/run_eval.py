"""Chạy một model trên một tập, ghi dự đoán vào runs/<tên-lượt>/predictions.jsonl.

Ví dụ:
  python scripts/run_eval.py --model rules --prompt v0_baseline --split dev
  python scripts/run_eval.py --model haiku --prompt v0_baseline --split dev --limit 5
  python scripts/run_eval.py --model haiku --prompt v3 --split test --i-am-done-tuning

- Chạy lại cùng tên lượt sẽ BỎ QUA các mẫu đã có kết quả và chạy lại các mẫu bị lỗi API
  (chạy tiếp khi bị ngắt mạng, hết tiền, sai cấu hình). Mẫu đã có câu trả lời thì không chạy lại.
- Tập test bị khóa: phải thêm --i-am-done-tuning, và mỗi tổ hợp model + prompt chỉ có 1 lượt test
  (kể cả khi đặt --run-name khác). Được phép chạy tiếp chính lượt đó để lấp các mẫu lỗi API.
"""
import argparse, json, sys, time, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scamdet import RUNS_DIR, DATA_VERSION
from scamdet.data import load_split, model_input
from scamdet.models import load_model_config, make_predictor
from scamdet.prompts import build_system_prompt, list_prompts

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="tên trong models.json")
    ap.add_argument("--prompt", default="v0_baseline", help=f"có: {list_prompts()}")
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--limit", type=int, help="chỉ chạy N mẫu đầu (thử nhanh)")
    ap.add_argument("--ids", help="chỉ chạy các id này, cách nhau dấu phẩy")
    ap.add_argument("--run-name", help="mặc định: <ngày>_<model>_<prompt>_<split>")
    ap.add_argument("--i-am-done-tuning", action="store_true", help="bắt buộc khi chạy test")
    a = ap.parse_args()

    if a.split == "test":
        if not a.i_am_done_tuning:
            raise SystemExit("Tập test đang khóa. Chỉ chạy khi đã CHỐT prompt, và thêm --i-am-done-tuning.")
        want_name = a.run_name or f"{datetime.date.today():%Y%m%d}_{a.model}_{a.prompt}_test"
        for p in RUNS_DIR.glob("*/meta.json"):
            m = json.loads(p.read_text(encoding="utf-8"))
            if (m.get("split") == "test" and m.get("model_key") == a.model and m.get("prompt") == a.prompt
                    and p.parent.name != want_name and (p.parent / "predictions.jsonl").exists()):
                raise SystemExit(f"Đã có lượt test cho {a.model} + {a.prompt}: {p.parent.name}. "
                                 f"Không chạy test lần hai (muốn lấp mẫu lỗi thì dùng --run-name {p.parent.name}).")

    cfg = load_model_config(a.model)
    system = build_system_prompt(a.prompt)
    gold = load_split(a.split)
    if a.ids:
        want = set(a.ids.split(","))
        gold = [g for g in gold if g["id"] in want]
    if a.limit:
        gold = gold[: a.limit]

    name = a.run_name or f"{datetime.date.today():%Y%m%d}_{a.model}_{a.prompt}_{a.split}"
    out_dir = RUNS_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "predictions.jsonl"
    meta = {"run_name": name, "model_key": a.model, "model": cfg["model"], "provider": cfg["provider"],
            "prompt": a.prompt, "split": a.split, "data_version": DATA_VERSION,
            "started": datetime.datetime.now().isoformat(timespec="seconds"), "n_requested": len(gold)}
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "system_prompt.txt").write_text(system, encoding="utf-8")

    seen, n_retry = set(), 0
    if pred_path.exists():
        old = [json.loads(l) for l in pred_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        keep = [r for r in old if r.get("error") is None or r.get("output") is not None]
        n_retry = len(old) - len(keep)
        if n_retry:  # bỏ các dòng lỗi API (không có câu trả lời) để chạy lại
            pred_path.with_suffix(".jsonl.bak").write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in old), encoding="utf-8")
            pred_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep), encoding="utf-8")
        seen = {r["id"] for r in keep}
    todo = [g for g in gold if g["id"] not in seen]
    print(f"[{name}] {len(todo)} mẫu cần chạy ({len(seen)} đã có"
          + (f", chạy lại {n_retry} mẫu lỗi API" if n_retry else "") + ").")

    pred = make_predictor(cfg, system, gold=gold)
    t0, n_err = time.time(), 0
    with open(pred_path, "a", encoding="utf-8") as f:
        for i, g in enumerate(todo, 1):
            r = pred.predict(model_input(g))
            r["id"] = g["id"]
            n_err += r["error"] is not None
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            if i % 10 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}  lỗi: {n_err}  ({time.time() - t0:.0f}s)")
    print(f"Xong. Chấm điểm:  python scripts/score.py runs/{name}")


if __name__ == "__main__":
    main()
