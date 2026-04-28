%define anolis_release 2
%global debug_package %{nil}

Name:           tokenless
Version:        0.2.0
Release:        %{anolis_release}%{?dist}
Summary:        LLM Token Optimization Toolkit - Schema/Response Compression + Command Rewriting

License:        MIT and Apache-2.0
URL:            https://github.com/alibaba/anolisa
Source0:        %{name}-%{version}.tar.gz
ExcludeArch:    aarch64

# Runtime dependencies
Requires:       jq
Requires:       bash

%description
Token-Less is an LLM token optimization toolkit that significantly reduces token
consumption through Schema/Response Compression, TOON Context Compression, and
Command Rewriting strategies.

Core Features:
- Schema Compression: Compresses OpenAI Function Calling tool definitions
- Response Compression: Compresses API/tool responses (removes debug/null/empty)
- TOON Context Compression: Encodes JSON to TOON format, chained after response compression
- Command Rewriting: Filters CLI command output via RTK
- Statistics Tracking: SQLite-based metrics for compression effectiveness

The package includes:
- tokenless: CLI tool for schema/response compression and toon integration
- rtk: High-performance CLI proxy for command rewriting (Apache-2.0 licensed)
- toon: JSON to TOON format encoder/decoder for LLM token optimization

Note: OpenClaw plugin and copilot-shell hooks are available under
/usr/share/tokenless/adapters/ for manual configuration.

%prep
%setup -q -n tokenless

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/tokenless
mkdir -p %{buildroot}%{_docdir}/tokenless

# Install pre-compiled binaries
install -m 0755 bin/tokenless %{buildroot}%{_bindir}/tokenless
install -m 0755 bin/rtk %{buildroot}%{_bindir}/rtk
install -m 0755 bin/toon %{buildroot}%{_bindir}/toon

# Install documentation
install -m 0644 docs/tokenless-user-manual-en.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 docs/tokenless-user-manual-zh.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 docs/response-compression.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 LICENSE %{buildroot}%{_docdir}/tokenless/

# Install adapters (agent-specific plugins/hooks)
mkdir -p %{buildroot}%{_datadir}/tokenless/adapters/openclaw
mkdir -p %{buildroot}%{_datadir}/tokenless/adapters/cosh
mkdir -p %{buildroot}%{_datadir}/tokenless/scripts

install -m 0644 openclaw/index.ts %{buildroot}%{_datadir}/tokenless/adapters/openclaw/
install -m 0644 openclaw/openclaw.plugin.json %{buildroot}%{_datadir}/tokenless/adapters/openclaw/
install -m 0644 openclaw/package.json %{buildroot}%{_datadir}/tokenless/adapters/openclaw/
install -m 0644 openclaw/README.md %{buildroot}%{_datadir}/tokenless/adapters/openclaw/

install -m 0755 hooks/copilot-shell/tokenless-*.sh %{buildroot}%{_datadir}/tokenless/adapters/cosh/
install -m 0644 hooks/copilot-shell/README.md %{buildroot}%{_datadir}/tokenless/adapters/cosh/

install -m 0755 scripts/install.sh %{buildroot}%{_datadir}/tokenless/scripts/

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/tokenless
%attr(0755,root,root) %{_bindir}/rtk
%attr(0755,root,root) %{_bindir}/toon
%doc %{_docdir}/tokenless/LICENSE
%doc %{_docdir}/tokenless/response-compression.md
%doc %{_docdir}/tokenless/tokenless-user-manual-en.md
%doc %{_docdir}/tokenless/tokenless-user-manual-zh.md
%dir %{_datadir}/tokenless
%dir %{_datadir}/tokenless/scripts
%dir %{_datadir}/tokenless/adapters
%dir %{_datadir}/tokenless/adapters/openclaw
%dir %{_datadir}/tokenless/adapters/cosh
%attr(0755,root,root) %{_datadir}/tokenless/scripts/install.sh
%attr(0755,root,root) %{_datadir}/tokenless/adapters/cosh/README.md
%attr(0755,root,root) %{_datadir}/tokenless/adapters/cosh/tokenless-*.sh
%{_datadir}/tokenless/adapters/openclaw/*

%post
if [ -x %{_datadir}/tokenless/scripts/install.sh ]; then
    %{_datadir}/tokenless/scripts/install.sh --install || true
fi

%preun
if [ $1 -eq 0 ] && [ -x %{_datadir}/tokenless/scripts/install.sh ]; then
    %{_datadir}/tokenless/scripts/install.sh --uninstall || true
fi

%changelog
* Tue Apr 28 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.2.0-2
- Restructure dirs: /usr/share/tokenless/{adapters/{openclaw,cosh}}
- Fix upstream reference, pull from main branch latest
- Refresh tarball and update README

* Sun Apr 26 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.2.0-1
- Bump to v0.2.0 with new features and fixes
  - feat: add TOON context compression support
  - feat: add compression stats with auto-record from real data
  - fix: skip compression for skill and content-retrieval tools
  - chore: upgrade Rust edition to 2024
- Switch to pre-compiled binary packaging (tokenless + rtk + toon)
- ExcludeArch: aarch64

* Sat Apr 25 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-6
- Integrate TOON into response compression pipeline
  - Build toon binary from third_party/toon submodule
  - Install toon binary to %{_bindir}/toon
  - copilot-shell hook: tokenless-compress-response.sh runs sequential pipeline
  - OpenClaw plugin: toon_compression_enabled option
  - Expected combined savings: 30-60% on structured JSON data

* Sat Apr 25 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-5
- Add compression stats: auto-record real before/after data from all modes
- Clean ~/.tokenless on RPM uninstall

* Sat Apr 25 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-4
- Fix: skip compression for content-retrieval tools and skill files

* Tue Apr 21 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-3
- Refactor stats system for comprehensive compression metrics tracking
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
