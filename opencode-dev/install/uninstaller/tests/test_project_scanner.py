"""
项目扫描器的属性测试

Property 8: Project Directory Scan Completeness
*For any* directory tree, all .opencode directories under the root should be found.

Validates: Requirements 5.3
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import ProjectScanner


class TestProjectScanner:
    """ProjectScanner 基本测试"""
    
    def test_initialization(self):
        """测试初始化"""
        scanner = ProjectScanner()
        assert scanner.max_depth == 10
    
    def test_initialization_with_custom_depth(self):
        """测试自定义深度初始化"""
        scanner = ProjectScanner(max_depth=5)
        assert scanner.max_depth == 5
    
    def test_scan_returns_list(self):
        """测试 scan 返回列表"""
        scanner = ProjectScanner()
        result = scanner.scan('.')
        assert isinstance(result, list)
    
    def test_scan_nonexistent_path(self):
        """测试扫描不存在的路径"""
        scanner = ProjectScanner()
        result = scanner.scan('/nonexistent/path/12345')
        assert result == []
    
    def test_scan_file_path(self):
        """测试扫描文件路径（应返回空）"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.txt')
            with open(filepath, 'w') as f:
                f.write('test')
            
            result = scanner.scan(filepath)
            assert result == []


class TestProjectDirectoryScanCompleteness:
    """
    Property 8: Project Directory Scan Completeness
    测试所有 .opencode 目录都能被找到
    """
    
    def test_find_single_opencode_dir(self):
        """测试找到单个 .opencode 目录"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 .opencode 目录
            opencode_dir = os.path.join(tmpdir, '.opencode')
            os.makedirs(opencode_dir)
            
            result = scanner.scan(tmpdir)
            
            assert len(result) == 1
            assert os.path.normpath(opencode_dir) in result[0]
    
    def test_find_nested_opencode_dirs(self):
        """测试找到嵌套的 .opencode 目录"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建多个嵌套的 .opencode 目录
            dirs_to_create = [
                os.path.join(tmpdir, '.opencode'),
                os.path.join(tmpdir, 'project1', '.opencode'),
                os.path.join(tmpdir, 'project2', 'subproject', '.opencode'),
            ]
            
            for d in dirs_to_create:
                os.makedirs(d)
            
            result = scanner.scan(tmpdir)
            
            assert len(result) == 3
    
    def test_find_all_opencode_dirs_in_tree(self):
        """测试在复杂目录树中找到所有 .opencode 目录"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建复杂的目录结构
            structure = [
                'project1/.opencode',
                'project1/src',
                'project1/tests',
                'project2/.opencode',
                'project2/lib/.opencode',
                'shared/common/.opencode',
                'docs',
            ]
            
            expected_opencode_count = 0
            for path in structure:
                full_path = os.path.join(tmpdir, path)
                os.makedirs(full_path, exist_ok=True)
                if '.opencode' in path:
                    expected_opencode_count += 1
            
            result = scanner.scan(tmpdir)
            
            assert len(result) == expected_opencode_count
    
    def test_results_are_sorted(self):
        """测试结果是排序的"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dirs = [
                os.path.join(tmpdir, 'z_project', '.opencode'),
                os.path.join(tmpdir, 'a_project', '.opencode'),
                os.path.join(tmpdir, 'm_project', '.opencode'),
            ]
            
            for d in dirs:
                os.makedirs(d)
            
            result = scanner.scan(tmpdir)
            
            assert result == sorted(result)
    
    def test_no_duplicates(self):
        """测试结果没有重复"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            opencode_dir = os.path.join(tmpdir, '.opencode')
            os.makedirs(opencode_dir)
            
            result = scanner.scan(tmpdir)
            
            assert len(result) == len(set(result))


class TestSkipDirectories:
    """测试跳过特定目录"""
    
    def test_skip_node_modules(self):
        """测试跳过 node_modules 目录"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 在 node_modules 中创建 .opencode（应该被跳过）
            node_modules_opencode = os.path.join(tmpdir, 'node_modules', '.opencode')
            os.makedirs(node_modules_opencode)
            
            # 在正常位置创建 .opencode
            normal_opencode = os.path.join(tmpdir, '.opencode')
            os.makedirs(normal_opencode)
            
            result = scanner.scan(tmpdir)
            
            # 应该只找到正常位置的 .opencode
            assert len(result) == 1
            assert 'node_modules' not in result[0]
    
    def test_skip_git_directory(self):
        """测试跳过 .git 目录"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 在 .git 中创建 .opencode（应该被跳过）
            git_opencode = os.path.join(tmpdir, '.git', '.opencode')
            os.makedirs(git_opencode)
            
            result = scanner.scan(tmpdir)
            
            assert len(result) == 0


class TestMaxDepth:
    """测试最大深度限制"""
    
    def test_respects_max_depth(self):
        """测试遵守最大深度限制"""
        scanner = ProjectScanner(max_depth=2)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建深度为 1 的 .opencode（应该被找到）
            shallow = os.path.join(tmpdir, 'level1', '.opencode')
            os.makedirs(shallow)
            
            # 创建深度为 5 的 .opencode（应该被跳过）
            deep = os.path.join(tmpdir, 'a', 'b', 'c', 'd', 'e', '.opencode')
            os.makedirs(deep)
            
            result = scanner.scan(tmpdir)
            
            # 应该只找到浅层的
            assert len(result) == 1


class TestScanMultiple:
    """测试扫描多个根目录"""
    
    def test_scan_multiple_roots(self):
        """测试扫描多个根目录"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                # 在两个目录中创建 .opencode
                os.makedirs(os.path.join(tmpdir1, '.opencode'))
                os.makedirs(os.path.join(tmpdir2, '.opencode'))
                
                result = scanner.scan_multiple([tmpdir1, tmpdir2])
                
                assert len(result) == 2
    
    def test_scan_multiple_deduplicates(self):
        """测试扫描多个根目录时去重"""
        scanner = ProjectScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.opencode'))
            
            # 扫描同一个目录两次
            result = scanner.scan_multiple([tmpdir, tmpdir])
            
            assert len(result) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
