import faxdatasdk # noqa
from faxdatasdk import *  # noqa
from .main import *  # noqa
import pqsdk.utils.file_util as fu
import json

# 登录faxdatasdk
config_file = 'config.sdk.json'
if fu.check_path_exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        sdk_config = json.loads(f.read())
    faxdatasdk.auth_by_token(token=sdk_config['token'], host=sdk_config['host'], audience=sdk_config['audience'])


__all__ = []
__all__.extend(faxdatasdk.__all__)  # noqa
__all__.extend(main.__all__)  # noqa
