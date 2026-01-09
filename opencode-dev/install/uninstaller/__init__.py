# OpenCode Uninstaller Package
"""
OpenCode 彻底删除工具包

提供完整的 opencode 卸载功能，包括：
- 可执行文件清理
- 包管理器卸载
- 配置目录清理
- 缓存和数据目录清理
- 项目目录扫描
- 详细的清理报告
"""

from .models import (
    UninstallResult,
    RemoveResult,
    PlatformPaths,
    UninstallReport,
)

__all__ = [
    'UninstallResult',
    'RemoveResult',
    'PlatformPaths',
    'UninstallReport',
]
