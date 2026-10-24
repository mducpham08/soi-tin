"""Phân tích một tin cho app: gọi model với prompt đã chốt, rồi hậu xử lý để hiển thị.

Hậu xử lý (không có trong lúc đánh giá dev/test, ghi rõ trong README):
  - gộp mã dấu hiệu bị lặp, bỏ mã lạ
  - tìm vị trí bằng chứng trong tin để tô sáng (chia tin thành các đoạn)
  - kiểm tra link / tên miền bằng danh sách tên miền chính thức (scamdet/links.py)
  - soi chữ bị biến dạng bằng luật (scamdet/obfuscation.py)
  - chia 3 mức theo confidence: ≥ 0.75 lừa đảo, ≤ 0.30 có vẻ an toàn, còn lại cần cẩn thận
    (ngưỡng chọn theo phân bố confidence của Haiku/Sonnet + v4 trên tập dev);
    nếu có tên miền nhái hoặc chữ bị cố tình biến dạng mà model vẫn cho là an toàn thì nâng lên "cần cẩn thận".
"""
import re, time, unicodedata
from difflib import SequenceMatcher
from . import SIGNAL_IDS
from .data import load_taxonomy
from .links import find_links
from .obfuscation import STRONG as OBF_STRONG, find_obfuscation

APP_PROMPT = "v4_rules"
MAX_CHARS = 4000
SCAM_AT, SAFE_AT = 0.75, 0.30

# Nhóm màu bút dạ quang trên giao diện
GROUPS = {
    "money": "Tiền và thông tin cá nhân",
    "imperson": "Mạo danh",
    "bait": "Mồi nhử",
    "pressure": "Hối thúc, cô lập",
    "channel": "Kênh liên lạc và link",
}

# Tên ngắn + một câu "vì sao đáng ngờ" cho người dùng (tên đầy đủ và định nghĩa nằm trong taxonomy.json)
SIGNAL_UI = {
    "S01": ("money", "Đòi chuyển tiền hoặc đóng phí",
            "Bên làm ăn đàng hoàng không bắt bạn trả tiền trước để nhận việc, nhận quà hay giải quyết hồ sơ."),
    "S02": ("bait", "Lợi ích bất ngờ, khó tin",
            "Trúng thưởng hay được duyệt khi bạn không hề đăng ký, lương quá cao cho việc quá dễ là mồi nhử quen thuộc."),
    "S03": ("bait", "Làm nhiệm vụ ăn hoa hồng",
            "Like, đánh giá, chốt đơn ảo để nhận hoa hồng thường dẫn tới bước bắt nạp tiền để rút lãi."),
    "S04": ("imperson", "Tự xưng cơ quan nhà nước",
            "Công an, toà án, cơ quan thuế, BHXH không làm việc qua tin nhắn kèm link lạ hay Zalo cá nhân."),
    "S05": ("imperson", "Tự xưng tổ chức nhưng liên lạc qua kênh lạ",
            "Tên ngân hàng, công ty đi kèm số cá nhân, Zalo, email miễn phí hoặc link không thuộc tổ chức đó."),
    "S06": ("imperson", "Giả làm người quen",
            "Người quen đổi số rồi nhờ chuyển tiền gấp: hãy gọi lại số cũ của họ để hỏi trước."),
    "S07": ("money", "Xin mật khẩu, mã OTP hoặc giấy tờ",
            "Không ai cần mật khẩu, mã OTP hay ảnh căn cước của bạn qua tin nhắn hoặc trang lạ."),
    "S08": ("money", "Thuê, mua tài khoản hoặc giấy tờ",
            "Cho thuê tài khoản ngân hàng, sim hay căn cước có thể khiến bạn liên đới khi chúng bị dùng để lừa người khác."),
    "S09": ("pressure", "Hối thúc hoặc đe doạ",
            "Hạn chót gấp, doạ khoá tài khoản, phạt hay khởi tố là để bạn làm theo trước khi kịp suy nghĩ."),
    "S10": ("pressure", "Bảo bạn giữ bí mật",
            "Bị dặn không được nói với ai hay không được kiểm tra lại là dấu hiệu rất mạnh."),
    "S11": ("channel", "Kéo sang kênh nhắn tin riêng",
            "Chuyển sang Zalo, Telegram hay inbox riêng giúp kẻ gian tránh sự kiểm soát của nền tảng."),
    "S12": ("channel", "Link hoặc ứng dụng đáng ngờ",
            "Tên miền nhái, đuôi lạ, link rút gọn hoặc file cài đặt ngoài kho ứng dụng chính thức."),
    "S13": ("bait", "Tuyển dụng không rõ ai tuyển",
            "Không nêu công ty, địa chỉ hay công việc cụ thể, chỉ hứa thu nhập và bảo nhắn tin riêng."),
    "S14": ("channel", "Chữ bị biến dạng để né bộ lọc",
            "Thay chữ bằng số, chèn ký tự lạ vào giữa từ để qua mặt bộ lọc tin rác."),
}
assert set(SIGNAL_UI) == set(SIGNAL_IDS)


def signal_catalog():
    tax = {s["id"]: s for s in load_taxonomy()["signals"]}
    return [{"id": i, "group": g, "name": n, "why": w, "full_name": tax[i]["name"]}
            for i, (g, n, w) in SIGNAL_UI.items()]


# ---------------------------------------------------------------- tìm bằng chứng trong tin

def _normalize_with_map(s, fold=False):
    """Chuẩn hoá để so khớp (chữ thường, gộp khoảng trắng, nháy cong → thẳng; fold=True thì bỏ dấu tiếng Việt)
    và giữ bản đồ vị trí về chuỗi gốc."""
    out, pos = [], []
    prev_space = False
    for i, ch in enumerate(unicodedata.normalize("NFC", s)):
        c = ch.lower()
        c = {"“": '"', "”": '"', "‘": "'", "’": "'"}.get(c, c)
        if fold:
            c = "d" if c == "đ" else unicodedata.normalize("NFD", c)[0]
        if c.isspace():
            if prev_space:
                continue
            c, prev_space = " ", True
        else:
            prev_space = False
        out.append(c)
        pos.append(i)
    return "".join(out), pos


def _approx(needle, hay):
    """Tìm đoạn trong hay gần giống needle (model sửa vài chữ, thêm dấu…). Trả về (đầu, cuối) hoặc None."""
    if len(needle) < 8:
        return None
    m = SequenceMatcher(None, hay, needle, autojunk=False).find_longest_match(0, len(hay), 0, len(needle))
    if m.size < max(5, len(needle) // 4):
        return None
    start = max(0, m.a - m.b - 4)
    end = min(len(hay), m.a + (len(needle) - m.b) + 4)
    sm = SequenceMatcher(None, hay[start:end], needle, autojunk=False)
    blocks = [x for x in sm.get_matching_blocks() if x.size]
    if not blocks or sum(x.size for x in blocks) / len(needle) < 0.8:
        return None
    return start + blocks[0].a, start + blocks[-1].a + blocks[-1].size


def locate_detail(evidence, text):
    """Trả về (spans, exact): spans là list (start, end) trong text; exact=False nếu phải so gần đúng.
    Bằng chứng có '…' thì tìm từng phần. Thứ tự thử: nguyên văn → bỏ khác biệt khoảng trắng/hoa thường
    → bỏ dấu → gần đúng (chỉ để tô sáng trên giao diện; số liệu 'bằng chứng có thật' khi đánh giá vẫn so nguyên văn)."""
    parts = [p.strip(" .\"'“”") for p in re.split(r"…|\.\.\.", evidence)]
    parts = [p for p in parts if len(p) >= 2]
    norm_text, pos = _normalize_with_map(text)
    fold_text, fpos = _normalize_with_map(text, fold=True)
    spans, exact = [], True
    for p in parts:
        i = text.find(p)
        if i >= 0:
            spans.append((i, i + len(p)))
            continue
        np_ = _normalize_with_map(p)[0].strip()
        j = norm_text.find(np_) if np_ else -1
        if j >= 0:
            spans.append((pos[j], pos[j + len(np_) - 1] + 1))
            continue
        fp = _normalize_with_map(p, fold=True)[0].strip()
        j = fold_text.find(fp) if fp else -1
        hit = (j, j + len(fp)) if j >= 0 else _approx(fp, fold_text)
        if hit:
            spans.append((fpos[hit[0]], fpos[hit[1] - 1] + 1))
            exact = False
    return spans, exact


def locate(evidence, text):
    return locate_detail(evidence, text)[0]


def segment(text, marks):
    """marks: list (start, end, signal_id) → các đoạn liên tiếp [{text, signals}] để tô sáng."""
    cuts = {0, len(text)}
    for a, b, _ in marks:
        cuts.update((a, b))
    cuts = sorted(c for c in cuts if 0 <= c <= len(text))
    segs = []
    for a, b in zip(cuts, cuts[1:]):
        if a == b:
            continue
        ids = sorted({sid for x, y, sid in marks if x <= a and b <= y}, key=SIGNAL_IDS.index)
        if segs and segs[-1]["signals"] == ids:
            segs[-1]["text"] += text[a:b]
        else:
            segs.append({"text": text[a:b], "signals": ids})
    return segs


# ---------------------------------------------------------------- kết quả cho app

def level_of(confidence, links, obfuscation=()):
    """Trả về (mức, lý do nâng mức hoặc None)."""
    if confidence >= SCAM_AT:
        return "scam", None
    if confidence > SAFE_AT:
        return "caution", None
    if any(l["kind"] == "lookalike" for l in links):
        return "caution", "Nâng lên mức cần cẩn thận vì trong tin có tên miền nhái."
    if any(o["kind"] in OBF_STRONG for o in obfuscation):
        return "caution", "Nâng lên mức cần cẩn thận vì chữ trong tin bị cố tình biến dạng."
    return "safe", None


def cost_of(usage, cfg):
    pin, pout = cfg.get("price_in", 0), cfg.get("price_out", 0)
    pcw = cfg.get("price_cache_write", pin * 1.25)
    pcr = cfg.get("price_cache_read", pin * 0.1)
    u = usage or {}
    return (u.get("input_tokens", 0) * pin + u.get("cache_write_tokens", 0) * pcw
            + u.get("cache_read_tokens", 0) * pcr + u.get("output_tokens", 0) * pout) / 1e6


class AnalyzeError(Exception):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status


def analyze(text, predictor, cfg):
    """text đã được kiểm tra độ dài. Trả về dict để gửi cho giao diện."""
    t0 = time.time()
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n")).strip()
    r = predictor.predict({"id": "app", "source_type": "sms", "text": text})
    out = r.get("output")
    if not out or not isinstance(out, dict) or out.get("label") not in ("scam", "legit"):
        raise AnalyzeError(r.get("error") or "Model không trả về kết quả đúng định dạng.")

    try:
        conf = float(out.get("confidence", 0.5))
    except (TypeError, ValueError):
        conf = 0.5
    conf = min(1.0, max(0.0, conf))
    notes = []
    signals, marks, seen = [], [], set()
    for s in out.get("signals") or []:
        sid = (s or {}).get("id")
        if sid not in SIGNAL_UI:
            continue
        if sid in seen:
            notes.append(f"Model nêu dấu hiệu “{SIGNAL_UI[sid][1]}” hai lần, app đã gộp lại.")
            continue
        seen.add(sid)
        ev = str(s.get("evidence") or "")[:300]
        spans, exact = locate_detail(ev, text)
        marks += [(a, b, sid) for a, b in spans]
        g, name, why = SIGNAL_UI[sid]
        signals.append({"id": sid, "group": g, "name": name, "why": why, "evidence": ev,
                        "found": bool(spans), "exact": bool(spans) and exact})
    signals.sort(key=lambda s: SIGNAL_IDS.index(s["id"]))

    links = find_links(text)
    obfuscation = find_obfuscation(text)
    level, why = level_of(conf, links, obfuscation)
    if why:
        notes.append(why)
    usage = r.get("usage") or {}
    return {
        "level": level,
        "label": out["label"],
        "confidence": round(conf, 3),
        "explanation": str(out.get("explanation") or "").strip(),
        "signals": signals,
        "segments": segment(text, marks),
        "links": links,
        "obfuscation": obfuscation,
        "notes": notes,
        "meta": {
            "model": cfg.get("name"),
            "model_id": cfg.get("model"),
            "prompt": APP_PROMPT,
            "latency_s": round(r.get("latency_s") or (time.time() - t0), 2),
            "cost_usd": round(cost_of(usage, cfg), 6),
            "input_tokens": usage.get("input_tokens", 0) + usage.get("cache_read_tokens", 0)
                            + usage.get("cache_write_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        },
    }
