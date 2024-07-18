from .test_tool import TestTool


def gen_asset_relative_path(testtool: TestTool) -> str:
    """
    如果是本地上传测试工具压缩包到COS上，那么使用此生成规则
    """
    return (
        f"testtools/{testtool.lang}/{testtool.name}/archive/{testtool.version}.tar.gz"
    )
