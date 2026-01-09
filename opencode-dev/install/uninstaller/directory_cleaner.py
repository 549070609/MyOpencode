"""
目录清理器

负责清理目录和文件。
"""

import os
import shutil
from typing import List

try:
    from .models import RemoveResult
except ImportError:
    from models import RemoveResult


class DirectoryCleaner:
    """清理目录和文件"""
    
    def __init__(self, dry_run: bool = False):
        """
        初始化目录清理器
        
        Args:
            dry_run: 如果为 True，只检测不实际删除
        """
        self.dry_run = dry_run
    
    def find_directories(self, paths: List[str]) -> List[str]:
        """
        查找存在的目录
        
        Args:
            paths: 要检查的路径列表
            
        Returns:
            存在的目录路径列表
        """
        existing = []
        for path in paths:
            normalized = os.path.normpath(os.path.expanduser(path))
            if os.path.exists(normalized) and os.path.isdir(normalized):
                existing.append(normalized)
        return existing
    
    def find_files(self, paths: List[str]) -> List[str]:
        """
        查找存在的文件
        
        Args:
            paths: 要检查的路径列表
            
        Returns:
            存在的文件路径列表
        """
        existing = []
        for path in paths:
            normalized = os.path.normpath(os.path.expanduser(path))
            if os.path.exists(normalized) and os.path.isfile(normalized):
                existing.append(normalized)
        return existing
    
    def remove_directory(self, path: str) -> RemoveResult:
        """
        删除目录（递归）
        
        Args:
            path: 要删除的目录路径
            
        Returns:
            删除结果
        """
        normalized = os.path.normpath(os.path.expanduser(path))
        
        if not os.path.exists(normalized):
            return RemoveResult(
                path=normalized,
                success=True,
                error=None
            )
        
        if not os.path.isdir(normalized):
            return RemoveResult(
                path=normalized,
                success=False,
                error='不是目录'
            )
        
        if self.dry_run:
            return RemoveResult(
                path=normalized,
                success=True,
                error=None
            )
        
        try:
            # Windows 特殊处理：移除只读属性
            def handle_remove_readonly(func, path, exc):
                """处理只读文件删除"""
                import stat
                if os.path.exists(path):
                    # 移除只读属性
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            
            shutil.rmtree(normalized, onerror=handle_remove_readonly)
            return RemoveResult(
                path=normalized,
                success=True,
                error=None
            )
        except PermissionError as e:
            return RemoveResult(
                path=normalized,
                success=False,
                error=f'权限不足: {e}'
            )
        except OSError as e:
            return RemoveResult(
                path=normalized,
                success=False,
                error=f'删除失败: {e}'
            )
    
    def remove_file(self, path: str) -> RemoveResult:
        """
        删除文件
        
        Args:
            path: 要删除的文件路径
            
        Returns:
            删除结果
        """
        normalized = os.path.normpath(os.path.expanduser(path))
        
        if not os.path.exists(normalized):
            return RemoveResult(
                path=normalized,
                success=True,
                error=None
            )
        
        if os.path.isdir(normalized):
            # 如果是目录，使用 remove_directory
            return self.remove_directory(normalized)
        
        if self.dry_run:
            return RemoveResult(
                path=normalized,
                success=True,
                error=None
            )
        
        try:
            # Windows 特殊处理：移除只读属性
            import stat
            if not os.access(normalized, os.W_OK):
                os.chmod(normalized, stat.S_IWRITE)
            
            os.remove(normalized)
            return RemoveResult(
                path=normalized,
                success=True,
                error=None
            )
        except PermissionError as e:
            return RemoveResult(
                path=normalized,
                success=False,
                error=f'权限不足: {e}'
            )
        except OSError as e:
            return RemoveResult(
                path=normalized,
                success=False,
                error=f'删除失败: {e}'
            )
    
    def remove_directories(self, paths: List[str]) -> List[RemoveResult]:
        """
        批量删除目录
        
        Args:
            paths: 要删除的目录路径列表
            
        Returns:
            每个目录的删除结果列表
        """
        results = []
        for path in paths:
            result = self.remove_directory(path)
            results.append(result)
        return results
    
    def remove_files(self, paths: List[str]) -> List[RemoveResult]:
        """
        批量删除文件
        
        Args:
            paths: 要删除的文件路径列表
            
        Returns:
            每个文件的删除结果列表
        """
        results = []
        for path in paths:
            result = self.remove_file(path)
            results.append(result)
        return results
    
    def remove_paths(self, paths: List[str]) -> List[RemoveResult]:
        """
        批量删除路径（自动判断是文件还是目录）
        
        Args:
            paths: 要删除的路径列表
            
        Returns:
            每个路径的删除结果列表
        """
        results = []
        for path in paths:
            normalized = os.path.normpath(os.path.expanduser(path))
            if os.path.isdir(normalized):
                result = self.remove_directory(normalized)
            else:
                result = self.remove_file(normalized)
            results.append(result)
        return results
