"""Lớp gọi model dùng chung. Đổi model chỉ cần đổi tên cấu hình trong models.json.

Mọi predictor trả về dict:
  output  – object JSON đã parse (hoặc None nếu lỗi)
  raw     – chuỗi thô model trả về (để soi lỗi định dạng)
  error   – thông báo lỗi (hoặc None)
  usage   – {"input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"}
  latency_s
"""
import json, os, re, time, unicodedata, urllib.request, urllib.error
from . import ROOT, SIGNAL_IDS
from .data import load_schema
from .prompts import build_user_message


def load_model_config(name):
    with open(ROOT / "models.json", encoding="utf-8") as f:
        cfgs = json.load(f)
    if name not in cfgs:
        raise SystemExit(f"Không có model '{name}' trong models.json. Có: {[k for k in cfgs if not k.startswith('_')]}")
    return dict(cfgs[name], name=name)


def load_dotenv(path=ROOT / ".env"):
    """Đọc .env đơn giản (KEY=VALUE), không ghi đè biến môi trường đã có."""
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _empty_usage():
    return {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0}


def _tool_schema():
    s = load_schema()
    return {k: v for k, v in s.items() if not k.startswith("$") and k not in ("title",)}


# Structured outputs của API không nhận các ràng buộc này; scorer vẫn kiểm tra bằng schema gốc.
_UNSUPPORTED = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
                "minLength", "maxLength", "uniqueItems", "maxItems", "title"}


def _api_json_schema(node=None):
    """Schema gốc → schema cho output_config.format (bỏ ràng buộc API không hỗ trợ)."""
    if node is None:
        node = _tool_schema()
    if isinstance(node, list):
        return [_api_json_schema(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {}
    for k, v in node.items():
        if k in _UNSUPPORTED or k.startswith("$"):
            continue
        if k == "minItems" and v not in (0, 1):
            continue
        if k == "properties":  # khóa con là tên trường, không phải từ khóa schema
            out[k] = {name: _api_json_schema(sub) for name, sub in v.items()}
        else:
            out[k] = v if k in ("enum", "required") else _api_json_schema(v)
    if "enum" in out and "type" not in out and all(isinstance(x, str) for x in out["enum"]):
        out["type"] = "string"
    return out


# ---------------------------------------------------------------- Anthropic
class AnthropicPredictor:
    """output_mode trong models.json:
      "tool"        – ép gọi tool "report" (tool_choice = tool). Dùng cho Haiku 5.5.
      "json_schema" – structured outputs (output_config.format). Dùng cho Sonnet 5.5,
                      vì model này chỉ nhận tool_choice "auto".
    Tùy chọn thêm: "thinking" (vd. {"type": "between_tools"}), "effort" (low/medium/high/...).
    """
    def __init__(self, cfg, system_prompt):
        load_dotenv()
        try:
            import anthropic
        except ImportError:
            raise SystemExit("Chưa cài thư viện anthropic: pip install -r requirements.txt")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("Thiếu ANTHROPIC_API_KEY. Tạo file .env theo mẫu .env.example.")
        self.client = anthropic.Anthropic(max_retries=5)
        self.cfg, self.system = cfg, system_prompt
        self.mode = cfg.get("output_mode", "tool")
        if self.mode not in ("tool", "json_schema"):
            raise SystemExit(f"output_mode không hợp lệ: {self.mode}")
        self.tool = {"name": "report", "description": "Ghi kết quả phân tích tin theo schema.",
                     "input_schema": _tool_schema()}
        self.json_schema = _api_json_schema()

    def predict(self, inp):
        t0 = time.time()
        kwargs = dict(
            model=self.cfg["model"],
            max_tokens=self.cfg.get("max_tokens", 1500),
            system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": build_user_message(inp)}],
        )
        extra = {}  # gửi qua extra_body để chạy được cả với bản thư viện anthropic cũ
        output_config = {}
        if self.mode == "tool":
            kwargs["tools"] = [self.tool]
            kwargs["tool_choice"] = {"type": "tool", "name": "report"}
        else:
            output_config["format"] = {"type": "json_schema", "schema": self.json_schema}
        if "effort" in self.cfg:
            output_config["effort"] = self.cfg["effort"]
        if output_config:
            extra["output_config"] = output_config
        if "thinking" in self.cfg:
            extra["thinking"] = self.cfg["thinking"]
        if extra:
            kwargs["extra_body"] = extra
        if "temperature" in self.cfg:
            kwargs["temperature"] = self.cfg["temperature"]
        try:
            resp = self.client.messages.create(**kwargs)
        except Exception as e:  # lỗi mạng / API: ghi lại, không dừng cả lượt chạy
            return {"output": None, "raw": None, "error": f"{type(e).__name__}: {e}", "usage": _empty_usage(),
                    "latency_s": time.time() - t0}
        u = resp.usage
        usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                 "cache_read_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
                 "cache_write_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0}
        stop = getattr(resp, "stop_reason", None)
        if self.mode == "json_schema":
            raw = "".join(getattr(b, "text", "") or "" for b in resp.content if b.type == "text")
            if stop in ("refusal", "max_tokens"):
                return {"output": None, "raw": raw, "error": f"stop_reason={stop}", "usage": usage,
                        "latency_s": time.time() - t0}
            try:
                out, err = json.loads(raw), None
            except json.JSONDecodeError as e:
                out, err = None, f"JSON lỗi: {e}"
            return {"output": out, "raw": raw, "error": err, "usage": usage, "latency_s": time.time() - t0}
        block = next((b for b in resp.content if b.type == "tool_use"), None)
        if block is None:
            raw = "".join(getattr(b, "text", "") for b in resp.content)
            return {"output": None, "raw": raw, "error": "Không có tool_use trong phản hồi", "usage": usage,
                    "latency_s": time.time() - t0}
        return {"output": block.input, "raw": json.dumps(block.input, ensure_ascii=False), "error": None,
                "usage": usage, "latency_s": time.time() - t0}


# ---------------------------------------------------------------- Ollama (chạy trên máy)
class OllamaPredictor:
    def __init__(self, cfg, system_prompt):
        load_dotenv()
        self.url = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/chat"
        self.cfg, self.system, self.schema = cfg, system_prompt, _tool_schema()

    def predict(self, inp):
        t0 = time.time()
        body = {"model": self.cfg["model"], "stream": False, "format": self.schema,
                "messages": [{"role": "system", "content": self.system},
                             {"role": "user", "content": build_user_message(inp)}],
                "options": {"temperature": self.cfg.get("temperature", 0), "num_ctx": self.cfg.get("num_ctx", 8192),
                            "num_predict": self.cfg.get("max_tokens", 1500)}}
        if "think" in self.cfg:  # model có chế độ suy nghĩ (vd. Qwen 3.5): tắt để trả JSON ngay
            body["think"] = self.cfg["think"]
        req = urllib.request.Request(self.url, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                resp = json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as e:
            return {"output": None, "raw": None, "error": f"Không gọi được Ollama ({self.url}): {e}",
                    "usage": _empty_usage(), "latency_s": time.time() - t0}
        msg = resp.get("message", {})
        raw = msg.get("content", "")
        usage = dict(_empty_usage(), input_tokens=resp.get("prompt_eval_count", 0), output_tokens=resp.get("eval_count", 0))
        if usage["input_tokens"] >= self.cfg.get("num_ctx", 8192) - 50:
            return {"output": None, "raw": raw, "error": "Prompt có thể đã bị cắt (vượt num_ctx)", "usage": usage,
                    "latency_s": time.time() - t0}
        try:
            out, err = json.loads(raw), None
        except json.JSONDecodeError as e:
            out, err = None, f"JSON lỗi: {e}"
            if not raw.strip() and msg.get("thinking"):
                err = f"Không có câu trả lời, chỉ có phần suy nghĩ ({len(msg['thinking'])} ký tự): cần think=false"
            elif resp.get("done_reason") == "length":
                err = "Hết num_predict trước khi xong JSON"
        return {"output": out, "raw": raw, "error": err, "usage": usage, "latency_s": time.time() - t0}


# ---------------------------------------------------------------- Baseline luật từ khóa (không dùng LLM)
def _fold(s):
    """Bỏ dấu tiếng Việt, giữ nguyên độ dài chuỗi (để cắt bằng chứng đúng vị trí)."""
    out = []
    for ch in s.lower():
        if ch == "đ":
            out.append("d")
        else:
            out.append(unicodedata.normalize("NFD", ch)[0])
    return "".join(out)


RULES = {
    "S01": r"chuyen khoan|nap tien|nap dau|dong phi|phi (ho so|xu ly|ship|bao hiem|giu cho)|dat coc|ky quy|ki quy|nop tien|thanh toan phi",
    "S02": r"trung thuong|chuc mung ban|mien phi|qua tang|loi nhuan|thu nhap (cao|hap dan|khung)|\d+ ?(k|tr|trieu)\s?/\s?(ngay|h)|nhan ngay",
    "S03": r"nhiem vu|cong tac vien|\bctv\b|danh gia (san pham|5 sao)|chot don|giat don|tha tim|subscribe|\blike\b",
    "S04": r"cong an|canh sat|toa an|vien kiem sat|co quan thue|cuc thue|bao hiem xa hoi|\bbhxh\b|\bcsgt\b|bo giao duc",
    "S05": r"(vietcombank|techcombank|bidv|vietinbank|agribank|mb ?bank|vpbank|momo|shopee|lazada|tiki|tiktok|zalo|viettel|vinamilk|grab|buu dien|dien may xanh)[^\n]{0,160}(https?://|zalo\.me|t\.me|telegram|@gmail)",
    "S06": r"\b(me|bo|ba|anh|chi|em|ban) oi\b[^\n]{0,120}(chuyen|muon|gui|nap)",
    "S07": r"\botp\b|mat khau|ma xac (nhan|thuc|minh)|\bcccd\b|can cuoc|dang nhap|xac minh thong tin|cap nhat thong tin",
    "S08": r"(thue|mua|muon) (lai )?tai khoan|mo tai khoan ho",
    "S09": r"trong (vong )?\d+ ?(gio|h|phut)|hom nay|het han|bi khoa|tam khoa|khoa tai khoan|qua han|truoc \d{1,2}(h|:|/)",
    "S10": r"bi mat|khong duoc (noi|tiet lo)|dung (goi|noi)|giu kin",
    "S11": r"telegram|zalo|t\.me/|zalo\.me|ket ban|\binbox\b|\bib\b|signal|whatsapp|nhan tin qua",
    "S12": r"bit\.ly|qrco\.de|t\.ly|\.(top|xyz|vip|cc|club|online|icu|shop|store|bond|buzz|space|fun|live)\b|\.apk\b",
    "S13": r"^(?!.*(cong ty|\bcty\b|tnhh|co phan|tap doan)).*(tuyen|viec lam)",
    "S14": r"\b\w*[a-z][0-9][a-z]\w*\b|\b(?:\w\.){3,}\w\b",
}
STRONG = {"S01", "S03", "S06", "S08", "S10", "S12"}


class RulesPredictor:
    """Baseline từ khóa: dùng làm mốc so sánh 'không cần LLM'."""
    def __init__(self, cfg, system_prompt=None):
        self.cfg = cfg
        self.rx = {k: re.compile(v, re.S) for k, v in RULES.items()}

    def predict(self, inp):
        t0 = time.time()
        text = inp["text"]
        folded = _fold(text)
        assert len(folded) == len(text)
        sigs = []
        for sid, rx in self.rx.items():
            if sid == "S13" and inp["source_type"] not in ("job_post", "sms", "chat"):
                continue
            m = rx.search(folded)
            if m:
                a, b = m.span()
                if sid == "S13":
                    a, b = m.start(2), m.end(2)
                ev = text[a:b][:200].strip() or text[:30]
                sigs.append({"id": sid, "evidence": ev})
        ids = {s["id"] for s in sigs}
        n = len(ids)
        scam = bool(ids & STRONG) or n >= 3
        conf = min(1.0, 0.15 + 0.2 * n + (0.3 if ids & STRONG else 0))
        out = {"label": "scam" if scam else "legit", "confidence": round(conf, 2), "signals": sigs,
               "explanation": f"Baseline từ khóa: khớp {', '.join(sorted(ids)) or 'không dấu hiệu nào'}."}
        return {"output": out, "raw": json.dumps(out, ensure_ascii=False), "error": None,
                "usage": _empty_usage(), "latency_s": time.time() - t0}


# ---------------------------------------------------------------- Oracle (chỉ để kiểm thử script chấm)
class OraclePredictor:
    def __init__(self, cfg, system_prompt=None, gold=None):
        self.gold = {g["id"]: g for g in (gold or [])}

    def predict(self, inp):
        g = self.gold[inp["id"]]
        ev = inp["text"][:40]
        out = {"label": g["label"], "confidence": 1.0 if g["label"] == "scam" else 0.0,
               "signals": [{"id": s, "evidence": ev} for s in g["signals"]],
               "explanation": "oracle"}
        return {"output": out, "raw": json.dumps(out, ensure_ascii=False), "error": None,
                "usage": _empty_usage(), "latency_s": 0.0}


def make_predictor(cfg, system_prompt, gold=None):
    p = cfg["provider"]
    if p == "anthropic":
        return AnthropicPredictor(cfg, system_prompt)
    if p == "ollama":
        return OllamaPredictor(cfg, system_prompt)
    if p == "rules":
        return RulesPredictor(cfg, system_prompt)
    if p == "oracle":
        return OraclePredictor(cfg, system_prompt, gold)
    raise SystemExit(f"provider không hỗ trợ: {p}")
