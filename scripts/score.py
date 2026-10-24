"""Chấm điểm một lượt chạy: python scripts/score.py runs/<tên-lượt> [--show-text]

Ghi ra runs/<tên-lượt>/scores.json và report.md, in tóm tắt ra màn hình.

Quy ước:
- Mẫu thiếu dự đoán hoặc đầu ra sai schema bị tính là SAI nhãn (scam bị coi là bỏ sót, legit bị coi là báo nhầm)
  và không có dấu hiệu nào.
- Dấu hiệu được chấm trên MỌI mẫu (scam và legit), vì nhãn vàng gán theo nội dung.
- Macro F1 dấu hiệu chỉ tính các dấu hiệu có ≥ 3 mẫu vàng trong tập và bỏ S08.
- Với tập test, report.md mặc định KHÔNG in nội dung tin (giữ test "niêm phong"); thêm --show-text nếu thật cần.
"""
import argparse, json, random, re, sys, statistics, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scamdet import SIGNAL_IDS
from scamdet.data import load_split, load_schema
from scamdet.models import load_model_config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import jsonschema
    _V = getattr(jsonschema, "Draft202012Validator", None) or jsonschema.Draft7Validator  # bản jsonschema cũ
    VALIDATOR = _V(load_schema())
except ImportError:  # vẫn chạy được, chỉ kiểm tra tối thiểu
    VALIDATOR = None

MIN_SUPPORT_MACRO = 3


# ------------------------------------------------------------------ tiện ích
def norm(s):
    s = unicodedata.normalize("NFC", str(s)).lower()
    s = re.sub(r"[\"“”'‘’«»]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def grounded(evidence, text):
    """Bằng chứng có thật trong tin không (cho phép model cắt bằng '…' hoặc '...')."""
    t = norm(text)
    parts = [p.strip(" .,;:-") for p in re.split(r"…|\.\.\.", norm(evidence))]
    parts = [p for p in parts if p]
    return bool(parts) and all(p in t for p in parts)


def validate(out):
    if not isinstance(out, dict):
        return ["không phải object JSON"]
    if VALIDATOR is not None:
        errs = [e.message for e in VALIDATOR.iter_errors(out)]
    else:
        errs = [] if {"label", "confidence", "signals", "explanation"} <= set(out) else ["thiếu trường"]
    ids = [s.get("id") for s in out.get("signals", []) if isinstance(s, dict)]
    if len(ids) != len(set(ids)):
        errs.append("dấu hiệu bị lặp")
    return errs


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if p is not None and r is not None else None)
    return p, r, f


def auc_roc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    win = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return win / (len(pos) * len(neg))


def avg_precision(scores, labels):
    order = sorted(zip(scores, labels), key=lambda x: -x[0])
    npos, tp, ap = sum(labels), 0, 0.0
    if not npos:
        return None
    for k, (_, y) in enumerate(order, 1):
        if y:
            tp += 1
            ap += tp / k
    return ap / npos


def bootstrap(rows, fn, n=1000, seed=0):
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        sample = [rows[rng.randrange(len(rows))] for _ in rows]
        v = fn(sample)
        if v is not None:
            vals.append(v)
    if not vals:
        return None
    vals.sort()
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]


def fmt(x, pct=True):
    if x is None:
        return "–"
    return f"{100 * x:.1f}%" if pct else f"{x:.3f}"


# ------------------------------------------------------------------ chấm
def score(run_dir, show_text=False):
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    gold = load_split(meta["split"])
    preds = {}
    for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            preds[r["id"]] = r          # dòng sau ghi đè dòng trước (nếu chạy lại)
    if meta.get("n_requested") and meta["n_requested"] < len(gold):
        gold = [g for g in gold if g["id"] in preds]   # lượt chạy thử --limit/--ids
    hide = meta["split"] == "test" and not show_text

    rows = []
    for g in gold:
        p = preds.get(g["id"])
        out = p["output"] if p else None
        errs = validate(out) if p and p["error"] is None else [p["error"] if p else "thiếu dự đoán"]
        ok = not errs
        if ok:
            plabel = out["label"]
            conf = float(out["confidence"])
            psig = {s["id"] for s in out["signals"]}
        else:
            plabel = "legit" if g["label"] == "scam" else "scam"   # tính là sai
            conf, psig = 0.5, set()
        rows.append({"g": g, "p": p, "out": out if ok else None, "ok": ok, "errs": errs,
                     "y": g["label"] == "scam", "yhat": plabel == "scam", "conf": conf,
                     "gsig": set(g["signals"]), "psig": psig})

    def label_stats(rs):
        tp = sum(r["y"] and r["yhat"] for r in rs)
        fp = sum((not r["y"]) and r["yhat"] for r in rs)
        fn = sum(r["y"] and not r["yhat"] for r in rs)
        tn = sum((not r["y"]) and not r["yhat"] for r in rs)
        p, rc, f = prf(tp, fp, fn)
        return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": p, "recall": rc, "f1": f,
                "accuracy": (tp + tn) / len(rs) if rs else None}

    def fpr(rs):
        neg = [r for r in rs if not r["y"]]
        return sum(r["yhat"] for r in neg) / len(neg) if neg else None

    L = label_stats(rows)
    legit = [r for r in rows if not r["y"]]
    hard = [r for r in legit if r["g"]["hard_negative"]]
    normal = [r for r in legit if not r["g"]["hard_negative"]]
    res = {"meta": meta, "n": len(rows), "n_valid": sum(r["ok"] for r in rows)}
    res["format_valid_rate"] = res["n_valid"] / len(rows)
    res["label"] = dict(L, fpr_all_legit=fpr(rows), fpr_hard_negative=fpr(hard), fpr_normal_legit=fpr(normal),
                        n_scam=sum(r["y"] for r in rows), n_legit=len(legit), n_hard=len(hard), n_normal=len(normal))
    res["label_ci95"] = {
        "recall": bootstrap(rows, lambda s: label_stats(s)["recall"]),
        "precision": bootstrap(rows, lambda s: label_stats(s)["precision"]),
        "f1": bootstrap(rows, lambda s: label_stats(s)["f1"]),
        "fpr_all_legit": bootstrap(rows, fpr),
    }
    res["roc_auc"] = auc_roc([r["conf"] for r in rows], [r["y"] for r in rows])
    res["pr_auc"] = avg_precision([r["conf"] for r in rows], [r["y"] for r in rows])
    res["label_conf_mismatch"] = sum(r["ok"] and ((r["yhat"] and r["conf"] < 0.5) or (not r["yhat"] and r["conf"] > 0.5))
                                     for r in rows)
    by_src = defaultdict(list)
    for r in rows:
        by_src[r["g"]["source_type"]].append(r)
    res["by_source_type"] = {k: {"n": len(v), "recall": label_stats(v)["recall"], "fpr": fpr(v)}
                             for k, v in sorted(by_src.items())}

    # dấu hiệu
    sig = {}
    for s in SIGNAL_IDS:
        tp = sum(s in r["gsig"] and s in r["psig"] for r in rows)
        fp = sum(s not in r["gsig"] and s in r["psig"] for r in rows)
        fn = sum(s in r["gsig"] and s not in r["psig"] for r in rows)
        p, rc, f = prf(tp, fp, fn)
        sig[s] = {"support": tp + fn, "tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": rc, "f1": f}
    TP, FP, FN = (sum(v[k] for v in sig.values()) for k in ("tp", "fp", "fn"))
    mp, mr, mf = prf(TP, FP, FN)
    macro_set = [s for s, v in sig.items() if v["support"] >= MIN_SUPPORT_MACRO and s != "S08"]
    res["signals"] = sig
    res["signals_micro"] = {"precision": mp, "recall": mr, "f1": mf}
    res["signals_macro_f1"] = statistics.mean(sig[s]["f1"] or 0 for s in macro_set) if macro_set else None
    res["signals_macro_set"] = macro_set
    res["signals_exact_match"] = sum(r["gsig"] == r["psig"] for r in rows) / len(rows)

    # bằng chứng
    ev = [(r, s) for r in rows if r["ok"] for s in r["out"]["signals"]]
    ung = [(r, s) for r, s in ev if not grounded(s["evidence"], r["g"]["text"])]
    res["evidence_grounded_rate"] = 1 - len(ung) / len(ev) if ev else None
    res["n_evidence"] = len(ev)

    # chi phí, thời gian
    try:
        cfg = load_model_config(meta["model_key"])
    except SystemExit:
        cfg = {"price_in": 0, "price_out": 0}
    U = Counter()
    lat = []
    for r in rows:
        if r["p"]:
            U.update(r["p"].get("usage") or {})
            lat.append(r["p"].get("latency_s") or 0)
    pin, pout = cfg.get("price_in", 0) / 1e6, cfg.get("price_out", 0) / 1e6
    # giá cache: lấy từ models.json nếu có (Sonnet 5.5 đọc cache = 0.05 × input), không thì theo tỉ lệ chuẩn
    pcw = cfg.get("price_cache_write", cfg.get("price_in", 0) * 1.25) / 1e6
    pcr = cfg.get("price_cache_read", cfg.get("price_in", 0) * 0.1) / 1e6
    cost = (U["input_tokens"] * pin + U["cache_write_tokens"] * pcw + U["cache_read_tokens"] * pcr
            + U["output_tokens"] * pout)
    res["usage"] = dict(U)
    res["cost_usd"] = cost
    res["cost_per_1000_msgs_usd"] = cost / len(rows) * 1000 if rows else None
    res["latency_mean_s"] = statistics.mean(lat) if lat else None
    res["latency_p95_s"] = sorted(lat)[int(0.95 * (len(lat) - 1))] if lat else None
    res["n_api_errors"] = sum(1 for r in rows if r["p"] and r["p"]["error"])

    (run_dir / "scores.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "report.md").write_text(report(res, rows, ung, hide), encoding="utf-8")
    return res


# ------------------------------------------------------------------ báo cáo
def report(res, rows, ung, hide):
    m, L, ci = res["meta"], res["label"], res["label_ci95"]
    def c(k):
        return f" (95% CI {fmt(ci[k][0])}–{fmt(ci[k][1])})" if ci.get(k) else ""
    out = [f"# Báo cáo: {m['run_name']}", "",
           f"Model `{m['model']}` · prompt `{m['prompt']}` · tập **{m['split']}** · dữ liệu v{m['data_version']} · {res['n']} mẫu", "",
           "## Nhãn scam / legit", "",
           "| Chỉ số | Giá trị |", "|---|---|",
           f"| Recall scam (bắt được bao nhiêu % lừa đảo) | {fmt(L['recall'])}{c('recall')} |",
           f"| Precision scam (cảnh báo đúng bao nhiêu %) | {fmt(L['precision'])}{c('precision')} |",
           f"| F1 | {fmt(L['f1'])}{c('f1')} |",
           f"| Báo nhầm trên legit (FPR) | {fmt(L['fpr_all_legit'])}{c('fpr_all_legit')} |",
           f"| … trên legit thường ({L['n_normal']} mẫu) | {fmt(L['fpr_normal_legit'])} |",
           f"| … trên hard negative ({L['n_hard']} mẫu) | {fmt(L['fpr_hard_negative'])} |",
           f"| Accuracy | {fmt(L['accuracy'])} |",
           f"| ROC-AUC / PR-AUC theo confidence | {fmt(res['roc_auc'], False)} / {fmt(res['pr_auc'], False)} |",
           f"| Ma trận | TP {L['tp']} · FN {L['fn']} · FP {L['fp']} · TN {L['tn']} |", "",
           "Theo loại nguồn:", "", "| source_type | n | recall | FPR |", "|---|---|---|---|"]
    out += [f"| {k} | {v['n']} | {fmt(v['recall'])} | {fmt(v['fpr'])} |" for k, v in res["by_source_type"].items()]
    out += ["", "## Dấu hiệu S01–S14", "",
            f"Micro: P {fmt(res['signals_micro']['precision'])} · R {fmt(res['signals_micro']['recall'])} · F1 {fmt(res['signals_micro']['f1'])}"
            f" · Macro F1 {fmt(res['signals_macro_f1'])} (trên {len(res['signals_macro_set'])} dấu hiệu có ≥{MIN_SUPPORT_MACRO} mẫu, bỏ S08)"
            f" · Khớp đúng cả bộ: {fmt(res['signals_exact_match'])}", "",
            "| Dấu hiệu | Số mẫu vàng | Precision | Recall | F1 | FP | FN |", "|---|---|---|---|---|---|---|"]
    for s, v in res["signals"].items():
        flag = " (ít mẫu)" if v["support"] < MIN_SUPPORT_MACRO else ""
        out.append(f"| {s}{flag} | {v['support']} | {fmt(v['precision'])} | {fmt(v['recall'])} | {fmt(v['f1'])} | {v['fp']} | {v['fn']} |")
    out += ["", "## Định dạng, bằng chứng, chi phí", "",
            f"- Đầu ra hợp lệ theo schema: {res['n_valid']}/{res['n']} ({fmt(res['format_valid_rate'])}); lỗi API: {res['n_api_errors']}",
            f"- Nhãn mâu thuẫn với confidence: {res['label_conf_mismatch']}",
            f"- Bằng chứng có thật trong tin: {fmt(res['evidence_grounded_rate'])} ({res['n_evidence']} bằng chứng)",
            f"- Token: {res['usage']}",
            f"- Chi phí lượt này: ${res['cost_usd']:.4f} · ước tính /1.000 tin: ${res['cost_per_1000_msgs_usd'] or 0:.3f}",
            f"- Thời gian mỗi tin: trung bình {res['latency_mean_s'] or 0:.2f}s · p95 {res['latency_p95_s'] or 0:.2f}s", ""]

    def show(r, why=""):
        g = r["g"]
        s = [f"### {g['id']} ({g['source_type']}) – vàng **{g['label']}**, dự đoán **{'scam' if r['yhat'] else 'legit'}**"
             f" (conf {r['conf']:.2f}){' · ' + why if why else ''}"]
        miss, extra = sorted(r["gsig"] - r["psig"]), sorted(r["psig"] - r["gsig"])
        s.append(f"- Dấu hiệu vàng: {sorted(r['gsig']) or '–'} · dự đoán: {sorted(r['psig']) or '–'}"
                 + (f" · **thiếu** {miss}" if miss else "") + (f" · **thừa** {extra}" if extra else ""))
        if not r["ok"]:
            s.append(f"- Lỗi: {'; '.join(map(str, r['errs']))[:300]}")
        if not hide:
            s.append("- Tin: " + g["text"].replace("\n", " ⏎ ")[:600])
            if r["out"]:
                s.append("- Giải thích của model: " + str(r["out"]["explanation"])[:400])
                for sg in r["out"]["signals"]:
                    s.append(f"  - {sg['id']}: “{sg['evidence']}”")
            if g.get("label_notes"):
                s.append("- Ghi chú gán nhãn: " + str(g["label_notes"])[:400])
        return "\n".join(s) + "\n"

    fn = [r for r in rows if r["y"] and not r["yhat"]]
    fp = [r for r in rows if not r["y"] and r["yhat"]]
    sig_err = [r for r in rows if r not in fn and r not in fp and r["gsig"] != r["psig"]]
    out.append("## Phân tích lỗi" + (" (tập test: ẩn nội dung tin)" if hide else ""))
    out.append(f"\n### Bỏ sót lừa đảo (FN): {len(fn)}\n")
    out += [show(r) for r in fn]
    out.append(f"\n### Báo nhầm (FP): {len(fp)}\n")
    out += [show(r, "hard negative" if r["g"]["hard_negative"] else "legit thường") for r in fp]
    out.append(f"\n### Đúng nhãn nhưng sai dấu hiệu: {len(sig_err)}\n")
    out += [show(r) for r in sig_err]
    if ung:
        out.append(f"\n### Bằng chứng không có trong tin: {len(ung)}\n")
        for r, s in ung[:50]:
            out.append(f"- {r['g']['id']} {s['id']}: “{s['evidence'][:150] if not hide else '…'}”")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--show-text", action="store_true")
    a = ap.parse_args()
    run = Path(a.run_dir)
    res = score(run, a.show_text)
    L = res["label"]
    print(f"{res['meta']['run_name']}  ({res['n']} mẫu, hợp lệ {fmt(res['format_valid_rate'])})")
    print(f"  Nhãn   : recall {fmt(L['recall'])} · precision {fmt(L['precision'])} · F1 {fmt(L['f1'])} · "
          f"FPR {fmt(L['fpr_all_legit'])} (hard {fmt(L['fpr_hard_negative'])}, thường {fmt(L['fpr_normal_legit'])})")
    print(f"  Dấu hiệu: micro F1 {fmt(res['signals_micro']['f1'])} · macro F1 {fmt(res['signals_macro_f1'])} · "
          f"bằng chứng có thật {fmt(res['evidence_grounded_rate'])}")
    print(f"  Chi phí ${res['cost_usd']:.4f} · {res['latency_mean_s'] or 0:.2f}s/tin")
    print(f"  Báo cáo: {run / 'report.md'}")


if __name__ == "__main__":
    main()
