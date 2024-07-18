import tempfile
from pathlib import Path
from typing import Callable

from loguru import logger
from requests import HTTPError

from ..model.test_tool import (
    StableIndexMetaData,
    MetaDataHistory,
    TestTool,
    TestToolMetadata,
)
from ..service.generator import Generator
from ..service.testtool import sort_test_tools
from ..util.file import download_file_to


class MetaMerger:
    def __init__(self, testtool: TestTool, asset_url_gen: Callable[[TestTool], str]):
        self.testtool = testtool

        gen = Generator(self.testtool, asset_url_gen)
        self.metadata = gen.generate_meta_data()

    def merge_index_and_history(self, output_dir: Path) -> None:
        """
        合并新的索引文件和版本文件
        :param output_dir:  registry目录
        :return:
        """
        new_index = self._download_and_merge_stable_index()
        new_history = self._download_and_merge_meta_history()

        index_file = Path(output_dir) / "testtools" / "stable.index.json"
        index_file.parent.mkdir(exist_ok=True, parents=True)
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(
                new_index.model_dump_json(by_alias=True, indent=2, exclude_none=True)
            )

        meta_file = (
            Path(output_dir)
            / "testtools"
            / self.testtool.lang
            / self.testtool.name
            / "metadata.json"
        )
        meta_file.parent.mkdir(exist_ok=True, parents=True)
        with open(
            meta_file,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(
                new_history.model_dump_json(by_alias=True, indent=2, exclude_none=True)
            )

    def _download_and_merge_stable_index(self) -> StableIndexMetaData:
        """
        合并稳定索引文件内容

        一般用于新版本发布后索引文件的更新
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            stable_index_file = Path(tmpdir) / "stable_index.json"

            try:
                # 正常下载就进行合并操作
                download_file_to(
                    url=self.testtool.index_file, to_file=stable_index_file
                )
                return self._merge_stable_index(stable_index_file)
            except HTTPError as e:
                if e.response.status_code == 404:
                    # 没有索引文件，直接新建一个索引，不合并
                    return self._create_new_stable_index()
                else:
                    raise

    def _download_and_merge_meta_history(self) -> MetaDataHistory:
        """
        合并工具元数据的版本历史
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            metadata = Path(tmpdir) / "metadata.json"

            try:
                download_file_to(url=self.testtool.version_file, to_file=metadata)

                with open(metadata, "r", encoding="utf-8") as f:
                    old_history = MetaDataHistory.model_validate_json(f.read())
                    return self._merge_meta_history(old_history)
            except HTTPError as e:
                if e.response.status_code == 404:
                    return self._create_new_metadata_history()
                else:
                    raise

    def _create_new_stable_index(self) -> StableIndexMetaData:
        logger.info("Creating stable index...")
        meta = StableIndexMetaData(tools=[self.testtool])

        return meta

    def _merge_stable_index(self, stable_index: Path) -> StableIndexMetaData:
        logger.info(f"Merging {stable_index.name}")
        with open(stable_index, "r") as f:
            stable_result = StableIndexMetaData.model_validate_json(f.read())

            stable_result.merge_stable_index([self.testtool])
            stable_result.tools = sort_test_tools(stable_result.tools)

            logger.info(
                f"Merge stable index: {stable_result.model_dump_json(by_alias=True, indent=2, exclude_none=True)}"
            )
            return stable_result

    def _merge_meta_history(self, history: MetaDataHistory) -> MetaDataHistory:
        logger.info("Merging meta history...")
        if not history.versions:
            history.versions = []

        self._upsert_meta_history(tool_meta=self.metadata, history=history)

        # 在历史记录中增加一个固定的stable版本，方便用户使用
        stable_version = self.metadata.model_copy(deep=True)
        stable_version.meta.version = "stable"
        self._upsert_meta_history(tool_meta=stable_version, history=history)

        logger.info(
            f"Merge meta history result: {history.model_dump_json(by_alias=True, indent=2, exclude_none=True)}"
        )

        return history

    @staticmethod
    def _upsert_meta_history(
        tool_meta: TestToolMetadata, history: MetaDataHistory
    ) -> MetaDataHistory:
        for index, version in enumerate(history.versions):
            if version.meta.version == tool_meta.meta.version:
                history.versions[index] = tool_meta
                break
        else:
            history.versions.append(tool_meta)

        return history

    def _create_new_metadata_history(self) -> MetaDataHistory:
        # 读取本地生成好的metadata文件
        logger.info("Creating meta history...")
        history = MetaDataHistory(versions=[self.metadata])

        # 在历史记录中增加一个固定的stable版本，方便用户使用
        stable_version = self.metadata.model_copy(deep=True)
        stable_version.meta.version = "stable"
        history.versions.append(stable_version)

        return history
