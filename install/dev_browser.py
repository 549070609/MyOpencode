#!/usr/bin/env python3
"""
OpenCode Desktop Browser Dev Script
====================================

在浏览器中启动 OpenCode 桌面应用进行开发调试。
无需打包，无需等待 Rust 编译，快速迭代前端代码。

Usage:
    python dev_browser.py [options]

Options:
    --port PORT         指定开发服务器端口 (默认: 1420)
    --host HOST         指定开发服务器主机 (默认: localhost)
    --no-open           不自动打开浏览器
    --browser BROWSER   指定浏览器: chrome, firefox, edge, safari (默认: 系统默认)
    --check-deps        只检查依赖，不启动服务器
    --install           自动安装依赖
    --help              显示帮助信息

Examples:
    python dev_browser.py
    python dev_browser.py --port 3000
    python dev_browser.py --browser chrome
    python dev_browser.py --install --no-open
"""

import os
import sys
import time
import signal
import socket
import argparse
import subprocess
import webbrowser
import platform
from pathlib import Path
from typing import Optional, List

# 项目路径配置
SCRIPT_DIR = Path(__file__).parent.absolute()
# install 目录的父目录是 openCode 根目录
ROOT_DIR = SCRIPT_DIR.parent
# opencode-dev 项目目录
OPENCODE_DEV_DIR = ROOT_DIR / "opencode-dev" / "opencode-dev"
DESKTOP_DIR = OPENCODE_DEV_DIR / "packages" / "desktop"

# ANSI 颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """打印启动横幅"""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║{Colors.BOLD}         🚀 OpenCode Desktop - Browser Dev Mode 🌐          {Colors.ENDC}{Colors.CYAN}║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)


def print_status(message: str, status: str = "info"):
    """打印带状态的消息"""
    icons = {
        "info": f"{Colors.BLUE}ℹ{Colors.ENDC}",
        "success": f"{Colors.GREEN}✓{Colors.ENDC}",
        "warning": f"{Colors.YELLOW}⚠{Colors.ENDC}",
        "error": f"{Colors.RED}✗{Colors.ENDC}",
        "wait": f"{Colors.CYAN}⏳{Colors.ENDC}",
    }
    icon = icons.get(status, icons["info"])
    print(f" {icon} {message}")


def check_command_exists(command: str) -> bool:
    """检查命令是否存在"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["where", command],
                capture_output=True,
                shell=True
            )
        else:
            result = subprocess.run(
                ["which", command],
                capture_output=True
            )
        return result.returncode == 0
    except Exception:
        return False


def check_port_available(port: int, host: str = "localhost") -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except Exception:
        return True


def wait_for_server(port: int, host: str = "localhost", timeout: int = 60) -> bool:
    """等待服务器启动"""
    print_status(f"等待开发服务器在 http://{host}:{port} 上启动...", "wait")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    
    return False


def check_dependencies() -> dict:
    """检查所有必要依赖"""
    deps = {
        "bun": check_command_exists("bun"),
        "node_modules": (OPENCODE_DEV_DIR / "node_modules").exists(),
        "desktop_package": (DESKTOP_DIR / "package.json").exists(),
    }
    return deps


def install_dependencies():
    """安装项目依赖"""
    print_status("正在安装项目依赖...", "wait")
    
    result = subprocess.run(
        ["bun", "install"],
        cwd=OPENCODE_DEV_DIR,
        shell=platform.system() == "Windows"
    )
    
    if result.returncode == 0:
        print_status("依赖安装成功!", "success")
        return True
    else:
        print_status("依赖安装失败!", "error")
        return False


def open_browser(url: str, browser: Optional[str] = None):
    """打开浏览器"""
    print_status(f"正在打开浏览器: {url}", "info")
    
    try:
        if browser:
            browser_map = {
                "chrome": "google-chrome" if platform.system() != "Windows" else "chrome",
                "firefox": "firefox",
                "edge": "microsoft-edge" if platform.system() != "Windows" else "msedge",
                "safari": "safari",
            }
            browser_cmd = browser_map.get(browser.lower(), browser)
            
            if platform.system() == "Windows":
                # Windows 下使用 start 命令
                if browser.lower() == "chrome":
                    subprocess.Popen(["start", "chrome", url], shell=True)
                elif browser.lower() == "edge":
                    subprocess.Popen(["start", "msedge", url], shell=True)
                elif browser.lower() == "firefox":
                    subprocess.Popen(["start", "firefox", url], shell=True)
                else:
                    webbrowser.open(url)
            else:
                webbrowser.get(browser_cmd).open(url)
        else:
            webbrowser.open(url)
        
        print_status("浏览器已打开!", "success")
    except Exception as e:
        print_status(f"无法打开浏览器: {e}", "warning")
        print_status(f"请手动访问: {url}", "info")


def get_rust_target() -> str:
    """获取当前平台的 Rust target"""
    system = platform.system()
    machine = platform.machine().lower()
    
    if system == "Windows":
        if machine in ("amd64", "x86_64"):
            return "x86_64-pc-windows-msvc"
        elif machine in ("arm64", "aarch64"):
            return "aarch64-pc-windows-msvc"
        else:
            return "i686-pc-windows-msvc"
    elif system == "Darwin":
        if machine in ("arm64", "aarch64"):
            return "aarch64-apple-darwin"
        else:
            return "x86_64-apple-darwin"
    else:  # Linux
        if machine in ("arm64", "aarch64"):
            return "aarch64-unknown-linux-gnu"
        else:
            return "x86_64-unknown-linux-gnu"


def start_backend_server(port: int) -> Optional[subprocess.Popen]:
    """启动 OpenCode 后端服务器"""
    # 检查 opencode 命令是否存在
    if not check_command_exists("opencode"):
        print_status("OpenCode CLI 未安装，无法启动后端服务器", "warning")
        print_status("请先构建或安装 opencode CLI", "info")
        return None
    
    # 检查端口
    if not check_port_available(port, "127.0.0.1"):
        print_status(f"后端端口 {port} 已被占用，可能服务器已在运行", "info")
        return None
    
    print_status(f"正在启动 OpenCode 后端服务器 (端口: {port})...", "wait")
    
    try:
        process = subprocess.Popen(
            ["opencode", "serve", f"--port={port}", "--cors=http://localhost:1420"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=platform.system() == "Windows"
        )
        
        # 等待服务器启动
        time.sleep(2)
        if process.poll() is None:  # 进程还在运行
            if not check_port_available(port, "127.0.0.1"):
                print_status(f"后端服务器已启动在 http://127.0.0.1:{port}", "success")
                return process
        
        print_status("后端服务器启动失败", "error")
        return None
        
    except Exception as e:
        print_status(f"启动后端服务器失败: {e}", "error")
        return None


def run_dev_server(port: int, host: str, open_browser_flag: bool, browser: Optional[str],
                   with_server: bool = False, server_port: int = 59123):
    """运行开发服务器"""
    backend_process = None
    
    # 如果需要，启动后端服务器
    if with_server:
        backend_process = start_backend_server(server_port)
    
    # 检查端口
    if not check_port_available(port, host):
        print_status(f"端口 {port} 已被占用!", "warning")
        print_status(f"服务器可能已经在运行，尝试打开浏览器...", "info")
        if open_browser_flag:
            open_browser(f"http://{host}:{port}", browser)
        return
    
    # 设置环境变量
    env = os.environ.copy()
    env["VITE_DEV_MODE"] = "browser"
    env["RUST_TARGET"] = get_rust_target()
    
    print_status(f"RUST_TARGET: {env['RUST_TARGET']}", "info")
    
    # 构建命令 - 先运行 predev，再启动 vite
    print_status("正在启动 Vite 开发服务器...", "wait")
    
    # 在 Windows 上运行 predev
    predev_result = subprocess.run(
        ["bun", "run", "predev"],
        cwd=DESKTOP_DIR,
        env=env,
        shell=platform.system() == "Windows"
    )
    
    if predev_result.returncode != 0:
        print_status("predev 脚本执行失败!", "warning")
    
    # 启动 Vite 开发服务器
    try:
        process = subprocess.Popen(
            ["bun", "run", "dev"],
            cwd=DESKTOP_DIR,
            env=env,
            shell=platform.system() == "Windows"
        )
        
        # 等待服务器启动
        if wait_for_server(port, host if host != "0.0.0.0" else "localhost"):
            print_status(f"开发服务器已启动!", "success")
            
            display_host = "localhost" if host in ["0.0.0.0", "localhost"] else host
            url = f"http://{display_host}:{port}"
            
            print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║  🎉 开发服务器运行中!                                         ║
╠══════════════════════════════════════════════════════════════╣
║  本地地址:   {url:<46} ║
║                                                              ║
║  {Colors.YELLOW}按 Ctrl+C 停止服务器{Colors.GREEN}                                      ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
""")
            
            # 打开浏览器
            if open_browser_flag:
                time.sleep(1)  # 等待一下确保服务器完全就绪
                open_browser(url, browser)
            
            # 等待进程结束
            process.wait()
        else:
            print_status("服务器启动超时!", "error")
            process.terminate()
    
    except KeyboardInterrupt:
        print_status("\n正在停止开发服务器...", "info")
        if 'process' in locals():
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        if backend_process:
            print_status("正在停止后端服务器...", "info")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
        print_status("开发服务器已停止", "success")
    
    except Exception as e:
        print_status(f"启动失败: {e}", "error")
        if backend_process:
            backend_process.terminate()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="在浏览器中启动 OpenCode 桌面应用进行开发调试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python dev_browser.py
    python dev_browser.py --port 3000
    python dev_browser.py --browser chrome
    python dev_browser.py --install
"""
    )
    
    parser.add_argument("--port", type=int, default=1420,
                        help="指定开发服务器端口 (默认: 1420)")
    parser.add_argument("--host", type=str, default="localhost",
                        help="指定开发服务器主机 (默认: localhost)")
    parser.add_argument("--no-open", action="store_true",
                        help="不自动打开浏览器")
    parser.add_argument("--browser", type=str, default=None,
                        choices=["chrome", "firefox", "edge", "safari"],
                        help="指定浏览器")
    parser.add_argument("--check-deps", action="store_true",
                        help="只检查依赖")
    parser.add_argument("--install", action="store_true",
                        help="自动安装依赖")
    parser.add_argument("--with-server", action="store_true",
                        help="同时启动 OpenCode 后端服务器")
    parser.add_argument("--server-port", type=int, default=59123,
                        help="后端服务器端口 (默认: 59123)")
    
    args = parser.parse_args()
    
    # 切换到项目目录
    os.chdir(OPENCODE_DEV_DIR)
    
    # 打印横幅
    print_banner()
    
    # 检查依赖
    print_status("正在检查依赖...", "wait")
    deps = check_dependencies()
    
    all_ok = True
    
    if deps["bun"]:
        print_status("Bun 运行时: 已安装", "success")
    else:
        print_status("Bun 运行时: 未安装", "error")
        print_status("请先安装 Bun: https://bun.sh", "info")
        all_ok = False
    
    if deps["node_modules"]:
        print_status("Node 模块: 已安装", "success")
    else:
        print_status("Node 模块: 未安装", "warning")
        if args.install:
            if not install_dependencies():
                all_ok = False
        else:
            print_status("运行 'python dev_browser.py --install' 安装依赖", "info")
            all_ok = False
    
    if deps["desktop_package"]:
        print_status("Desktop 包: 已找到", "success")
    else:
        print_status("Desktop 包: 未找到", "error")
        all_ok = False
    
    # 如果只是检查依赖，到此结束
    if args.check_deps:
        if all_ok:
            print_status("\n所有依赖检查通过!", "success")
        else:
            print_status("\n部分依赖缺失!", "error")
        sys.exit(0 if all_ok else 1)
    
    # 检查依赖是否满足
    if not all_ok:
        print_status("\n请先解决上述依赖问题!", "error")
        sys.exit(1)
    
    print()
    
    # 启动开发服务器
    run_dev_server(
        port=args.port,
        host=args.host,
        open_browser_flag=not args.no_open,
        browser=args.browser,
        with_server=args.with_server,
        server_port=args.server_port
    )


if __name__ == "__main__":
    main()

