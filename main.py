from scraping.modules.cves.NVD import _download_archive, _parse_files
from utils.temp_manager import TempManager
from utils.logger import Logger
import json

# TODO x:
# 1: Add function comments
# 2: Magic Number / Hardcoded string
# 3: Add explanation comments
# 4: Spaghetti code, fix if possible
# 5: Add error handling