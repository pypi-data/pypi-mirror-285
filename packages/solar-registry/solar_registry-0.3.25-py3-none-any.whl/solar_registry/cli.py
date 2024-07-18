import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from typing_extensions import Annotated

from .commands.meta_merger import MetaMerger
from .service.cos_sync import CosSyncService
from .service.pr_generator import PullRequestGenerator
from .service.testtool import get_testtool, github_asset_gen
from .service.validator import ToolValidator

app = typer.Typer()


@app.command()
def merge(tool_name: str, output: str, working_dir: Optional[str] = None) -> None:
    """
    合并工具版本元数据

    :param tool_name: 工具名称
    :param output: registry仓库本地目录
    :param working_dir: 可选工作目录
    """
    testtool = get_testtool(tool_name, working_dir)
    merger = MetaMerger(testtool, asset_url_gen=github_asset_gen)
    merger.merge_index_and_history(Path(output))


@app.command()
def pull_request(
    tool_name: Annotated[str, typer.Argument(help="工具名称")],
    working_dir: Annotated[Optional[str], typer.Argument(help="可选工作目录")] = None,
) -> None:
    """
    合并元数据之后，向项目提PR进行合并操作
    """
    testtool = get_testtool(tool_name, working_dir)
    pr_gen = PullRequestGenerator(testtool)
    pr_gen.merge_and_create_pull_request()


@app.command()
def validate(
    tool_name: str, working_dir: Optional[str] = None, verbose: bool = False
) -> None:
    """
    校验测试工具的testtools.yaml是否符合要求

    :param verbose: 是否显示详细日志
    :param tool_name: 工具名称
    :param working_dir: 可选工作目录
    """
    if not verbose:
        logger.remove()
        logger.add(sys.stdout, level="INFO")

    testtool = get_testtool(tool_name, working_dir)
    logger.info(f"✅ 测试工具 {testtool.name} 有效性校验通过")


@app.command()
def validate_json(working_dir: Optional[str] = None) -> None:
    """
    校验当前目录下的json文件是否符合要求

    :param working_dir: 可选工作目录
    """
    validator = ToolValidator(working_dir)
    validator.validate()


@app.command()
def sync_cos(working_dir: Optional[str] = None, force: bool = False) -> None:
    """
    同步数据到COS上

    :param working_dir: 可选工作目录
    :param force: 是否强制更新COS上的文件
    """
    sync = CosSyncService(working_dir)
    sync.sync_meta_data(force)


def cli_entry() -> None:
    app()


if __name__ == "__main__":
    app()
