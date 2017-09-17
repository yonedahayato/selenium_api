import logging, os
import os.path

# ログの出力名を設定
logger = logging.getLogger("stock_patterns")
# ログレベルの設定
logger.setLevel(10)

# ログのファイル出力先を設定
if not os.path.exists("./log"): os.mkdir("./log")
fh = logging.FileHandler("./log/test.log")
logger.addHandler(fh)

# ログのコンソール出力の設定
sh = logging.StreamHandler()
logger.addHandler(sh)

# ログの出力形式の設定
formatter = logging.Formatter("%(asctime)s:%(lineno)d:%(levelname)s:%(message)s")
fh.setFormatter(formatter)
sh.setFormatter(formatter)
