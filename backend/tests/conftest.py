"""測試共用設定，將專案根目錄加入模組搜尋路徑。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
