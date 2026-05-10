#!/bin/bash
# Token-Less RPM 打包脚本
# 从 GitHub anolisa 下载源码，本地编译，打包二进制 + 资源文件构建 RPM

set -e

REPO_URL="https://github.com/alibaba/anolisa.git"
# 通过环境变量指定 TAG（如 tokenless/v0.3.0）或 VERSION（如 0.3.0）
# 未指定时从 Cargo.toml 解析版本号，自动推断 release 分支
TAG="${TAG:-}"
VERSION_HINT="${VERSION:-}"
if [ -n "${TAG}" ]; then
    CLONE_REF="${TAG}"
else
    if [ -n "${VERSION_HINT}" ]; then
        MAJOR=$(echo "${VERSION_HINT}" | cut -d. -f1)
        MINOR=$(echo "${VERSION_HINT}" | cut -d. -f2)
        CLONE_REF="release/tokenless/v${MAJOR}.${MINOR}"
    else
        # 解析本地 anolisa Cargo.toml 推断版本，回退到 main
        LOCAL_CARGO="/root/anolisa/src/tokenless/Cargo.toml"
        if [ -f "${LOCAL_CARGO}" ]; then
            V=$(grep -E 'version\s*=' "${LOCAL_CARGO}" | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
            if [ -n "${V}" ]; then
                MAJOR=$(echo "${V}" | cut -d. -f1)
                MINOR=$(echo "${V}" | cut -d. -f2)
                CLONE_REF="release/tokenless/v${MAJOR}.${MINOR}"
            else
                CLONE_REF="main"
            fi
        else
            CLONE_REF="main"
        fi
    fi
fi
WORKSPACE_DIR="$PWD"
TEMP_DIR="${WORKSPACE_DIR}/.tokenless-build-$$"
OUTPUT_DIR="${WORKSPACE_DIR}/packages"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    log_info "清理临时目录..."
    rm -rf "${TEMP_DIR}"
}
trap cleanup EXIT

main() {
    log_info "=========================================="
    log_info "Token-Less RPM 打包（本地编译模式）"
    log_info "源码: ${REPO_URL} @ ${CLONE_REF}"
    log_info "=========================================="

    if ! command -v cargo &> /dev/null; then
        log_error "未找到 cargo，请先安装 Rust (>= 1.88)"
        exit 1
    fi
    log_info "Cargo: $(cargo --version 2>&1 | awk '{print $2}') (需要 >= 1.88)"

    mkdir -p "${OUTPUT_DIR}" "${TEMP_DIR}"

    # === 1. 克隆源码 ===
    log_info "步骤 1: 克隆 anolisa (${CLONE_REF})..."
    cd "${TEMP_DIR}"
    git clone --branch "${CLONE_REF}" --depth 1 "${REPO_URL}" anolisa || {
        log_error "无法克隆 ${REPO_URL} @ ${CLONE_REF}"
        exit 1
    }

    # === 2. 初始化 submodule ===
    log_info "步骤 2: 初始化 submodule (rtk + toon)..."
    cd "${TEMP_DIR}/anolisa"
    git submodule update --init --recursive src/tokenless/third_party/rtk src/tokenless/third_party/toon 2>/dev/null || {
        log_warn "submodule 更新失败，请检查网络"
    }

    # === 3. 解析版本号 ===
    VERSION=$(grep -E 'version\s*=' "src/tokenless/Cargo.toml" | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
    if [ -z "$VERSION" ]; then
        log_error "无法从 Cargo.toml 解析版本号"
        exit 1
    fi
    log_info "上游版本: ${VERSION}"
    SRCDIR="${TEMP_DIR}/anolisa/src/tokenless"

    # === 4. 应用 RTK patch ===
    log_info "步骤 3: 应用 RTK patch..."
    patch --forward -p1 --no-backup-if-mismatch -d "${SRCDIR}/third_party/rtk" < "${SRCDIR}/third_party/patches/rtk-tokenless-stats.patch" 2>&1 || {
        log_info "patch 已应用或无需应用"
    }

    # === 5. 本地编译 ===
    log_info "步骤 4: 编译 tokenless..."
    cd "${SRCDIR}"
    cargo build --release 2>&1 | tail -3

    log_info "步骤 5: 编译 rtk..."
    cargo build --release --manifest-path third_party/rtk/Cargo.toml 2>&1 | tail -3

    log_info "步骤 6: 编译 toon..."
    cargo build --release --manifest-path third_party/toon/Cargo.toml --features cli 2>&1 | tail -3

    # === 6. 准备打包目录 ===
    log_info "步骤 7: 准备打包目录..."
    PKG="${TEMP_DIR}/tokenless"
    mkdir -p "${PKG}/bin"

    cp "${SRCDIR}/target/release/tokenless" "${PKG}/bin/"
    cp "${SRCDIR}/third_party/rtk/target/release/rtk" "${PKG}/bin/"
    cp "${SRCDIR}/third_party/toon/target/release/toon" "${PKG}/bin/"

    cp -r "${SRCDIR}/openclaw" "${PKG}/"
    cp -r "${SRCDIR}/cosh-extension" "${PKG}/"
    cp -r "${SRCDIR}/core" "${PKG}/"
    cp -r "${SRCDIR}/scripts" "${PKG}/"
    cp -r "${SRCDIR}/docs" "${PKG}/"
    cp "${SRCDIR}/LICENSE" "${PKG}/"

    # Remove __pycache__ from cosh-extension hooks
    rm -rf "${PKG}/cosh-extension/hooks/__pycache__"

    log_info "打包目录: ${PKG}"
    ls "${PKG}/bin/"

    # === 7. 打 tar 包 ===
    log_info "步骤 8: 创建源码包..."
    cd "${TEMP_DIR}"
    TARBALL_NAME="tokenless-${VERSION}.tar.gz"
    tar -czf "${OUTPUT_DIR}/${TARBALL_NAME}" tokenless
    cp "${OUTPUT_DIR}/${TARBALL_NAME}" "${WORKSPACE_DIR}/"
    log_info "打包完成: ${OUTPUT_DIR}/${TARBALL_NAME} ($(du -h "${OUTPUT_DIR}/${TARBALL_NAME}" | cut -f1))"

    # === 8. 构建 RPM ===
    log_info "步骤 9: 构建 RPM..."
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
