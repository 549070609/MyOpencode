"""
数据模型定义

定义卸载过程中使用的所有数据类。
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class UninstallResult:
    """单个卸载操作的结果"""
    target: str           # 目标（文件路径或包管理器名称）
    success: bool         # 是否成功
    message: str          # 结果消息
    error: Optional[str] = None  # 错误信息（如果失败）


@dataclass
class RemoveResult:
    """目录或文件删除结果"""
    path: str             # 路径
    success: bool         # 是否成功
    error: Optional[str] = None  # 错误信息（如果失败）


@dataclass
class PlatformPaths:
    """平台特定路径配置"""
    config_dirs: List[str] = field(default_factory=list)
    cache_dirs: List[str] = field(default_factory=list)
    data_dirs: List[str] = field(default_factory=list)
    executable_extensions: List[str] = field(default_factory=list)
    package_manager_dirs: List[str] = field(default_factory=list)


@dataclass
class UninstallReport:
    """卸载报告"""
    executables_removed: List[str] = field(default_factory=list)
    executables_failed: List[Tuple[str, str]] = field(default_factory=list)  # (path, reason)
    package_managers_success: List[str] = field(default_factory=list)
    package_managers_failed: List[Tuple[str, str]] = field(default_factory=list)  # (name, reason)
    package_managers_skipped: List[str] = field(default_factory=list)  # 未安装的包管理器
    config_dirs_removed: List[str] = field(default_factory=list)
    config_dirs_failed: List[Tuple[str, str]] = field(default_factory=list)
    config_dirs_skipped: List[str] = field(default_factory=list)  # 用户跳过的
    cache_dirs_removed: List[str] = field(default_factory=list)
    cache_dirs_failed: List[Tuple[str, str]] = field(default_factory=list)
    data_dirs_removed: List[str] = field(default_factory=list)
    data_dirs_failed: List[Tuple[str, str]] = field(default_factory=list)
    project_dirs_removed: List[str] = field(default_factory=list)
    project_dirs_failed: List[Tuple[str, str]] = field(default_factory=list)
    project_dirs_skipped: bool = False  # 用户是否跳过项目目录扫描
    dry_run: bool = False  # 是否为预览模式
    
    @property
    def is_complete(self) -> bool:
        """判断卸载是否完全成功（无失败项）"""
        return (
            len(self.executables_failed) == 0 and
            len(self.package_managers_failed) == 0 and
            len(self.config_dirs_failed) == 0 and
            len(self.cache_dirs_failed) == 0 and
            len(self.data_dirs_failed) == 0 and
            len(self.project_dirs_failed) == 0
        )
    
    @property
    def total_removed(self) -> int:
        """返回总共删除的项目数"""
        return (
            len(self.executables_removed) +
            len(self.config_dirs_removed) +
            len(self.cache_dirs_removed) +
            len(self.data_dirs_removed) +
            len(self.project_dirs_removed)
        )
    
    @property
    def total_failed(self) -> int:
        """返回总共失败的项目数"""
        return (
            len(self.executables_failed) +
            len(self.package_managers_failed) +
            len(self.config_dirs_failed) +
            len(self.cache_dirs_failed) +
            len(self.data_dirs_failed) +
            len(self.project_dirs_failed)
        )
    
    def display(self) -> None:
        """在控制台显示报告"""
        print(self.to_string())
    
    def to_string(self) -> str:
        """转换为格式化字符串"""
        lines = []
        
        if self.dry_run:
            lines.append('=' * 50)
            lines.append('预览模式 - 以下项目将被删除（实际未删除）')
            lines.append('=' * 50)
        else:
            lines.append('=' * 50)
            lines.append('OpenCode 卸载报告')
            lines.append('=' * 50)
        
        # 可执行文件
        if self.executables_removed or self.executables_failed:
            lines.append('\n【可执行文件】')
            for path in self.executables_removed:
                lines.append(f'  ✓ 已删除: {path}')
            for path, reason in self.executables_failed:
                lines.append(f'  ✗ 删除失败: {path} ({reason})')
        
        # 包管理器
        if self.package_managers_success or self.package_managers_failed or self.package_managers_skipped:
            lines.append('\n【包管理器卸载】')
            for name in self.package_managers_success:
                lines.append(f'  ✓ {name}: 卸载成功')
            for name, reason in self.package_managers_failed:
                lines.append(f'  ✗ {name}: 卸载失败 ({reason})')
            for name in self.package_managers_skipped:
                lines.append(f'  - {name}: 未安装，跳过')
        
        # 配置目录
        if self.config_dirs_removed or self.config_dirs_failed or self.config_dirs_skipped:
            lines.append('\n【配置目录】')
            for path in self.config_dirs_removed:
                lines.append(f'  ✓ 已删除: {path}')
            for path, reason in self.config_dirs_failed:
                lines.append(f'  ✗ 删除失败: {path} ({reason})')
            for path in self.config_dirs_skipped:
                lines.append(f'  - 用户跳过: {path}')
        
        # 缓存目录
        if self.cache_dirs_removed or self.cache_dirs_failed:
            lines.append('\n【缓存目录】')
            for path in self.cache_dirs_removed:
                lines.append(f'  ✓ 已删除: {path}')
            for path, reason in self.cache_dirs_failed:
                lines.append(f'  ✗ 删除失败: {path} ({reason})')
        
        # 数据目录
        if self.data_dirs_removed or self.data_dirs_failed:
            lines.append('\n【数据目录】')
            for path in self.data_dirs_removed:
                lines.append(f'  ✓ 已删除: {path}')
            for path, reason in self.data_dirs_failed:
                lines.append(f'  ✗ 删除失败: {path} ({reason})')
        
        # 项目目录
        if self.project_dirs_removed or self.project_dirs_failed:
            lines.append('\n【项目 .opencode 目录】')
            for path in self.project_dirs_removed:
                lines.append(f'  ✓ 已删除: {path}')
            for path, reason in self.project_dirs_failed:
                lines.append(f'  ✗ 删除失败: {path} ({reason})')
        elif self.project_dirs_skipped:
            lines.append('\n【项目 .opencode 目录】')
            lines.append('  - 用户跳过扫描')
        
        # 总结
        lines.append('\n' + '=' * 50)
        if self.dry_run:
            lines.append(f'预览完成: 共 {self.total_removed} 个项目将被删除')
        else:
            lines.append(f'卸载{"完成" if self.is_complete else "部分完成"}')
            lines.append(f'  成功删除: {self.total_removed} 项')
            if self.total_failed > 0:
                lines.append(f'  删除失败: {self.total_failed} 项')
            lines.append(f'  包管理器卸载成功: {len(self.package_managers_success)} 个')
        lines.append('=' * 50)
        
        return '\n'.join(lines)
