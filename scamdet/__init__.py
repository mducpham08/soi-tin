"""scamdet – đánh giá LLM phát hiện dấu hiệu lừa đảo trong tin tiếng Việt."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_VERSION = "1.0"
DATA_DIR = ROOT / "data" / f"v{DATA_VERSION}"
SCHEMA_PATH = ROOT / "schema" / "output.schema.json"
PROMPT_DIR = ROOT / "prompts"
RUNS_DIR = ROOT / "runs"
SIGNAL_IDS = [f"S{i:02d}" for i in range(1, 15)]
