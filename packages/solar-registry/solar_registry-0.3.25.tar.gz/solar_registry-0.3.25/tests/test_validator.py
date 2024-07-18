from pathlib import Path

from solar_registry.service.validator import ToolValidator


def test_validate_meta_json() -> None:
    workdir = str(
        (Path(__file__).parent / "testdata" / "stable_index_file_check").resolve()
    )
    validator = ToolValidator(workdir)

    validator.validate()
