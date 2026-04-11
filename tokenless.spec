%define anolis_release 3
%global debug_package %{nil}

Name:           tokenless
Version:        0.1.0
Release:        %{anolis_release}%{?dist}
Summary:        CLI tool for LLM schema and response compression with RTK
License:        MIT
URL:            https://code.alibaba-inc.com/Agentic-OS/Token-Less
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  rust >= 1.70

%description
Token-Less is a CLI tool for LLM schema and response compression.
It helps developers compress large language model schemas and responses
efficiently.

This package includes:
- tokenless: LLM schema and response compression tool
- rtk: Rust Token Killer - High-performance CLI proxy to minimize LLM token consumption

%prep
%setup -q -n tokenless-%{version}

%build
# Build tokenless (main workspace) using vendored dependencies
cargo build --release --offline

# Build rtk (third_party submodule) using vendored dependencies
# Change to rtk directory to use its own .cargo/config.toml and vendor
cd third_party/rtk
cargo build --release --offline

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}/usr/share/tokenless/openclaw
mkdir -p %{buildroot}/usr/share/tokenless/scripts
mkdir -p %{buildroot}/usr/share/tokenless/hooks/copilot-shell

# Return to main project directory
cd %{_builddir}/tokenless-%{version}

# Install tokenless binary
install -m 0755 target/release/tokenless %{buildroot}%{_bindir}/tokenless

# Install rtk binary
install -m 0755 third_party/rtk/target/release/rtk %{buildroot}%{_bindir}/rtk

# Install openclaw .ts and .json files
install -m 0644 openclaw/index.ts %{buildroot}/usr/share/tokenless/openclaw/
install -m 0644 openclaw/openclaw.plugin.json %{buildroot}/usr/share/tokenless/openclaw/
install -m 0644 openclaw/package.json %{buildroot}/usr/share/tokenless/openclaw/

# Install unified script (install.sh handles postinstall and preuninstall)
install -m 0755 scripts/install.sh %{buildroot}/usr/share/tokenless/scripts/

# Install hooks for cosh (copilot-shell)
mkdir -p %{buildroot}/usr/share/tokenless/hooks/copilot-shell
install -m 0755 hooks/copilot-shell/*.sh %{buildroot}/usr/share/tokenless/hooks/copilot-shell/
install -m 0644 hooks/copilot-shell/README.md %{buildroot}/usr/share/tokenless/hooks/copilot-shell/

%files
%{_bindir}/tokenless
%{_bindir}/rtk
/usr/share/tokenless/

%post
# Configure copilot-shell hooks after installation
if [ -x /usr/share/tokenless/scripts/install.sh ]; then
    /usr/share/tokenless/scripts/install.sh --install || true
fi

%preun
# Clean up configuration before uninstallation
# $1 = 0: full uninstall
# $1 = 1: upgrade
if [ -x /usr/share/tokenless/scripts/install.sh ]; then
    if [ $1 -eq 1 ]; then
        /usr/share/tokenless/scripts/install.sh --upgrade || true
    else
        /usr/share/tokenless/scripts/install.sh --uninstall || true
    fi
fi

%changelog
* Sat Apr 11 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-3
- Fix: Response compression not working issue
  - Fixed `tokenless compress-response` command not taking effect
  - Fixed `tokenless-compress-response.sh` hook script execution failure

* Sat Apr 11 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-2
- Unified install.sh script combining postinstall and preuninstall functionality
  - Single script handles: source install, RPM post-install, RPM pre-uninstall
  - Modes: --install, --uninstall, --upgrade, --uninstall-source, --help
  - Backward compatible with existing RPM workflow
- Added cosh (copilot-shell) hook support
  - tokenless-compress-schema.sh: Compress LLM schema for cosh
  - tokenless-compress-response.sh: Compress LLM response for cosh
  - tokenless-rewrite.sh: Rewrite requests for cosh integration
- Automatic copilot-shell hook configuration via %post/%preun scriptlets
  - Supports both ~/.copilot-shell/settings.json and ~/.qwen-code/settings.json
  - Idempotent installation (no duplicate hooks on reinstall)
  - Complete cleanup on uninstall (removes empty hooks arrays)
  - Fail-open design: gracefully handles missing dependencies

* Fri Apr 10 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-1
- Initial package for tokenless 0.1.0
- Include rtk (Rust Token Killer) binary
- Include openclaw TypeScript and JSON files
- Include install.sh script
