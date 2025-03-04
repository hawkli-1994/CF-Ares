#!/bin/bash

# CF-Ares PyPI 发布脚本
# 此脚本用于构建和发布 CF-Ares 包到 PyPI

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的工具是否安装
check_requirements() {
    print_info "检查必要的工具..."
    
    if ! command -v python &> /dev/null; then
        print_error "未找到 Python，请安装 Python 3.8 或更高版本"
        exit 1
    fi
    
    if ! python -c "import build" &> /dev/null; then
        print_warning "未找到 build 包，正在安装..."
        pip install build
    fi
    
    if ! python -c "import twine" &> /dev/null; then
        print_warning "未找到 twine 包，正在安装..."
        pip install twine
    fi
    
    print_success "所有必要的工具已就绪"
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    if [ "$1" = "--skip-tests" ]; then
        print_warning "跳过测试"
        return 0
    fi
    
    if ! command -v pytest &> /dev/null; then
        print_warning "未找到 pytest，正在安装..."
        pip install pytest
    fi
    
    if pytest; then
        print_success "测试通过"
    else
        print_error "测试失败"
        read -p "测试失败，是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 清理旧的构建文件
clean_build() {
    print_info "清理旧的构建文件..."
    rm -rf build/ dist/ *.egg-info
    print_success "清理完成"
}

# 构建包
build_package() {
    print_info "构建包..."
    python -m build
    print_success "构建完成"
    
    print_info "构建的包:"
    ls -l dist/
}

# 发布到 PyPI 或 TestPyPI
publish_package() {
    local target="$1"
    local cmd="twine upload"
    
    if [ "$target" = "test" ]; then
        print_info "发布到 TestPyPI..."
        cmd="$cmd --repository testpypi"
    else
        print_info "发布到 PyPI..."
    fi
    
    if $cmd dist/*; then
        print_success "发布完成!"
    else
        print_error "发布失败"
        exit 1
    fi
}

# 主函数
main() {
    local skip_tests=false
    local target="pypi"
    
    # 解析命令行参数
    for arg in "$@"; do
        case $arg in
            --skip-tests)
                skip_tests=true
                ;;
            --test)
                target="test"
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --skip-tests    跳过测试"
                echo "  --test          发布到 TestPyPI 而不是 PyPI"
                echo "  --help          显示此帮助信息"
                exit 0
                ;;
        esac
    done
    
    check_requirements
    
    if [ "$skip_tests" = false ]; then
        run_tests
    fi
    
    clean_build
    build_package
    
    # 确认发布
    if [ "$target" = "test" ]; then
        read -p "是否要发布到 TestPyPI? (y/n) " -n 1 -r
    else
        read -p "是否要发布到 PyPI? (y/n) " -n 1 -r
    fi
    
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "取消发布"
        exit 0
    fi
    
    publish_package "$target"
}

# 执行主函数
main "$@" 