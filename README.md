# Token-Less RPM Package

Token-Less 的 RPM 打包仓库，包含完整的 spec 文件和构建说明。

## 项目介绍

Token-Less 是一个用于 LLM schema 和响应压缩的 CLI 工具，帮助开发者高效地压缩大型语言模型的 schema 和响应。

本 RPM 包包含：
- **tokenless**: LLM schema 和响应压缩工具
- **rtk**: Rust Token Killer - 高性能 CLI 代理，最小化 LLM token 消耗
- **openclaw**: TypeScript 和 JSON 配置文件
- **install.sh**: 安装脚本
- **hooks/copilot-shell/**: copilot-shell hook 脚本（命令重写、响应压缩、schema 压缩）

## 系统要求

- Alibaba Cloud Linux 4 (Anolis OS 23)
- 或其他基于 RPM 的 Linux 发行版（RHEL/CentOS/Fedora）

## 特性

- **离线构建支持**: 源码包包含完整的 Rust 依赖 vendor 目录，可在无公网环境下编译
- **双二进制**: 同时打包 tokenless 和 rtk 两个工具
- **OpenClaw 集成**: 包含完整的 OpenClaw 插件配置和脚本
- **cosh Hook 支持**: 包含 copilot-shell 的 PreToolUse/PostToolUse/BeforeModel 三个阶段的 hook 脚本

## 目录结构

```
.
├── README.md                 # 本说明文档
├── tokenless.spec            # RPM spec 文件
└── tokenless-0.1.0.tar.gz    # 源码包
```

## Building RPM Package

### 1. Prepare Build Environment

```bash
# Install necessary tools
sudo yum install -y rpm-build cargo rust

# Create rpmbuild directory structure
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
```

### 2. Copy Files to rpmbuild Directory

```bash
cp tokenless.spec ~/rpmbuild/SPECS/
cp tokenless-0.1.0.tar.gz ~/rpmbuild/SOURCES/
```

### 3. Build RPM

```bash
cd ~/rpmbuild
rpmbuild -ba SPECS/tokenless.spec
```

After build completes, RPM packages are located at:
- Binary package: `~/rpmbuild/RPMS/x86_64/tokenless-0.1.0-1.alnx4.x86_64.rpm`
- Source package: `~/rpmbuild/SRPMS/tokenless-0.1.0-1.alnx4.src.rpm`

## Installing RPM Package

```bash
# Install using yum/dnf (recommended, auto-resolves dependencies)
sudo yum install ./tokenless-0.1.0-1.alnx4.x86_64.rpm

# Or use rpm command
sudo rpm -ivh tokenless-0.1.0-1.alnx4.x86_64.rpm
```

## Verifying Installation

```bash
# Check installed files
rpm -ql tokenless

# View package information
rpm -qi tokenless

# View changelog
rpm -q --changelog tokenless
```

## Unified Install.sh Script

The `install.sh` script is a unified installation and configuration script that supports multiple modes:

### Usage

```bash
# Auto-detect installation source and install
./install.sh

# Force source installation
./install.sh --source

# RPM post-installation configuration (called by %post scriptlet)
./install.sh --install

# RPM pre-uninstallation cleanup, full uninstall (called by %preun scriptlet)
./install.sh --uninstall

# RPM pre-uninstallation cleanup, upgrade scenario (called by %preun scriptlet)
./install.sh --upgrade

# Show help
./install.sh --help
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INSTALL_DIR` | `$HOME/.local/bin` | Installation directory for source install |
| `OPENCLAW_DIR` | `$HOME/.openclaw/extensions/tokenless` | OpenClaw plugin directory |
| `COPILOT_SHELL_HOOK_DIR` | `$HOME/.local/share/tokenless/hooks` | Hook scripts directory |

## Post-Installation Configuration (RPM)

After RPM installation, the `%post` scriptlet automatically:

1. **Detect Configuration File**: `~/.copilot-shell/settings.json` or `~/.qwen-code/settings.json`
2. **Register Hooks**: Adds PreToolUse, PostToolUse, and BeforeModel hooks
3. **Hook Scripts Location**: `/usr/share/tokenless/hooks/copilot-shell/`

To manually reconfigure:
```bash
/usr/share/tokenless/scripts/install.sh --install
```

### Hook Features

| Hook Event | Feature | Token Savings |
|----------|------|-----------|
| PreToolUse | Command rewriting (RTK) | 60-90% |
| PostToolUse | Response compression | ~26% |
| BeforeModel | Schema compression | ~57% |

### Manual Reconfiguration

If you need to reconfigure hooks, run manually:

```bash
sudo /usr/share/tokenless/scripts/install.sh --install
```

### Manual Configuration

If automatic configuration fails, manually add the following to `~/.copilot-shell/settings.json` or `~/.qwen-code/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Shell",
        "hooks": [
          {
            "type": "command",
            "command": "/usr/share/tokenless/hooks/copilot-shell/tokenless-rewrite.sh",
            "name": "tokenless-rewrite",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/share/tokenless/hooks/copilot-shell/tokenless-compress-response.sh",
            "name": "tokenless-compress-response",
            "timeout": 10000
          }
        ]
      }
    ],
    "BeforeModel": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/share/tokenless/hooks/copilot-shell/tokenless-compress-schema.sh",
            "name": "tokenless-compress-schema",
            "timeout": 10000
          }
        ]
      }
    ]
  }
}
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

## Installed Files

### Binaries
- `/usr/bin/tokenless` - Main program
- `/usr/bin/rtk` - RTK proxy tool

### Shared Files
- `/usr/share/tokenless/openclaw/index.ts` - OpenClaw TypeScript entry
- `/usr/share/tokenless/openclaw/openclaw.plugin.json` - OpenClaw plugin configuration
- `/usr/share/tokenless/openclaw/package.json` - Node.js package configuration
- `/usr/share/tokenless/scripts/install.sh` - Installation script
- `/usr/share/tokenless/scripts/postinstall.sh` - Post-installation configuration script (auto-configures copilot-shell hooks)
- `/usr/share/tokenless/scripts/preuninstall.sh` - Pre-uninstallation cleanup script
- `/usr/share/tokenless/hooks/copilot-shell/tokenless-rewrite.sh` - Command rewriting hook
- `/usr/share/tokenless/hooks/copilot-shell/tokenless-compress-response.sh` - Response compression hook
- `/usr/share/tokenless/hooks/copilot-shell/tokenless-compress-schema.sh` - Schema compression hook
- `/usr/share/tokenless/hooks/copilot-shell/README.md` - Hook usage documentation

### Automatically Configured
After installation, hook scripts in `/usr/share/tokenless/hooks/copilot-shell/` are automatically registered in the user's copilot-shell configuration file (`~/.copilot-shell/settings.json` or `~/.qwen-code/settings.json`).

## Spec File Description

```spec
Name:           tokenless
Version:        0.1.0
Release:        1.alnx4
Summary:        CLI tool for LLM schema and response compression with RTK
License:        MIT
BuildRequires:  cargo, rust >= 1.70
```

## Version History

### 0.1.0-2 (2026-04-11)
- Unified install.sh script combining postinstall and preuninstall functionality
  - Single script handles: source install, RPM post-install, RPM pre-uninstall
  - Modes: --install, --uninstall, --upgrade, --uninstall-source, --help
  - Backward compatible with existing RPM workflow
- Added cosh (copilot-shell) hook support
  - tokenless-rewrite.sh: Command rewriting hook (PreToolUse)
  - tokenless-compress-response.sh: Response compression hook (PostToolUse)
  - tokenless-compress-schema.sh: Schema compression hook (BeforeModel)
- Automatic copilot-shell hook configuration via %post/%preun scriptlets
  - Idempotent installation (no duplicate hooks on reinstall)
  - Complete cleanup on uninstall (removes empty hooks arrays)
  - Supports both ~/.copilot-shell/settings.json and ~/.qwen-code/settings.json
  - Fail-open design: gracefully handles missing dependencies
- Updated vendor dependencies (main project + RTK submodule)

### 0.1.0-1 (2026-04-10)
- Initial version
- Includes tokenless and rtk binaries
- Includes openclaw TypeScript and JSON configuration files
- Includes install.sh script

## Frequently Asked Questions

### Q: Rust version issues during build?
A: Ensure Rust >= 1.70 is installed. You can install the latest version using `rustup`:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Q: How to uninstall?
A: Use the following command to uninstall:
```bash
sudo yum remove tokenless
# or
sudo rpm -e tokenless
```

The `%preun` scriptlet will automatically:
1. Backup your settings.json (with timestamp)
2. Remove tokenless hooks from configuration
3. Clean up empty hooks arrays

To manually uninstall source installation:
```bash
./install.sh --uninstall-source
```

## Contact

Token-Less
- Author: Lin Sheng
- Email: linyan.lin@alibaba-inc.com

RPM Package
- Author: Zhang Shile
- Email: shile.zhang@linux.alibaba.com

## License

MIT License
