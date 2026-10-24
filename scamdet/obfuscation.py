"""Soi chữ bị biến dạng để né bộ lọc (dấu hiệu S14) bằng luật, chạy song song với model.

Không dịch ngược về câu gốc (kiểu xáo trộn như "Qqủuầà" mơ hồ, dịch sai còn gây hiểu lầm),
chỉ chỉ ra CHỖ nào bị biến dạng để người dùng tự thấy. Đây là lớp gợi ý của app, không dùng khi đánh giá.

Trên dữ liệu v1.0 (đo 24/10/2026): bắt được 6/7 tin có S14 ở dev, không báo nhầm tin nào trong 78 tin còn lại.
"""
import re, unicodedata

INVISIBLE = re.compile("[​-‏⁠-⁤﻿­]")
_L = "A-Za-zÀ-ỹ"
_DIGIT_IN_WORD = re.compile(rf"[{_L}][0-9]+[{_L}]")
_SYMBOL_IN_WORD = re.compile(rf"[{_L}][|@¢$!][{_L}]")
_EMAIL = re.compile(r"@[\w-]+\.\w")

KINDS = {
    "scramble": ("Chữ bị xáo trộn, lặp lại", "Chữ hoa thường đảo liên tục hoặc mỗi chữ lặp hai lần với dấu khác nhau để bộ lọc không đọc được."),
    "symbol": ("Ký hiệu chen vào giữa chữ", "Thay chữ bằng ký hiệu như @, |, ! để qua mặt bộ lọc tin rác."),
    "digit": ("Số chen vào giữa chữ", "Thay chữ bằng số trông giống (o → 0, i → 1) để qua mặt bộ lọc."),
    "homoglyph": ("Chữ của bảng chữ cái khác", "Trộn chữ Kirin hoặc Hy Lạp trông giống chữ Latin, thường dùng để làm giả tên thương hiệu."),
    "fancy": ("Chữ kiểu Unicode", "Chữ in đậm hoặc toàn khổ dạng ký tự đặc biệt, bộ lọc không đọc được như chữ thường."),
    "invisible": ("Ký tự ẩn", "Ký tự không nhìn thấy chen vào giữa chữ hoặc link."),
}
# Các loại gần như không gặp ở tin thật: được dùng để nâng mức "có vẻ an toàn" lên "cần cẩn thận"
STRONG = {"scramble", "symbol", "homoglyph", "invisible"}


def _base(c):
    return "d" if c in "đĐ" else unicodedata.normalize("NFD", c.lower())[0]


def _script(c):
    n = unicodedata.name(c, "")
    return "CYR" if "CYRILLIC" in n else "GRK" if "GREEK" in n else "LAT" if "LATIN" in n else None


def _is_fancy(c):
    return "MATHEMATICAL" in unicodedata.name(c, "") or 0xFF01 <= ord(c) <= 0xFF5E


def _around(s, a, b, pad=8):
    """Lấy đoạn quanh vị trí khớp để làm ví dụ, cắt theo chữ/số."""
    i, j = a, b
    while i > 0 and a - i < pad and (s[i - 1].isalnum() or s[i - 1] in "|@¢$!_"):
        i -= 1
    while j < len(s) and j - b < pad and (s[j].isalnum() or s[j] in "|@¢$!_"):
        j += 1
    return ("…" if i > 0 else "") + s[i:j] + ("…" if j < len(s) else "")


def normalize_text(text):
    """Bản chuẩn hoá để TÌM LINK (không gửi cho model): đổi chữ kiểu Unicode về chữ thường, bỏ ký tự ẩn."""
    t = INVISIBLE.sub("", text)
    return "".join(unicodedata.normalize("NFKC", c) if _is_fancy(c) else c for c in t)


def find_obfuscation(text):
    """Trả về list {kind, label, note, samples} theo thứ tự KINDS, mỗi loại tối đa 4 ví dụ."""
    hits = {k: [] for k in KINDS}

    def add(kind, sample):
        sample = sample[:40] + ("…" if len(sample) > 40 else "")
        if sample not in hits[kind] and len(hits[kind]) < 4:
            hits[kind].append(sample)

    n_inv = len(INVISIBLE.findall(text))
    if n_inv:
        add("invisible", f"{n_inv} ký tự")
    fancy = [c for c in text if _is_fancy(c)]
    if len(fancy) >= 3:
        run = re.search(r"(?:[\U0001D400-\U0001D7FF！-～][̀-ͯ]*\s?){3,}", text)
        add("fancy", run.group(0).strip() if run else "".join(fancy[:12]))

    for tok in re.findall(r"\S+", INVISIBLE.sub("", text)):
        core = tok.strip("()[]{}<>.,;:!?\"'*“”")
        if not core or "://" in core or core.lower().startswith("www.") or _EMAIL.search(core):
            continue
        if not re.fullmatch(r"[0-9A-Z_\-/.]+", core):     # bỏ mã viết hoa + số như ST5KM, H5N1, HK1
            for m in _DIGIT_IN_WORD.finditer(core):
                add("digit", _around(core, m.start(), m.end()))
        for m in _SYMBOL_IN_WORD.finditer(core):
            add("symbol", _around(core, m.start(), m.end()))
        flips = sum(1 for a, b in zip(core, core[1:]) if a.isalpha() and b.isalpha() and a.islower() and b.isupper())
        pairs = sum(1 for a, b in zip(core, core[1:])
                    if a.isalpha() and b.isalpha() and a != b and _base(a) == _base(b))
        if flips >= 3 or pairs >= 3:
            add("scramble", core)
        scripts = {_script(c) for c in core if c.isalpha()} - {None}
        if "LAT" in scripts and scripts & {"CYR", "GRK"}:
            add("homoglyph", core)

    return [{"kind": k, "label": KINDS[k][0], "note": KINDS[k][1], "samples": v} for k, v in hits.items() if v]
