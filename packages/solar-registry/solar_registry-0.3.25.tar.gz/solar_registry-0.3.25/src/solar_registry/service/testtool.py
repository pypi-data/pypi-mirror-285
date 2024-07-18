import os
from pathlib import Path
from typing import Optional, Tuple, List

import yaml
from loguru import logger

from ..model.test_tool import TestTool


def get_testtool(tool_name: str, workdir: Optional[str]) -> TestTool:
    logger.debug(f"querying testtool for {tool_name}")
    workdir = workdir or os.getcwd()
    return get_testtool_by_file_path(Path(workdir) / tool_name / "testtool.yaml")


def get_testtool_by_file_path(file_path: Path) -> TestTool:
    logger.debug(f"querying testtool for {file_path}")
    return _parse_testtool(file_path, strict=True)


def _parse_testtool(yaml_file: Path, strict: bool) -> TestTool:
    with open(yaml_file) as f:
        context = {}
        if strict:
            context["strict"] = True

        testtool = TestTool.model_validate(yaml.safe_load(f), context=context)
        logger.debug(
            f"loaded testtool: {testtool.model_dump_json(by_alias=True, indent=2, exclude_none=True)}"
        )
        return testtool


def github_asset_gen(testtool: TestTool) -> str:
    return f"https://github.com/OpenTestSolar/testtool-{testtool.lang}-{testtool.name}/archive/refs/tags/{testtool.version}.tar.gz"


def sort_test_tools(tools: List[TestTool]) -> List[TestTool]:
    sorted_tools = sorted(list(enumerate(tools)), key=_sort_key)
    return [tool for index, tool in sorted_tools]


def _sort_key(item: Tuple[int, TestTool]) -> Tuple[int, int]:
    """
    按照优先级对其进行排序，如果没有优先级则保持原有排序

    如果 priority 为 None，返回 (0, index)，其中 index 是元素在原列表中的索引。
    如果 priority 不为 None，返回 (1, -priority)，这样 priority 越大，排序值越小，顺序越靠前。
    """
    index, tool = item
    if tool.priority is None:
        return 1, index
    else:
        return 0, -tool.priority
