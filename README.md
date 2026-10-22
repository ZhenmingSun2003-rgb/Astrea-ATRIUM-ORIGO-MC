# ASTREA · ORIGO

> **From curiosity, a world begins.**  
> 从好奇出发，让世界诞生。

**ORIGO** 是 ASTREA 世界观下的 Minecraft 世界；**ATRIUM** 是承载、部署和管理该世界的基础设施。本仓库用于记录 ORIGO 的客户端发行配置、构建流程，以及未来接入深圳 ATRIUM 主控/Worker 系统的服务器侧工程。

当前阶段：**客户端视觉方案 v0.1（配置确定，尚待完整联机实测）**。本仓库并不宣称已经部署服务器，也不包含 Minecraft 本体或第三方资源的重新分发副本。

## 三种客户端 · 同一个世界

三种客户端都是 **Minecraft Java Edition 26.2**，共用 **Fabric + Sodium + Iris**，预计连接同一 ORIGO Java 服务器。它们仅在本地纹理、光影和性能取向上不同，不对应三个不同的存档或服务器。

| 发行配置 | 视觉定位 | 材质包 | 光影包 |
| --- | --- | --- | --- |
| **ORIGO · Ethereal** | 清新、柔和、简洁，偏童话式的探索与建造 | [Dandelion X](https://modrinth.com/resourcepack/dandelion-x/version/nBLlBjME) 16×（26.2） | [Complementary Reimagined](https://modrinth.com/shader/complementary-reimagined) |
| **ORIGO · Arcane** | 中世纪魔法、RPG 与细节丰富的建筑美学 | [Alacrity](https://modrinth.com/resourcepack/alacrity) 32×（适配 26.2） | [BSL Shaders](https://modrinth.com/shader/bsl-shaders/version/Y68yiql9) 10.1.8 |
| **ORIGO · Origin** | 保留原版形态的精修质感，以光影塑造现实感 | [Vanilla Experience+](https://modrinth.com/resourcepack/vanilla-exp/version/UBuTOpY1) v2.0 | [iterationT](https://www.minegraph.cn/shaderpacks/12) 3.2.0 |

**已确认的取舍：** Origin 采用 Vanilla Experience+ v2.0，**不使用先前讨论的 Faithful 32×**；Arcane 默认 BSL 10.1.8，Complementary 仅用于早期方案对比；Ethereal 选择 Complementary **Reimagined**（不是 Unbound）。Astraliyte's Animated Textures 等额外资源目前不属于三套正式配置。

## 体验定位

### Ethereal · 空灵

适合长期生存、探索与轻快的建筑创作。Dandelion X 提供统一的色彩语言，Complementary Reimagined 保留 Minecraft 的风格化外观。它是三套中的**相对轻量视觉方案**，但并不意味着对所有电脑都能保持固定帧率。

### Arcane · 奥术

强调魔法、古典建筑和沉浸氛围。Alacrity 的 32× 纹理、立体细节与 BSL 的光照组成奇幻式观感。相较于 Ethereal，材质细节和特效可能需要更高的图形性能。

### Origin · 本源

保留熟悉的原版 Minecraft 语言，以 Vanilla Experience+ 统一修饰材质与交互细节，以 iterationT 3.2.0 创造更鲜明的光照与空间氛围。**Origin 的初始建议**是 JVM 分配 6 GiB 内存，渲染距离 10 chunks；这是配置建议，不是客户端或服务器强制要求。

## 仓库内容

```text
.
├── README.md                        # 项目中文首页
├── clients/
│   ├── ethereal.json                # Ethereal 客户端配置清单
│   ├── arcane.json                  # Arcane 客户端配置清单
│   ├── origin.json                  # Origin 客户端配置清单
│   └── README.md                    # 安装、限制和来源说明
├── scripts/
│   └── build_clients.py             # 生成三个 .mrpack 的构建脚本
├── tests/
│   └── test_build_clients.py        # 离线单元测试
└── .github/workflows/
    └── build-clients.yml            # 自动构建与打包
```

### 构建 Modrinth 客户端导入包

建议使用 **Python 3.10+**。构建时需要联网访问 Modrinth API；此过程**不会**下载、重新托管或打包受版权保护的第三方材质/光影原始文件，而是在 `.mrpack` 内写入原作者的下载地址及哈希。

```bash
python scripts/build_clients.py --all
```

产物在 `dist/`，共三个 `.mrpack`：

- `ORIGO-Ethereal-0.1.0.mrpack`
- `ORIGO-Arcane-0.1.0.mrpack`
- `ORIGO-Origin-0.1.0.mrpack`

可在支持 Modrinth modpack 导入格式的启动器中使用。导入包负责 Fabric、Sodium、Iris 及已确认可以从 Modrinth 官方下载的资源；**Origin 的 iterationT 3.2.0 必须由使用者通过作者发布页取得并手动放到实例的 `shaderpacks/`，之后在游戏内选择**。这不是替换光影，而是由于尚未验证其可用于自动分发的官方文件链接与许可，因此不随导入包分发。详见 [客户端说明](clients/README.md)。

```bash
python -m unittest discover -s tests -v
```

> `dist/` 是生成目录。仓库保存构建代码和清单，CI 生成可下载的构建工件；需要发布正式发行版时，先完成实机验证和授权检查。

## 客户端与服务器的边界

- **客户端侧：** Fabric / Sodium / Iris / 材质包 / 光影包，只影响本地渲染与体验；不要求玩家改装服务器。
- **服务器侧（规划）：** ORIGO Java 世界作为深圳 **ATRIUM** 下的独立服务模块运行，由 ATRIUM 负责生命周期、权限、备份和远程管理；具体部署、插件和网络规则须在后续服务器工程中确认。
- **联机兼容性：** 三套 Java 26.2 客户端的目标是一服互通，实际互通、资源加载与帧率尚未完成联机测试；版本、服务端协议和必要依赖应在上线前锁定并核验。

## 版权与第三方项目

Minecraft、Fabric、Sodium、Iris、资源包和光影包各归对应作者／权利人所有。**本仓库的清单、脚本及文档不授予任何第三方资源的重新分发权。** 请遵守各项目下载页面的许可和条款，尤其不要将保留所有权利的 Alacrity、BSL 等直接复制进公开仓库。资源来源及特殊处理见 [clients/README.md](clients/README.md)。

---

**ASTREA** · **ATRIUM** / **ORIGO**  
*好奇即美德，求知即正义。*
