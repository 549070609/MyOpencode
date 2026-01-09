"""
主卸载器

协调所有组件执行 opencode 彻底删除。
"""

import os
from typing import Optional, Callable

try:
    from .models import UninstallReport
    from .platform_detector import PlatformDetector
    from .executable_detector import ExecutableDetector
    from .package_manager import PackageManagerUninstaller
    from .directory_cleaner import DirectoryCleaner
    from .project_scanner import ProjectScanner
except ImportError:
    from models import UninstallReport
    from platform_detector import PlatformDetector
    from executable_detector import ExecutableDetector
    from package_manager import PackageManagerUninstaller
    from directory_cleaner import DirectoryCleaner
    from project_scanner import ProjectScanner


class OpenCodeUninstaller:
    """OpenCode 卸载器"""
    
    def __init__(self, dry_run: bool = False, 
                 input_func: Optional[Callable[[str], str]] = None,
                 print_func: Optional[Callable[[str], None]] = None):
        """
        初始化卸载器
        
        Args:
            dry_run: 如果为 True，只预览不实际删除
            input_func: 自定义输入函数（用于测试）
            print_func: 自定义打印函数（用于测试）
        """
        self.dry_run = dry_run
        self._input = input_func or input
        self._print = print_func or print
        
        # 初始化组件
        self.platform = PlatformDetector()
        self.executable_detector = ExecutableDetector(self.platform)
        self.package_manager = PackageManagerUninstaller()
        self.directory_cleaner = DirectoryCleaner(dry_run=dry_run)
        self.project_scanner = ProjectScanner()
        
        # 报告
        self.report = UninstallReport(dry_run=dry_run)
    
    def run(self) -> UninstallReport:
        """
        执行卸载流程
        
        Returns:
            卸载报告
        """
        # 1. 显示警告并确认
        if not self._show_warning_and_confirm():
            self._print('\n已取消卸载操作。')
            return self.report
        
        # 2. 检测并删除可执行文件
        self._process_executables()
        
        # 3. 通过包管理器卸载
        self._process_package_managers()
        
        # 4. 处理配置目录
        self._process_config_directories()
        
        # 5. 处理缓存和数据目录
        self._process_cache_directories()
        self._process_data_directories()
        
        # 6. 询问是否扫描项目目录
        self._process_project_directories()
        
        # 7. 显示报告
        self.report.display()
        
        return self.report
    
    def _show_warning_and_confirm(self) -> bool:
        """显示警告并获取用户确认"""
        self._print('=' * 50)
        self._print('OpenCode 彻底删除工具')
        self._print('=' * 50)
        
        if self.dry_run:
            self._print('\n⚠ 预览模式 - 不会实际删除任何文件')
        
        self._print('\n此操作将删除:')
        self._print('  - opencode 可执行文件')
        self._print('  - 通过包管理器安装的 opencode')
        self._print('  - opencode 配置目录')
        self._print('  - opencode 缓存和数据目录')
        self._print('  - 项目中的 .opencode 目录（可选）')
        
        self._print('\n' + '=' * 50)
        
        return self.confirm_with_user('确定要继续吗？(y/n): ')
    
    def confirm_with_user(self, message: str) -> bool:
        """
        获取用户确认
        
        Args:
            message: 提示消息
            
        Returns:
            用户是否确认
        """
        try:
            response = self._input(message).strip().lower()
            return response in ('y', 'yes', '是', '确定')
        except (EOFError, KeyboardInterrupt):
            return False
    
    def prompt_for_input(self, message: str) -> str:
        """
        获取用户输入
        
        Args:
            message: 提示消息
            
        Returns:
            用户输入
        """
        try:
            return self._input(message).strip()
        except (EOFError, KeyboardInterrupt):
            return ''
    
    def _process_executables(self) -> None:
        """处理可执行文件"""
        self._print('\n【检测可执行文件】')
        
        executables = self.executable_detector.find_executables()
        
        if not executables:
            self._print('  未找到 opencode 可执行文件')
            return
        
        self._print(f'  找到 {len(executables)} 个可执行文件/目录')
        
        for path in executables:
            if self.dry_run:
                self._print(f'  [预览] 将删除: {path}')
                self.report.executables_removed.append(path)
            else:
                result = self.directory_cleaner.remove_file(path)
                if result.success:
                    self._print(f'  ✓ 已删除: {path}')
                    self.report.executables_removed.append(path)
                else:
                    self._print(f'  ✗ 删除失败: {path} ({result.error})')
                    self.report.executables_failed.append((path, result.error or '未知错误'))
    
    def _process_package_managers(self) -> None:
        """处理包管理器卸载"""
        self._print('\n【包管理器卸载】')
        
        if self.dry_run:
            self._print('  [预览] 将尝试通过以下包管理器卸载:')
            for manager in self.package_manager.get_supported_managers():
                if self.package_manager.is_manager_available(manager):
                    self._print(f'    - {manager}')
                    self.report.package_managers_success.append(manager)
                else:
                    self.report.package_managers_skipped.append(manager)
            return
        
        results, skipped = self.package_manager.uninstall_all()
        
        for result in results:
            if result.success:
                self._print(f'  ✓ {result.target}: {result.message}')
                manager = result.target.split(':')[0]
                if manager not in self.report.package_managers_success:
                    self.report.package_managers_success.append(manager)
            else:
                self._print(f'  ✗ {result.target}: {result.message}')
                self.report.package_managers_failed.append((result.target, result.error or '未知错误'))
        
        self.report.package_managers_skipped = skipped
    
    def _process_config_directories(self) -> None:
        """处理配置目录"""
        self._print('\n【配置目录】')
        
        config_dirs = self.platform.get_config_directories()
        existing_dirs = self.directory_cleaner.find_directories(config_dirs)
        
        if not existing_dirs:
            self._print('  未找到配置目录')
            return
        
        self._print(f'  找到 {len(existing_dirs)} 个配置目录:')
        for d in existing_dirs:
            self._print(f'    - {d}')
        
        if not self.confirm_with_user('\n  是否删除这些配置目录？(y/n): '):
            self._print('  已跳过配置目录删除')
            self.report.config_dirs_skipped = existing_dirs
            return
        
        for path in existing_dirs:
            if self.dry_run:
                self._print(f'  [预览] 将删除: {path}')
                self.report.config_dirs_removed.append(path)
            else:
                result = self.directory_cleaner.remove_directory(path)
                if result.success:
                    self._print(f'  ✓ 已删除: {path}')
                    self.report.config_dirs_removed.append(path)
                else:
                    self._print(f'  ✗ 删除失败: {path} ({result.error})')
                    self.report.config_dirs_failed.append((path, result.error or '未知错误'))
    
    def _process_cache_directories(self) -> None:
        """处理缓存目录"""
        self._print('\n【缓存目录】')
        
        cache_dirs = self.platform.get_cache_directories()
        existing_dirs = self.directory_cleaner.find_directories(cache_dirs)
        
        if not existing_dirs:
            self._print('  未找到缓存目录')
            return
        
        for path in existing_dirs:
            if self.dry_run:
                self._print(f'  [预览] 将删除: {path}')
                self.report.cache_dirs_removed.append(path)
            else:
                result = self.directory_cleaner.remove_directory(path)
                if result.success:
                    self._print(f'  ✓ 已删除: {path}')
                    self.report.cache_dirs_removed.append(path)
                else:
                    self._print(f'  ✗ 删除失败: {path} ({result.error})')
                    self.report.cache_dirs_failed.append((path, result.error or '未知错误'))
    
    def _process_data_directories(self) -> None:
        """处理数据目录"""
        self._print('\n【数据目录】')
        
        data_dirs = self.platform.get_data_directories()
        existing_dirs = self.directory_cleaner.find_directories(data_dirs)
        
        if not existing_dirs:
            self._print('  未找到数据目录')
            return
        
        for path in existing_dirs:
            if self.dry_run:
                self._print(f'  [预览] 将删除: {path}')
                self.report.data_dirs_removed.append(path)
            else:
                result = self.directory_cleaner.remove_directory(path)
                if result.success:
                    self._print(f'  ✓ 已删除: {path}')
                    self.report.data_dirs_removed.append(path)
                else:
                    self._print(f'  ✗ 删除失败: {path} ({result.error})')
                    self.report.data_dirs_failed.append((path, result.error or '未知错误'))
    
    def _process_project_directories(self) -> None:
        """处理项目目录"""
        self._print('\n【项目 .opencode 目录】')
        
        if not self.confirm_with_user('  是否扫描项目中的 .opencode 目录？(y/n): '):
            self._print('  已跳过项目目录扫描')
            self.report.project_dirs_skipped = True
            return
        
        root_path = self.prompt_for_input('  请输入要扫描的根目录路径: ')
        
        if not root_path:
            self._print('  未输入路径，跳过扫描')
            self.report.project_dirs_skipped = True
            return
        
        root_path = os.path.expanduser(root_path)
        
        if not os.path.exists(root_path):
            self._print(f'  路径不存在: {root_path}')
            self.report.project_dirs_skipped = True
            return
        
        self._print(f'  正在扫描: {root_path}')
        project_dirs = self.project_scanner.scan(root_path)
        
        if not project_dirs:
            self._print('  未找到 .opencode 目录')
            return
        
        self._print(f'  找到 {len(project_dirs)} 个 .opencode 目录:')
        for d in project_dirs:
            self._print(f'    - {d}')
        
        if not self.confirm_with_user('\n  是否删除这些目录？(y/n): '):
            self._print('  已跳过项目目录删除')
            return
        
        for path in project_dirs:
            if self.dry_run:
                self._print(f'  [预览] 将删除: {path}')
                self.report.project_dirs_removed.append(path)
            else:
                result = self.directory_cleaner.remove_directory(path)
                if result.success:
                    self._print(f'  ✓ 已删除: {path}')
                    self.report.project_dirs_removed.append(path)
                else:
                    self._print(f'  ✗ 删除失败: {path} ({result.error})')
                    self.report.project_dirs_failed.append((path, result.error or '未知错误'))


def main():
    """主入口函数"""
    import sys
    
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    uninstaller = OpenCodeUninstaller(dry_run=dry_run)
    report = uninstaller.run()
    
    # 返回退出码
    sys.exit(0 if report.is_complete else 1)


if __name__ == '__main__':
    main()
