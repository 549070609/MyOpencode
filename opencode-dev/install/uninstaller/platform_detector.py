"""
平台检测器

检测当前操作系统并提供平台特定的路径配置。
"""

import os
import sys
from typing import List

try:
    from .models import PlatformPaths
except ImportError:
    from models import PlatformPaths


class PlatformDetector:
    """检测操作系统并提供平台特定路径"""
    
    PLATFORM_WINDOWS = 'windows'
    PLATFORM_MACOS = 'macos'
    PLATFORM_LINUX = 'linux'
    
    def __init__(self):
        self._platform = self._detect_platform()
        self._home_dir = os.path.expanduser('~')
    
    def _detect_platform(self) -> str:
        """检测当前操作系统"""
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            return self.PLATFORM_WINDOWS
        elif sys.platform == 'darwin':
            return self.PLATFORM_MACOS
        else:
            return self.PLATFORM_LINUX
    
    def get_platform(self) -> str:
        """返回当前平台标识"""
        return self._platform
    
    def get_home_dir(self) -> str:
        """返回用户主目录"""
        return self._home_dir
    
    def get_config_directories(self) -> List[str]:
        """返回 opencode 配置目录路径列表"""
        if self._platform == self.PLATFORM_WINDOWS:
            return self._get_windows_config_dirs()
        else:
            return self._get_unix_config_dirs()
    
    def get_cache_directories(self) -> List[str]:
        """返回 opencode 缓存目录路径列表"""
        if self._platform == self.PLATFORM_WINDOWS:
            return self._get_windows_cache_dirs()
        elif self._platform == self.PLATFORM_MACOS:
            return self._get_macos_cache_dirs()
        else:
            return self._get_linux_cache_dirs()
    
    def get_data_directories(self) -> List[str]:
        """返回 opencode 数据目录路径列表"""
        if self._platform == self.PLATFORM_WINDOWS:
            return self._get_windows_data_dirs()
        elif self._platform == self.PLATFORM_MACOS:
            return self._get_macos_data_dirs()
        else:
            return self._get_linux_data_dirs()
    
    def get_executable_extensions(self) -> List[str]:
        """返回可执行文件扩展名列表"""
        if self._platform == self.PLATFORM_WINDOWS:
            return ['', '.exe', '.cmd', '.bat', '.ps1']
        else:
            return ['']
    
    def get_package_manager_directories(self) -> List[str]:
        """返回包管理器全局安装目录列表"""
        dirs = []
        
        # bun 全局目录
        bun_dir = os.path.join(self._home_dir, '.bun')
        if os.path.exists(bun_dir):
            dirs.append(os.path.join(bun_dir, 'bin'))
            dirs.append(os.path.join(bun_dir, 'install', 'global', 'node_modules'))
        
        # npm 全局目录
        if self._platform == self.PLATFORM_WINDOWS:
            appdata = os.environ.get('APPDATA', os.path.join(self._home_dir, 'AppData', 'Roaming'))
            dirs.append(os.path.join(appdata, 'npm'))
            dirs.append(os.path.join(appdata, 'npm', 'node_modules'))
        else:
            dirs.append('/usr/local/bin')
            dirs.append('/usr/local/lib/node_modules')
            dirs.append(os.path.join(self._home_dir, '.npm-global', 'bin'))
            dirs.append(os.path.join(self._home_dir, '.npm-global', 'lib', 'node_modules'))
        
        # pnpm 全局目录
        if self._platform == self.PLATFORM_WINDOWS:
            localappdata = os.environ.get('LOCALAPPDATA', os.path.join(self._home_dir, 'AppData', 'Local'))
            pnpm_home = os.environ.get('PNPM_HOME', os.path.join(localappdata, 'pnpm'))
            dirs.append(pnpm_home)
        else:
            pnpm_home = os.environ.get('PNPM_HOME', os.path.join(self._home_dir, '.local', 'share', 'pnpm'))
            dirs.append(pnpm_home)
        
        # yarn 全局目录
        if self._platform == self.PLATFORM_WINDOWS:
            localappdata = os.environ.get('LOCALAPPDATA', os.path.join(self._home_dir, 'AppData', 'Local'))
            dirs.append(os.path.join(localappdata, 'Yarn', 'bin'))
            dirs.append(os.path.join(localappdata, 'Yarn', 'Data', 'global', 'node_modules'))
        else:
            dirs.append(os.path.join(self._home_dir, '.yarn', 'bin'))
            dirs.append(os.path.join(self._home_dir, '.config', 'yarn', 'global', 'node_modules'))
        
        return dirs
    
    def get_all_paths(self) -> PlatformPaths:
        """返回所有平台特定路径的配置对象"""
        return PlatformPaths(
            config_dirs=self.get_config_directories(),
            cache_dirs=self.get_cache_directories(),
            data_dirs=self.get_data_directories(),
            executable_extensions=self.get_executable_extensions(),
            package_manager_dirs=self.get_package_manager_directories()
        )
    
    # Windows 特定路径
    def _get_windows_config_dirs(self) -> List[str]:
        """Windows 配置目录"""
        appdata = os.environ.get('APPDATA', os.path.join(self._home_dir, 'AppData', 'Roaming'))
        localappdata = os.environ.get('LOCALAPPDATA', os.path.join(self._home_dir, 'AppData', 'Local'))
        
        return [
            os.path.join(self._home_dir, '.opencode'),
            os.path.join(self._home_dir, '.config', 'opencode'),
            os.path.join(appdata, 'opencode'),
            os.path.join(localappdata, 'opencode'),
            os.path.join(localappdata, 'opencode-nodejs'),
        ]
    
    def _get_windows_cache_dirs(self) -> List[str]:
        """Windows 缓存目录"""
        localappdata = os.environ.get('LOCALAPPDATA', os.path.join(self._home_dir, 'AppData', 'Local'))
        temp = os.environ.get('TEMP', os.path.join(localappdata, 'Temp'))
        
        return [
            os.path.join(localappdata, 'opencode', 'cache'),
            os.path.join(temp, 'opencode'),
        ]
    
    def _get_windows_data_dirs(self) -> List[str]:
        """Windows 数据目录"""
        localappdata = os.environ.get('LOCALAPPDATA', os.path.join(self._home_dir, 'AppData', 'Local'))
        
        return [
            os.path.join(localappdata, 'opencode', 'data'),
        ]
    
    # Unix (macOS/Linux) 通用配置目录
    def _get_unix_config_dirs(self) -> List[str]:
        """Unix 配置目录"""
        return [
            os.path.join(self._home_dir, '.opencode'),
            os.path.join(self._home_dir, '.config', 'opencode'),
        ]
    
    # macOS 特定路径
    def _get_macos_cache_dirs(self) -> List[str]:
        """macOS 缓存目录"""
        return [
            os.path.join(self._home_dir, 'Library', 'Caches', 'opencode'),
        ]
    
    def _get_macos_data_dirs(self) -> List[str]:
        """macOS 数据目录"""
        return [
            os.path.join(self._home_dir, 'Library', 'Application Support', 'opencode'),
        ]
    
    # Linux 特定路径
    def _get_linux_cache_dirs(self) -> List[str]:
        """Linux 缓存目录"""
        xdg_cache = os.environ.get('XDG_CACHE_HOME', os.path.join(self._home_dir, '.cache'))
        return [
            os.path.join(xdg_cache, 'opencode'),
        ]
    
    def _get_linux_data_dirs(self) -> List[str]:
        """Linux 数据目录"""
        xdg_data = os.environ.get('XDG_DATA_HOME', os.path.join(self._home_dir, '.local', 'share'))
        return [
            os.path.join(xdg_data, 'opencode'),
        ]
