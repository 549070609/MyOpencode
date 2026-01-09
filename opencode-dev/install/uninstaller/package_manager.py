"""
包管理器卸载器

通过各种包管理器卸载 opencode。
"""

import subprocess
from typing import List, Dict, Tuple

try:
    from .models import UninstallResult
except ImportError:
    from models import UninstallResult


class PackageManagerUninstaller:
    """通过包管理器卸载 opencode"""
    
    # 包管理器配置: (管理器名称, 检查命令, 卸载命令列表)
    PACKAGE_MANAGERS: Dict[str, Dict] = {
        'bun': {
            'check_cmd': ['bun', '--version'],
            'uninstall_cmds': [
                ['bun', 'remove', '-g', 'opencode'],
                ['bun', 'remove', '-g', 'opencode-ai'],
                ['bun', 'remove', '-g', 'oh-my-opencode'],
            ]
        },
        'npm': {
            'check_cmd': ['npm', '--version'],
            'uninstall_cmds': [
                ['npm', 'uninstall', '-g', 'opencode'],
                ['npm', 'uninstall', '-g', 'opencode-ai'],
                ['npm', 'uninstall', '-g', 'oh-my-opencode'],
            ]
        },
        'pnpm': {
            'check_cmd': ['pnpm', '--version'],
            'uninstall_cmds': [
                ['pnpm', 'remove', '-g', 'opencode'],
                ['pnpm', 'remove', '-g', 'opencode-ai'],
                ['pnpm', 'remove', '-g', 'oh-my-opencode'],
            ]
        },
        'yarn': {
            'check_cmd': ['yarn', '--version'],
            'uninstall_cmds': [
                ['yarn', 'global', 'remove', 'opencode'],
                ['yarn', 'global', 'remove', 'opencode-ai'],
                ['yarn', 'global', 'remove', 'oh-my-opencode'],
            ]
        },
        'scoop': {
            'check_cmd': ['scoop', '--version'],
            'uninstall_cmds': [
                ['scoop', 'uninstall', 'opencode'],
            ]
        },
        'choco': {
            'check_cmd': ['choco', '--version'],
            'uninstall_cmds': [
                ['choco', 'uninstall', 'opencode', '-y'],
            ]
        },
    }
    
    def __init__(self):
        self._available_managers: Dict[str, bool] = {}
    
    def get_supported_managers(self) -> List[str]:
        """返回支持的包管理器列表"""
        return list(self.PACKAGE_MANAGERS.keys())
    
    def is_manager_available(self, manager: str) -> bool:
        """检查包管理器是否可用"""
        if manager not in self.PACKAGE_MANAGERS:
            return False
        
        # 缓存检查结果
        if manager in self._available_managers:
            return self._available_managers[manager]
        
        check_cmd = self.PACKAGE_MANAGERS[manager]['check_cmd']
        
        try:
            result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10
            )
            available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
            available = False
        
        self._available_managers[manager] = available
        return available
    
    def uninstall(self, manager: str) -> List[UninstallResult]:
        """
        使用指定包管理器卸载 opencode
        
        返回每个卸载命令的结果列表
        """
        results: List[UninstallResult] = []
        
        if manager not in self.PACKAGE_MANAGERS:
            results.append(UninstallResult(
                target=manager,
                success=False,
                message=f'不支持的包管理器: {manager}',
                error='unsupported'
            ))
            return results
        
        if not self.is_manager_available(manager):
            results.append(UninstallResult(
                target=manager,
                success=False,
                message=f'{manager} 未安装',
                error='not_installed'
            ))
            return results
        
        uninstall_cmds = self.PACKAGE_MANAGERS[manager]['uninstall_cmds']
        
        for cmd in uninstall_cmds:
            package_name = cmd[-1] if cmd[-1] != '-y' else cmd[-2]
            result = self._run_uninstall_command(manager, cmd, package_name)
            results.append(result)
        
        return results
    
    def uninstall_all(self) -> Tuple[List[UninstallResult], List[str]]:
        """
        尝试使用所有可用的包管理器卸载 opencode
        
        返回: (结果列表, 跳过的包管理器列表)
        """
        all_results: List[UninstallResult] = []
        skipped: List[str] = []
        
        for manager in self.get_supported_managers():
            if not self.is_manager_available(manager):
                skipped.append(manager)
                continue
            
            results = self.uninstall(manager)
            all_results.extend(results)
        
        return all_results, skipped
    
    def _run_uninstall_command(self, manager: str, cmd: List[str], package_name: str) -> UninstallResult:
        """执行卸载命令并返回结果"""
        target = f'{manager}:{package_name}'
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=60
            )
            
            if result.returncode == 0:
                return UninstallResult(
                    target=target,
                    success=True,
                    message=f'通过 {manager} 成功卸载 {package_name}',
                    error=None
                )
            else:
                # 某些包管理器在包不存在时也返回非零退出码
                # 检查输出是否表明包不存在
                output = (result.stdout + result.stderr).lower()
                if 'not found' in output or 'not installed' in output or 'no such' in output:
                    return UninstallResult(
                        target=target,
                        success=True,
                        message=f'{package_name} 未通过 {manager} 安装',
                        error=None
                    )
                
                return UninstallResult(
                    target=target,
                    success=False,
                    message=f'通过 {manager} 卸载 {package_name} 失败',
                    error=result.stderr.strip() or f'退出码: {result.returncode}'
                )
        
        except subprocess.TimeoutExpired:
            return UninstallResult(
                target=target,
                success=False,
                message=f'通过 {manager} 卸载 {package_name} 超时',
                error='timeout'
            )
        except subprocess.SubprocessError as e:
            return UninstallResult(
                target=target,
                success=False,
                message=f'通过 {manager} 卸载 {package_name} 出错',
                error=str(e)
            )
