#!/bin/bash
# Token-Less RPM 打包脚本
# 从 anolisa monorepo 获取 tokenless 源码，本地编译二进制 + 生成适配器资源，打包构建 RPM。
# 预编译模型：RPM 构建阶段只 install，不编译（供离线分发）。

set -e

REPO_URL="https://github.com/alibaba/anolisa.git"
# 通过环境变量指定 TAG（如 tokenless/v0.6.0）或 VERSION（如 0.6.0）
# 未指定时从本地 anolisa Cargo.toml 解析版本号，自动推断 release 分支
TAG="${TAG:-}"
VERSION_HINT="${VERSION:-}"
# 指向本地 anolisa 仓库根目录（避免从 GitHub 克隆）；未设置则浅克隆
ANOLISA_DIR="${ANOLISA_DIR:-}"

if [ -n "${TAG}" ]; then
    CLONE_REF="${TAG}"
elif [ -n "${VERSION_HINT}" ]; then
    MAJOR=$(echo "${VERSION_HINT}" | cut -d. -f1)
    MINOR=$(echo "${VERSION_HINT}" | cut -d. -f2)
    CLONE_REF="release/tokenless/v${MAJOR}.${MINOR}.y"
else
    LOCAL_CARGO="/root/anolisa/src/tokenless/Cargo.toml"
    if [ -f "${LOCAL_CARGO}" ]; then
        V=$(grep -E 'version\s*=' "${LOCAL_CARGO}" | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
        MAJOR=$(echo "${V}" | cut -d. -f1)
        MINOR=$(echo "${V}" | cut -d. -f2)
        CLONE_REF="release/tokenless/v${MAJOR}.${MINOR}.y"
    else
        CLONE_REF="main"
    fi
fi

WORKSPACE_DIR="$PWD"
TEMP_DIR="${WORKSPACE_DIR}/.tokenless-build-$$"
OUTPUT_DIR="${WORKSPACE_DIR}/packages"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() { log_info "清理临时目录..."; rm -rf "${TEMP_DIR}"; }
trap cleanup EXIT

# Extract normalized destination paths from a spec's %files section.
# Strips %attr/%defattr/%dir/%doc/%license modifiers and comments so entries
# differing only in formatting (e.g. "%attr(0755,root,root) %{_bindir}/rtk" vs
# "%{_bindir}/rtk") compare equal. A bare "%{_bindir}/rtk" path is NOT mistaken
# for a section header because section headers are "%word" (letters only).
extract_files_paths() {
    awk '
        /^%files[[:space:]]*$/ { in_files=1; next }
        in_files && /^%[a-zA-Z]+[[:space:]]*$/ { in_files=0; next }
        in_files {
            line=$0
            sub(/#.*/, "", line)
            gsub(/%attr\([^)]*\)[[:space:]]*/, "", line)
            gsub(/%defattr\([^)]*\)[[:space:]]*/, "", line)
            sub(/^%dir[[:space:]]+/, "", line)
            sub(/^%doc[[:space:]]+/, "", line)
            sub(/^%license[[:space:]]+/, "", line)
            sub(/^[[:space:]]+/, "", line)
            sub(/[[:space:]]+$/, "", line)
            if (line != "") print line
        }
    ' "$1" | sort -u
}

# Hard-fail if the build-repo tokenless.spec %files manifest is missing any
# destination path declared by the source tokenless.spec.in. The build-repo
# spec is an install-only variant (no %build, pre-compiled binaries from the
# tarball), so %install source paths legitimately differ — but the %files
# destination set must be a superset of the source's, otherwise files declared
# by the source (e.g. component.toml) get silently dropped from the RPM.
sync_check_spec_files() {
    local src_spec_in="${SRCDIR}/tokenless.spec.in"
    local pkg_spec="${WORKSPACE_DIR}/tokenless.spec"
    [ -f "$src_spec_in" ] || { log_error "源码 spec.in 不存在: $src_spec_in"; exit 1; }
    [ -f "$pkg_spec" ]    || { log_error "构建仓 spec 不存在: $pkg_spec"; exit 1; }

    local src_files pkg_files missing
    src_files=$(extract_files_paths "$src_spec_in")
    pkg_files=$(extract_files_paths "$pkg_spec")
    missing=$(comm -23 <(printf '%s\n' "$src_files") <(printf '%s\n' "$pkg_files"))
    if [ -n "$missing" ]; then
        log_error "构建仓 tokenless.spec 的 %files 缺少源码 spec.in 声明的以下路径 (spec 漂移):"
        printf '%s\n' "$missing" | sed 's/^/    /'
        log_error "请在构建仓 tokenless.spec 的 %install 与 %files 段补齐上述路径，使其与源码 spec.in 同步后重试。"
        exit 1
    fi
    log_info "spec %%files 同步校验通过 (源码 $(printf '%s\n' "$src_files" | wc -l) 项, 构建仓 $(printf '%s\n' "$pkg_files" | wc -l) 项)"
}

main() {
    log_info "=========================================="
    log_info "Token-Less RPM 打包（本地编译模式）"
    [ -n "${ANOLISA_DIR}" ] && log_info "源码: 本地 ${ANOLISA_DIR}" || log_info "源码: ${REPO_URL} @ ${CLONE_REF}"
    log_info "=========================================="

    command -v cargo &> /dev/null || { log_error "未找到 cargo，请先安装 Rust (>= 1.88)"; exit 1; }
    command -v just &> /dev/null || { log_error "未找到 just（rtk setup 需要）"; exit 1; }
    log_info "Cargo: $(cargo --version 2>&1 | awk '{print $2}') (需要 >= 1.88)"

    mkdir -p "${OUTPUT_DIR}" "${TEMP_DIR}"

    # === 1. 获取源码 ===
    if [ -n "${ANOLISA_DIR}" ]; then
        [ -f "${ANOLISA_DIR}/src/tokenless/Cargo.toml" ] || { log_error "ANOLISA_DIR/src/tokenless/Cargo.toml 不存在"; exit 1; }
        SRCDIR="${ANOLISA_DIR}/src/tokenless"
        log_info "步骤 1: 使用本地 anolisa 源码 ${SRCDIR}"
    else
        log_info "步骤 1: 克隆 anolisa (${CLONE_REF})..."
        git clone --branch "${CLONE_REF}" --depth 1 "${REPO_URL}" "${TEMP_DIR}/anolisa" || { log_error "克隆失败"; exit 1; }
        SRCDIR="${TEMP_DIR}/anolisa/src/tokenless"
    fi

    # Pre-flight: fail fast before compiling if the build-repo spec has drifted
    # from the source spec.in (e.g. a newly shipped file like component.toml is
    # missing from tokenless.spec's %files).
    sync_check_spec_files

    # === 2. setup rtk（clone + patch，幂等：已存在则跳过）===
    log_info "步骤 2: setup rtk (just setup-rtk)..."
    (cd "${SRCDIR}" && just setup-rtk)

    # === 3. 生成适配器模板（.in -> manifest.json/plugin.json/...）===
    log_info "步骤 3: stamp adapter templates (make stamp-adapter-templates)..."
    (cd "${SRCDIR}" && make stamp-adapter-templates)

    # === 4. 编译 OpenClaw TS 插件 -> dist/index.js ===
    log_info "步骤 4: build openclaw plugin (make build-openclaw-plugin)..."
    (cd "${SRCDIR}" && make build-openclaw-plugin)

    # === 5. 编译二进制 ===
    log_info "步骤 5: 编译 tokenless..."
    (cd "${SRCDIR}" && cargo build --release 2>&1 | tail -3)
    log_info "步骤 6: 编译 rtk..."
    (cd "${SRCDIR}" && cargo build --release --manifest-path third_party/rtk/Cargo.toml 2>&1 | tail -3)
    log_info "步骤 7: 编译 toon (cargo install toon-format 0.5.0)..."
    cargo install toon-format --version 0.5.0 --root "${TEMP_DIR}/toon-root" --locked 2>&1 | tail -3

    # === 6. 解析版本号 ===
    VERSION=$(grep -E 'version\s*=' "${SRCDIR}/Cargo.toml" | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
    [ -n "$VERSION" ] || { log_error "无法解析版本号"; exit 1; }
    log_info "上游版本: ${VERSION}"

    # === 7. 准备打包目录（spec 期望的扁平布局）===
    log_info "步骤 8: 准备打包目录..."
    PKG="${TEMP_DIR}/tokenless"
    mkdir -p "${PKG}/bin" "${PKG}/adapters" "${PKG}/docs"

    cp "${SRCDIR}/target/release/tokenless" "${PKG}/bin/"
    cp "${SRCDIR}/third_party/rtk/target/release/rtk" "${PKG}/bin/"
    cp "${TEMP_DIR}/toon-root/bin/toon" "${PKG}/bin/"

    cp -r "${SRCDIR}/adapters/tokenless" "${PKG}/adapters/"
    # 清理 .in 模板、node_modules、__pycache__
    find "${PKG}/adapters" -name "*.in" -delete
    find "${PKG}/adapters" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "${PKG}/adapters" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true

    cp "${SRCDIR}/docs/tokenless-user-manual-en.md" "${PKG}/docs/"
    cp "${SRCDIR}/docs/tokenless-user-manual-zh.md" "${PKG}/docs/"
    cp "${SRCDIR}/docs/response-compression.md" "${PKG}/docs/"
    cp "${SRCDIR}/LICENSE" "${PKG}/"

    # Stage the RPM component contract (regenerated from .in by make
    # stamp-adapter-templates in step 3). The install-only spec ships it from
    # the tarball root: .anolisa/component.toml
    mkdir -p "${PKG}/.anolisa"
    cp "${SRCDIR}/.anolisa/component.toml" "${PKG}/.anolisa/"

    log_info "打包目录:"; ls "${PKG}/bin/"

    # === 8. 打 tar 包 ===
    log_info "步骤 9: 创建源码包..."
    cd "${TEMP_DIR}"
    TARBALL_NAME="tokenless-${VERSION}.tar.gz"
    tar -czf "${OUTPUT_DIR}/${TARBALL_NAME}" tokenless
    cp "${OUTPUT_DIR}/${TARBALL_NAME}" "${WORKSPACE_DIR}/"
    log_info "打包完成: ${OUTPUT_DIR}/${TARBALL_NAME} ($(du -h "${OUTPUT_DIR}/${TARBALL_NAME}" | cut -f1))"

    # === 9. 构建 RPM ===
    log_info "步骤 10: 构建 RPM..."
    mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
    cp "${OUTPUT_DIR}/${TARBALL_NAME}" ~/rpmbuild/SOURCES/
    cp "${WORKSPACE_DIR}/tokenless.spec" ~/rpmbuild/SPECS/tokenless.spec
    cd ~/rpmbuild
    rpmbuild -ba --nodeps SPECS/tokenless.spec 2>&1 || { log_error "RPM 构建失败"; exit 1; }

    log_info "=========================================="
    log_info "完成!"
    log_info "  tarball: ${WORKSPACE_DIR}/${TARBALL_NAME}"
    ls -lh ~/rpmbuild/RPMS/x86_64/tokenless-*.rpm
    log_info "=========================================="
}

main "$@"
