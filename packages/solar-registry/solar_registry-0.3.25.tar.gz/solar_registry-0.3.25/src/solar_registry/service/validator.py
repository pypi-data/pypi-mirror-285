import os
from pathlib import Path
from typing import Optional

from loguru import logger

from ..model.test_tool import StableIndexMetaData, MetaDataHistory


class ToolValidator:
    def __init__(self, workdir: Optional[str]) -> None:
        if workdir:
            self.workdir = Path(workdir)
        else:
            self.workdir = Path.cwd()

    def validate(self) -> None:
        """
        检查json文件是否符合要求
        """

        self.validate_stable_index()
        self.validate_tool_meta_json()

    def validate_stable_index(self) -> None:
        stable_index_file = Path(self.workdir) / "testtools" / "stable.index.json"
        logger.info(f"Validating stable index file [{stable_index_file}]")

        with open(stable_index_file) as f:
            sim = StableIndexMetaData.model_validate_json(f.read())

            logger.info(f"✅ Validated stable index file [{stable_index_file}] OK.")
            logger.info(f"✅ It has {len(sim.tools)} tools.")

    def validate_tool_meta_json(self) -> None:
        for dir_path, _, filenames in os.walk(self.workdir / "testtools"):
            for filename in filenames:
                if filename != "stable.index.json":
                    metafile = Path(dir_path) / filename
                    logger.info(f"Validating tool meta file [{metafile}]")
                    with open(metafile) as f:
                        re = MetaDataHistory.model_validate_json(f.read())
                        if re.versions:
                            # 检查versions中是否有重复版本
                            all_versions = set(x.meta.version for x in re.versions)

                            if len(all_versions) != len(re.versions):
                                raise RuntimeError(
                                    f"去重之后的版本数目 [{len(all_versions)}] != 原始版本数目 [{len(re.versions)}]"
                                )

                            logger.info(
                                f"✅ Validated tool [{re.versions[0].meta.name}] OK."
                            )
