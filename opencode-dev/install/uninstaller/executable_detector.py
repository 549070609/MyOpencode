"""
可执行文件检测器

检测系统中的 opencode 可执行文件。
"""

import os
import subprocess
from typing import List, Set

try:
    from .platform_detector import PlatformDetector
except ImportError:
    from platform_detector import PlatformDetector


class ExecutableDetector:
    """检测 opencode 可执行文件"""
    
    # opencode 相关的可执行文件名
    EXECUTABLE_NAMES = ['opencode', 'opencode-ai', 'oh-my-opencode']
    
    def __init__(self, platform_detector: PlatformDetector = None):
        self.platform = platform_detector or PlatformDetector()
    
    def find_executables(self) -> List[str]:
        """查找所有 opencode 可执行文件路径"""
        found: Set[str] = set()
        
        # 1. 通过系统 PATH 查找
        found.update(self.find_in_path())
        
        # 2. 在包管理器目录中查找
        found.update(self.find_in_package_manager_dirs())
        
        # 3. 在 bun 全局目录中查找
        found.update(self.find_in_bun_dir())
        
        # 返回排序后的列表
        return sorted(list(found))
    
    def find_in_path(self) -> List[str]:
        """通过系统 PATH 查找 opencode 可执行文件"""
        found: Set[str] = set()
        
        for name in self.EXECUTABLE_NAMES:
            paths = self._find_command_in_path(name)
            found.update(paths)
        
        return list(found)
    
    def find_in_package_manager_dirs(self) -> List[str]:
        """在包管理器目录中查找 opencode 可执行文件"""
        found: Set[str] = set()
        extensions = self.platform.get_executable_extensions()
        pm_dirs = self.platform.get_package_manager_directories()
        
        for pm_dir in pm_dirs:
            if not os.path.exists(pm_dir):
                continue
            
            for name in self.EXECUTABLE_NAMES:
                for ext in extensions:
                    file_path = os.path.join(pm_dir, name + ext)
                    if os.path.isfile(file_path):
                        found.add(os.path.normpath(file_path))
        
        return list(found)
    
    def find_in_bun_dir(self) -> List[str]:
        """在 bun 全局目录中查找 opencode 相关文件"""
        found: Set[str] = set()
        home_dir = self.platform.get_home_dir()
        bun_dir = os.path.join(home_dir, '.bun')
        
        if not os.path.exists(bun_dir):
            return []
        
        # 检查 bin 目录
        bun_bin = os.path.join(bun_dir, 'bin')
        if os.path.exists(bun_bin):
            found.update(self._find_opencode_files_in_dir(bun_bin))
        
        # 检查全局 node_modules
        global_modules = os.path.join(bun_dir, 'install', 'global', 'node_modules')
        if os.path.exists(global_modules):
            for name in self.EXECUTABLE_NAMES:
                pkg_dir = os.path.join(global_modules, name)
                if os.path.exists(pkg_dir):
                    # 添加包目录（用于后续删除）
                    found.add(os.path.normpath(pkg_dir))
        
        return list(found)
    
    def _find_command_in_path(self, command: str) -> List[str]:
        """使用系统命令查找可执行文件路径"""
        found: List[str] = []
        
        if self.platform.get_platform() == PlatformDetector.PLATFORM_WINDOWS:
            # Windows 使用 where 命令
            try:
                result = subprocess.run(
                    ['where', command],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                if result.returncode == 0 and result.stdout.strip():
                    paths = result.stdout.strip().split('\n')
                    for path in paths:
                        path = path.strip()
                        if path and os.path.exists(path):
                            found.append(os.path.normpath(path))
            except (FileNotFoundError, subprocess.SubprocessError):
                pass
        else:
            # Unix 使用 which 命令
            try:
                result = subprocess.run(
                    ['which', '-a', command],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                if result.returncode == 0 and result.stdout.strip():
                    paths = result.stdout.strip().split('\n')
                    for path in paths:
                        path = path.strip()
                        if path and os.path.exists(path):
                            found.append(os.path.normpath(path))
            except (FileNotFoundError, subprocess.SubprocessError):
                pass
        
        return found
    
    def _find_opencode_files_in_dir(self, directory: str) -> List[str]:
        """在指定目录中查找 opencode 相关文件"""
        found: List[str] = []
        
        if not os.path.exists(directory):
            return found
        
        try:
            for filename in os.listdir(directory):
                # 检查文件名是否包含 opencode
                if 'opencode' in filename.lower():
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        found.append(os.path.normpath(file_path))
        except (PermissionError, OSError):
            pass
        
        return found
