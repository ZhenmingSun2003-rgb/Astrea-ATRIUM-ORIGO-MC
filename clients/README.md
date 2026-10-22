# ORIGO — 中文客户端使用手册

> 当前版：**v0.1.0** / Minecraft **Java 26.2** / Fabric **0.19.5**

三套客户端共用 **Sodium 0.9.2** 和 **Iris 1.11.4**，对服务器不要求不同存档。本仓库存放安装清单和构建工具，不存放他人所有的 Mod、材质或光影文件。

## 版本对照

| 客户端 | 纹理（官方发布版本） | 光影（官方发布版本） | 安装方式 |
| --- | --- | --- | --- |
| [Ethereal](ethereal.json) | [Dandelion X 26.2](https://modrinth.com/resourcepack/dandelion-x/version/nBLlBjME) | [Complementary Reimagined r5.9.3](https://modrinth.com/shader/complementary-reimagined/version/Bqen1mJX) | Modrinth 依赖下载，游戏内启用 |
| [Arcane](arcane.json) | [Alacrity #39](https://modrinth.com/resourcepack/alacrity/version/39) | [BSL 10.1.8](https://modrinth.com/shader/bsl-shaders/version/Y68yiql9) | Modrinth 依赖下载，游戏内启用 |
| [Origin](origin.json) | [Vanilla Experience+ v2.0](https://modrinth.com/resourcepack/vanilla-exp/version/UBuTOpY1) | [iterationT 3.2.0](https://www.minegraph.cn/shaderpacks/12) | 材质自动依赖；**iterationT 手动安装** |

## 两种构建方式

**方式一：GitHub Actions** —— 在 [Build ORIGO Clients](https://github.com/ZhenmingSun2003-rgb/Astrea-ATRIUM-ORIGO-MC/actions/workflows/build-clients.yml) 工作流中选择 Run workflow。成功运行后下载 Artifacts 内的三个 .mrpack 文件。

**方式二：本地脚本** —— 安装 Python 3.10+ 后，在仓库根目录执行：

~~~bash
python scripts/build_clients.py --all
# 或仅生成其中一个版本：
python scripts/build_clients.py --profile origin
# 离线测试：
python -m unittest discover -s tests -v
~~~

输出路径为 <code>dist/</code>。脚本通过 Modrinth 官方 API 获取固定发布版本的文件 URL、哈希和大小，**不把上游 JAR/ZIP 放进 .mrpack**。如果文件被上游下架，构建会失败，不会悄悄改用随机最新版。请检查 CI 结果，不要将“脚本存在”误认为“实机已成功验证”。

## 玩家使用说明

1. 用支持 **Modrinth .mrpack** 格式的启动器分别导入三个包，并建立**独立实例**，避免配置冲突。
2. 确认实例 Minecraft 版本为 **Java 26.2**、Loader 为 **Fabric 0.19.5**。
3. 启动一次游戏，确认 Sodium/Iris 加载；若有问题先关闭光影排除渲染兼容故障。
4. 在游戏内打开 **Options → Resource Packs**，启用本客户端对应材质包。
5. 在 Iris 的 **Shader Packs** 中启用对应光影，建议从 Low / Medium 等预设起步。
6. Origin 还须从 [iterationT 原作者来源入口](https://www.minegraph.cn/shaderpacks/12) 自行取得 **3.2.0** ZIP，将完整 ZIP 放进实例的 <code>shaderpacks/</code>，**不要解压**，然后通过 Iris 启用。
7. 确认纹理正确显示、无崩溃；保存日志后再参与联机测试。

**重要：** Java 26.2 的安装目标和上游资源页面适配信息已经核对，但某些光影、材质增强特性仍需要实机与服务器联机测试。iterationT 发布信息显示不支持 macOS / Apple Silicon。

## 问题排查

| 问题 | 检查点 |
| --- | --- |
| 无法导入 .mrpack | 启动器是否支持该格式，是否从完整的 GitHub 构建产物获取 |
| 上游下载失败 | Modrinth 连通性、下载链接是否仍可用、哈希校验、网络限制 |
| 材质没有生效 | 是否在资源包菜单手动启用，是否与其他高优先级资源包冲突 |
| 没有光影选项 | Fabric / Iris 的版本和加载日志；是否误用不兼容的渲染组件 |
| 光影卡顿 | 降低阴影分辨率、体积云、视距和反射；更新显卡驱动 |
| Arcane 部分模型缺失 | 作者部分增强特性可能需要 EMF / ETF 等依赖，本版暂不包含 |
| Origin 在 Mac 上异常 | iterationT 官方发布信息不支持 Mac/Apple Silicon，请关闭该光影 |
| 登录服务器失败 | 核实 Java 26.2 协议、服务器端白名单和可能的必要 Mod，而非修改客户端材质 |

## 性能档位（非实测）

经验性 1080p 规划：Ethereal **GTX 1650 / RX 580 起、4 GiB JVM**；Arcane **RTX 2060 / RX 6600 起、5–6 GiB JVM**；Origin **RTX 3060 / RX 6700 XT 起、6 GiB JVM**。建议系统内存至少 16 GB，更复杂的地图可配 32 GB。所有具体 FPS、分辨率与显存结果均待统一场景测试。

## 维护规则

- 核心 Mod 已锁定版本；未来候选 Mod 都必须先验证 **26.2 + Fabric + Iris/Sodium** 的兼容性与许可，再分别加入 Profile 并测试。
- **不自动覆写**已有玩家的图像设置、键位或本地个人文件；资源和光影由玩家手动启用。
- 不把 OptiFine 与 Sodium/Iris 混装，也不将服务器侧运维凭据打包进客户端。
- 上游素材归作者所有，Alacrity 明确禁止第三方重新托管原始资源包；这里只使用上游链接和 SHA 引用。[查看完整鸣谢与权利说明](../docs/CREDITS.md)。
