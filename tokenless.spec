%define anolis_release 2
%global debug_package %{nil}

Name:           tokenless
Version:        0.3.2
Release:        %{anolis_release}%{?dist}
Summary:        LLM Token Optimization Toolkit - Schema/Response Compression + Command Rewriting + Tool Ready

License:        MIT and Apache-2.0
URL:            https://github.com/alibaba/anolisa
Source0:        %{name}-%{version}.tar.gz
ExcludeArch:    aarch64

# Runtime dependencies
Requires:       python3
Requires:       jq
Requires:       bash

%description
Token-Less is an LLM token optimization toolkit that significantly reduces token
consumption through Schema/Response Compression, TOON Context Compression,
Command Rewriting, and Tool Ready environment pre-check strategies.

Core Features:
- Schema Compression: Compresses OpenAI Function Calling tool definitions
- Response Compression: Compresses API/tool responses (removes debug/null/empty)
- TOON Context Compression: Encodes JSON to TOON format, chained after response compression
- Command Rewriting: Filters CLI command output via RTK
- Tool Ready: Pre-execution environment check, auto-fix, and failure attribution
- Statistics Tracking: SQLite-based metrics for compression effectiveness

The package includes:
- tokenless: CLI tool for schema/response compression and toon integration
- rtk: High-performance CLI proxy for command rewriting (Apache-2.0 licensed)
- toon: JSON to TOON format encoder/decoder for LLM token optimization

Note: OpenClaw plugin is available under /usr/share/tokenless/adapters/.
Copilot-shell extension is auto-discovered from /usr/share/anolisa/extensions/tokenless/.

%prep
%setup -q -n tokenless

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libexecdir}/tokenless
mkdir -p %{buildroot}%{_datadir}/tokenless
mkdir -p %{buildroot}%{_docdir}/tokenless

# Install pre-compiled binaries — tokenless to /usr/bin, helpers to /usr/libexec
install -m 0755 bin/tokenless %{buildroot}%{_bindir}/tokenless
install -m 0755 bin/rtk %{buildroot}%{_libexecdir}/tokenless/rtk
install -m 0755 bin/toon %{buildroot}%{_libexecdir}/tokenless/toon

# Create symlinks so rtk and toon are discoverable via PATH
ln -sf ../libexec/tokenless/rtk %{buildroot}%{_bindir}/rtk
ln -sf ../libexec/tokenless/toon %{buildroot}%{_bindir}/toon

# Install documentation
install -m 0644 docs/tokenless-user-manual-en.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 docs/tokenless-user-manual-zh.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 docs/response-compression.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 LICENSE %{buildroot}%{_docdir}/tokenless/

# Install core env-check (shared across all agents)
mkdir -p %{buildroot}%{_datadir}/tokenless/core/env-check
install -m 0644 core/env-check/tool-ready-spec.json %{buildroot}%{_datadir}/tokenless/core/env-check/
install -m 0755 core/env-check/tokenless-env-fix.sh %{buildroot}%{_datadir}/tokenless/core/env-check/

# Install OpenClaw adapter and cosh extension (copilot-shell auto-discovery)
mkdir -p %{buildroot}%{_datadir}/tokenless/adapters/openclaw
mkdir -p %{buildroot}%{_datadir}/anolisa/extensions/tokenless/hooks
mkdir -p %{buildroot}%{_datadir}/anolisa/extensions/tokenless/commands
mkdir -p %{buildroot}%{_datadir}/tokenless/scripts

install -m 0644 openclaw/index.js %{buildroot}%{_datadir}/tokenless/adapters/openclaw/
install -m 0644 openclaw/openclaw.plugin.json %{buildroot}%{_datadir}/tokenless/adapters/openclaw/
install -m 0644 openclaw/package.json %{buildroot}%{_datadir}/tokenless/adapters/openclaw/
install -m 0644 openclaw/README.md %{buildroot}%{_datadir}/tokenless/adapters/openclaw/

install -m 0644 cosh-extension/cosh-extension.json %{buildroot}%{_datadir}/anolisa/extensions/tokenless/
install -m 0644 cosh-extension/COPILOT.md %{buildroot}%{_datadir}/anolisa/extensions/tokenless/
install -m 0644 cosh-extension/README.md %{buildroot}%{_datadir}/anolisa/extensions/tokenless/
install -m 0755 cosh-extension/hooks/*.py %{buildroot}%{_datadir}/anolisa/extensions/tokenless/hooks/
install -m 0755 cosh-extension/hooks/*.sh %{buildroot}%{_datadir}/anolisa/extensions/tokenless/hooks/
install -m 0644 cosh-extension/commands/*.toml %{buildroot}%{_datadir}/anolisa/extensions/tokenless/commands/

install -m 0755 scripts/install.sh %{buildroot}%{_datadir}/tokenless/scripts/

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/tokenless
%{_bindir}/rtk
%{_bindir}/toon
%dir %attr(0755,root,root) %{_libexecdir}/tokenless
%attr(0755,root,root) %{_libexecdir}/tokenless/rtk
%attr(0755,root,root) %{_libexecdir}/tokenless/toon
%doc %{_docdir}/tokenless/LICENSE
%doc %{_docdir}/tokenless/response-compression.md
%doc %{_docdir}/tokenless/tokenless-user-manual-en.md
%doc %{_docdir}/tokenless/tokenless-user-manual-zh.md
%dir %{_datadir}/tokenless
%dir %{_datadir}/tokenless/core
%dir %{_datadir}/tokenless/core/env-check
%dir %{_datadir}/tokenless/scripts
%dir %{_datadir}/tokenless/adapters
%dir %{_datadir}/tokenless/adapters/openclaw
%dir %{_datadir}/anolisa
%dir %{_datadir}/anolisa/extensions
%dir %{_datadir}/anolisa/extensions/tokenless
%dir %{_datadir}/anolisa/extensions/tokenless/hooks
%dir %{_datadir}/anolisa/extensions/tokenless/commands
%attr(0755,root,root) %{_datadir}/tokenless/scripts/install.sh
%attr(0644,root,root) %{_datadir}/tokenless/core/env-check/tool-ready-spec.json
%attr(0755,root,root) %{_datadir}/tokenless/core/env-check/tokenless-env-fix.sh
%attr(0755,root,root) %{_datadir}/anolisa/extensions/tokenless/hooks/*.py
%attr(0755,root,root) %{_datadir}/anolisa/extensions/tokenless/hooks/*.sh
%attr(0644,root,root) %{_datadir}/anolisa/extensions/tokenless/cosh-extension.json
%attr(0644,root,root) %{_datadir}/anolisa/extensions/tokenless/COPILOT.md
%attr(0644,root,root) %{_datadir}/anolisa/extensions/tokenless/README.md
%attr(0644,root,root) %{_datadir}/anolisa/extensions/tokenless/commands/*.toml
%{_datadir}/tokenless/adapters/openclaw/*

%post
if [ -x %{_datadir}/tokenless/scripts/install.sh ]; then
    %{_datadir}/tokenless/scripts/install.sh --install || true
fi

%preun
if [ -x %{_datadir}/tokenless/scripts/install.sh ]; then
    if [ $1 -eq 1 ]; then
        %{_datadir}/tokenless/scripts/install.sh --upgrade || true
    else
        %{_datadir}/tokenless/scripts/install.sh --uninstall || true
    fi
fi

%changelog
* Thu May 14 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.3.2-2
- fix: compile openclaw index.ts to index.js during packaging

* Wed May 13 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.3.2-1
- Bump to v0.3.2 with multiple fixes

* Wed May 13 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.3.1-2
- fix(tokenless): add schema migration for before_output/after_output columns
- fix(tokenless): use official CLI for openclaw plugin and fix RPM install/uninstall
- fix(tokenless): redesign tool-ready for 4-category spec model and fix env-check bugs

* Sun May 10 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.3.1-1
- fix(openclaw): add activation onCapabilities hook for high-version plugin compatibility

* Sun May 10 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.3.0-1
- Bump to v0.3.0 with tool-ready env pre-check and multiple fixes
  - feat: add tool-ready 4-phase environment pre-check with cosh extension integration
  - refactor: convert cosh hooks to cosh-extension format per cosh dev guide
  - fix: skip compression and stats when no token savings
  - fix: preserve tool result message structure in TOON encoding
  - fix: resolve rtk/toon binary paths for RPM-installed plugins
- Switch binaries to /usr/libexec + symlink layout (FHS)
- Add python3 runtime dependency
- Add core/env-check module (tool-ready-spec.json + tokenless-env-fix.sh)
- Add cosh-extension auto-discovery at /usr/share/anolisa/extensions/tokenless/

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
