from pathlib import Path

import pytest

from solar_registry.service.pr_generator import PullRequestGenerator
from solar_registry.service.testtool import get_testtool


@pytest.mark.skip(reason="跳过真正合并github文件流程")
def test_merge_and_create_pull_request() -> None:
    workdir = str(Path(__file__).parent.joinpath("testdata").resolve())
    testtool = get_testtool(tool_name="pytest", workdir=workdir)

    gen = PullRequestGenerator(testtool)
    gen.merge_and_create_pull_request()
