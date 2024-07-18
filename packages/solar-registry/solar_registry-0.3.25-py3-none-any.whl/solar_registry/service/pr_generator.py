import os
import subprocess
import tempfile
from pathlib import Path

from loguru import logger

from ..commands.meta_merger import MetaMerger
from ..model.test_tool import TestTool
from .testtool import github_asset_gen


class PullRequestGenerator:
    def __init__(self, testtool: TestTool):
        self.testtool = testtool

    def merge_and_create_pull_request(self) -> None:
        if "GH_TOKEN" not in os.environ:
            raise ValueError("Missing GH_TOKEN environment variable")

        with tempfile.TemporaryDirectory() as temp_dir:
            args = ["gh", "repo", "clone", "OpenTestSolar/testtool-registry", temp_dir]
            logger.debug(f"Running command: {' '.join(args)}")
            subprocess.run(
                args,
                check=True,
            )
            git_dir = Path(temp_dir)
            branch_name = f"testtools/{self.testtool.lang}/{self.testtool.name}/{self.testtool.version}"
            subprocess.run(
                [
                    "git",
                    "checkout",
                    "-b",
                    branch_name,
                ],
                cwd=git_dir,
                check=True,
            )

            merger = MetaMerger(self.testtool, asset_url_gen=github_asset_gen)
            merger.merge_index_and_history(git_dir)

            subprocess.run(["git", "add", "."], cwd=git_dir, check=True)
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"release {branch_name}",
                ],
                cwd=git_dir,
                check=True,
            )
            token = os.environ["GH_TOKEN"]
            subprocess.run(
                [
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    f"https://{token}@github.com/OpenTestSolar/testtool-registry.git",
                ],
                cwd=git_dir,
                check=True,
            )
            subprocess.run(
                ["git", "push", "--set-upstream", "origin", branch_name],
                cwd=git_dir,
                check=True,
            )
            subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    f"🤖Release {branch_name}",
                    "--body",
                    f"发布测试工具 {self.testtool.name} 版本 {self.testtool.version}",
                    "--base",
                    "main",
                ],
                cwd=git_dir,
                check=True,
            )
