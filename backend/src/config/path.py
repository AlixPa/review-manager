from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PathConfig:
    _src_static: Path = Path(__file__).resolve().parents[1] / "static"
    front_dist: Path = _src_static.parents[2] / "frontend" / "dist"
    sqlite_db_file: Path = _src_static / "localdb.sqlite"

    current_mock_user_json_file = _src_static / "current_mock_user.json"

    def __post_init__(self):
        self._src_static.mkdir(parents=True, exist_ok=True)


path_config = PathConfig()
