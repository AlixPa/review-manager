from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT_PATH = Path(__file__).resolve().parents[2]
load_dotenv(
    dotenv_path=REPO_ROOT_PATH / ".env",
    override=False,
)
