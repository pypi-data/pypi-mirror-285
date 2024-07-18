# solar-registry
命令行工具`solar-registry`，提供以下功能：

- 根据测试工具的`testtool.yaml`生成对应的元数据信息
- 读取最新的元数据文件并合并
- 下载指定的发布包，并计算sha256值
- 自动提交PR到registry仓库，发布的新版本元数据


## 生成元数据

将当前仓库的指定测试工具元数据，生成到指定位置。

- 包含工具Spec
- 包含最新工具Target

```shell
solar-registry merge pytest ./output/testsolar
```

## 推送合并后文件到registry仓库

- 推送合并之后的变更到registry仓库的特定分支
- 使用gh命令行创建PR

```shell
solar-registry pull-request pytest
```