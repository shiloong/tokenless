#!/bin/bash
# Token-Loss 源码打包脚本
# 生成 tokenless-<version>.tar.gz 源码包

set -e

# 配置
REPO_URL="git@gitlab.alibaba-inc.com:Agentic-OS/Token-Less.git"
WORKSPACE_DIR="$PWD"
REPO_DIR="${WORKSPACE_DIR}/Token-Less"
OUTPUT_DIR="${WORKSPACE_DIR}/packages"
TEMP_DIR="${WORKSPACE_DIR}/.tokenless-build-$$"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cleanup() {
    log_info "清理临时目录..."
    rm -rf "${TEMP_DIR}"
}

trap cleanup EXIT

# 获取版本号
get_version() {
    local version=""
    if [ -f "${REPO_DIR}/Cargo.toml" ]; then
        version=$(grep -E '^version[[:space:]]*=' "${REPO_DIR}/Cargo.toml" | head -1 | sed 's/^version[[:space:]]*=[[:space:]]*"\([^"]*\)"/\1/')
    fi
    if [ -z "$version" ]; then
        version="0.0.0"
    fi
    echo "$version"
}

# 1. 下载最新源代码（包括 submodule）
download_source() {
    log_info "步骤 1: 下载最新源代码..."

    if [ -d "${REPO_DIR}/.git" ]; then
        log_info "仓库已存在，尝试 git pull 更新..."
        cd "${REPO_DIR}"
        if git fetch origin 2>/dev/null; then
            git reset --hard origin/HEAD 2>/dev/null || git reset --hard origin/main 2>/dev/null || git reset --hard origin/master
            git clean -fd
        else
            log_warn "无法连接远程仓库，使用本地现有代码"
        fi
    elif [ -d "${REPO_DIR}" ]; then
        log_warn "目录存在但非 git 仓库，使用现有代码"
    else
        log_info "克隆仓库..."
        mkdir -p "${WORKSPACE_DIR}"
        if ! git clone "${REPO_URL}" "${REPO_DIR}"; then
            log_error "无法克隆仓库，请检查网络连接或访问权限"
            exit 1
        fi
        cd "${REPO_DIR}"
    fi

    # 初始化和更新 submodule
    log_info "初始化和更新 submodule..."
    cd "${REPO_DIR}"
    if ! git submodule update --init --recursive 2>/dev/null; then
        log_warn "submodule 更新失败，检查是否已初始化"
    fi
}

# 2. 使用 cargo vendor 命令下载全部 vendor 包
download_vendors() {
    log_info "步骤 2: 下载 cargo vendor 包..."
    cd "${REPO_DIR}"

    # 执行 cargo vendor 下载 vendor 包（主项目）
    log_info "执行 cargo vendor 创建主项目 vendor 目录..."
    cargo vendor --versioned-dirs "${REPO_DIR}/vendor"

    # 检查是否有第三方的 RTK submodule 需要 vendor
    if [ -d "third_party/rtk" ] && [ -f "third_party/rtk/Cargo.toml" ]; then
        log_info "发现 RTK submodule，执行 RTK vendor..."
        cd "third_party/rtk"

        # RTK 的 vendor 目录（放在 rtk 目录下）
        local rtk_vendor_dir="${REPO_DIR}/third_party/rtk/vendor"

        # 执行 RTK 的 cargo vendor
        cargo vendor --versioned-dirs "${rtk_vendor_dir}"

        # 创建 RTK 的 cargo config
        mkdir -p "${REPO_DIR}/third_party/rtk/.cargo"
        cat > "${REPO_DIR}/third_party/rtk/.cargo/config.toml" << 'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

        log_info "RTK vendor 完成，vendor 位于 third_party/rtk/vendor/"
        cd "${REPO_DIR}"
    fi

    # 创建主项目 cargo config 配置 vendor 源
    mkdir -p "${REPO_DIR}/.cargo"
    cat > "${REPO_DIR}/.cargo/config.toml" << 'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

    log_info "Vendor 下载完成"
}

# 3. 清理无关文件
cleanup_files() {
    log_info "步骤 3: 清理无关文件..."
    cd "${REPO_DIR}"

    # 删除 macOS 文件
    log_info "删除 macOS 文件..."
    find . -name ".DS_Store" -delete
    find . -name "._*" -delete

    # 删除 git 配置文件
    log_info "删除 git 配置文件..."
    rm -rf .git
    rm -f .gitignore
    rm -f .gitmodules

    # 删除其他无关文件
    log_info "删除其他构建产物和缓存..."
    rm -rf target/
    rm -rf .cargo/registry/

    # 删除主 vendor 中的 .git 目录和 vcs 信息
    if [ -d "vendor" ]; then
        log_info "清理 vendor 中的 .git 目录..."
        find vendor -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
        find vendor -name ".cargo_vcs_info.json" -delete 2>/dev/null || true
    fi

    # 删除 RTK vendor 中的 .git 目录和 vcs 信息
    if [ -d "third_party/rtk/vendor" ]; then
        log_info "清理 third_party/rtk/vendor 中的 .git 目录..."
        find third_party/rtk/vendor -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
        find third_party/rtk/vendor -name ".cargo_vcs_info.json" -delete 2>/dev/null || true
    fi

    # 删除 submodule 的 git 信息
    if [ -d "third_party/rtk/.git" ]; then
        rm -rf third_party/rtk/.git
    fi

    # 删除 RTK 目录中的 .cargo 配置（因为使用了相对路径，保留即可）
    # 但需要清理可能存在的 registry 缓存
    if [ -d "third_party/rtk/.cargo/registry" ]; then
        rm -rf third_party/rtk/.cargo/registry
    fi

    log_info "清理完成"
}

# 4. 打包
create_tarball() {
    log_info "步骤 4: 创建 tar 包..."
    
    local version=$(get_version)
    local package_name="tokenless-${version}"
    local tarball_name="${package_name}.tar.gz"
    
    # 创建输出目录
    mkdir -p "${OUTPUT_DIR}"
    
    # 创建临时目录用于打包
    mkdir -p "${TEMP_DIR}"
    cp -r "${REPO_DIR}" "${TEMP_DIR}/${package_name}"
    
    # 创建 tar 包
    cd "${TEMP_DIR}"
    tar -czf "${OUTPUT_DIR}/${tarball_name}" "${package_name}"
    
    # 复制一份到当前目录方便访问
    cp "${OUTPUT_DIR}/${tarball_name}" "${WORKSPACE_DIR}/"
    
    log_info "打包完成: ${OUTPUT_DIR}/${tarball_name}"
    log_info "文件大小: $(du -h "${OUTPUT_DIR}/${tarball_name}" | cut -f1)"
    
    # 列出包内容
    log_info "包内容预览:"
    tar -tzf "${OUTPUT_DIR}/${tarball_name}" | head -20
    echo "..."
}

# 主函数
main() {
    log_info "=========================================="
    log_info "Token-Loss 源码打包脚本"
    log_info "=========================================="

    # 检查 Rust 版本
    if ! command -v cargo &> /dev/null; then
        log_error "未找到 cargo 命令，请先安装 Rust (建议版本 >= 1.85)"
        exit 1
    fi

    local cargo_version=$(cargo --version 2>&1 | awk '{print $2}')
    log_info "当前 Cargo 版本: ${cargo_version}"
    log_info "注意: 项目依赖可能需要 Rust >= 1.85 以支持 edition 2024"

    # 确保工作目录存在
    mkdir -p "${WORKSPACE_DIR}"

    # 执行各步骤
    download_source
    download_vendors
    cleanup_files
    create_tarball

    log_info "=========================================="
    log_info "打包成功完成!"
    log_info "输出文件：${WORKSPACE_DIR}/tokenless-*.tar.gz"
    log_info "=========================================="
}

# 运行主函数
main "$@"
