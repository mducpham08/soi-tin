"""Kiểm thử app và phần hậu xử lý. Chạy:  python -m unittest discover -s tests -v
Không gọi API thật: dùng model giả."""
import os, sys, unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scamdet.analyze import AnalyzeError, analyze, level_of, locate, segment  # noqa: E402
from scamdet.links import find_links  # noqa: E402


class StubPredictor:
    def __init__(self, output=None, error=None):
        self.output, self.error = output, error

    def predict(self, inp):
        return {"output": self.output, "raw": "", "error": self.error, "latency_s": 1.0,
                "usage": {"input_tokens": 100, "output_tokens": 200, "cache_read_tokens": 6000, "cache_write_tokens": 0}}


HAIKU = {"name": "haiku", "model": "claude-haiku-5-5", "price_in": 0.10, "price_out": 0.50, "price_cache_read": 0.01}


def kinds(text):
    return {l["host"]: l["kind"] for l in find_links(text)}


class LinkTests(unittest.TestCase):
    def test_lookalike_brand(self):
        self.assertEqual(kinds("vao https://vietcombank-xacthuc.top/kyc ngay"), {"vietcombank-xacthuc.top": "lookalike"})
        self.assertEqual(kinds("vtvcab.giahan-kenh.cc"), {"vtvcab.giahan-kenh.cc": "lookalike"})
        self.assertEqual(kinds("http://vietc0mbank.net"), {"vietc0mbank.net": "lookalike"})

    def test_fake_government(self):
        k = kinds("Tra cuu tai [http://thuedientu.gdt-gov.vip]")
        self.assertEqual(k, {"thuedientu.gdt-gov.vip": "lookalike"})

    def test_official_and_gov(self):
        self.assertEqual(kinds("https://km.vtmoney.vn/abc"), {"km.vtmoney.vn": "official"})
        self.assertEqual(kinds("dichvucong.gov.vn"), {"dichvucong.gov.vn": "gov"})
        self.assertEqual(kinds("info@uef.edu.vn"), {"uef.edu.vn": "edu"})

    def test_channels(self):
        self.assertEqual(kinds("ib zalo.me/0123456789 hoac t.me/abc"), {"zalo.me": "messaging", "t.me": "messaging"})
        self.assertEqual(kinds("bit.ly/qua-tang"), {"bit.ly": "shortener"})
        self.assertEqual(kinds("gui CV ve hr.tuyendung@gmail.com"), {"gmail.com": "freemail"})

    def test_defanged_and_no_false_positive(self):
        self.assertEqual(kinds("evil[.]top"), {"evil.top": "unknown"})
        self.assertEqual(kinds("So tien 2.000.000 VND tai TP.HCM, v.v."), {})


class ObfuscationTests(unittest.TestCase):
    def kinds(self, text):
        from scamdet.obfuscation import find_obfuscation
        return {o["kind"]: o["samples"] for o in find_obfuscation(text)}

    def test_detects_tricks(self):
        k = self.kinds("*VjgOLLìỉiXxịìSsiịêệuụHhóottTaáamChjjínnNghhijìnn<auZ0gVZHX.njzalo.me)")
        self.assertIn("scramble", k)
        self.assertEqual(self.kinds("Th0ng bao: vui l0ng dang nhap")["digit"], ["Th0ng", "l0ng"])
        self.assertIn("digit", self.kinds("[B00king_CTV] Thông báo tuyển dụng"))
        self.assertIn("symbol", self.kinds("Ch|ic mung b@n trung thuong"))
        self.assertIn("homoglyph", self.kinds("Tài khoản Vіetcombank của bạn"))   # 'і' Kirin
        self.assertIn("invisible", self.kinds("Vietcom\u200bbank"))
        self.assertIn("fancy", self.kinds("𝐓𝐡𝐨̂𝐧𝐠 𝐭𝐢𝐧 𝐜𝐡𝐢 𝐭𝐢𝐞̂́𝐭"))

    def test_no_false_alarm(self):
        for t in ["Gói ST5KM đã hết hạn, soạn D15 gửi 1543. Virus H5N1, mạng 4G/5G, HK1.",
                  "Gửi CV về hr@congty.vn hoặc truy cập https://abc.vn/tuyen-dung2026",
                  "Bạn lưu ý hưu trí và cứu trợ, iPhone 17 Pro giá tốt tại LazaDa.",
                  "Quy khach dang thuc hien thanh toan QR, ma OTP 482913 hieu luc 3 phut"]:
            self.assertEqual(self.kinds(t), {}, t)

    def test_links_after_normalizing(self):
        self.assertEqual(kinds("vào 𝐛𝐢𝐭.𝐥𝐲/abc"), {"bit.ly": "shortener"})
        self.assertEqual(kinds("trang vietcombank(dot)xacminh(.)top"), {"vietcombank.xacminh.top": "lookalike"})
        self.assertEqual(kinds("<auZ0gVZHX.njzalo.me)"), {"auz0gvzhx.njzalo.me": "lookalike"})
        self.assertEqual(kinds("https://mfa.gov.bn/hoc-bong"), {"mfa.gov.bn": "gov"})
        self.assertEqual(kinds("zalopay.vn momo.vn devnet.io"), {"zalopay.vn": "official", "momo.vn": "official",
                                                               "devnet.io": "unknown"})


class EvidenceTests(unittest.TestCase):
    def test_exact_and_normalized(self):
        t = "Tai khoan cua Quy khach  se bi\nKHOA trong 24h"
        self.assertEqual(locate("Quy khach", t), [(14, 23)])
        a, b = locate("se bi khoa trong 24h", t)[0]
        self.assertEqual(t[a:b], "se bi\nKHOA trong 24h")

    def test_ellipsis_and_missing(self):
        t = "Ban da trung thuong 50 trieu. Vui long nap phi 200k de nhan."
        spans = locate("trung thuong … nap phi 200k", t)
        self.assertEqual([t[a:b] for a, b in spans], ["trung thuong", "nap phi 200k"])
        self.assertEqual(locate("khong co trong tin", t), [])

    def test_rewritten_evidence(self):
        from scamdet.analyze import locate_detail
        t = "[Sh0pee] Ch|ic mung b@n trung giai thuong iPhone 17 trong chuong trinh tri an khach hang."
        spans, exact = locate_detail("Chúc mừng bạn trúng giải thưởng iPhone 17 trong chương trình tri ân", t)
        self.assertFalse(exact)
        self.assertEqual(t[spans[0][0]:spans[0][1]], "Ch|ic mung b@n trung giai thuong iPhone 17 trong chuong trinh tri an")
        spans, exact = locate_detail("Nhận quà ngay", "Nhan qua ngay hom nay")
        self.assertEqual((spans, exact), ([(0, 13)], False))
        self.assertEqual(locate_detail("một câu hoàn toàn không có trong tin này", t), ([], True))

    def test_segment_overlap(self):
        segs = segment("abcdefgh", [(1, 5, "S02"), (3, 7, "S11")])
        self.assertEqual([(s["text"], s["signals"]) for s in segs],
                         [("a", []), ("bc", ["S02"]), ("de", ["S02", "S11"]), ("fg", ["S11"]), ("h", [])])
        self.assertEqual("".join(s["text"] for s in segs), "abcdefgh")


class AnalyzeTests(unittest.TestCase):
    TEXT = "[VCB] Tai khoan se bi khoa trong 24h. Cap nhat tai https://vietcombank-xacthuc.top/kyc"

    def test_postprocess(self):
        out = {"label": "scam", "confidence": 0.95, "explanation": "Mạo danh ngân hàng.",
               "signals": [{"id": "S12", "evidence": "https://vietcombank-xacthuc.top/kyc"},
                           {"id": "S09", "evidence": "se bi khoa trong 24h"},
                           {"id": "S09", "evidence": "trong 24h"},
                           {"id": "S99", "evidence": "x"},
                           {"id": "S05", "evidence": "câu không có trong tin"}]}
        r = analyze(self.TEXT, StubPredictor(out), HAIKU)
        self.assertEqual(r["level"], "scam")
        self.assertEqual([s["id"] for s in r["signals"]], ["S05", "S09", "S12"])
        self.assertEqual([s["found"] for s in r["signals"]], [False, True, True])
        self.assertEqual(len(r["notes"]), 1)
        self.assertEqual("".join(s["text"] for s in r["segments"]), self.TEXT)
        self.assertEqual(r["links"][0]["kind"], "lookalike")
        self.assertAlmostEqual(r["meta"]["cost_usd"], (100 * .10 + 6000 * .01 + 200 * .50) / 1e6)

    def test_levels(self):
        self.assertEqual(level_of(0.75, [])[0], "scam")
        self.assertEqual(level_of(0.5, [])[0], "caution")
        self.assertEqual(level_of(0.3, [])[0], "safe")
        self.assertEqual(level_of(0.1, [{"kind": "lookalike"}])[0], "caution")
        self.assertEqual(level_of(0.1, [], [{"kind": "scramble"}])[0], "caution")
        self.assertEqual(level_of(0.1, [], [{"kind": "fancy"}])[0], "safe")

    def test_lookalike_bumps_safe(self):
        out = {"label": "legit", "confidence": 0.1, "explanation": "ok", "signals": []}
        r = analyze(self.TEXT, StubPredictor(out), HAIKU)
        self.assertEqual(r["level"], "caution")
        self.assertTrue(r["notes"])

    def test_confidence_clamped(self):
        r = analyze("abc", StubPredictor({"label": "scam", "confidence": 7, "signals": [], "explanation": ""}), HAIKU)
        self.assertEqual(r["confidence"], 1.0)

    def test_model_error(self):
        with self.assertRaises(AnalyzeError):
            analyze("abc", StubPredictor(None, "JSON lỗi"), HAIKU)


class AppTests(unittest.TestCase):
    def make(self, **kw):
        from app.main import create_app
        return create_app(**kw).test_client()

    def test_fake_mode_end_to_end(self):
        c = self.make(fake=True)
        cfg = c.get("/api/config").get_json()
        self.assertEqual(cfg["mode"], "fake")
        self.assertEqual(len(cfg["signals"]), 14)
        r = c.post("/api/check", json={"text": cfg["samples"][1]["text"], "model": "haiku"})
        self.assertEqual(r.status_code, 200)
        j = r.get_json()
        self.assertIn(j["level"], ("scam", "caution", "safe"))
        self.assertEqual(r.headers["Cache-Control"], "no-store")
        self.assertIn("default-src 'self'", r.headers["Content-Security-Policy"])

    def test_validation(self):
        c = self.make(fake=True)
        self.assertEqual(c.post("/api/check", json={"text": "  "}).status_code, 400)
        self.assertEqual(c.post("/api/check", json={"text": "x" * 4001}).status_code, 400)
        self.assertEqual(c.post("/api/check", json={"text": "abc", "model": "gpt"}).status_code, 400)
        self.assertEqual(c.post("/api/check", data="không phải json").status_code, 400)

    def test_missing_key_marks_claude_unavailable(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "", "OLLAMA_URL": "http://127.0.0.1:9"}):
            c = self.make()
            models = {m["key"]: m for m in c.get("/api/config").get_json()["models"]}
            self.assertFalse(models["haiku"]["available"])
            self.assertFalse(models["qwen-local"]["available"])
            r = c.post("/api/check", json={"text": "abc", "model": "haiku"})
            self.assertEqual(r.status_code, 503)

    def test_public_limits(self):
        with mock.patch.dict(os.environ, {"APP_DAILY_PER_IP": "2", "APP_DAILY_TOTAL": "100"}):
            c = self.make(fake=True, public=True)
            cfg = c.get("/api/config").get_json()
            self.assertEqual([m["key"] for m in cfg["models"]], ["haiku"])
            self.assertEqual(c.post("/api/check", json={"text": "abc", "model": "sonnet"}).status_code, 400)
            codes = [c.post("/api/check", json={"text": "abc", "model": "haiku"}).status_code for _ in range(3)]
            self.assertEqual(codes, [200, 200, 429])

    def test_static(self):
        c = self.make(fake=True)
        for path, code in [("/", 200), ("/static/app.js", 200), ("/static/fonts/inter-400.woff", 200),
                           ("/static/../models.json", 404)]:
            with c.get(path) as r:
                self.assertEqual(r.status_code, code, path)


if __name__ == "__main__":
    unittest.main()
