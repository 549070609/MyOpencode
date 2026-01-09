"""
目录清理器的属性测试

Property 1: File Deletion Completeness
*For any* list of detected files/directories, when deletion is executed, 
each should either be successfully deleted or have a failure reason recorded.

Property 9: Continuation After Failure
*For any* failure during the uninstall process, the uninstaller should 
continue processing remaining items and not terminate early.

Validates: Requirements 1.2, 1.3, 4.4
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from directory_cleaner import DirectoryCleaner
from models import RemoveResult


class TestDirectoryCleaner:
    """DirectoryCleaner 基本测试"""
    
    def test_initialization(self):
        """测试初始化"""
        cleaner = DirectoryCleaner()
        assert cleaner.dry_run is False
    
    def test_initialization_with_dry_run(self):
        """测试 dry_run 模式初始化"""
        cleaner = DirectoryCleaner(dry_run=True)
        assert cleaner.dry_run is True
    
    def test_find_directories_returns_list(self):
        """测试 find_directories 返回列表"""
        cleaner = DirectoryCleaner()
        result = cleaner.find_directories([])
        assert isinstance(result, list)
    
    def test_find_files_returns_list(self):
        """测试 find_files 返回列表"""
        cleaner = DirectoryCleaner()
        result = cleaner.find_files([])
        assert isinstance(result, list)


class TestFindDirectories:
    """测试目录查找功能"""
    
    def test_find_existing_directory(self):
        """测试查找存在的目录"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cleaner.find_directories([tmpdir])
            assert len(result) == 1
            assert os.path.normpath(tmpdir) in result[0]
    
    def test_find_nonexistent_directory(self):
        """测试查找不存在的目录"""
        cleaner = DirectoryCleaner()
        result = cleaner.find_directories(['/nonexistent/path/12345'])
        assert len(result) == 0
    
    def test_find_mixed_directories(self):
        """测试查找混合的目录（存在和不存在）"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = [tmpdir, '/nonexistent/path/12345']
            result = cleaner.find_directories(paths)
            assert len(result) == 1
    
    def test_find_file_not_included_as_directory(self):
        """测试文件不会被当作目录返回"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 在临时目录中创建文件
            filepath = os.path.join(tmpdir, 'test.txt')
            with open(filepath, 'w') as f:
                f.write('test')
            
            result = cleaner.find_directories([filepath])
            assert len(result) == 0


class TestRemoveDirectory:
    """测试目录删除功能"""
    
    def test_remove_existing_directory(self):
        """测试删除存在的目录"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as parent:
            # 创建一个子目录
            subdir = os.path.join(parent, 'test_subdir')
            os.makedirs(subdir)
            
            # 在子目录中创建文件
            test_file = os.path.join(subdir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # 删除子目录
            result = cleaner.remove_directory(subdir)
            
            assert result.success is True
            assert result.error is None
            assert not os.path.exists(subdir)
    
    def test_remove_nonexistent_directory(self):
        """测试删除不存在的目录（应该成功）"""
        cleaner = DirectoryCleaner()
        result = cleaner.remove_directory('/nonexistent/path/12345')
        
        assert result.success is True
        assert result.error is None
    
    def test_remove_file_as_directory_fails(self):
        """测试删除文件作为目录失败"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 在临时目录中创建文件
            filepath = os.path.join(tmpdir, 'test.txt')
            with open(filepath, 'w') as f:
                f.write('test')
            
            result = cleaner.remove_directory(filepath)
            assert result.success is False
            assert '不是目录' in result.error


class TestRemoveFile:
    """测试文件删除功能"""
    
    def test_remove_existing_file(self):
        """测试删除存在的文件"""
        cleaner = DirectoryCleaner()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            filepath = tmpfile.name
        
        result = cleaner.remove_file(filepath)
        
        assert result.success is True
        assert result.error is None
        assert not os.path.exists(filepath)
    
    def test_remove_nonexistent_file(self):
        """测试删除不存在的文件（应该成功）"""
        cleaner = DirectoryCleaner()
        result = cleaner.remove_file('/nonexistent/file/12345.txt')
        
        assert result.success is True
        assert result.error is None


class TestDryRunMode:
    """
    Property 6 相关: Dry Run Safety
    测试 dry run 模式不实际删除
    """
    
    def test_dry_run_does_not_delete_directory(self):
        """测试 dry run 模式不删除目录"""
        cleaner = DirectoryCleaner(dry_run=True)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建子目录
            subdir = os.path.join(tmpdir, 'test_subdir')
            os.makedirs(subdir)
            
            result = cleaner.remove_directory(subdir)
            
            assert result.success is True
            assert os.path.exists(subdir)  # 目录应该仍然存在
    
    def test_dry_run_does_not_delete_file(self):
        """测试 dry run 模式不删除文件"""
        cleaner = DirectoryCleaner(dry_run=True)
        
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            filepath = tmpfile.name
        
        try:
            result = cleaner.remove_file(filepath)
            
            assert result.success is True
            assert os.path.exists(filepath)  # 文件应该仍然存在
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestFileDeletionCompleteness:
    """
    Property 1: File Deletion Completeness
    测试每个文件/目录要么成功删除，要么有失败原因
    """
    
    def test_all_results_have_status(self):
        """测试所有结果都有状态"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建多个子目录
            subdirs = []
            for i in range(3):
                subdir = os.path.join(tmpdir, f'subdir_{i}')
                os.makedirs(subdir)
                subdirs.append(subdir)
            
            results = cleaner.remove_directories(subdirs)
            
            assert len(results) == 3
            for result in results:
                assert isinstance(result, RemoveResult)
                assert isinstance(result.success, bool)
                assert result.path is not None
    
    def test_failed_deletion_has_error_message(self):
        """测试失败的删除有错误消息"""
        cleaner = DirectoryCleaner()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            filepath = tmpfile.name
        
        try:
            # 尝试将文件作为目录删除
            result = cleaner.remove_directory(filepath)
            
            assert result.success is False
            assert result.error is not None
            assert len(result.error) > 0
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestContinuationAfterFailure:
    """
    Property 9: Continuation After Failure
    测试失败后继续处理
    """
    
    def test_continues_after_failure(self):
        """测试一个失败不会阻止其他操作"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一个有效目录
            valid_dir = os.path.join(tmpdir, 'valid')
            os.makedirs(valid_dir)
            
            # 创建一个文件（作为目录删除会失败）
            invalid_path = os.path.join(tmpdir, 'invalid.txt')
            with open(invalid_path, 'w') as f:
                f.write('test')
            
            # 另一个有效目录
            valid_dir2 = os.path.join(tmpdir, 'valid2')
            os.makedirs(valid_dir2)
            
            paths = [valid_dir, invalid_path, valid_dir2]
            results = cleaner.remove_directories(paths)
            
            # 应该有 3 个结果
            assert len(results) == 3
            
            # 第一个和第三个应该成功
            assert results[0].success is True
            assert results[2].success is True
            
            # 第二个应该失败（因为是文件不是目录）
            assert results[1].success is False
    
    def test_batch_remove_processes_all(self):
        """测试批量删除处理所有项目"""
        cleaner = DirectoryCleaner()
        
        paths = [
            '/nonexistent/path/1',
            '/nonexistent/path/2',
            '/nonexistent/path/3',
        ]
        
        results = cleaner.remove_directories(paths)
        
        # 应该处理所有路径
        assert len(results) == len(paths)


class TestRemovePaths:
    """测试 remove_paths 方法"""
    
    def test_remove_mixed_paths(self):
        """测试删除混合路径（文件和目录）"""
        cleaner = DirectoryCleaner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建目录
            subdir = os.path.join(tmpdir, 'subdir')
            os.makedirs(subdir)
            
            # 创建文件
            filepath = os.path.join(tmpdir, 'file.txt')
            with open(filepath, 'w') as f:
                f.write('test')
            
            paths = [subdir, filepath]
            results = cleaner.remove_paths(paths)
            
            assert len(results) == 2
            assert all(r.success for r in results)
            assert not os.path.exists(subdir)
            assert not os.path.exists(filepath)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
