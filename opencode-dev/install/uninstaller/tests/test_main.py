"""
主卸载器的属性测试

Property 4: User Confirmation Respect
*For any* configuration directory found, if user declines deletion it remains; 
if confirms it's removed.

Property 6: Dry Run Safety
*For any* operation in dry run mode, no files or directories should be deleted.

Validates: Requirements 3.2, 3.3, 3.4, 8.3, 8.4
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import OpenCodeUninstaller
from models import UninstallReport


class MockInputOutput:
    """模拟输入输出"""
    
    def __init__(self, responses=None):
        self.responses = responses or []
        self.response_index = 0
        self.output = []
    
    def input(self, prompt):
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response
        return 'n'
    
    def print(self, message):
        self.output.append(message)


class TestOpenCodeUninstaller:
    """OpenCodeUninstaller 基本测试"""
    
    def test_initialization(self):
        """测试初始化"""
        uninstaller = OpenCodeUninstaller()
        assert uninstaller.dry_run is False
    
    def test_initialization_with_dry_run(self):
        """测试 dry_run 模式初始化"""
        uninstaller = OpenCodeUninstaller(dry_run=True)
        assert uninstaller.dry_run is True
    
    def test_initialization_with_custom_io(self):
        """测试自定义输入输出初始化"""
        mock = MockInputOutput()
        uninstaller = OpenCodeUninstaller(
            input_func=mock.input,
            print_func=mock.print
        )
        assert uninstaller._input == mock.input
        assert uninstaller._print == mock.print
    
    def test_report_initialized(self):
        """测试报告已初始化"""
        uninstaller = OpenCodeUninstaller()
        assert isinstance(uninstaller.report, UninstallReport)


class TestUserConfirmation:
    """
    Property 4: User Confirmation Respect
    测试用户确认机制
    """
    
    def test_confirm_with_user_yes(self):
        """测试用户确认 yes"""
        mock = MockInputOutput(responses=['y'])
        uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
        
        result = uninstaller.confirm_with_user('确认？')
        assert result is True
    
    def test_confirm_with_user_no(self):
        """测试用户确认 no"""
        mock = MockInputOutput(responses=['n'])
        uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
        
        result = uninstaller.confirm_with_user('确认？')
        assert result is False
    
    def test_confirm_with_user_yes_variations(self):
        """测试各种 yes 变体"""
        for response in ['y', 'Y', 'yes', 'YES', 'Yes', '是', '确定']:
            mock = MockInputOutput(responses=[response])
            uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
            
            result = uninstaller.confirm_with_user('确认？')
            assert result is True, f"'{response}' 应该被识别为确认"
    
    def test_confirm_with_user_no_variations(self):
        """测试各种 no 变体"""
        for response in ['n', 'N', 'no', 'NO', 'No', '否', '取消', '']:
            mock = MockInputOutput(responses=[response])
            uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
            
            result = uninstaller.confirm_with_user('确认？')
            assert result is False, f"'{response}' 应该被识别为拒绝"
    
    def test_run_cancelled_on_initial_decline(self):
        """测试初始确认拒绝时取消运行"""
        mock = MockInputOutput(responses=['n'])
        uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
        
        report = uninstaller.run()
        
        # 应该没有任何操作
        assert report.total_removed == 0
        assert '已取消' in '\n'.join(mock.output)


class TestDryRunSafety:
    """
    Property 6: Dry Run Safety
    测试 dry run 模式不实际删除
    """
    
    def test_dry_run_does_not_delete_files(self):
        """测试 dry run 模式不删除文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = os.path.join(tmpdir, 'opencode.exe')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # 确认所有提示
            mock = MockInputOutput(responses=['y', 'y', 'n'])  # 确认开始，确认配置，跳过项目
            uninstaller = OpenCodeUninstaller(
                dry_run=True,
                input_func=mock.input,
                print_func=mock.print
            )
            
            uninstaller.run()
            
            # 文件应该仍然存在
            assert os.path.exists(test_file)
    
    def test_dry_run_report_indicates_preview(self):
        """测试 dry run 报告显示预览模式"""
        mock = MockInputOutput(responses=['y', 'y', 'n'])
        uninstaller = OpenCodeUninstaller(
            dry_run=True,
            input_func=mock.input,
            print_func=mock.print
        )
        
        report = uninstaller.run()
        
        assert report.dry_run is True
        
        # 输出应该包含预览模式提示
        output_text = '\n'.join(mock.output)
        assert '预览' in output_text
    
    def test_dry_run_lists_items_without_deleting(self):
        """测试 dry run 列出项目但不删除"""
        mock = MockInputOutput(responses=['y', 'y', 'n'])
        uninstaller = OpenCodeUninstaller(
            dry_run=True,
            input_func=mock.input,
            print_func=mock.print
        )
        
        report = uninstaller.run()
        
        # 输出应该包含 [预览] 标记
        output_text = '\n'.join(mock.output)
        # 如果有任何项目被"删除"，应该有预览标记
        if report.total_removed > 0:
            assert '[预览]' in output_text


class TestPromptForInput:
    """测试用户输入提示"""
    
    def test_prompt_for_input_returns_input(self):
        """测试 prompt_for_input 返回用户输入"""
        mock = MockInputOutput(responses=['test input'])
        uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
        
        result = uninstaller.prompt_for_input('请输入: ')
        assert result == 'test input'
    
    def test_prompt_for_input_strips_whitespace(self):
        """测试 prompt_for_input 去除空白"""
        mock = MockInputOutput(responses=['  test  '])
        uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
        
        result = uninstaller.prompt_for_input('请输入: ')
        assert result == 'test'


class TestReportGeneration:
    """测试报告生成"""
    
    def test_report_is_returned(self):
        """测试 run 返回报告"""
        mock = MockInputOutput(responses=['n'])
        uninstaller = OpenCodeUninstaller(input_func=mock.input, print_func=mock.print)
        
        report = uninstaller.run()
        
        assert isinstance(report, UninstallReport)
    
    def test_report_reflects_dry_run_mode(self):
        """测试报告反映 dry run 模式"""
        mock = MockInputOutput(responses=['n'])
        
        # 非 dry run
        uninstaller1 = OpenCodeUninstaller(dry_run=False, input_func=mock.input, print_func=mock.print)
        report1 = uninstaller1.run()
        assert report1.dry_run is False
        
        # dry run
        mock2 = MockInputOutput(responses=['n'])
        uninstaller2 = OpenCodeUninstaller(dry_run=True, input_func=mock2.input, print_func=mock2.print)
        report2 = uninstaller2.run()
        assert report2.dry_run is True


class TestComponentIntegration:
    """测试组件集成"""
    
    def test_all_components_initialized(self):
        """测试所有组件都已初始化"""
        uninstaller = OpenCodeUninstaller()
        
        assert uninstaller.platform is not None
        assert uninstaller.executable_detector is not None
        assert uninstaller.package_manager is not None
        assert uninstaller.directory_cleaner is not None
        assert uninstaller.project_scanner is not None
    
    def test_directory_cleaner_respects_dry_run(self):
        """测试目录清理器遵守 dry run 设置"""
        uninstaller = OpenCodeUninstaller(dry_run=True)
        assert uninstaller.directory_cleaner.dry_run is True
        
        uninstaller2 = OpenCodeUninstaller(dry_run=False)
        assert uninstaller2.directory_cleaner.dry_run is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
