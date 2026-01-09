"""
项目扫描器

扫描项目中的 .opencode 目录。
"""

import os
from typing import List, Set


class ProjectScanner:
    """扫描项目 .opencode 目录"""
    
    # 要查找的目录名
    TARGET_DIR_NAME = '.opencode'
    
    # 要跳过的目录（避免扫描这些目录以提高性能）
    SKIP_DIRS = {
        'node_modules',
        '.git',
        '.svn',
        '.hg',
        '__pycache__',
        '.venv',
        'venv',
        '.env',
        'env',
        'dist',
        'build',
        '.next',
        '.nuxt',
        'target',
        'vendor',
    }
    
    def __init__(self, max_depth: int = 10):
        """
        初始化项目扫描器
        
        Args:
            max_depth: 最大扫描深度，防止无限递归
        """
        self.max_depth = max_depth
    
    def scan(self, root_path: str) -> List[str]:
        """
        扫描指定根目录下的所有 .opencode 目录
        
        Args:
            root_path: 要扫描的根目录路径
            
        Returns:
            找到的 .opencode 目录路径列表
        """
        root_path = os.path.normpath(os.path.expanduser(root_path))
        
        if not os.path.exists(root_path):
            return []
        
        if not os.path.isdir(root_path):
            return []
        
        found: Set[str] = set()
        self._scan_recursive(root_path, found, 0)
        
        return sorted(list(found))
    
    def _scan_recursive(self, current_path: str, found: Set[str], depth: int) -> None:
        """
        递归扫描目录
        
        Args:
            current_path: 当前扫描的目录
            found: 找到的目录集合
            depth: 当前深度
        """
        if depth > self.max_depth:
            return
        
        try:
            entries = os.listdir(current_path)
        except (PermissionError, OSError):
            return
        
        for entry in entries:
            entry_path = os.path.join(current_path, entry)
            
            # 检查是否是目录
            try:
                if not os.path.isdir(entry_path):
                    continue
            except (PermissionError, OSError):
                continue
            
            # 检查是否是目标目录
            if entry == self.TARGET_DIR_NAME:
                found.add(os.path.normpath(entry_path))
                continue  # 不需要继续扫描 .opencode 内部
            
            # 跳过特定目录
            if entry in self.SKIP_DIRS:
                continue
            
            # 跳过隐藏目录（除了我们要找的 .opencode）
            if entry.startswith('.') and entry != self.TARGET_DIR_NAME:
                continue
            
            # 递归扫描子目录
            self._scan_recursive(entry_path, found, depth + 1)
    
    def scan_multiple(self, root_paths: List[str]) -> List[str]:
        """
        扫描多个根目录
        
        Args:
            root_paths: 要扫描的根目录路径列表
            
        Returns:
            找到的所有 .opencode 目录路径列表（去重）
        """
        all_found: Set[str] = set()
        
        for root_path in root_paths:
            found = self.scan(root_path)
            all_found.update(found)
        
        return sorted(list(all_found))
