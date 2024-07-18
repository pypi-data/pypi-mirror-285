from pathlib import Path

import pytest

from solar_registry.service.cos_sync import CosSyncService


@pytest.mark.skip(reason="Can only run in local")
def test_sync_meta_data_to_cos() -> None:
    workdir = str(
        (Path(__file__).parent / "testdata" / "stable_index_file_check").resolve()
    )

    cos_sync = CosSyncService(workdir)
    cos_sync.sync_meta_data(force=False)
