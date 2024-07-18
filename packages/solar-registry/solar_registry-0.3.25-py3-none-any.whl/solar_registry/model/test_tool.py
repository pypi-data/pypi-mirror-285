"""
测试工具模型定义

这里面的模型都是对外体现的
"""

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, ValidationInfo, model_validator
from typing_extensions import Self

from .legacy import LegacySpec


class ParamChoice(BaseModel):
    value: str = Field(title="选项值")
    display_name: str = Field("", alias="displayName", title="UI显示名称")
    desc: str = Field(title="选项描述")

    @model_validator(mode="after")
    def check_valid(self, info: ValidationInfo) -> Self:
        context = info.context
        if context and context.get("strict"):
            if not self.display_name:
                raise ValueError("ParamChoice displayName must be set")

        return self


class ParamWidget(str, Enum):
    Code = "code"
    Text = "text"
    Number = "number"
    Choices = "choices"
    TextArea = "text-area"


class ParamDef(BaseModel):
    name: str = Field(
        title="参数名称",
        description="""
参数名称，在实际执行的时候会被转换为环境变量下发。
    
这些参数在用户 use 测试工具的时候会通过 with 进行设置，并最终会被传递给对应的脚本文件，传递的方式是 环境变量，映射方式如下：

TESTSOLAR_TTP_大写名称

举例:
- useVirtualEnv -> TESTSOLAR_TTP_USEVIRTUALENV
- workerCount -> TESTSOLAR_TTP_WORKERCOUNT

    """,
    )
    value: str = Field(title="参数值", description="格式必须是字符串")
    desc: str = Field("", title="参数描述信息")

    default: str = Field("", title="参数默认值")
    choices: Optional[list[ParamChoice]] = Field(None, title="参数选项")

    # 兼容历史工具
    lang: Optional[str] = Field(
        None, title="参数语言", description="用于前端UI显示，判断语法高亮类型"
    )
    qta_name: Optional[str] = Field(
        None,
        alias="qtaName",
        title="qta属性名称",
        description="用于兼容相同含义QTA属性名称",
    )
    input_widget: Optional[ParamWidget] = Field(
        None,
        alias="inputWidget",
        title="输入控件类型",
        description="""
    输入控件的类型，用于前端界面显示。
    
    当前支持的控件类型如下：
    - code: 代码类型控件，支持语法高亮
    - text: 文本类型控件，不支持语法高亮
    - number: 数字类型
    - choices: 选项类型
    """,
    )

    @model_validator(mode="after")
    def check_valid(self, info: ValidationInfo) -> Self:
        context = info.context
        if context and context.get("strict"):
            if not self.desc:
                raise ValueError("ParamDef desc must be set")
            if not self.input_widget:
                raise ValueError("ParamDef inputWidget must be set")

        return self


class Entry(BaseModel):
    load: str
    run: str


class OsType(str, Enum):
    Linux = "linux"
    Windows = "windows"
    Darwin = "darwin"
    Android = "android"


class ArchType(str, Enum):
    Amd64 = "amd64"
    Arm64 = "arm64"


class TestCatalog(str, Enum):
    UnitTest = "unit"  # 单元测试
    ServerAPITest = "server-api"  # 服务端测试
    UITest = "ui"  # UI测试


class TestDomain(str, Enum):
    Android = "android"
    IOS = "ios"
    Windows = "windows"
    Web = "web"
    Macos = "macos"
    Server = "server"


class TestTool(BaseModel):
    __test__ = False

    """
    测试工具模型定义
    """

    schema_version: float = Field(alias="schemaVersion")
    name: str = Field(
        pattern=r"^[a-zA-Z-0-9_]+$",
        title="工具名称",
        description="允许英文字母+数字+`-`",
    )
    name_zh: str = Field("", alias="nameZh", title="工具中文名称")
    legacy_name: str = Field(
        "",
        alias="legacyName",
        title="遗留工具名称",
        description="""
由于部分工具还未切换到TestSolar引擎，因此增加一个遗留工具字段。

- TestSolar工具此字段为空
- 遗留工具此字段为老的工具ID(比如pytest)
    """,
    )
    description: str = Field(
        min_length=10,
        max_length=1000,
        title="工具描述",
        description="""
工具描述信息，10~1000个字符。

简要描述工具的使用场景。
    """,
    )

    # x.x.x 格式版本
    version: str = Field(
        pattern=r"^(\d+\.\d+\.\d+|stable)$",
        title="工具版本",
        description="""
工具版本，需要符合一定格式：

- x.x.x: 满足语义化版本(https://semver.org/lang/zh-CN/)
- stable: 用于指定稳定版本，通常是最后一次发布的版本，以方便用户使用
    """,
    )
    lang: Literal["python", "golang", "javascript", "java", "cpp"]
    base_image: str = Field(
        alias="defaultBaseImage",
        title="使用的默认镜像",
        description="""
在没有指定镜像时，TestSolar会使用此默认镜像作为基础镜像。

用户也可以使用其他自定义镜像来满足自己的需求。
    """,
    )
    supported_certified_images: Optional[list[str]] = Field(
        None,
        alias="supportedCertifiedImages",
        title="经过认证的官方测试镜像列表",
        description="""
测试工具提供的，官方支持的测试镜像列表。

这些测试镜像由官方发布，经过官方测试和验证，确保使用稳定性。    
    """,
    )
    lang_type: Literal["COMPILED", "INTERPRETED"] = Field(
        alias="langType",
        title="语言类型",
        description="""
指定是解释型语言还是编译型语言。

- COMPILED: 编译型语言
- INTERPRETED: 解释型语言
    """,
    )
    param_defs: Optional[list[ParamDef]] = Field(None, alias="parameterDefs")
    home_page: str = Field(alias="homePage", title="工具首页")
    version_file: str = Field(
        alias="versionFile",
        title="版本文件地址",
        description="""
版本文件地址，指向历史版本元数据文件。

版本文件中，保存了测试工具发布的历史版本。TestSolar测试工具的用户可以选择某个特定的历史版本使用。
    """,
    )
    index_file: str = Field(
        alias="indexFile",
        title="稳定版本索引",
        description="""
稳定版本索引，包含各个测试工具的稳定版本元数据信息。

由于稳定版本是通常使用的版本，因此外部系统仅需要访问此稳定版本元数据信息，即可快速读取需要使用的测试工具数据。
    """,
    )
    scaffold_repo: str = Field(
        "",
        alias="scaffoldRepo",
        title="脚手架仓库URL",
        description="""
指向测试工具使用的脚手架仓库信息。

TestSolar使用此信息来快速生成一个测试工具的用例库，用户可在此用例库的基础上继续开发。
    """,
    )
    support_os: Optional[list[OsType]] = Field(
        None, alias="supportOS", title="支持的系统"
    )
    support_arch: Optional[list[ArchType]] = Field(
        None, alias="supportArch", title="支持的CPU架构"
    )
    entry: Optional[Entry] = Field(
        None,
        alias="entry",
        title="测试工具交互入口文件",
        description="""
定义跟uniSDK之间交互的调用方式。

使用场景：
- 测试工具install.sh/install.ps脚本中需要安装uniSDK
- 测试工具run.sh/run.ps脚本中需要启动uniSDK并指定使用的测试工具

entry中需要定义2个入口：
- 加载用例入口(load)
- 执行用例入口(run)

实际执行的时候会把字符串中定义的 $1 换成入口参数文件。

具体使用方式请参考uniSDK的相关文档。
    """,
    )

    repository: Optional[str] = Field(
        None,
        alias="repository",
        title="测试工具源码仓库地址",
        description="""
测试工具的源代码仓库地址。        
        """,
    )

    git_pkg_url: Optional[str] = Field(
        None,
        alias="gitPkgUrl",
        title="Git方式使用地址",
        description="""
指定测试工具在Git模式下的使用地址。

通常不推荐，我们优先推荐使用Http元数据方式。
- Http方式无需安装Git
- Http方式无需Git认证，下载成功率更高
    """,
    )

    http_pkg_url: Optional[str] = Field(
        None,
        alias="httpPkgUrl",
        title="Http方式使用地址",
        description="""
指定测试工具在Http模式下的使用地址。        
        """,
    )

    legacy_spec: Optional[LegacySpec] = Field(
        None,
        alias="legacySpec",
        title="遗留工具规范",
        description="""
    老的遗留工具中使用的一些额外字段。
    
    这些字段仅在遗留工具中使用，TestSolar平台工具不再支持。
    """,
    )
    certified: bool = Field(
        False,
        alias="certified",
        title="是否是TestSolar官方认证插件",
        description="""
是否是TestSolar官方支持工具（包括遗留工具）。

官方支持工具由TestSolar官方维护，质量上有保证，能够得到官方支持。
        """,
    )

    archived: Optional[bool] = Field(
        None,
        alias="archived",
        title="是否已经归档",
        description="""
部分测试工具已经无人使用，标记为归档。

各系统可根据此信息来决定相关处理策略。        
        """,
    )

    test_catalog: TestCatalog = Field(
        TestCatalog.UnitTest,
        alias="testCatalog",
        title="测试分类",
        description="""
说明测试工具的使用分类。    
        """,
    )

    test_domains: Optional[list[TestDomain]] = Field(
        None,
        alias="testDomains",
        title="测试领域",
        description="""
说明测试工具的测试领域。

一个测试工具可以支持多个不同的测试领域。    
    """,
    )

    priority: Optional[int] = Field(
        None,
        title="测试工具优先级定义",
        description="""
用于前端展示。

优先级越高，显示越靠前。
    """,
    )

    @model_validator(mode="after")
    def check_valid(self, info: ValidationInfo) -> Self:
        """
        检查测试工具定义是否合法

        直接在模型中增加非None检查会导致旧版本的测试工具元数据解析报错，所以单独提取一个函数用于校验，需要的时候再调用
        """
        context = info.context
        if context and context.get("strict"):
            if not self.support_os:
                raise ValueError("supportOS must be set")
            if not len(self.support_os) > 0:
                raise ValueError("need at least 1 support OS")

            if not self.support_arch:
                raise ValueError("need at least 1 support arch")
            if not len(self.support_arch) > 0:
                raise ValueError("need at least 1 support arch")

            if not self.legacy_spec:
                if not self.git_pkg_url:
                    raise ValueError("gitPkgUrl must be set")
                if not self.http_pkg_url:
                    raise ValueError("httpPkgUrl must be set")
                if not self.version_file:
                    raise ValueError("versionFile must be set")
                if not self.index_file:
                    raise ValueError("indexFile must be set")
                if not self.scaffold_repo:
                    raise ValueError("scaffoldRepo must be set")
                if not self.repository:
                    raise ValueError("repository must be set")
            else:
                if not self.legacy_name:
                    raise ValueError("legacyName must be set")

            if not self.name_zh:
                raise ValueError("name_zh must be set")

        return self


class TestToolTarget(BaseModel):
    __test__ = False

    """
    发布包模型定义
    """

    os: OsType
    arch: ArchType
    download_url: str = Field(alias="downloadUrl")
    sha256: str


class StableIndexMetaData(BaseModel):
    """
    稳定版本索引文件
    """

    meta_version: str = Field("1", alias="metaVersion")
    tools: list[TestTool]

    def merge_stable_index(self, tools_want_to_merge: list[TestTool]) -> None:
        if not self.tools:
            self.tools = []

        for tool_to_merge in tools_want_to_merge:
            for index, tool in enumerate(self.tools):
                if tool.name == tool_to_merge.name:
                    self.tools[index] = tool_to_merge
                    break
            else:
                self.tools.append(tool_to_merge)


class TestToolMetadata(BaseModel):
    __test__ = False

    """
    通过solar-registry生成的最新版本发布元数据

    包含元数据信息和target信息
    """

    meta: TestTool
    target: list[TestToolTarget]


class MetaDataHistory(BaseModel):
    """
    工具元数据版本文件
    """

    meta_version: str = Field("1", alias="metaVersion")
    versions: list[TestToolMetadata]
