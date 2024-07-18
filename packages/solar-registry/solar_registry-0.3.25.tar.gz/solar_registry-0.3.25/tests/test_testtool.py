from pathlib import Path

import pytest
from pydantic import ValidationError
from rich import print

from solar_registry.model.test_tool import OsType, ArchType, ParamWidget, TestTool
from solar_registry.service.testtool import (
    get_testtool,
    _parse_testtool,
    get_testtool_by_file_path,
    sort_test_tools,
)


def test_validate_correct_pytest_tool() -> None:
    workdir = str((Path(__file__).parent / "testdata").resolve())

    tool = get_testtool("pytest", workdir)

    assert tool.name == "pytest"
    assert tool.version == "0.1.6"
    assert tool.name_zh == "pytest自动化测试"
    assert tool.git_pkg_url == "github.com/OpenTestSolar/testtool-python@main:pytest"
    assert (
        tool.http_pkg_url
        == "https://opentestsolar.github.io/testtool-registry/testtools/python/pytest/metadata.json@stable"
    )
    assert tool.repository == "https://github.com/OpenTestSolar/testtool-python-pytest"

    assert tool.param_defs
    assert tool.param_defs[0].choices
    assert tool.param_defs[0].choices[0].display_name == "自动解析模式"
    assert tool.param_defs[0].qta_name == "parse_mode"

    assert tool.support_os
    assert tool.support_os[0] == OsType.Windows
    assert tool.support_os[1] == OsType.Linux
    assert tool.support_os[2] == OsType.Darwin

    assert tool.support_arch
    assert tool.support_arch[0] == ArchType.Amd64
    assert tool.support_arch[1] == ArchType.Arm64

    assert tool.supported_certified_images
    assert len(tool.supported_certified_images) == 4
    assert tool.supported_certified_images[0] == "python:3.9"

    assert tool.test_catalog == "unit"
    assert tool.test_domains == ["windows", "macos", "server"]


def test_validate_loose() -> None:
    _parse_testtool(
        Path(__file__).parent
        / "testdata"
        / "error_meta_files"
        / "error_yaml_with_loose.yaml",
        strict=False,
    )


def test_validate_strict_with_errors() -> None:
    with pytest.raises(ValidationError) as ve:
        _parse_testtool(
            Path(__file__).parent
            / "testdata"
            / "error_meta_files"
            / "error_yaml_with_strict.yaml",
            strict=True,
        )

    print(ve.value)

    assert r"String should match pattern '^[a-zA-Z-0-9_]+$'" in str(ve.value)
    assert r"Input should be 'COMPILED' or 'INTERPRETED'" in str(ve.value)
    assert r"Input should be 'python', 'golang', 'javascript', 'java' or 'cpp'" in str(
        ve.value
    )
    assert r"String should match pattern '^(\d+\.\d+\.\d+|stable)$'" in str(ve.value)
    assert r"Input should be 'linux', 'windows', 'darwin' or 'android'" in str(ve.value)
    assert r"Input should be 'amd64' or 'arm64'" in str(ve.value)


def test_validate_strict_with_no_os() -> None:
    with pytest.raises(ValidationError) as ve:
        _parse_testtool(
            Path(__file__).parent
            / "testdata"
            / "error_meta_files"
            / "error_yaml_with_strict_no_os.yaml",
            strict=True,
        )

    print(ve.value)
    assert r"Value error, supportOS must be set" in str(ve.value)


def test_validate_strict_with_no_arch() -> None:
    with pytest.raises(ValidationError) as ve:
        _parse_testtool(
            Path(__file__).parent
            / "testdata"
            / "error_meta_files"
            / "error_yaml_with_strict_no_arch.yaml",
            strict=True,
        )

    print(ve.value)
    assert r" Value error, need at least 1 support arch" in str(ve.value)


def test_parse_legacy_tool() -> None:
    tool = _parse_testtool(
        Path(__file__).parent / "testdata" / "legacy" / "testtool.yaml", strict=True
    )

    assert tool.name == "qt4s_pot-line"
    assert not tool.git_pkg_url
    assert tool.param_defs
    param1 = tool.param_defs[0]
    assert param1.name == "setup_cmdline"
    assert param1.value == "初始化命令"
    assert param1.desc == "加载/执行用例前的初始化命令"
    assert param1.default == "# place your extra init command here"
    assert param1.lang == "bash"
    assert param1.input_widget == ParamWidget.Code

    assert tool.legacy_spec
    assert tool.legacy_name == "qt4s"
    assert tool.legacy_spec.report_type == "junit"
    assert tool.legacy_spec.maintainers == ["aa", "bb"]
    assert tool.legacy_spec.testcase_runner.cli == "test"
    assert tool.legacy_spec.testcase_loader.cli == "test"
    assert tool.legacy_spec.testcase_analyzer.cli == "test"
    assert tool.legacy_spec.scaffolding_tool.cli == "test"
    assert tool.legacy_spec.node_setup.cli == "test"
    assert tool.legacy_spec.node_cleanup.cli == "test"
    assert tool.legacy_spec.global_setup.cli == "test"
    assert tool.legacy_spec.global_cleanup.cli == "test"
    assert tool.legacy_spec.res_pkg_url == "https://sample.com/pkg"
    assert tool.legacy_spec.doc_url == "https://sample.com/doc"
    assert tool.legacy_spec.logo_img_url == "https://sample.com/logo"
    assert not tool.legacy_spec.enable_code_coverage
    assert tool.legacy_spec.test_type == "auto-test"


def test_get_testtool_by_file_path() -> None:
    tool = get_testtool_by_file_path(
        Path(__file__).parent / "testdata" / "legacy" / "testtool.yaml"
    )
    assert tool.name == "qt4s_pot-line"


def test_sort_testtools_by_priority() -> None:
    tools = [
        TestTool(
            schemaVersion=1,
            name="a",
            defaultBaseImage="a",
            description="测试数据测试数据测试数据",
            homePage="a",
            indexFile="a",
            lang="python",
            langType="INTERPRETED",
            version="0.1.1",
            versionFile="a",
            priority=1,
        ),
        TestTool(
            schemaVersion=1,
            name="b",
            defaultBaseImage="a",
            description="测试数据测试数据测试数据",
            homePage="a",
            indexFile="a",
            lang="python",
            langType="INTERPRETED",
            version="0.1.1",
            versionFile="a",
            priority=200,
        ),
        TestTool(
            schemaVersion=1,
            name="c",
            defaultBaseImage="a",
            description="测试数据测试数据测试数据",
            homePage="a",
            indexFile="a",
            lang="python",
            langType="INTERPRETED",
            version="0.1.1",
            versionFile="a",
        ),
        TestTool(
            schemaVersion=1,
            name="d",
            defaultBaseImage="a",
            description="测试数据测试数据测试数据",
            homePage="a",
            indexFile="a",
            lang="python",
            langType="INTERPRETED",
            version="0.1.1",
            versionFile="a",
        ),
    ]

    sorted_tools = sort_test_tools(tools)
    assert sorted_tools[0].name == "b"
    assert sorted_tools[1].name == "a"
    assert sorted_tools[2].name == "c"
    assert sorted_tools[3].name == "d"
