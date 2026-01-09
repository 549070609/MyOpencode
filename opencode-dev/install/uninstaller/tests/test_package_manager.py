"""
包管理器卸载器的属性测试

Property 2: Package Manager Attempt Coverage
*For any* set of supported package managers, the uninstaller should attempt 
each available one and record the result.

Property 3: Missing Package Manager Handling
*For any* package manager not installed, the uninstaller should skip it without error.

Validates: Requirements 2.1, 2.2, 2.3, 2.4
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from package_manager import PackageManagerUninstaller
from models import UninstallResult


class TestPackageManagerUninstaller:
    """PackageManagerUninstaller 单元测试"""
    
    def test_initialization(self):
        """测试初始化"""
        uninstaller = PackageManagerUninstaller()
        assert uninstaller is not None
    
    def test_get_supported_managers_not_empty(self):
        """测试支持的包管理器列表不为空"""
        uninstaller = PackageManagerUninstaller()
        managers = uninstaller.get_supported_managers()
        
        assert isinstance(managers, list)
        assert len(managers) > 0
    
    def test_supported_managers_include_common_ones(self):
        """测试支持常见的包管理器"""
        uninstaller = PackageManagerUninstaller()
        managers = uninstaller.get_supported_managers()
        
        # 应该支持这些常见的包管理器
        assert 'npm' in managers
        assert 'bun' in managers
        assert 'pnpm' in managers
        assert 'yarn' in managers
    
    def test_is_manager_available_returns_bool(self):
        """测试 is_manager_available 返回布尔值"""
        uninstaller = PackageManagerUninstaller()
        
        for manager in uninstaller.get_supported_managers():
            result = uninstaller.is_manager_available(manager)
            assert isinstance(result, bool)
    
    def test_is_manager_available_caches_result(self):
        """测试 is_manager_available 缓存结果"""
        uninstaller = PackageManagerUninstaller()
        manager = 'npm'
        
        # 第一次调用
        result1 = uninstaller.is_manager_available(manager)
        
        # 第二次调用应该使用缓存
        result2 = uninstaller.is_manager_available(manager)
        
        assert result1 == result2
        assert manager in uninstaller._available_managers
    
    def test_unsupported_manager_returns_false(self):
        """测试不支持的包管理器返回 False"""
        uninstaller = PackageManagerUninstaller()
        result = uninstaller.is_manager_available('nonexistent_manager_12345')
        assert result is False


class TestPackageManagerAttemptCoverage:
    """
    Property 2: Package Manager Attempt Coverage
    测试所有可用的包管理器都会被尝试
    """
    
    def test_uninstall_all_attempts_available_managers(self):
        """测试 uninstall_all 尝试所有可用的包管理器"""
        uninstaller = PackageManagerUninstaller()
        results, skipped = uninstaller.uninstall_all()
        
        # 结果应该是列表
        assert isinstance(results, list)
        assert isinstance(skipped, list)
        
        # 所有支持的包管理器要么在结果中，要么在跳过列表中
        all_managers = set(uninstaller.get_supported_managers())
        
        # 从结果中提取包管理器名称
        attempted_managers = set()
        for result in results:
            # target 格式是 "manager:package"
            manager = result.target.split(':')[0]
            attempted_managers.add(manager)
        
        skipped_set = set(skipped)
        
        # 每个支持的包管理器要么被尝试，要么被跳过
        for manager in all_managers:
            assert manager in attempted_managers or manager in skipped_set
    
    def test_uninstall_returns_results_for_each_package(self):
        """测试 uninstall 为每个包返回结果"""
        uninstaller = PackageManagerUninstaller()
        
        # 找一个可用的包管理器
        available_manager = None
        for manager in uninstaller.get_supported_managers():
            if uninstaller.is_manager_available(manager):
                available_manager = manager
                break
        
        if available_manager is None:
            pytest.skip("没有可用的包管理器")
        
        results = uninstaller.uninstall(available_manager)
        
        # 应该有结果
        assert len(results) > 0
        
        # 每个结果都应该是 UninstallResult
        for result in results:
            assert isinstance(result, UninstallResult)
            assert result.target is not None
            assert isinstance(result.success, bool)
            assert result.message is not None


class TestMissingPackageManagerHandling:
    """
    Property 3: Missing Package Manager Handling
    测试未安装的包管理器被正确跳过
    """
    
    def test_unavailable_manager_in_skipped_list(self):
        """测试不可用的包管理器出现在跳过列表中"""
        uninstaller = PackageManagerUninstaller()
        results, skipped = uninstaller.uninstall_all()
        
        # 检查每个跳过的包管理器确实不可用
        for manager in skipped:
            assert not uninstaller.is_manager_available(manager)
    
    def test_uninstall_unavailable_manager_returns_error(self):
        """测试卸载不可用的包管理器返回错误结果"""
        uninstaller = PackageManagerUninstaller()
        
        # 找一个不可用的包管理器
        unavailable_manager = None
        for manager in uninstaller.get_supported_managers():
            if not uninstaller.is_manager_available(manager):
                unavailable_manager = manager
                break
        
        if unavailable_manager is None:
            pytest.skip("所有包管理器都可用")
        
        results = uninstaller.uninstall(unavailable_manager)
        
        # 应该返回一个表示未安装的结果
        assert len(results) == 1
        assert results[0].success is False
        assert 'not_installed' in (results[0].error or '')
    
    def test_uninstall_unsupported_manager_returns_error(self):
        """测试卸载不支持的包管理器返回错误"""
        uninstaller = PackageManagerUninstaller()
        results = uninstaller.uninstall('nonexistent_manager_12345')
        
        assert len(results) == 1
        assert results[0].success is False
        assert 'unsupported' in (results[0].error or '')
    
    def test_no_exception_on_missing_manager(self):
        """测试缺少包管理器时不抛出异常"""
        uninstaller = PackageManagerUninstaller()
        
        # 这不应该抛出异常
        try:
            results, skipped = uninstaller.uninstall_all()
            assert True
        except Exception as e:
            pytest.fail(f"uninstall_all 不应该抛出异常: {e}")


class TestUninstallResultFormat:
    """测试卸载结果的格式"""
    
    def test_result_has_required_fields(self):
        """测试结果包含所有必需字段"""
        uninstaller = PackageManagerUninstaller()
        results, _ = uninstaller.uninstall_all()
        
        for result in results:
            assert hasattr(result, 'target')
            assert hasattr(result, 'success')
            assert hasattr(result, 'message')
            assert hasattr(result, 'error')
    
    def test_successful_result_has_no_error(self):
        """测试成功的结果没有错误信息（或错误为 None）"""
        uninstaller = PackageManagerUninstaller()
        results, _ = uninstaller.uninstall_all()
        
        for result in results:
            if result.success:
                # 成功时 error 应该是 None
                assert result.error is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
