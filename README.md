# Token-Less RPM Package

Token-Less 的 RPM 打包仓库，从 GitHub anolisa monorepo 下载 tokenless 源码并构建 RPM。

## 项目介绍

Token-Less 是一个 LLM token 优化工具包，通过 Schema/Response 压缩、TOON 格式编码和命令重写策略显著减少 token 消耗。

本 RPM 包包含：
- **tokenless**: CLI 工具（schema 压缩 + response 压缩 + 统计跟踪）
- **rtk**: Rust Token Killer - 高性能 CLI 代理，命令重写（Apache-2.0）
- **toon**: JSON → TOON 格式编码/解码器（MIT）
- **openclaw**: TypeScript 插件及配置文件
- **hooks/copilot-shell/**: copilot-shell hook 脚本（PreToolUse / PostToolUse / BeforeModel）
- **install.sh**: 统一安装/配置脚本

## 系统要求

- Anolis OS 23 / Alibaba Cloud Linux 4
- 或其他基于 RPM 的 Linux 发行版（RHEL/CentOS/Fedora）
- RPM 依赖：jq, bash
- 构建 RPM 需要：Rust >= 1.88（仅 `package-tokenless.sh` 编译阶段需要）

## 目录结构

```
.
├── README.md              # 本说明文档
├── package-tokenless.sh   # 一键打包构建脚本
├── tokenless.spec         # RPM spec 文件
└── tokenless-0.2.0.tar.gz # 源码包（含预编译二进制 + 资源文件）
```

## 构建 RPM

### 一键构建

```bash
bash package-tokenless.sh
```

脚本自动完成：
1. 从 `https://github.com/alibaba/anolisa.git` 浅克隆（tag `tokenless/v0.2.0`）
2. 初始化 rtk + toon submodule
3. 从上游 Cargo.toml 解析版本号
4. 编译 tokenless、rtk、toon 三个二进制
5. 打包二进制 + 资源文件为 `tokenless-<version>.tar.gz`
6. 使用本地 `tokenless.spec` 构建 RPM 和 SRPM

### 手动构建

```bash
# 准备环境
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# 运行打包脚本（生成 tarball + 构建 RPM）
bash package-tokenless.sh

# 或分步执行
cp tokenless-0.2.0.tar.gz ~/rpmbuild/SOURCES/
cp tokenless.spec ~/rpmbuild/SPECS/tokenless.spec
cd ~/rpmbuild && rpmbuild -ba --nodeps SPECS/tokenless.spec
```

构建产物：
- 二进制包：`~/rpmbuild/RPMS/x86_64/tokenless-0.2.0-1.alnx4.x86_64.rpm`
- 源码包：`~/rpmbuild/SRPMS/tokenless-0.2.0-1.alnx4.src.rpm`

## 安装 RPM

```bash
sudo dnf install ./tokenless-0.2.0-1.alnx4.x86_64.rpm
# 或
sudo rpm -ivh tokenless-0.2.0-1.alnx4.x86_64.rpm
```

## 验证安装

```bash
# 检查已安装文件
rpm -ql tokenless

# 查看包信息
rpm -qi tokenless

# 查看 changelog
rpm -q --changelog tokenless

# 验证二进制
tokenless --version   # tokenless 0.2.0
rtk --version         # rtk 0.36.0
toon --version        # toon 0.4.5
```

## 已安装文件

### 二进制
- `/usr/bin/tokenless` — 主程序
- `/usr/bin/rtk` — RTK 命令重写
- `/usr/bin/toon` — TOON 格式编码

### 文档
- `/usr/share/doc/tokenless/LICENSE`
- `/usr/share/doc/tokenless/tokenless-user-manual-en.md`
- `/usr/share/doc/tokenless/tokenless-user-manual-zh.md`
- `/usr/share/doc/tokenless/response-compression.md`

### 共享文件
- `/usr/share/tokenless/openclaw/` — OpenClaw 插件（index.ts / plugin.json / package.json / README）
- `/usr/share/tokenless/scripts/install.sh` — 统一安装/配置脚本
- `/usr/share/tokenless/hooks/copilot-shell/` — Hook 脚本和 README

## 卸载

```bash
sudo dnf remove tokenless
# 或
sudo rpm -e tokenless
```

`%preun` scriptlet 自动清理：
- 备份 `~/.copilot-shell/settings.json`
- 移除 tokenless hooks 配置
- 清理 `~/.tokenless` 统计数据

## Post-install 配置

RPM 安装后自动执行：
1. 安装 OpenClaw 插件到 `~/.openclaw/extensions/tokenless/`，编译 index.ts
2. 注册 copilot-shell hooks（PreToolUse / PostToolUse / BeforeModel）

手动重新配置：
```bash
/usr/share/tokenless/scripts/install.sh --install
```

### Hook 功能

| Hook 事件 | 功能 | Token 节省 |
|-----------|------|-----------|
| PreToolUse | 命令重写（RTK） | 60-90% |
| PostToolUse | Response → TOON 压缩 | 30-60%（合并） |
| BeforeModel | Schema 压缩 | ~57% |

## 离线构建

源码包包含预编译的二进制文件（tokenless、rtk、toon），RPM 构建阶段无需网络和 Rust 工具链。如需从源码重新编译，请在有网络的环境中运行 `package-tokenless.sh`。

## Spec 文件说明

`tokenless.spec` 采用预编译二进制打包方式，RPM 构建阶段不执行编译：

```spec
Name:           tokenless
Version:        0.2.0
Release:        1.alnx4
Summary:        LLM Token Optimization Toolkit
License:        MIT and Apache-2.0
Requires:       jq, bash
```

## 版本说明

版本号从上游 `src/tokenless/Cargo.toml` 的 `[workspace.package]` 自动解析，与 anolisa monorepo 保持一致。发布新版本时只需更新脚本中的 `TAG` 变量。

## 联系

- Token-Less: linyan.lin@alibaba-inc.com
- RPM Package: shile.zhang@linux.alibaba.com

## License

MIT and Apache-2.0
