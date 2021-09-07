from logging import getLogger, INFO, basicConfig


SAVE_DIR = 'dirname'
SAVE_PATH = '/path' + '/' + SAVE_DIR
TARGET_URL = 'https://xxxx/'
USER_AGENT \
        = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) ' \
          'Chrome/92.0.4515.159 Mobile Safari/537.36 '
CONFIG_HEADER = {
        'User-Agent': USER_AGENT,
        'Referer': 'https://xxxx',
        'sec-ch-ua-mobil': '?1',
        'sec-ch-ua': '"Chromium";v="92", "Not A;Brand";v="99", "Google Chrome";v="92"'
    }

basicConfig(level=INFO, format=' %(levelname)s - %(message)s')
LOGGER = getLogger(__name__)

