"""Tìm link / tên miền / email trong tin và so với danh sách tên miền chính thức (data/official_domains.json).

Đây là lớp GỢI Ý chạy ngoài model, không dùng khi đánh giá trên dev/test:
  official   – tên miền thật của một thương hiệu trong danh sách
  gov / edu  – đuôi .gov.vn / .edu.vn
  freemail   – email miễn phí (gmail, yahoo…)
  lookalike  – chứa tên thương hiệu / cơ quan nhưng không phải tên miền thật của họ
  shortener  – link rút gọn, không thấy đích đến
  messaging  – dẫn sang Zalo, Telegram, Messenger…
  unknown    – không có trong danh sách
"""
import json, re, unicodedata
from functools import lru_cache
from . import ROOT
from .obfuscation import normalize_text

DOMAINS_PATH = ROOT / "data" / "official_domains.json"

_TLDS = ("com|net|org|vn|info|biz|top|xyz|vip|cc|me|io|co|ly|link|site|online|shop|store|club|live|app|dev|"
         "ml|tk|ga|cf|gq|icu|bond|buzz|space|fun|asia|pro|cn|ru|in|us|uk|gl|gd|ws|tv|cloud|work|email|life|"
         "today|page|at|id|de|be|sh|so|to|ai|win|bet|cyou|sbs|cfd|click|lol|rest|monster|homes|mobi")
_URL_RX = re.compile(r"(?:https?://|www\.)[^\s<>\"'\]\)\}]+", re.I)
_EMAIL_RX = re.compile(r"[\w.+-]+@((?:[a-z0-9-]+\.)+[a-z]{2,})", re.I)
_BARE_RX = re.compile(rf"(?<![\w@.-])((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:{_TLDS}))(?=$|[/\s:?#),.;!\]\"'])", re.I)
_LEET = str.maketrans({"0": "o", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b"})


@lru_cache(maxsize=1)
def load_domains():
    with open(DOMAINS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _host_of(url):
    u = re.sub(r"^(?:https?://)", "", url, flags=re.I)
    host = re.split(r"[/?#:]", u, maxsplit=1)[0].lower().strip(".")
    return host[4:] if host.startswith("www.") else host


def _ends_with(host, domain):
    return host == domain or host.endswith("." + domain)


def _lev1(a, b):
    """True nếu a và b khác nhau đúng một ký tự (thêm, bớt hoặc thay)."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    s, l = (a, b) if len(a) < len(b) else (b, a)
    return any(l[:i] + l[i + 1:] == s for i in range(len(l)))


def classify_host(host):
    cfg = load_domains()
    for d, platform in cfg["messaging"].items():
        if _ends_with(host, d):
            return {"kind": "messaging", "brand": platform,
                    "note": f"Dẫn sang {platform}: người ở đầu bên kia có thể là bất kỳ ai."}
    for b in cfg["brands"]:
        if any(_ends_with(host, d) for d in b["domains"]):
            return {"kind": "official", "brand": b["name"], "note": f"Tên miền thật của {b['name']}."}
    if host.endswith(cfg["gov_suffix"]):
        return {"kind": "gov", "brand": None, "note": "Tên miền .gov.vn của cơ quan nhà nước."}
    m = re.search(r"\.gov(\.[a-z]{2})?$", host)
    if m:
        return {"kind": "gov", "brand": None, "note": f"Tên miền chính phủ nước ngoài ({m.group(0)})."}
    if host.endswith(cfg.get("edu_suffix", ".edu.vn")):
        return {"kind": "edu", "brand": None, "note": "Tên miền .edu.vn của cơ sở giáo dục."}
    if host in cfg.get("freemail", []):
        return {"kind": "freemail", "brand": None,
                "note": "Email miễn phí, ai cũng tạo được. Tổ chức thật thường dùng email theo tên miền riêng."}
    # các phần chữ của tên miền, bỏ đuôi cuối (vd. vietcombank-xacthuc.top → vietcombank, xacthuc)
    labels = host.split(".")[:-1] or host.split(".")
    pieces = [p for lab in labels for p in re.split(r"[-_]", lab) if p]
    norm_labels = [lab.translate(_LEET) for lab in labels]
    for b in cfg["brands"]:
        for t in b["tokens"]:
            if len(t) <= 3:      # chữ quá ngắn (vcb, evn, gov): phải đứng riêng, tránh khớp nhầm
                hit = t in pieces or t in [p.translate(_LEET) for p in pieces]
            elif len(t) == 4:    # zalo, momo, bidv…: được nằm trong chữ khác (njzalo.me)
                hit = any(t in lab for lab in norm_labels)
            else:
                hit = any(t in lab for lab in norm_labels) or any(_lev1(t, p.translate(_LEET)) for p in pieces)
            if hit:
                who = b["name"]
                note = ("Giả dạng cơ quan nhà nước nhưng không có đuôi .gov.vn." if who == "cơ quan nhà nước"
                        else f"Có chữ giống “{t}” nhưng không phải tên miền thật của {who}.")
                return {"kind": "lookalike", "brand": who, "note": note}
    for d in cfg["shorteners"]:
        if _ends_with(host, d):
            return {"kind": "shortener", "brand": None, "note": "Link rút gọn, không xem được đích đến thật."}
    return {"kind": "unknown", "brand": None, "note": "Không có trong danh sách tên miền đã biết."}


def find_links(text):
    """Trả về danh sách {text, host, source: url|email|domain, kind, brand, note}, không trùng host."""
    t = unicodedata.normalize("NFC", normalize_text(text))
    t = re.sub(r"\s?(?:\[\.\]|\(\.\)|\{\.\}|\[dot\]|\(dot\))\s?", ".", t, flags=re.I)   # link viết né: abc[.]com, abc(dot)com
    found, seen = [], set()

    def add(raw, host, source):
        host = host.lower().strip(".")
        if not host or "." not in host or host in seen:
            return
        seen.add(host)
        found.append(dict(text=raw, host=host, source=source, **classify_host(host)))

    spans = []
    for m in _URL_RX.finditer(t):
        raw = m.group(0).rstrip(".,;!?")
        add(raw, _host_of(raw), "url")
        spans.append(m.span())
    for m in _EMAIL_RX.finditer(t):
        add(m.group(0), m.group(1), "email")
        spans.append(m.span())
    for m in _BARE_RX.finditer(t):
        if any(a <= m.start() < b for a, b in spans):
            continue
        add(m.group(1), m.group(1), "domain")
    return found
