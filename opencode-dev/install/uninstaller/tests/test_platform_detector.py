"""
平台检测器的属性测试

Property 5: Platform Path Correctness
*For any* detected platform (Windows, macOS, Linux), the paths returned 
by PlatformDetector should match the expected standard locations for that platform.
Validates: Requirements 7.2, 7.3, 7.4
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platform_detector import PlatformDetector


class TestPlatformDetector:
    """
    Property 5: Platform Path Correctness
    测试平台检测器返回正确的平台特定路径
    """
    
    def test_platform_detection(self):
        """测试平台检测返回有效值"""
        detector = PlatformDetector()
        platform = detector.get_platform()
        
        assert platform in [
            PlatformDetector.PLATFORM_WINDOWS,
            PlatformDetector.PLATFORM_MACOS,
            PlatformDetector.PLATFORM_LINUX
        ]
    
    def test_home_dir_exists(self):
        """测试主目录存在"""
        detector = PlatformDetector()
        home_dir = detector.get_home_dir()
        
        assert home_dir is not None
        assert len(home_dir) > 0
        assert os.path.exists(home_dir)
    
    def test_config_directories_not_empty(self):
        """测试配置目录列表不为空"""
        detector = PlatformDetector()
        config_dirs = detector.get_config_directories()
        
        assert isinstance(config_dirs, list)
        assert len(config_dirs) > 0
    
    def test_config_directories_contain_opencode(self):
        """测试配置目录路径包含 opencode"""
        detector = PlatformDetector()
        config_dirs = detector.get_config_directories()
        
        for path in config_dirs:
            assert 'opencode' in path.lower()
    
    def test_cache_directories_not_empty(self):
        """测试缓存目录列表不为空"""
        detector = PlatformDetector()
        cache_dirs = detector.get_cache_directories()
        
        assert isinstance(cache_dirs, list)
        assert len(cache_dirs) > 0
    
    def test_data_directories_not_empty(self):
        """测试数据目录列表不为空"""
        detector = PlatformDetector()
        data_dirs = detector.get_data_directories()
        
        assert isinstance(data_dirs, list)
        assert len(data_dirs) > 0
    
    def test_executable_extensions_not_empty(self):
        """测试可执行文件扩展名列表不为空"""
        detector = PlatformDetector()
        extensions = detector.get_executable_extensions()
        
        assert isinstance(extensions, list)
        assert len(extensions) > 0
    
    def test_windows_specific_paths(self):
        """测试 Windows 特定路径格式"""
        detector = PlatformDetector()
        
        if detector.get_platform() == PlatformDetector.PLATFORM_WINDOWS:
            config_dirs = detector.get_config_directories()
            
            # Windows 路径应包含 AppData 或 .opencode
            has_appdata = any('AppData' in path or '.opencode' in path for path in config_dirs)
            assert has_appdata, "Windows 配置目录应包含 AppData 路径"
            
            # Windows 可执行文件扩展名应包含 .exe
            extensions = detector.get_executable_extensions()
            assert '.exe' in extensions, "Windows 应支持 .exe 扩展名"
            assert '.cmd' in extensions, "Windows 应支持 .cmd 扩展名"
    
    def test_unix_specific_paths(self):
        """测试 Unix (macOS/Linux) 特定路径格式"""
        detector = PlatformDetector()
        
        if detector.get_platform() in [PlatformDetector.PLATFORM_MACOS, PlatformDetector.PLATFORM_LINUX]:
            config_dirs = detector.get_config_directories()
            
            # Unix 路径应包含 .opencode 或 .config/opencode
            has_unix_path = any('.opencode' in path or '.config/opencode' in path for path in config_dirs)
            assert has_unix_path, "Unix 配置目录应包含 .opencode 或 .config/opencode"
            
            # Unix 可执行文件通常没有扩展名
            extensions = detector.get_executable_extensions()
            assert '' in extensions, "Unix 应支持无扩展名的可执行文件"
    
    def test_macos_specific_paths(self):
        """测试 macOS 特定路径格式"""
        detector = PlatformDetector()
        
        if detector.get_platform() == PlatformDetector.PLATFORM_MACOS:
            cache_dirs = detector.get_cache_directories()
            data_dirs = detector.get_data_directories()
            
            # macOS 缓存应在 Library/Caches
            has_library_caches = any('Library/Caches' in path for path in cache_dirs)
            assert has_library_caches, "macOS 缓存目录应在 Library/Caches"
            
            # macOS 数据应在 Library/Application Support
            has_app_support = any('Application Support' in path for path in data_dirs)
            assert has_app_support, "macOS 数据目录应在 Library/Application Support"
    
    def test_linux_specific_paths(self):
        """测试 Linux 特定路径格式"""
        detector = PlatformDetector()
        
        if detector.get_platform() == PlatformDetector.PLATFORM_LINUX:
            cache_dirs = detector.get_cache_directories()
            data_dirs = detector.get_data_directories()
            
            # Linux 缓存应在 .cache
            has_cache = any('.cache' in path for path in cache_dirs)
            assert has_cache, "Linux 缓存目录应在 .cache"
            
            # Linux 数据应在 .local/share
            has_local_share = any('.local/share' in path or '.local\\share' in path for path in data_dirs)
            assert has_local_share, "Linux 数据目录应在 .local/share"
    
    def test_package_manager_directories(self):
        """测试包管理器目录列表"""
        detector = PlatformDetector()
        pm_dirs = detector.get_package_manager_directories()
        
        assert isinstance(pm_dirs, list)
        # 应该至少有一些包管理器目录
        assert len(pm_dirs) > 0
    
    def test_get_all_paths_returns_platform_paths(self):
        """测试 get_all_paths 返回完整的 PlatformPaths 对象"""
        detector = PlatformDetector()
        paths = detector.get_all_paths()
        
        from models import PlatformPaths
        assert isinstance(paths, PlatformPaths)
        
        # 验证所有字段都有值
        assert len(paths.config_dirs) > 0
        assert len(paths.cache_dirs) > 0
        assert len(paths.data_dirs) > 0
        assert len(paths.executable_extensions) > 0
    
    def test_paths_are_absolute(self):
        """测试返回的路径是绝对路径"""
        detector = PlatformDetector()
        
        for path in detector.get_config_directories():
            assert os.path.isabs(path), f"配置目录路径应为绝对路径: {path}"
        
        for path in detector.get_cache_directories():
            assert os.path.isabs(path), f"缓存目录路径应为绝对路径: {path}"
        
        for path in detector.get_data_directories():
            assert os.path.isabs(path), f"数据目录路径应为绝对路径: {path}"


class TestPlatformPathsConsistency:
    """测试平台路径的一致性"""
    
    def test_no_duplicate_config_dirs(self):
        """测试配置目录没有重复"""
        detector = PlatformDetector()
        config_dirs = detector.get_config_directories()
        
        # 规范化路径后检查重复
        normalized = [os.path.normpath(p) for p in config_dirs]
        assert len(normalized) == len(set(normalized)), "配置目录不应有重复"
    
    def test_no_duplicate_cache_dirs(self):
        """测试缓存目录没有重复"""
        detector = PlatformDetector()
        cache_dirs = detector.get_cache_directories()
        
        normalized = [os.path.normpath(p) for p in cache_dirs]
        assert len(normalized) == len(set(normalized)), "缓存目录不应有重复"
    
    def test_no_duplicate_data_dirs(self):
        """测试数据目录没有重复"""
        detector = PlatformDetector()
        data_dirs = detector.get_data_directories()
        
        normalized = [os.path.normpath(p) for p in data_dirs]
        assert len(normalized) == len(set(normalized)), "数据目录不应有重复"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
