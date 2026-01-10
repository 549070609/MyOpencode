#!/usr/bin/env python3
"""
OpenCode 打包工具
=================

打包 opencode-dev 项目的工具。
默认打包桌面应用，并执行清理后重新构建。

Usage:
    python build_packages.py [options]

Options:
    --desktop               构建桌面应用 (默认开启)
    --no-desktop            不构建桌面应用
    --bundle-type TYPE      桌面应用打包类型: nsis, msi, dmg, deb, rpm, appimage
    --clean                 清理构建产物后再构建 (默认，仅清理 dist 目录)
    --no-clean              不清理构建产物 (增量构建)
    --deep-clean            深度清理 (包括 node_modules 和 Rust target)
    --output DIR            输出目录 (默认: ./dist)
    --release               发布模式 (默认)
    --debug                 调试模式
    --skip-install          跳过依赖安装
    --version VERSION       设置版本号
    --help                  显示帮助信息

Examples:
    # 打包项目 (默认包含桌面应用，清理 dist 后构建)
    python build_packages.py

    # 打包指定桌面应用打包类型
    python build_packages.py --bundle-type nsis

    # 不清理，增量构建 (最快)
    python build_packages.py --no-clean

    # 深度清理后构建 (删除 node_modules，适合解决依赖问题)
    python build_packages.py --deep-clean

    # 设置自定义输出目录
    python build_packages.py --output ./my-dist
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
import platform
import time
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# =============================================================================
# 配置
# =============================================================================

class BuildMode(Enum):
    RELEASE = "release"
    DEBUG = "debug"


@dataclass
class BuildConfig:
    """构建配置"""
    build_desktop: bool = True
    bundle_type: Optional[str] = None
    clean: bool = True
    deep_clean: bool = False
    output_dir: Path = None
    mode: BuildMode = BuildMode.RELEASE
    skip_install: bool = False
    version: Optional[str] = None


@dataclass
class BuildResult:
    """构建结果"""
    project: str
    success: bool
    duration: float
    output_files: List[Path]
    error: Optional[str] = None


# =============================================================================
# 路径配置
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.absolute()
# install 目录的父目录是 openCode 根目录
ROOT_DIR = SCRIPT_DIR.parent
# opencode-dev 项目目录
OPENCODE_DEV_DIR = ROOT_DIR / "opencode-dev" / "opencode-dev"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "opencode-dev" / "dist"


# =============================================================================
# 工具函数
# =============================================================================

class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def disable(cls):
        """禁用颜色 (Windows 旧版终端)"""
        cls.HEADER = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.RED = ''
        cls.ENDC = ''
        cls.BOLD = ''
        cls.UNDERLINE = ''


# Windows 颜色支持
if platform.system() == "Windows":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()


def print_header(text: str):
    """打印标题"""
    width = 64
    print(f"\n{Colors.CYAN}╔{'═' * width}╗{Colors.ENDC}")
    print(f"{Colors.CYAN}║{Colors.BOLD} {text.center(width - 2)} {Colors.ENDC}{Colors.CYAN}║{Colors.ENDC}")
    print(f"{Colors.CYAN}╚{'═' * width}╝{Colors.ENDC}\n")


def print_section(text: str):
    """打印章节"""
    print(f"\n{Colors.BLUE}▶ {text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'─' * 50}{Colors.ENDC}")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    """打印信息"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    capture_output: bool = False
) -> Tuple[int, Optional[str], Optional[str]]:
    """
    运行命令
    
    Returns:
        (return_code, stdout, stderr)
    """
    print(f"   {Colors.YELLOW}$ {' '.join(cmd)}{Colors.ENDC}")
    
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    
    # Windows 需要 shell=True
    use_shell = platform.system() == "Windows"
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd, cwd=cwd, env=merged_env, shell=use_shell,
                capture_output=True, text=True
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, cwd=cwd, env=merged_env, shell=use_shell)
            return result.returncode, None, None
    except Exception as e:
        return -1, None, str(e)


def check_bun_installed() -> bool:
    """检查 bun 是否安装"""
    try:
        result = subprocess.run(
            ["bun", "--version"],
            capture_output=True,
            shell=platform.system() == "Windows"
        )
        return result.returncode == 0
    except:
        return False


def format_duration(seconds: float) -> str:
    """格式化时长"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


# =============================================================================
# 清理函数
# =============================================================================

def clean_opencode(deep: bool = False):
    """
    清理 opencode-dev 构建产物
    
    Args:
        deep: 如果为 True，也删除 node_modules 和 Rust target（完全清理）
    """
    print_section("清理 opencode-dev")
    
    # 清理各个包的 dist 目录
    packages_dir = OPENCODE_DEV_DIR / "packages"
    if packages_dir.exists():
        for package in packages_dir.iterdir():
            if package.is_dir():
                dist = package / "dist"
                if dist.exists():
                    print(f"   删除 {dist}")
                    shutil.rmtree(dist, ignore_errors=True)
    
    # 深度清理
    if deep:
        # 清理 node_modules
        node_modules = OPENCODE_DEV_DIR / "node_modules"
        if node_modules.exists():
            print(f"   删除 {node_modules}")
            shutil.rmtree(node_modules, ignore_errors=True)
        
        # 清理各个包的 node_modules
        if packages_dir.exists():
            for package in packages_dir.iterdir():
                if package.is_dir():
                    pkg_node_modules = package / "node_modules"
                    if pkg_node_modules.exists():
                        print(f"   删除 {pkg_node_modules}")
                        shutil.rmtree(pkg_node_modules, ignore_errors=True)
        
        # 清理 Tauri 构建
        tauri_target = OPENCODE_DEV_DIR / "packages" / "desktop" / "src-tauri" / "target"
        if tauri_target.exists():
            print(f"   删除 {tauri_target}")
            shutil.rmtree(tauri_target, ignore_errors=True)
    
    print_success("opencode-dev 清理完成")


def clean_output(output_dir: Path):
    """清理输出目录"""
    print_section("清理输出目录")
    
    if output_dir.exists():
        print(f"   删除 {output_dir}")
        shutil.rmtree(output_dir, ignore_errors=True)
    
    print_success("输出目录清理完成")


# =============================================================================
# 构建函数
# =============================================================================

def install_dependencies_opencode() -> bool:
    """安装 opencode-dev 依赖"""
    print("   安装依赖...")
    code, _, stderr = run_command(["bun", "install"], cwd=OPENCODE_DEV_DIR)
    return code == 0


def build_opencode(config: BuildConfig) -> BuildResult:
    """构建 opencode-dev"""
    start_time = time.time()
    output_files = []
    
    print_section("构建 opencode-dev")
    
    # 检查目录
    if not OPENCODE_DEV_DIR.exists():
        return BuildResult(
            project="opencode-dev",
            success=False,
            duration=time.time() - start_time,
            output_files=[],
            error=f"目录不存在: {OPENCODE_DEV_DIR}"
        )
    
    # 安装依赖
    if not config.skip_install:
        if not install_dependencies_opencode():
            return BuildResult(
                project="opencode-dev",
                success=False,
                duration=time.time() - start_time,
                output_files=[],
                error="依赖安装失败"
            )
    
    # 类型检查
    print("   执行类型检查...")
    code, _, stderr = run_command(["bun", "run", "typecheck"], cwd=OPENCODE_DEV_DIR)
    if code != 0:
        print_warning("类型检查有警告，继续构建...")
    
    # 构建各个包
    packages_to_build = [
        "packages/util",
        "packages/sdk",
        "packages/plugin",
        "packages/opencode",
        "packages/app",
    ]
    
    for pkg in packages_to_build:
        pkg_dir = OPENCODE_DEV_DIR / pkg
        if pkg_dir.exists():
            pkg_json = pkg_dir / "package.json"
            if pkg_json.exists():
                with open(pkg_json, "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                if "build" in pkg_data.get("scripts", {}):
                    print(f"   构建 {pkg}...")
                    code, _, _ = run_command(
                        ["bun", "run", "build"],
                        cwd=pkg_dir
                    )
                    if code != 0:
                        print_warning(f"{pkg} 构建失败，继续...")
    
    # 收集输出文件
    for pkg in packages_to_build:
        dist = OPENCODE_DEV_DIR / pkg / "dist"
        if dist.exists():
            output_files.append(dist)
    
    # 复制到输出目录
    if config.output_dir:
        dest_dir = config.output_dir / "opencode-dev"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for pkg in packages_to_build:
            dist = OPENCODE_DEV_DIR / pkg / "dist"
            if dist.exists():
                pkg_name = Path(pkg).name
                shutil.copytree(dist, dest_dir / pkg_name / "dist", dirs_exist_ok=True)
    
    return BuildResult(
        project="opencode-dev",
        success=True,
        duration=time.time() - start_time,
        output_files=output_files
    )


def build_desktop(config: BuildConfig) -> BuildResult:
    """构建桌面应用"""
    start_time = time.time()
    output_files = []
    
    print_section("构建桌面应用")
    
    desktop_dir = OPENCODE_DEV_DIR / "packages" / "desktop"
    
    if not desktop_dir.exists():
        return BuildResult(
            project="desktop",
            success=False,
            duration=time.time() - start_time,
            output_files=[],
            error=f"目录不存在: {desktop_dir}"
        )
    
    # 使用现有的 build_desktop.py 脚本
    build_script = SCRIPT_DIR / "build_desktop.py"
    
    if build_script.exists():
        cmd = [sys.executable, str(build_script)]
        
        if config.mode == BuildMode.DEBUG:
            cmd.append("--debug")
        
        if config.bundle_type:
            cmd.extend(["--bundle-type", config.bundle_type])
        
        code, _, stderr = run_command(cmd, cwd=SCRIPT_DIR)
        
        if code != 0:
            return BuildResult(
                project="desktop",
                success=False,
                duration=time.time() - start_time,
                output_files=[],
                error=stderr or "桌面应用构建失败"
            )
    else:
        # 直接运行 Tauri 构建
        cmd = ["bun", "run", "tauri", "build"]
        
        if config.mode == BuildMode.DEBUG:
            cmd.append("--debug")
        
        if config.bundle_type:
            cmd.extend(["--bundles", config.bundle_type])
        
        # 添加 cargo 路径 (Windows)
        env = {}
        if platform.system() == "Windows":
            cargo_bin = Path.home() / ".cargo" / "bin"
            env["PATH"] = f"{cargo_bin};{os.environ.get('PATH', '')}"
        
        code, _, stderr = run_command(cmd, cwd=desktop_dir, env=env)
        
        if code != 0:
            return BuildResult(
                project="desktop",
                success=False,
                duration=time.time() - start_time,
                output_files=[],
                error=stderr or "桌面应用构建失败"
            )
    
    # 收集输出文件
    tauri_dir = desktop_dir / "src-tauri"
    
    if config.mode == BuildMode.RELEASE:
        bundle_dir = tauri_dir / "target" / "release" / "bundle"
    else:
        bundle_dir = tauri_dir / "target" / "debug" / "bundle"
    
    if bundle_dir.exists():
        for item in bundle_dir.iterdir():
            if item.is_dir():
                for f in item.iterdir():
                    output_files.append(f)
            else:
                output_files.append(item)
    
    # 复制到输出目录
    if config.output_dir and bundle_dir.exists():
        dest_dir = config.output_dir / "desktop"
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(bundle_dir, dest_dir / "bundle", dirs_exist_ok=True)
    
    return BuildResult(
        project="desktop",
        success=True,
        duration=time.time() - start_time,
        output_files=output_files
    )


# =============================================================================
# 主构建流程
# =============================================================================

def run_build(config: BuildConfig) -> List[BuildResult]:
    """执行构建"""
    results = []
    
    # 打印构建信息
    print_header("OpenCode 打包工具")
    
    clean_status = "深度清理" if config.deep_clean else ("清理 dist" if config.clean else "不清理")
    print(f"""
{Colors.CYAN}构建配置:{Colors.ENDC}
   • 桌面应用:        {'✓' if config.build_desktop else '✗'}
   • 构建模式:        {config.mode.value}
   • 清理模式:        {clean_status}
   • 输出目录:        {config.output_dir}
   • 版本号:          {config.version or '(默认)'}
""")
    
    # 检查环境
    print_section("环境检查")
    
    if not check_bun_installed():
        print_error("未检测到 bun，请先安装: https://bun.sh")
        return results
    
    print_success(f"bun 已安装")
    
    # 清理
    if config.clean:
        print_section("清理构建产物")
        clean_opencode(deep=config.deep_clean)
        if config.output_dir:
            clean_output(config.output_dir)
    
    # 创建输出目录
    if config.output_dir:
        config.output_dir.mkdir(parents=True, exist_ok=True)
    
    # 构建 opencode-dev
    result = build_opencode(config)
    results.append(result)
    
    if not result.success:
        print_error(f"opencode-dev 构建失败: {result.error}")
    
    # 构建桌面应用
    if config.build_desktop:
        result = build_desktop(config)
        results.append(result)
        
        if not result.success:
            print_error(f"桌面应用构建失败: {result.error}")
    
    return results


def print_summary(results: List[BuildResult], config: BuildConfig):
    """打印构建摘要"""
    print_header("构建摘要")
    
    total_duration = sum(r.duration for r in results)
    success_count = sum(1 for r in results if r.success)
    
    for result in results:
        status = f"{Colors.GREEN}成功{Colors.ENDC}" if result.success else f"{Colors.RED}失败{Colors.ENDC}"
        print(f"   • {result.project}: {status} ({format_duration(result.duration)})")
        
        if result.output_files:
            for f in result.output_files[:5]:
                print(f"      📦 {f.name}")
            if len(result.output_files) > 5:
                print(f"      ... 还有 {len(result.output_files) - 5} 个文件")
        
        if result.error:
            print(f"      {Colors.RED}错误: {result.error}{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}总计: {success_count}/{len(results)} 成功, 总耗时: {format_duration(total_duration)}{Colors.ENDC}")
    
    if config.output_dir and config.output_dir.exists():
        print(f"\n{Colors.GREEN}📂 输出目录: {config.output_dir}{Colors.ENDC}")
    
    # 生成构建报告
    if config.output_dir:
        report_path = config.output_dir / "build-report.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": config.version,
            "mode": config.mode.value,
            "results": [
                {
                    "project": r.project,
                    "success": r.success,
                    "duration": r.duration,
                    "output_files": [str(f) for f in r.output_files],
                    "error": r.error
                }
                for r in results
            ],
            "total_duration": total_duration
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.CYAN}📋 构建报告: {report_path}{Colors.ENDC}")


# =============================================================================
# 入口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="OpenCode 打包工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # 构建选项
    build_group = parser.add_argument_group("构建选项")
    build_group.add_argument("--desktop", action="store_true", default=True,
                             help="构建桌面应用 (默认)")
    build_group.add_argument("--no-desktop", action="store_true",
                             help="不构建桌面应用")
    build_group.add_argument("--bundle-type", type=str, default=None,
                             choices=["nsis", "msi", "app", "dmg", "deb", "rpm", "appimage"],
                             help="桌面应用打包类型")
    build_group.add_argument("--clean", action="store_true", default=True,
                             help="清理构建产物后再构建 (默认，仅清理 dist)")
    build_group.add_argument("--no-clean", action="store_true",
                             help="不清理构建产物")
    build_group.add_argument("--deep-clean", action="store_true",
                             help="深度清理 (包括 node_modules 和 Rust target)")
    build_group.add_argument("--output", "-o", type=str, default=None,
                             help="输出目录 (默认: ./dist)")
    build_group.add_argument("--release", action="store_true", default=True,
                             help="发布模式 (默认)")
    build_group.add_argument("--debug", action="store_true",
                             help="调试模式")
    build_group.add_argument("--skip-install", action="store_true",
                             help="跳过依赖安装")
    build_group.add_argument("--version", "-v", type=str, default=None,
                             help="设置版本号")
    
    args = parser.parse_args()
    
    # 构建配置
    config = BuildConfig(
        build_desktop=not args.no_desktop,
        bundle_type=args.bundle_type,
        clean=not args.no_clean,
        deep_clean=args.deep_clean,
        output_dir=Path(args.output) if args.output else DEFAULT_OUTPUT_DIR,
        mode=BuildMode.DEBUG if args.debug else BuildMode.RELEASE,
        skip_install=args.skip_install,
        version=args.version
    )
    
    # 执行构建
    try:
        results = run_build(config)
        
        if results:
            print_summary(results, config)
            
            # 退出码
            if all(r.success for r in results):
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print_error("没有执行任何构建")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  构建已取消")
        sys.exit(130)
    except Exception as e:
        print_error(f"构建出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

