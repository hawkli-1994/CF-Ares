#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CF-Ares PyPI 发布脚本
此脚本用于构建和发布 CF-Ares 包到 PyPI
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# 颜色定义
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(message, color):
    """打印带颜色的消息"""
    print(f"{color}{message}{Colors.ENDC}")


def print_info(message):
    """打印信息消息"""
    print_colored(f"[INFO] {message}", Colors.BLUE)


def print_success(message):
    """打印成功消息"""
    print_colored(f"[SUCCESS] {message}", Colors.GREEN)


def print_warning(message):
    """打印警告消息"""
    print_colored(f"[WARNING] {message}", Colors.YELLOW)


def print_error(message):
    """打印错误消息"""
    print_colored(f"[ERROR] {message}", Colors.RED)


def run_command(command, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=True
        )
        return result.returncode == 0, result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {e}")
        return False, str(e)


def check_requirements():
    """检查必要的工具是否安装"""
    print_info("检查必要的工具...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print_error("Python 版本必须是 3.8 或更高")
        return False
    
    # 检查 build 包
    try:
        import build
    except ImportError:
        print_warning("未找到 build 包，正在安装...")
        success, _ = run_command("pip install build")
        if not success:
            print_error("安装 build 包失败")
            return False
    
    # 检查 twine 包
    try:
        import twine
    except ImportError:
        print_warning("未找到 twine 包，正在安装...")
        success, _ = run_command("pip install twine")
        if not success:
            print_error("安装 twine 包失败")
            return False
    
    print_success("所有必要的工具已就绪")
    return True


def run_tests(skip_tests=False):
    """运行测试"""
    if skip_tests:
        print_warning("跳过测试")
        return True
    
    print_info("运行测试...")
    
    # 检查 pytest 包
    try:
        import pytest
    except ImportError:
        print_warning("未找到 pytest 包，正在安装...")
        success, _ = run_command("pip install pytest")
        if not success:
            print_error("安装 pytest 包失败")
            return False
    
    # 运行测试
    success, output = run_command("pytest", check=False)
    if success:
        print_success("测试通过")
        return True
    else:
        print_error("测试失败")
        print(output)
        
        # 询问是否继续
        response = input("测试失败，是否继续? (y/n): ").lower()
        return response in ('y', 'yes')


def clean_build():
    """清理旧的构建文件"""
    print_info("清理旧的构建文件...")
    
    # 删除 build 目录
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # 删除 dist 目录
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # 删除 *.egg-info 目录
    for item in os.listdir("."):
        if item.endswith(".egg-info") and os.path.isdir(item):
            shutil.rmtree(item)
    
    print_success("清理完成")
    return True


def build_package():
    """构建包"""
    print_info("构建包...")
    
    success, output = run_command("python -m build")
    if not success:
        print_error("构建失败")
        print(output)
        return False
    
    print_success("构建完成")
    
    # 列出构建的包
    print_info("构建的包:")
    if os.path.exists("dist"):
        for item in os.listdir("dist"):
            print(f"  - {item}")
    
    return True


def publish_package(repository="pypi"):
    """发布到 PyPI 或 TestPyPI"""
    if repository == "test":
        print_info("发布到 TestPyPI...")
        cmd = "twine upload --repository testpypi dist/*"
    else:
        print_info("发布到 PyPI...")
        cmd = "twine upload dist/*"
    
    success, output = run_command(cmd)
    if not success:
        print_error("发布失败")
        print(output)
        return False
    
    print_success("发布完成!")
    return True


def confirm_action(message):
    """确认操作"""
    response = input(f"{message} (y/n): ").lower()
    return response in ('y', 'yes')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CF-Ares PyPI 发布脚本")
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    parser.add_argument("--test", action="store_true", help="发布到 TestPyPI 而不是 PyPI")
    parser.add_argument("--no-confirm", action="store_true", help="不需要确认即可发布")
    args = parser.parse_args()
    
    # 检查必要的工具
    if not check_requirements():
        return 1
    
    # 运行测试
    if not run_tests(args.skip_tests):
        return 1
    
    # 清理旧的构建文件
    if not clean_build():
        return 1
    
    # 构建包
    if not build_package():
        return 1
    
    # 确认发布
    repository = "test" if args.test else "pypi"
    if not args.no_confirm:
        message = f"是否要发布到 {'TestPyPI' if args.test else 'PyPI'}?"
        if not confirm_action(message):
            print_warning("取消发布")
            return 0
    
    # 发布包
    if not publish_package(repository):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 