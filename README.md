# Token-Less RPM Package

Token-Less 的 RPM 打包仓库，包含完整的 spec 文件和构建说明。

## 项目介绍

Token-Less 是一个用于 LLM schema 和响应压缩的 CLI 工具，帮助开发者高效地压缩大型语言模型的 schema 和响应。

本 RPM 包包含：
- **tokenless**: LLM schema 和响应压缩工具
- **rtk**: Rust Token Killer - 高性能 CLI 代理，最小化 LLM token 消耗
- **openclaw**: TypeScript 和 JSON 配置文件
- **install.sh**: 安装脚本

## 系统要求

- Alibaba Cloud Linux 4 (Anolis OS 23)
- 或其他基于 RPM 的 Linux 发行版（RHEL/CentOS/Fedora）

## 特性

- **离线构建支持**: 源码包包含完整的 Rust 依赖 vendor 目录，可在无公网环境下编译
- **双二进制**: 同时打包 tokenless 和 rtk 两个工具
- **OpenClaw 集成**: 包含完整的 OpenClaw 插件配置和脚本

## 目录结构

```
.
├── README.md                 # 本说明文档
├── tokenless.spec            # RPM spec 文件
└── tokenless-0.1.0.tar.gz    # 源码包
```

## 构建 RPM 包

### 1. 准备构建环境

```bash
# 安装必要的工具
sudo yum install -y rpm-build cargo rust

# 创建 rpmbuild 目录结构
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
```

### 2. 复制文件到 rpmbuild 目录

```bash
cp tokenless.spec ~/rpmbuild/SPECS/
cp tokenless-0.1.0.tar.gz ~/rpmbuild/SOURCES/
```

### 3. 构建 RPM

```bash
cd ~/rpmbuild
rpmbuild -ba SPECS/tokenless.spec
```

构建完成后，RPM 包位于：
- 二进制包：`~/rpmbuild/RPMS/x86_64/tokenless-0.1.0-1.alnx4.x86_64.rpm`
- 源码包：`~/rpmbuild/SRPMS/tokenless-0.1.0-1.alnx4.src.rpm`

## 安装 RPM 包

```bash
# 使用 yum/dnf 安装（推荐，自动解决依赖）
sudo yum install ./tokenless-0.1.0-1.alnx4.x86_64.rpm

# 或使用 rpm 命令
sudo rpm -ivh tokenless-0.1.0-1.alnx4.x86_64.rpm
```

## 验证安装

```bash
# 检查已安装的文件
rpm -ql tokenless

# 查看包信息
rpm -qi tokenless

# 查看 changelog
rpm -q --changelog tokenless
```

## 已安装文件

### 二进制文件
- `/usr/bin/tokenless` - 主程序
- `/usr/bin/rtk` - RTK 代理工具

### 共享文件
- `/usr/share/tokenless/openclaw/index.ts` - OpenClaw TypeScript 入口
- `/usr/share/tokenless/openclaw/openclaw.plugin.json` - OpenClaw 插件配置
- `/usr/share/tokenless/openclaw/package.json` - Node.js 包配置
- `/usr/share/tokenless/scripts/install.sh` - 安装脚本

## Spec 文件说明

```spec
Name:           tokenless
Version:        0.1.0
Release:        1.alnx4
Summary:        CLI tool for LLM schema and response compression with RTK
License:        MIT
BuildRequires:  cargo, rust >= 1.70
```

## 版本历史

### 0.1.0-1 (2026-04-10)
- 初始版本
- 包含 tokenless 和 rtk 两个二进制文件
- 包含 openclaw TypeScript 和 JSON 配置文件
- 包含 install.sh 安装脚本

## 常见问题

### Q: 构建时遇到 Rust 版本问题？
A: 确保安装了 Rust >= 1.70，可以使用 `rustup` 安装最新版本：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Q: 如何卸载？
A: 使用以下命令卸载：
```bash
sudo yum remove tokenless
# 或
sudo rpm -e tokenless
```

## 联系方式
Token-Less
- 作者：林生
- 邮箱：linyan.lin@alibaba-inc.com
rpm package
- 作者：Shile Zhang
- 邮箱：shile.zhang@linux.alibaba.com

## 许可证

MIT License
