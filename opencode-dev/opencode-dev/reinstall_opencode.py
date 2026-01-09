#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCode 重装工具 - Python 交互式版本
支持卸载、安装和自定义大模型配置
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class OpenCodeReinstaller:
    """OpenCode 重装工具"""

    def __init__(self):
        self.paths = {
            'opencode_config': Path.home() / '.config' / 'opencode',
            'opencode_auth': Path.home() / '.opencode',
            'claude_todos': Path.home() / '.claude' / 'todos',
            'claude_transcripts': Path.home() / '.claude' / 'transcripts',
            'project_config': Path.cwd() / '.opencode',
        }

    def print_header(self, text: str):
        """打印标题"""
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{text}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

    def print_success(self, text: str):
        """打印成功信息"""
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} {text}")

    def print_error(self, text: str):
        """打印错误信息"""
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {text}")

    def print_warning(self, text: str):
        """打印警告信息"""
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {text}")

    def print_info(self, text: str):
        """打印信息"""
        print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} {text}")

    def run_command(self, cmd: List[str], check: bool = True) -> Tuple[bool, str]:
        """运行命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True,
                check=check
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)
        except FileNotFoundError:
            return False, "Command not found"

    def check_bun(self) -> bool:
        """检查 bun 是否安装"""
        success, _ = self.run_command(['where', 'bun'])
        if not success:
            self.print_error("未找到 bun！请先安装 bun")
            self.print_info("安装方式：")
            print("  curl -fsSL https://bun.sh/install | bash")
            print("  或访问：https://bun.sh")
            return False
        self.print_success("bun 已安装")
        return True

    def check_opencode_installed(self) -> bool:
        """检查 OpenCode 是否已安装"""
        success, output = self.run_command(['where', 'opencode'])
        if success and 'opencode' in output.lower():
            success, version = self.run_command(['opencode', '--version'], check=False)
            if success:
                print(f"  版本: {version.strip()}")
            return True
        return False

    def uninstall(self) -> bool:
        """卸载 OpenCode"""
        self.print_header("卸载 OpenCode")

        # 确认卸载
        print(f"{Colors.WARNING}将删除以下内容：{Colors.ENDC}")
        print("1. opencode-ai 全局包")
        print(f"2. {self.paths['opencode_config']} 配置目录")
        print(f"3. {self.paths['opencode_auth']} 认证数据")
        print(f"4. {self.paths['claude_todos']} (Claude Code 兼容)")
        print(f"5. {self.paths['claude_transcripts']} (Claude Code 兼容)")
        print(f"6. {self.paths['project_config']} 项目配置")
        print()

        confirm = input("确认卸载？(输入 yes 继续): ")
        if confirm.lower() != 'yes':
            self.print_warning("已取消卸载")
            return False

        self.print_info("开始卸载...")

        # 1. 卸载 opencode-ai
        self.print_info("1. 卸载 opencode-ai...")
        success, _ = self.run_command(['bun', 'remove', '-g', 'opencode-ai'], check=False)
        if success:
            self.print_success("opencode-ai 已卸载")
        else:
            self.print_warning("opencode-ai 可能未安装或卸载失败")

        # 2. 删除配置文件
        self.print_info("2. 删除配置文件和认证数据...")

        for name, path in self.paths.items():
            if path.exists():
                try:
                    if path.is_dir():
                        import shutil
                        shutil.rmtree(path)
                        self.print_success(f"已删除: {name}")
                    else:
                        path.unlink()
                        self.print_success(f"已删除: {name}")
                except Exception as e:
                    self.print_error(f"删除失败 {name}: {e}")
            else:
                self.print_info(f"跳过（不存在）: {name}")

        # 3. 验证卸载
        self.print_info("验证卸载...")
        success, _ = self.run_command(['where', 'opencode'])
        if success:
            self.print_warning("opencode 仍在系统中")
            success, output = self.run_command(['where', 'opencode'])
            print(f"  路径: {output}")
            self.print_info("可能需要手动删除该文件")
        else:
            self.print_success("opencode 已完全移除")

        print()
        return True

    def install(self) -> bool:
        """安装 OpenCode"""
        self.print_header("安装 OpenCode")

        # 检查 bun
        if not self.check_bun():
            return False

        # 配置模型参数
        model_config = self.configure_models()
        if not model_config:
            self.print_warning("已取消安装")
            return False

        # Step 1: 安装 OpenCode
        self.print_info("Step 1: 安装 OpenCode...")
        print("  命令: bun install -g opencode-ai")
        print()

        success, output = self.run_command(['bun', 'install', '-g', 'opencode-ai'])
        if not success:
            self.print_error(f"OpenCode 安装失败: {output}")
            self.print_info("请检查网络连接或手动安装：https://opencode.ai/docs")
            return False
        self.print_success("OpenCode 安装成功")

        # Step 2: 安装 oh-my-opencode 插件
        self.print_info("Step 2: 安装 Oh My OpenCode 插件...")

        # 构建安装命令
        install_args = ['bunx', 'oh-my-opencode', 'install', '--no-tui']
        for key, value in model_config.items():
            if value:
                install_args.append(f"--{key}={value}")

        cmd_str = ' '.join(install_args)
        print(f"  命令: {cmd_str}")
        print()

        success, output = self.run_command(install_args)
        if not success:
            self.print_error(f"插件安装失败: {output}")
            self.print_info("请检查网络连接或重试")
            return False
        self.print_success("插件安装成功")

        # Step 3: 验证安装
        self.print_info("Step 3: 验证安装...")

        success, version = self.run_command(['opencode', '--version'], check=False)
        if success:
            print(f"  版本: {version.strip()}")
        else:
            self.print_warning("无法获取版本信息")

        # 检查插件配置
        config_file = self.paths['opencode_config'] / 'opencode.json'
        if config_file.exists():
            content = config_file.read_text()
            if 'oh-my-opencode' in content:
                self.print_success("oh-my-opencode 插件已注册")
            else:
                self.print_warning("插件配置可能有问题")
        else:
            self.print_error("找不到 opencode.json 配置文件")

        # Step 4: 配置认证提示
        self.print_info("Step 4: 配置认证")
        print()

        if model_config.get('claude') != 'no':
            print(f"{Colors.WARNING}配置 Claude (Anthropic){Colors.ENDC}")
            print("  运行: opencode auth login")
            print("  选择: Anthropic -> Claude Pro/Max")
            print()

            auth_now = input("现在配置 Claude 认证吗？(y/n): ")
            if auth_now.lower() == 'y':
                self.run_command(['opencode', 'auth', 'login'], check=False)
            else:
                self.print_info("稍后运行 opencode auth login 配置")

        return True

    def configure_models(self) -> Dict[str, str]:
        """配置大模型参数"""
        self.print_header("配置大模型参数")

        config = {}

        # Claude 配置
        print(f"{Colors.BOLD}Claude 配置{Colors.ENDC}")
        print("  1. 使用 Claude Pro/Max (标准模式)")
        print("  2. 使用 Claude Max20 (20倍加速模式)")
        print("  3. 不使用 Claude")
        print()

        claude_choice = input("选择 Claude 选项 (1/2/3，默认 1): ").strip()
        if claude_choice == '2':
            config['claude'] = 'max20'
            self.print_success("Claude: max20 模式")
        elif claude_choice == '3':
            config['claude'] = 'no'
            self.print_info("Claude: 不使用")
        else:
            config['claude'] = 'yes'
            self.print_success("Claude: 标准 Pro/Max 模式")

        print()

        # ChatGPT 配置
        print(f"{Colors.BOLD}ChatGPT 配置{Colors.ENDC}")
        chatgpt_choice = input("你有 ChatGPT 订阅吗？(y/n，默认 n): ").strip().lower()
        if chatgpt_choice == 'y':
            config['chatgpt'] = 'yes'
            self.print_success("ChatGPT: 有订阅")
        else:
            config['chatgpt'] = 'no'
            self.print_info("ChatGPT: 无订阅")

        print()

        # Gemini 配置
        print(f"{Colors.BOLD}Gemini 配置{Colors.ENDC}")
        gemini_choice = input("你想集成 Gemini 模型吗？(y/n，默认 n): ").strip().lower()
        if gemini_choice == 'y':
            config['gemini'] = 'yes'
            self.print_success("Gemini: 启用")
        else:
            config['gemini'] = 'no'
            self.print_info("Gemini: 禁用")

        print()
        print(f"{Colors.BOLD}配置摘要：{Colors.ENDC}")
        for key, value in config.items():
            print(f"  {key}: {value}")

        print()
        confirm = input("确认配置？(y/n，默认 y): ").strip().lower()
        if confirm == 'n':
            return {}

        return config

    def show_main_menu(self):
        """显示主菜单"""
        while True:
            self.print_header("OpenCode 重装工具")

            # 显示当前状态
            self.print_info("当前状态：")
            if self.check_opencode_installed():
                self.print_success("OpenCode 已安装")
            else:
                self.print_warning("OpenCode 未安装")

            print()
            print(f"{Colors.BOLD}主菜单：{Colors.ENDC}")
            print("  1. 卸载 OpenCode")
            print("  2. 安装 OpenCode")
            print("  3. 完全重装（卸载 + 安装）")
            print("  4. 检查安装状态")
            print("  0. 退出")
            print()

            choice = input(f"{Colors.BOLD}请选择操作 (0-4): {Colors.ENDC}").strip()

            if choice == '0':
                print()
                print(f"{Colors.OKGREEN}再见！{Colors.ENDC}")
                break
            elif choice == '1':
                self.uninstall()
                input("\n按回车键继续...")
            elif choice == '2':
                self.install()
                input("\n按回车键继续...")
            elif choice == '3':
                if self.uninstall():
                    input("\n按回车键继续安装...")
                    self.install()
                input("\n按回车键继续...")
            elif choice == '4':
                self.check_status()
                input("\n按回车键继续...")
            else:
                self.print_warning("无效选择，请重试")
                input("\n按回车键继续...")

    def check_status(self):
        """检查安装状态"""
        self.print_header("检查安装状态")

        print(f"{Colors.BOLD}OpenCode 安装状态：{Colors.ENDC}")
        if self.check_opencode_installed():
            self.print_success("OpenCode 已安装")
        else:
            self.print_error("OpenCode 未安装")

        print()
        print(f"{Colors.BOLD}配置文件状态：{Colors.ENDC}")
        for name, path in self.paths.items():
            if path.exists():
                self.print_success(f"✓ {name}: 存在")
            else:
                self.print_warning(f"✗ {name}: 不存在")

        print()
        print(f"{Colors.BOLD}Bun 版本：{Colors.ENDC}")
        success, version = self.run_command(['bun', '--version'])
        if success:
            print(f"  {version.strip()}")
        else:
            self.print_error("  未安装")


def main():
    """主函数"""
    try:
        reinstall_tool = OpenCodeReinstaller()
        reinstall_tool.show_main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}用户中断操作{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}发生错误：{e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
