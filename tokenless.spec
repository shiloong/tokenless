%define anolis_release 1
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
%setup -q -n Token-Less

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

# Return to main project directory
cd %{_builddir}/Token-Less

# Install tokenless binary
install -m 0755 target/release/tokenless %{buildroot}%{_bindir}/tokenless

# Install rtk binary
install -m 0755 third_party/rtk/target/release/rtk %{buildroot}%{_bindir}/rtk

# Install openclaw .ts and .json files
install -m 0644 openclaw/index.ts %{buildroot}/usr/share/tokenless/openclaw/
install -m 0644 openclaw/openclaw.plugin.json %{buildroot}/usr/share/tokenless/openclaw/
install -m 0644 openclaw/package.json %{buildroot}/usr/share/tokenless/openclaw/

# Install scripts
install -m 0755 scripts/install.sh %{buildroot}/usr/share/tokenless/scripts/

%files
%{_bindir}/tokenless
%{_bindir}/rtk
/usr/share/tokenless/

%changelog
* Fri Apr 10 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-1
- Initial package for tokenless 0.1.0
- Include rtk (Rust Token Killer) binary
- Include openclaw TypeScript and JSON files
- Include install.sh script
