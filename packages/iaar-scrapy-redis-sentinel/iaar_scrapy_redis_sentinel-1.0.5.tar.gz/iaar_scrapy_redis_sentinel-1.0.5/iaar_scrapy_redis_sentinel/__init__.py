# -*- coding: utf-8 -*-

__original_author__ = "Rolando Espinoza"
__author__ = "Gie"
__email__ = "593443714@qq.com"
__version__ = "2.0.0"

from pathlib import Path

from iaar_tools.iaarLog import IaarLoguru
from iaar_tools.inner_ip import get_inner_ip

inner_ip = get_inner_ip()

PRODUCTION_ENV_TAG = 'Linux'
# 不是以10.90开头的，认为是非生产环境
if inner_ip[1] == PRODUCTION_ENV_TAG:
    nested_dir = Path('~/logs/crawler')
    nested_dir.mkdir(parents=True, exist_ok=True)
    iaar_log = IaarLoguru(deep=2, log_file='~/logs/crawler/crawler.log')
else:
    iaar_log = IaarLoguru()
    inner_ip = "127.0.0.1"
