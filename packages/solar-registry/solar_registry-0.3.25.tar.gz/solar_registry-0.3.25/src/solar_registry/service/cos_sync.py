import hashlib
import os
import tarfile
import tempfile
from pathlib import Path
from typing import Callable, Optional

from loguru import logger
from qcloud_cos import CosS3Client, CosConfig  # type: ignore[import-untyped]

from ..model.asset import gen_asset_relative_path
from ..model.test_tool import TestTool


class CosSyncService:
    def __init__(
        self,
        workdir: Optional[str] = None,
        endpoint_gen: Optional[Callable[[str], str]] = None,
    ) -> None:
        self.workdir = workdir or os.getcwd()
        if "COS_SECRET_ID" not in os.environ:
            raise ValueError("Environment COS_SECRET_ID variables not set")
        self.cos_secret_id = os.environ["COS_SECRET_ID"]
        if "COS_SECRET_KEY" not in os.environ:
            raise ValueError("Environment COS_SECRET_KEY variables not set")
        self.cos_secret_key = os.environ["COS_SECRET_KEY"]
        if "COS_REGION" not in os.environ:
            raise ValueError("Environment COS_REGION variables not set")
        self.cos_region = os.environ["COS_REGION"]
        if "COS_BUCKET" not in os.environ:
            raise ValueError("Environment COS_BUCKET variables not set")
        self.cos_bucket = os.environ["COS_BUCKET"]

        if endpoint_gen:
            config = CosConfig(
                Region=self.cos_region,
                SecretId=self.cos_secret_id,
                SecretKey=self.cos_secret_key,
                Endpoint=endpoint_gen(self.cos_region),
            )
        else:
            config = CosConfig(
                Region=self.cos_region,
                SecretId=self.cos_secret_id,
                SecretKey=self.cos_secret_key,
            )

        self.cos_client = CosS3Client(config)

    def sync_meta_data(self, force: bool) -> None:
        for dir_path, _, filenames in os.walk(Path(self.workdir) / "testtools"):
            for filename in filenames:
                full_path = Path(dir_path, filename)
                logger.info(f"Syncing {full_path}")
                relative_path = os.path.relpath(full_path, self.workdir)
                logger.info(f"Relative path = {relative_path}")

                # 上传本地文件，相同文件跳过不上传
                self.upload_relative_file(relative_path, force)

    def upload_relative_file(self, relative_file: str, force: bool) -> None:
        full_path = Path(self.workdir, relative_file)

        if force:
            logger.info(f"Overwriting {relative_file}...")
            self.upload_file_to_cos(
                relative_file=relative_file, full_path=str(full_path)
            )
        else:
            if self.cos_client.object_exists(Bucket=self.cos_bucket, Key=relative_file):
                with tempfile.TemporaryDirectory() as temp:
                    output_path = Path(temp) / relative_file
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    logger.info(f"Download {relative_file} to {output_path}...")
                    self.cos_client.download_file(
                        Bucket=self.cos_bucket,
                        Key=relative_file,
                        DestFilePath=str(output_path),
                    )

                    logger.info("Compare MD5...")
                    if calculate_md5(full_path) == calculate_md5(output_path):
                        logger.info(
                            f"✨ relative_file {relative_file} not changed, skip upload"
                        )
                    else:
                        self.upload_file_to_cos(
                            relative_file=relative_file, full_path=str(full_path)
                        )
            else:
                logger.info(
                    f"File {relative_file} does not exist on cos, start upload..."
                )
                self.upload_file_to_cos(
                    relative_file=relative_file, full_path=str(full_path)
                )

    def upload_archive_file(self, test_tool: TestTool) -> None:
        # 生成对应测试工具的压缩包，并上传到COS的指定位置
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / f"{test_tool.name}.tar.gz"
            with tarfile.open(output_file, "w:gz") as tar:
                tar.add(Path(self.workdir) / test_tool.name, arcname=test_tool.name)

            cos_file_path = gen_asset_relative_path(testtool=test_tool)
            logger.info(f"Uploading {cos_file_path} to COS bucket {self.cos_bucket}...")
            self.upload_file_to_cos(
                relative_file=cos_file_path, full_path=str(output_file)
            )
            logger.info(f"✅ Uploaded {cos_file_path} to COS bucket {self.cos_bucket}")

    def upload_file_to_cos(self, relative_file: str, full_path: str) -> None:
        response = self.cos_client.upload_file(
            Bucket=self.cos_bucket,
            Key=relative_file,
            LocalFilePath=full_path,
            EnableMD5=True,
            progress_callback=None,
        )
        logger.info(
            f"✅ relative_file {relative_file} uploaded, ETag: {response['ETag']}"
        )


def calculate_md5(file_path: Path) -> str:
    """
    计算文件的 MD5 码。

    Args:
        file_path: 文件路径。

    Returns:
        文件的 MD5 码。
    """

    with open(file_path, "rb") as f:
        file_content = f.read()
        md5_hash = hashlib.md5()
        md5_hash.update(file_content)
        return md5_hash.hexdigest()
