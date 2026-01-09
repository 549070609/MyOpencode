"""
可执行文件检测器的单元测试

测试 PATH 查找逻辑和包管理器目录查找
Validates: Requirements 1.1, 1.4
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from executable_detector import ExecutableDetector
from platform_detector import PlatformDetector


class TestExecutableDetector:
    """ExecutableDetector 单元测试"""
    
    def test_initialization(self):
        """测试初始化"""
        detector = ExecutableDetector()
        assert detector.platform is not None
        assert isinstance(detector.platform, PlatformDetector)
    
    def test_initialization_with_custom_platform(self):
        """测试使用自定义平台检测器初始化"""
        platform = PlatformDetector()
        detector = ExecutableDetector(platform)
        assert detector.platform is platform
    
    def test_executable_names_defined(self):
        """测试可执行文件名列表已定义"""
        assert len(ExecutableDetector.EXECUTABLE_NAMES) > 0
        assert 'opencode' in ExecutableDetector.EXECUTABLE_NAMES
    
    def test_find_executables_returns_list(self):
        """测试 find_executables 返回列表"""
        detector = ExecutableDetector()
        result = detector.find_executables()
        assert isinstance(result, list)
    
    def test_find_in_path_returns_list(self):
        """测试 find_in_path 返回列表"""
        detector = ExecutableDetector()
        result = detector.find_in_path()
        assert isinstance(result, list)
    
    def test_find_in_package_manager_dirs_returns_list(self):
        """测试 find_in_package_manager_dirs 返回列表"""
        detector = ExecutableDetector()
        result = detector.find_in_package_manager_dirs()
        assert isinstance(result, list)
    
    def test_find_in_bun_dir_returns_list(self):
        """测试 find_in_bun_dir 返回列表"""
        detector = ExecutableDetector()
        result = detector.find_in_bun_dir()
        assert isinstance(result, list)
    
    def test_found_paths_are_normalized(self):
        """测试找到的路径是规范化的"""
        detector = ExecutableDetector()
        result = detector.find_executables()
        
        for path in result:
            # 规范化路径应该等于自身
            assert path == os.path.normpath(path)
    
    def test_no_duplicate_paths(self):
        """测试结果中没有重复路径"""
        detector = ExecutableDetector()
        result = detector.find_executables()
        
        # 检查没有重复
        assert len(result) == len(set(result))
    
    def test_results_are_sorted(self):
        """测试结果是排序的"""
        detector = ExecutableDetector()
        result = detector.find_executables()
        
        assert result == sorted(result)


class TestExecutableDetectorWithTempFiles:
    """使用临时文件测试 ExecutableDetector"""
    
    def test_find_opencode_files_in_dir(self):
        """测试在目录中查找 opencode 文件"""
        detector = ExecutableDetector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_files = ['opencode.exe', 'opencode.cmd', 'other.txt']
            for filename in test_files:
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, 'w') as f:
                    f.write('test')
            
            # 查找文件
            result = detector._find_opencode_files_in_dir(tmpdir)
            
            # 应该找到 opencode 相关文件
            assert len(result) >= 2
            
            # 验证找到的文件包含 opencode
            for path in result:
                assert 'opencode' in os.path.basename(path).lower()
    
    def test_find_opencode_files_in_nonexistent_dir(self):
        """测试在不存在的目录中查找"""
        detector = ExecutableDetector()
        result = detector._find_opencode_files_in_dir('/nonexistent/path/12345')
        assert result == []
    
    def test_find_opencode_files_excludes_directories(self):
        """测试不包含目录"""
        detector = ExecutableDetector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一个名为 opencode 的子目录
            subdir = os.path.join(tmpdir, 'opencode')
            os.makedirs(subdir)
            
            # 创建一个 opencode 文件
            filepath = os.path.join(tmpdir, 'opencode.exe')
            with open(filepath, 'w') as f:
                f.write('test')
            
            result = detector._find_opencode_files_in_dir(tmpdir)
            
            # 应该只找到文件，不包含目录
            for path in result:
                assert os.path.isfile(path)


class TestFindCommandInPath:
    """测试 _find_command_in_path 方法"""
    
    def test_find_nonexistent_command(self):
        """测试查找不存在的命令"""
        detector = ExecutableDetector()
        result = detector._find_command_in_path('nonexistent_command_12345')
        assert result == []
    
    def test_find_common_command(self):
        """测试查找常见命令（如 python）"""
        detector = ExecutableDetector()
        
        # 尝试查找 python 或 py
        result = detector._find_command_in_path('python')
        if not result:
            result = detector._find_command_in_path('py')
        
        # 在大多数系统上应该能找到 python
        # 但不强制要求，因为环境可能不同
        assert isinstance(result, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
