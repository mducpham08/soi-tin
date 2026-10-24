"""Web app kiểm tra tin nhắn lừa đảo (Flask).

Chạy trên máy:
    python -m app.main                 # http://127.0.0.1:8000, có Haiku / Sonnet / Qwen (nếu đã mở Ollama)
    python -m app.main --fake          # không gọi AI: dùng luật từ khóa, để thử giao diện
    python -m app.main --public        # chế độ công khai: chỉ Haiku, giới hạn lượt / IP / ngày

Biến môi trường (đặt trong .env):
    ANTHROPIC_API_KEY      key Claude (bản công khai nên dùng key riêng, có giới hạn chi tiêu)
    OLLAMA_URL             mặc định http://localhost:11434
    APP_DAILY_PER_IP       số lượt / IP / ngày ở chế độ công khai (mặc định 20)
    APP_DAILY_TOTAL        tổng số lượt / ngày ở chế độ công khai (mặc định 300)
    APP_TRUST_PROXY=1      lấy IP từ X-Forwarded-For (chỉ bật khi chạy sau reverse proxy)

App KHÔNG lưu nội dung tin: không ghi file, không ghi log nội dung.
"""
import argparse, datetime, json, os, sys, threading, urllib.request
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scamdet.analyze import (APP_PROMPT, GROUPS, MAX_CHARS, SAFE_AT, SCAM_AT, AnalyzeError, analyze,
                             signal_catalog)
from scamdet.models import RulesPredictor, load_dotenv, load_model_config, make_predictor
from scamdet.prompts import build_system_prompt

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"

MODEL_CHOICES = [
    {"key": "haiku", "label": "Haiku 5.5", "hint": "Nhanh, rẻ. Mặc định."},
    {"key": "sonnet", "label": "Sonnet 5.5", "hint": "Chính xác hơn, đắt hơn khoảng 14 lần."},
    {"key": "qwen-local", "label": "Qwen trên máy", "hint": "Tin không rời khỏi máy, chậm hơn."},
]


class DailyLimiter:
    """Đếm lượt theo ngày, giữ trong RAM (khởi động lại thì đếm lại)."""
    def __init__(self, per_ip, total):
        self.per_ip, self.total = per_ip, total
        self.lock = threading.Lock()
        self.day, self.by_ip, self.count = None, {}, 0

    def hit(self, ip):
        today = datetime.date.today()
        with self.lock:
            if today != self.day:
                self.day, self.by_ip, self.count = today, {}, 0
            if self.count >= self.total:
                return "Hôm nay app đã hết lượt kiểm tra. Bạn quay lại vào ngày mai nhé."
            if self.by_ip.get(ip, 0) >= self.per_ip:
                return f"Mỗi người được kiểm tra {self.per_ip} tin mỗi ngày. Bạn quay lại vào ngày mai nhé."
            self.by_ip[ip] = self.by_ip.get(ip, 0) + 1
            self.count += 1
            return None


def ollama_status(model_tag):
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=0.8) as r:
            tags = {m.get("name") for m in json.loads(r.read().decode("utf-8")).get("models", [])}
    except Exception:
        return False, "Chưa mở Ollama trên máy."
    if model_tag not in tags and f"{model_tag}:latest" not in tags:
        return False, f"Ollama chưa có model {model_tag} (chạy: ollama pull {model_tag})."
    return True, None


def create_app(fake=False, public=False):
    load_dotenv()
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
    app.json.sort_keys = False
    system_prompt = build_system_prompt(APP_PROMPT)
    samples = json.loads((HERE / "samples.json").read_text(encoding="utf-8"))
    limiter = DailyLimiter(int(os.environ.get("APP_DAILY_PER_IP", 20)), int(os.environ.get("APP_DAILY_TOTAL", 300)))
    predictors, lock = {}, threading.Lock()
    mode = "fake" if fake else "public" if public else "local"

    def choices():
        out = []
        for c in MODEL_CHOICES:
            if public and c["key"] != "haiku":
                continue
            ok, why = True, None
            if not fake:
                cfg = load_model_config(c["key"])
                if cfg["provider"] == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
                    ok, why = False, "Thiếu ANTHROPIC_API_KEY trong .env."
                elif cfg["provider"] == "ollama":
                    ok, why = ollama_status(cfg["model"])
            out.append(dict(c, available=ok, reason=why))
        return out

    def get_predictor(key):
        with lock:
            if key not in predictors:
                if fake:
                    predictors[key] = (RulesPredictor({"name": "rules"}), {"name": key, "model": "luật từ khóa"})
                else:
                    cfg = load_model_config(key)
                    predictors[key] = (make_predictor(cfg, system_prompt), cfg)
            return predictors[key]

    def client_ip():
        if os.environ.get("APP_TRUST_PROXY") == "1" and request.headers.get("X-Forwarded-For"):
            return request.headers["X-Forwarded-For"].split(",")[0].strip()
        return request.remote_addr or "?"

    @app.after_request
    def security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.get("/")
    def index():
        return send_from_directory(STATIC, "index.html")

    @app.get("/static/<path:name>")
    def static_files(name):
        return send_from_directory(STATIC, name)

    @app.get("/api/config")
    def config():
        return jsonify({
            "mode": mode,
            "prompt": APP_PROMPT,
            "max_chars": MAX_CHARS,
            "thresholds": {"scam": SCAM_AT, "safe": SAFE_AT},
            "models": choices(),
            "groups": GROUPS,
            "signals": signal_catalog(),
            "samples": samples,
            "limits": {"per_ip": limiter.per_ip, "total": limiter.total} if public else None,
        })

    @app.post("/api/check")
    def check():
        body = request.get_json(silent=True) or {}
        text = str(body.get("text") or "").strip()
        key = str(body.get("model") or "haiku")
        if not text:
            return jsonify(error="Bạn chưa dán nội dung tin."), 400
        if len(text) > MAX_CHARS:
            n = lambda x: f"{x:,}".replace(",", ".")
            return jsonify(error=f"Tin dài {n(len(text))} ký tự, quá giới hạn {n(MAX_CHARS)}. "
                                 "Hãy chỉ dán phần nội dung đáng ngờ."), 400
        choice = next((c for c in choices() if c["key"] == key), None)
        if choice is None:
            return jsonify(error="Model này không có ở chế độ hiện tại."), 400
        if not choice["available"]:
            return jsonify(error=choice["reason"]), 503
        if public:
            why = limiter.hit(client_ip())
            if why:
                return jsonify(error=why), 429
        predictor, cfg = get_predictor(key)
        try:
            result = analyze(text, predictor, dict(cfg, name=key))
        except AnalyzeError as e:
            return jsonify(error=f"Không nhận được kết quả từ model: {e}"), e.status
        if fake:
            result["meta"]["model_id"] = "luật từ khóa (chế độ thử)"
        return jsonify(result)

    return app


def main():
    ap = argparse.ArgumentParser(description="Web app kiểm tra tin nhắn lừa đảo")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--fake", action="store_true", help="không gọi AI, dùng luật từ khóa (thử giao diện)")
    ap.add_argument("--public", action="store_true", help="chỉ Haiku, bật giới hạn lượt")
    a = ap.parse_args()
    app = create_app(fake=a.fake, public=a.public)
    print(f"Mở trình duyệt: http://{a.host}:{a.port}   (chế độ: {'thử' if a.fake else 'công khai' if a.public else 'trên máy'})")
    app.run(host=a.host, port=a.port, threaded=True, debug=False)


if __name__ == "__main__":
    main()
