%define anolis_release 1
%global debug_package %{nil}

Name:           tokenless
Version:        0.4.1
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

Note: OpenClaw plugin is available under /usr/share/anolisa/adapters/tokenless/openclaw/.
Copilot-shell extension is auto-discovered from /usr/share/anolisa/extensions/tokenless/.
Hermes Agent plugin (response compression, TOON encoding, command rewriting via RTK,
and Tool Ready) is available under /usr/share/anolisa/adapters/tokenless/hermes/.
Run the install script to register with Hermes: hermes/scripts/install.sh

%prep
%setup -q -n tokenless

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libexecdir}/anolisa/tokenless
mkdir -p %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/hooks
mkdir -p %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/commands
mkdir -p %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/scripts
mkdir -p %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/dist
mkdir -p %{buildroot}%{_datadir}/anolisa/adapters/tokenless/hermes/scripts
mkdir -p %{buildroot}%{_docdir}/tokenless

# Install pre-compiled binaries — tokenless to /usr/bin, helpers to /usr/libexec/anolisa/tokenless
install -m 0755 bin/tokenless %{buildroot}%{_bindir}/tokenless
install -m 0755 bin/rtk %{buildroot}%{_libexecdir}/anolisa/tokenless/rtk
install -m 0755 bin/toon %{buildroot}%{_libexecdir}/anolisa/tokenless/toon

# Create symlinks so rtk and toon are discoverable via PATH
ln -sf ../libexec/anolisa/tokenless/rtk %{buildroot}%{_bindir}/rtk
ln -sf ../libexec/anolisa/tokenless/toon %{buildroot}%{_bindir}/toon

# Install documentation
install -m 0644 docs/tokenless-user-manual-en.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 docs/tokenless-user-manual-zh.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 docs/response-compression.md %{buildroot}%{_docdir}/tokenless/
install -m 0644 LICENSE %{buildroot}%{_docdir}/tokenless/

# Install adapter bundle (common hooks/spec + openclaw)
install -m 0644 adapters/tokenless/manifest.json %{buildroot}%{_datadir}/anolisa/adapters/tokenless/
install -m 0644 adapters/tokenless/common/tool-ready-spec.json %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/
install -m 0755 adapters/tokenless/common/tokenless-env-fix.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/
install -m 0644 adapters/tokenless/common/cosh-extension.json %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/
install -m 0755 adapters/tokenless/common/hooks/*.py %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/hooks/
install -m 0755 adapters/tokenless/common/hooks/*.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/hooks/
install -m 0644 adapters/tokenless/common/commands/tokenless-stats.toml %{buildroot}%{_datadir}/anolisa/adapters/tokenless/common/commands/
install -m 0755 adapters/tokenless/openclaw/scripts/detect.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/scripts/
install -m 0755 adapters/tokenless/openclaw/scripts/install.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/scripts/
install -m 0755 adapters/tokenless/openclaw/scripts/uninstall.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/scripts/
install -m 0644 adapters/tokenless/openclaw/dist/index.js %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/dist/
install -m 0644 adapters/tokenless/openclaw/openclaw.plugin.json %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/
install -m 0644 adapters/tokenless/openclaw/package.json %{buildroot}%{_datadir}/anolisa/adapters/tokenless/openclaw/

# Install Hermes Agent plugin (Python hooks + install scripts)
install -m 0755 adapters/tokenless/hermes/__init__.py %{buildroot}%{_datadir}/anolisa/adapters/tokenless/hermes/
install -m 0644 adapters/tokenless/hermes/plugin.yaml %{buildroot}%{_datadir}/anolisa/adapters/tokenless/hermes/
install -m 0755 adapters/tokenless/hermes/scripts/detect.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/hermes/scripts/
install -m 0755 adapters/tokenless/hermes/scripts/install.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/hermes/scripts/
install -m 0755 adapters/tokenless/hermes/scripts/uninstall.sh %{buildroot}%{_datadir}/anolisa/adapters/tokenless/hermes/scripts/

# Install cosh extension for auto-discovery at /usr/share/anolisa/extensions/tokenless/
mkdir -p %{buildroot}%{_datadir}/anolisa/extensions/tokenless/hooks
mkdir -p %{buildroot}%{_datadir}/anolisa/extensions/tokenless/commands
install -m 0644 adapters/tokenless/common/cosh-extension.json %{buildroot}%{_datadir}/anolisa/extensions/tokenless/
install -m 0644 adapters/tokenless/common/tool-ready-spec.json %{buildroot}%{_datadir}/anolisa/extensions/tokenless/
install -m 0755 adapters/tokenless/common/tokenless-env-fix.sh %{buildroot}%{_datadir}/anolisa/extensions/tokenless/
install -m 0755 adapters/tokenless/common/hooks/*.py %{buildroot}%{_datadir}/anolisa/extensions/tokenless/hooks/
install -m 0755 adapters/tokenless/common/hooks/*.sh %{buildroot}%{_datadir}/anolisa/extensions/tokenless/hooks/
install -m 0644 adapters/tokenless/common/commands/tokenless-stats.toml %{buildroot}%{_datadir}/anolisa/extensions/tokenless/commands/

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/tokenless
%{_bindir}/rtk
%{_bindir}/toon
%dir %attr(0755,root,root) %{_libexecdir}/anolisa/tokenless
%attr(0755,root,root) %{_libexecdir}/anolisa/tokenless/rtk
%attr(0755,root,root) %{_libexecdir}/anolisa/tokenless/toon
%doc %{_docdir}/tokenless/LICENSE
%doc %{_docdir}/tokenless/response-compression.md
%doc %{_docdir}/tokenless/tokenless-user-manual-en.md
%doc %{_docdir}/tokenless/tokenless-user-manual-zh.md
%dir %{_datadir}/anolisa
%dir %{_datadir}/anolisa/adapters
%dir %{_datadir}/anolisa/adapters/tokenless
%dir %{_datadir}/anolisa/adapters/tokenless/common
%dir %{_datadir}/anolisa/adapters/tokenless/common/hooks
%dir %{_datadir}/anolisa/adapters/tokenless/common/commands
%dir %{_datadir}/anolisa/adapters/tokenless/openclaw
%dir %{_datadir}/anolisa/adapters/tokenless/openclaw/scripts
%dir %{_datadir}/anolisa/adapters/tokenless/openclaw/dist
%dir %{_datadir}/anolisa/adapters/tokenless/hermes
%dir %{_datadir}/anolisa/adapters/tokenless/hermes/scripts
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/manifest.json
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/common/tool-ready-spec.json
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/common/cosh-extension.json
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/common/tokenless-env-fix.sh
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/common/hooks/*.py
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/common/hooks/*.sh
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/common/commands/tokenless-stats.toml
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/openclaw/scripts/detect.sh
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/openclaw/scripts/install.sh
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/openclaw/scripts/uninstall.sh
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/openclaw/dist/index.js
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/openclaw/openclaw.plugin.json
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/openclaw/package.json
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/hermes/__init__.py
%attr(0644,root,root) %{_datadir}/anolisa/adapters/tokenless/hermes/plugin.yaml
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/hermes/scripts/detect.sh
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/hermes/scripts/install.sh
%attr(0755,root,root) %{_datadir}/anolisa/adapters/tokenless/hermes/scripts/uninstall.sh
# Cosh extension — auto-discovered from /usr/share/anolisa/extensions/
%dir %{_datadir}/anolisa/extensions
%dir %{_datadir}/anolisa/extensions/tokenless
%dir %{_datadir}/anolisa/extensions/tokenless/hooks
%dir %{_datadir}/anolisa/extensions/tokenless/commands
%attr(0644,root,root) %{_datadir}/anolisa/extensions/tokenless/cosh-extension.json
%attr(0644,root,root) %{_datadir}/anolisa/extensions/tokenless/tool-ready-spec.json
%attr(0755,root,root) %{_datadir}/anolisa/extensions/tokenless/tokenless-env-fix.sh
%attr(0755,root,root) %{_datadir}/anolisa/extensions/tokenless/hooks/*.py
%attr(0755,root,root) %{_datadir}/anolisa/extensions/tokenless/hooks/*.sh
%attr(0644,root,root) %{_datadir}/anolisa/extensions/tokenless/commands/tokenless-stats.toml

%post
# Clean up stale files from old install.sh (pre-FHS refactor).
for stale_bin in "$HOME/.local/bin/tokenless" "$HOME/.local/bin/rtk" "$HOME/.local/bin/rtk.bak" "$HOME/.local/bin/toon"; do
    rm -f "$stale_bin" 2>/dev/null || true
done
rm -f "$HOME/.local/lib/anolisa/tokenless/rtk" 2>/dev/null || true
rm -f "$HOME/.local/lib/anolisa/tokenless/toon" 2>/dev/null || true
rm -rf "$HOME/.local/share/anolisa/adapters/tokenless" 2>/dev/null || true
rmdir "$HOME/.local/lib/anolisa/tokenless" 2>/dev/null || true
rmdir "$HOME/.local/lib/anolisa" 2>/dev/null || true
rmdir "$HOME/.local/lib" 2>/dev/null || true
# Remove stale user-level cosh extension (system-level takes priority)
rm -rf "$HOME/.copilot-shell/extensions/tokenless" 2>/dev/null || true
# Clean up stale hermes-plugin dir (renamed to hermes/ with scripts)
rm -rf "/usr/share/anolisa/adapters/tokenless/hermes-plugin" 2>/dev/null || true
rm -rf "$HOME/.local/share/anolisa/adapters/tokenless/hermes-plugin" 2>/dev/null || true
# Clean up stale paths from v0.3.2 RPM layout (libexec/tokenless -> libexec/anolisa/tokenless)
rm -rf "/usr/libexec/tokenless" 2>/dev/null || true
rm -rf "/usr/share/tokenless" 2>/dev/null || true
hash -r 2>/dev/null || true

%preun
# On uninstall ($1=0): clean openclaw plugin and stale config entries
if [ $1 -eq 0 ]; then
    PLUGIN_DIR="$HOME/.openclaw/extensions/tokenless-openclaw"
    if [ -d "$PLUGIN_DIR" ]; then
        if command -v openclaw &>/dev/null; then
            openclaw plugins uninstall tokenless-openclaw --force || true
        else
            rm -rf "$PLUGIN_DIR" || true
        fi
    fi
    # Remove stale config entries from openclaw.json even if openclaw CLI is unavailable
    OPENCLAW_CFG="$HOME/.openclaw/openclaw.json"
    if [ -f "$OPENCLAW_CFG" ] && command -v jq &>/dev/null; then
        jq '(.plugins.allow // [] | map(select(. != "tokenless-openclaw"))) as $allow |
            (.plugins.entries // {} | del(.["tokenless-openclaw"])) as $entries |
            .plugins.allow = $allow | .plugins.entries = $entries' \
            "$OPENCLAW_CFG" > "${OPENCLAW_CFG}.tmp" && mv "${OPENCLAW_CFG}.tmp" "$OPENCLAW_CFG"
    fi
    # Uninstall hermes plugin (disable + remove via hermes CLI or manual cleanup)
    HERMES_SCRIPT="%{_datadir}/anolisa/adapters/tokenless/hermes/scripts/uninstall.sh"
    if [ -f "$HERMES_SCRIPT" ]; then
        bash "$HERMES_SCRIPT" || true
    elif [ -d "$HOME/.hermes/plugins/tokenless" ]; then
        rm -rf "$HOME/.hermes/plugins/tokenless" 2>/dev/null || true
    fi
fi

%changelog
* Wed May 27 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.4.1-1
- fix(tokenless): derive adapter plugin versions from Cargo.toml instead of hardcoding
- fix(tokenless): normalize adapter version numbers to 0.4.0
- fix(tokenless): derive Makefile version from Cargo.toml, fix spec changelog weekday

* Mon May 25 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.4.0-1
- feat(tokenless): add hermes agent plugin
- refactor(tokenless): align FHS paths, restructure adapter dir, remove install.sh
- refactor(tokenless): support staged installs
- fix(tokenless): correct 5 bugs in stats, naming, SQL, paths and permissions
- fix(tokenless): address code review findings across schema, env-check, hooks, and plugin
- fix(tokenless): security hardening & critical algorithm correctness
- fix(tokenless): behavioral correctness & logic fixes
- fix(tokenless): dedup, dead code removal & cosmetic cleanup
- fix(tokenless): support Debian/Ubuntu FHS paths and harden binary resolution
- fix(tokenless): build OpenClaw plugin to dist/index.js
- Align RPM install paths with upstream FHS layout (/usr/libexec/anolisa/, /usr/share/anolisa/adapters/)

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
- Fix: response compression command not working

* Sat Apr 11 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-2
- Add copilot-shell hooks and unified install script

* Fri Apr 10 2026 Shile Zhang <shile.zhang@linux.alibaba.com> - 0.1.0-1
- Initial package