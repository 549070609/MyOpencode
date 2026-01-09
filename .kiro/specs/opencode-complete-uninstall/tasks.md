# Implementation Plan: OpenCode Complete Uninstall

## Overview

将 `create_doc.py` 扩展为完整的 opencode 卸载工具，实现模块化的组件架构，支持彻底删除、dry run 预览、项目目录扫描和详细报告。

## Tasks

- [x] 1. 创建数据模型和基础结构
  - [x] 1.1 创建 `uninstaller/models.py` 定义数据类
    - 实现 `UninstallResult`、`RemoveResult`、`PlatformPaths`、`UninstallReport` 数据类
    - _Requirements: 6.2_
  - [x] 1.2 编写数据模型的属性测试
    - **Property 7: Report Completeness**
    - **Validates: Requirements 6.2, 6.3**

- [x] 2. 实现平台检测器
  - [x] 2.1 创建 `uninstaller/platform_detector.py`
    - 实现 `PlatformDetector` 类
    - 实现 `get_platform()`、`get_config_directories()`、`get_cache_directories()`、`get_data_directories()`、`get_executable_extensions()` 方法
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [x] 2.2 编写平台路径正确性的属性测试
    - **Property 5: Platform Path Correctness**
    - **Validates: Requirements 7.2, 7.3, 7.4**

- [x] 3. 实现可执行文件检测器
  - [x] 3.1 创建 `uninstaller/executable_detector.py`
    - 实现 `ExecutableDetector` 类
    - 实现 `find_executables()`、`find_in_path()`、`find_in_package_manager_dirs()` 方法
    - _Requirements: 1.1, 1.4_
  - [x] 3.2 编写可执行文件检测的单元测试
    - 测试 PATH 查找逻辑
    - 测试包管理器目录查找
    - _Requirements: 1.1, 1.4_

- [x] 4. 实现包管理器卸载器
  - [x] 4.1 创建 `uninstaller/package_manager.py`
    - 实现 `PackageManagerUninstaller` 类
    - 实现 `get_supported_managers()`、`is_manager_available()`、`uninstall()`、`uninstall_all()` 方法
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 4.2 编写包管理器处理的属性测试
    - **Property 2: Package Manager Attempt Coverage**
    - **Property 3: Missing Package Manager Handling**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [x] 5. 实现目录清理器
  - [x] 5.1 创建 `uninstaller/directory_cleaner.py`
    - 实现 `DirectoryCleaner` 类
    - 实现 `find_directories()`、`remove_directory()`、`remove_directories()` 方法
    - _Requirements: 3.1, 3.3, 4.1, 4.2, 4.3_
  - [x] 5.2 编写目录清理的属性测试
    - **Property 1: File Deletion Completeness**
    - **Property 9: Continuation After Failure**
    - **Validates: Requirements 1.2, 1.3, 4.4**

- [x] 6. 实现项目扫描器
  - [x] 6.1 创建 `uninstaller/project_scanner.py`
    - 实现 `ProjectScanner` 类
    - 实现 `scan()` 方法，递归查找 `.opencode` 目录
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 6.2 编写项目扫描的属性测试
    - **Property 8: Project Directory Scan Completeness**
    - **Validates: Requirements 5.3**

- [x] 7. 实现主卸载器
  - [x] 7.1 创建 `uninstaller/main.py`
    - 实现 `OpenCodeUninstaller` 类
    - 实现 `run()`、`confirm_with_user()`、`prompt_for_input()` 方法
    - 集成所有组件
    - _Requirements: 8.1, 8.2_
  - [x] 7.2 编写用户确认和 dry run 的属性测试
    - **Property 4: User Confirmation Respect**
    - **Property 6: Dry Run Safety**
    - **Validates: Requirements 3.2, 3.3, 3.4, 8.3, 8.4**

- [x] 8. 集成到 create_doc.py
  - [x] 8.1 更新 `create_doc.py` 使用新的卸载器
    - 导入并使用 `OpenCodeUninstaller`
    - 添加 dry run 选项
    - 保持向后兼容的用户界面
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 9. Checkpoint - 确保所有测试通过
  - 运行所有单元测试和属性测试
  - 确保所有测试通过，如有问题请询问用户

- [x] 10. 最终集成测试
  - [x] 10.1 手动测试完整卸载流程
    - 测试 dry run 模式
    - 测试实际删除模式
    - 测试项目目录扫描
    - _Requirements: 6.1, 6.3_

## Notes

- 所有任务均为必需，包括测试任务
- 使用 Python 标准库，避免额外依赖
- 属性测试使用 hypothesis 库
- 所有文件操作需要处理权限错误
- 保持与现有 `create_doc.py` 的用户界面一致性
