import tempfile
from pathlib import Path
from typing import Callable, Optional

from solar_registry.commands.meta_merger import MetaMerger
from solar_registry.model.test_tool import MetaDataHistory, TestToolMetadata
from solar_registry.service.testtool import get_testtool, github_asset_gen


def test_merge_meta_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = str(Path(__file__).parent.joinpath("testdata").resolve())
        testtool = get_testtool(tool_name="pytest", workdir=workdir)
        gen = MetaMerger(testtool, asset_url_gen=github_asset_gen)
        gen.merge_index_and_history(Path(tmpdir))

        index_file = Path(tmpdir) / "testtools/stable.index.json"
        meta_file = Path(tmpdir) / "testtools/python/pytest/metadata.json"

        assert index_file.exists()
        assert meta_file.exists()

        with open(meta_file) as f:
            history = MetaDataHistory.model_validate_json(f.read())

            # 能够找到stable版本和当前版本，并且数据一致
            stable = find_if(history.versions, lambda x: x.meta.version == "stable")
            assert stable

            current = find_if(
                history.versions, lambda x: x.meta.version == testtool.version
            )
            assert current

            assert stable.target == current.target


def find_if(
    lst: list[TestToolMetadata], predicate: Callable[[TestToolMetadata], bool]
) -> Optional[TestToolMetadata]:
    return next((x for x in lst if predicate(x)), None)
