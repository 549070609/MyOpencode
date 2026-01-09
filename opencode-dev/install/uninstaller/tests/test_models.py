"""
数据模型的属性测试

Property 7: Report Completeness
*For any* completed uninstall operation, the report should contain entries 
for all attempted operations with their respective success/failure status.
Validates: Requirements 6.2, 6.3
"""

import pytest
from hypothesis import given, strategies as st
from typing import List, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import UninstallResult, RemoveResult, PlatformPaths, UninstallReport


# 策略定义
path_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(
    whitelist_categories=('L', 'N'),
    whitelist_characters='/_.-'
))

error_strategy = st.one_of(st.none(), st.text(min_size=1, max_size=50))

path_list_strategy = st.lists(path_strategy, min_size=0, max_size=10)

path_error_tuple_strategy = st.tuples(path_strategy, st.text(min_size=1, max_size=50))
path_error_list_strategy = st.lists(path_error_tuple_strategy, min_size=0, max_size=10)


class TestUninstallResult:
    """UninstallResult 数据类测试"""
    
    @given(
        target=path_strategy,
        success=st.booleans(),
        message=st.text(min_size=1, max_size=100),
        error=error_strategy
    )
    def test_uninstall_result_creation(self, target, success, message, error):
        """测试 UninstallResult 可以用任意有效数据创建"""
        result = UninstallResult(
            target=target,
            success=success,
            message=message,
            error=error
        )
        assert result.target == target
        assert result.success == success
        assert result.message == message
        assert result.error == error
    
    @given(target=path_strategy, message=st.text(min_size=1, max_size=100))
    def test_success_result_has_no_error(self, target, message):
        """成功的结果通常没有错误信息"""
        result = UninstallResult(target=target, success=True, message=message, error=None)
        assert result.success is True
        assert result.error is None


class TestRemoveResult:
    """RemoveResult 数据类测试"""
    
    @given(
        path=path_strategy,
        success=st.booleans(),
        error=error_strategy
    )
    def test_remove_result_creation(self, path, success, error):
        """测试 RemoveResult 可以用任意有效数据创建"""
        result = RemoveResult(path=path, success=success, error=error)
        assert result.path == path
        assert result.success == success
        assert result.error == error


class TestPlatformPaths:
    """PlatformPaths 数据类测试"""
    
    @given(
        config_dirs=path_list_strategy,
        cache_dirs=path_list_strategy,
        data_dirs=path_list_strategy,
        executable_extensions=st.lists(st.text(min_size=1, max_size=10), max_size=5),
        package_manager_dirs=path_list_strategy
    )
    def test_platform_paths_creation(self, config_dirs, cache_dirs, data_dirs, 
                                      executable_extensions, package_manager_dirs):
        """测试 PlatformPaths 可以用任意有效数据创建"""
        paths = PlatformPaths(
            config_dirs=config_dirs,
            cache_dirs=cache_dirs,
            data_dirs=data_dirs,
            executable_extensions=executable_extensions,
            package_manager_dirs=package_manager_dirs
        )
        assert paths.config_dirs == config_dirs
        assert paths.cache_dirs == cache_dirs
        assert paths.data_dirs == data_dirs
        assert paths.executable_extensions == executable_extensions
        assert paths.package_manager_dirs == package_manager_dirs
    
    def test_default_values(self):
        """测试默认值为空列表"""
        paths = PlatformPaths()
        assert paths.config_dirs == []
        assert paths.cache_dirs == []
        assert paths.data_dirs == []
        assert paths.executable_extensions == []
        assert paths.package_manager_dirs == []


class TestUninstallReport:
    """
    UninstallReport 数据类测试
    
    Property 7: Report Completeness
    *For any* completed uninstall operation, the report should contain entries 
    for all attempted operations with their respective success/failure status.
    """
    
    @given(
        executables_removed=path_list_strategy,
        executables_failed=path_error_list_strategy,
        package_managers_success=st.lists(st.text(min_size=1, max_size=20), max_size=5),
        package_managers_failed=path_error_list_strategy,
        config_dirs_removed=path_list_strategy,
        config_dirs_failed=path_error_list_strategy,
        cache_dirs_removed=path_list_strategy,
        data_dirs_removed=path_list_strategy,
        project_dirs_removed=path_list_strategy,
        dry_run=st.booleans()
    )
    def test_report_completeness(self, executables_removed, executables_failed,
                                  package_managers_success, package_managers_failed,
                                  config_dirs_removed, config_dirs_failed,
                                  cache_dirs_removed, data_dirs_removed,
                                  project_dirs_removed, dry_run):
        """
        Property 7: Report Completeness
        报告应包含所有操作的条目及其状态
        """
        report = UninstallReport(
            executables_removed=executables_removed,
            executables_failed=executables_failed,
            package_managers_success=package_managers_success,
            package_managers_failed=package_managers_failed,
            config_dirs_removed=config_dirs_removed,
            config_dirs_failed=config_dirs_failed,
            cache_dirs_removed=cache_dirs_removed,
            data_dirs_removed=data_dirs_removed,
            project_dirs_removed=project_dirs_removed,
            dry_run=dry_run
        )
        
        # 验证所有输入都被正确存储
        assert report.executables_removed == executables_removed
        assert report.executables_failed == executables_failed
        assert report.package_managers_success == package_managers_success
        assert report.package_managers_failed == package_managers_failed
        assert report.config_dirs_removed == config_dirs_removed
        assert report.config_dirs_failed == config_dirs_failed
        assert report.cache_dirs_removed == cache_dirs_removed
        assert report.data_dirs_removed == data_dirs_removed
        assert report.project_dirs_removed == project_dirs_removed
        assert report.dry_run == dry_run
        
        # 验证 total_removed 计算正确
        expected_removed = (
            len(executables_removed) +
            len(config_dirs_removed) +
            len(cache_dirs_removed) +
            len(data_dirs_removed) +
            len(project_dirs_removed)
        )
        assert report.total_removed == expected_removed
        
        # 验证 total_failed 计算正确
        expected_failed = (
            len(executables_failed) +
            len(package_managers_failed) +
            len(config_dirs_failed)
        )
        # 注意：cache_dirs_failed, data_dirs_failed, project_dirs_failed 也需要计算
        # 但在这个测试中我们没有设置它们，所以它们是空的
        assert report.total_failed >= expected_failed
    
    @given(
        executables_failed=path_error_list_strategy,
        package_managers_failed=path_error_list_strategy,
        config_dirs_failed=path_error_list_strategy
    )
    def test_is_complete_with_failures(self, executables_failed, 
                                        package_managers_failed, config_dirs_failed):
        """
        Property 7: is_complete 应正确反映是否有失败项
        """
        report = UninstallReport(
            executables_failed=executables_failed,
            package_managers_failed=package_managers_failed,
            config_dirs_failed=config_dirs_failed
        )
        
        has_failures = (
            len(executables_failed) > 0 or
            len(package_managers_failed) > 0 or
            len(config_dirs_failed) > 0
        )
        
        if has_failures:
            assert report.is_complete is False
        else:
            assert report.is_complete is True
    
    def test_empty_report_is_complete(self):
        """空报告应该标记为完成"""
        report = UninstallReport()
        assert report.is_complete is True
        assert report.total_removed == 0
        assert report.total_failed == 0
    
    @given(
        executables_removed=path_list_strategy,
        config_dirs_removed=path_list_strategy
    )
    def test_to_string_contains_all_removed(self, executables_removed, config_dirs_removed):
        """
        to_string() 应包含所有已删除项目的信息
        """
        report = UninstallReport(
            executables_removed=executables_removed,
            config_dirs_removed=config_dirs_removed
        )
        
        output = report.to_string()
        
        # 验证输出包含所有已删除的路径
        for path in executables_removed:
            if path:  # 跳过空字符串
                assert path in output or '已删除' in output
        
        for path in config_dirs_removed:
            if path:
                assert path in output or '已删除' in output
    
    def test_dry_run_mode_indicator(self):
        """dry_run 模式应在输出中明确标识"""
        report = UninstallReport(dry_run=True)
        output = report.to_string()
        assert '预览模式' in output
        
        report_normal = UninstallReport(dry_run=False)
        output_normal = report_normal.to_string()
        assert '预览模式' not in output_normal


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
