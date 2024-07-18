from pathlib import Path
from typing import Union
import requests
from loguru import logger
from retry import retry


@retry(tries=5, delay=1, backoff=2)
def download_file_to(url: str, to_file: Union[str, Path]) -> None:
    logger.info(f"Downloading {url} to {to_file}")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(to_file, "wb") as f:
        # 逐块写入文件内容
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:  # 过滤掉保持连接活动的新块
                f.write(chunk)

        logger.info(f"Downloaded {url} to {to_file}")
