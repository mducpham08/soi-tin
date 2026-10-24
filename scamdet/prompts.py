"""Dựng prompt từ template trong thư mục prompts/ và taxonomy.json.

Template dùng các chỗ trống:
  {taxonomy_brief}  – mã + tên dấu hiệu
  {taxonomy_full}   – mã + tên + định nghĩa + cụm từ gợi ý + trường hợp không gán
Mỗi phiên bản prompt là một file prompts/<tên>.txt: sửa prompt thì tạo file mới, không sửa đè.
"""
from . import PROMPT_DIR
from .data import load_taxonomy


def _brief(tax):
    return "\n".join(f"- {s['id']}: {s['name']}" for s in tax["signals"])


def _full(tax):
    parts = []
    for s in tax["signals"]:
        parts.append(
            f"### {s['id']} – {s['name']}\n"
            f"Gán khi: {s['definition']}\n"
            f"Cụm từ gợi ý: {s['cues']}\n"
            f"Không gán khi: {s['exclusions']}"
        )
    return "\n\n".join(parts)


def build_system_prompt(name):
    template = (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")
    tax = load_taxonomy()
    return template.replace("{taxonomy_brief}", _brief(tax)).replace("{taxonomy_full}", _full(tax))


def build_user_message(inp, with_source_type=False):
    """Mặc định KHÔNG cho model biết loại nguồn: trong v1.0 mọi mẫu chat/email đều là scam,
    nên đưa source_type vào prompt sẽ tạo 'đường tắt' làm điểm đẹp giả."""
    head = f"Loại nguồn: {inp['source_type']}\n\n" if with_source_type else ""
    return f"{head}Nội dung tin:\n<<<\n{inp['text']}\n>>>"


def list_prompts():
    return sorted(p.stem for p in PROMPT_DIR.glob("*.txt"))
