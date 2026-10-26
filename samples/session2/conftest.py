"""第 2 回 ハンズオン⑥（テスト生成）用の pytest 設定。

責任分界：
- 本ファイル（conftest.py）：受講者が **Inline Chat / Agent モードで生成したテストファイル**を
  そのまま `pytest tests/` で実行できるよう、最低限の sys.path 調整を行う安全網。
  conftest.py は pytest 起動時に**自動発見**されるため、複雑な設定なしに動く前提を作る。
- pyproject.toml：プロジェクトのデフォルト pytest オプション（`addopts`、`testpaths`、`pythonpath`）。
  CLI で再指定すれば上書きされる位置づけ。
- ワークブックの `pytest tests/ --cov=buggy_book_app -v`：
  pyproject.toml の `addopts = "-v"` と `testpaths = ["tests"]` と一部重複しているが、
  受講者が**コピペで動作する**ことを優先した冗長記述。実害なし。
"""

import sys
from pathlib import Path

# pyproject.toml の pythonpath = ["."] と合わせて二重保険。
# どちらかが効いていれば import が通る設計。
sys.path.insert(0, str(Path(__file__).parent))
