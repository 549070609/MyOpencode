# Requirements Document

## Introduction

实现 opencode 的彻底删除功能，确保在卸载时能够清理所有相关的可执行文件、配置目录、缓存数据和项目残留文件。该功能需要支持 Windows、macOS 和 Linux 平台，并提供用户确认机制以避免误删重要数据。

## Glossary

- **Uninstaller**: 负责执行 opencode 彻底删除操作的系统组件
- **Config_Directory**: opencode 存储用户配置的目录（如 `~/.opencode`、`~/.config/opencode`）
- **Cache_Directory**: opencode 存储缓存数据的目录
- **Data_Directory**: opencode 存储运行时数据的目录
- **Project_Directory**: 项目中的 `.opencode` 目录
- **Executable_File**: opencode 的可执行文件（如 `opencode.exe`、`opencode.cmd`）
- **Package_Manager**: 用于安装/卸载 opencode 的包管理器（npm、bun、pnpm、yarn、scoop、choco）

## Requirements

### Requirement 1: 可执行文件清理

**User Story:** As a user, I want to remove all opencode executable files, so that the command is no longer available in my system.

#### Acceptance Criteria

1. WHEN the Uninstaller runs, THE Uninstaller SHALL detect all opencode executable files using system path lookup
2. WHEN executable files are found, THE Uninstaller SHALL remove each executable file and report the result
3. WHEN an executable file cannot be removed, THE Uninstaller SHALL report the failure reason and continue with other files
4. THE Uninstaller SHALL check common installation locations including bun global directory, npm global directory, and system PATH locations

### Requirement 2: 包管理器卸载

**User Story:** As a user, I want opencode to be uninstalled from all package managers, so that no package manager references remain.

#### Acceptance Criteria

1. THE Uninstaller SHALL attempt to uninstall opencode using all supported package managers (npm, bun, pnpm, yarn, scoop, choco)
2. WHEN a package manager is not installed, THE Uninstaller SHALL skip that package manager silently
3. WHEN a package manager uninstall succeeds, THE Uninstaller SHALL report the success
4. WHEN a package manager uninstall fails, THE Uninstaller SHALL report the failure and continue with other package managers

### Requirement 3: 配置目录清理

**User Story:** As a user, I want to remove all opencode configuration directories, so that no personal settings remain on my system.

#### Acceptance Criteria

1. THE Uninstaller SHALL detect opencode configuration directories at standard locations:
   - Windows: `%USERPROFILE%\.opencode`, `%APPDATA%\opencode`, `%LOCALAPPDATA%\opencode`
   - macOS/Linux: `~/.opencode`, `~/.config/opencode`
2. WHEN configuration directories are found, THE Uninstaller SHALL prompt the user for confirmation before deletion
3. WHEN the user confirms deletion, THE Uninstaller SHALL remove the configuration directories recursively
4. WHEN the user declines deletion, THE Uninstaller SHALL skip the configuration directory cleanup
5. IF deletion fails, THEN THE Uninstaller SHALL report the failure reason

### Requirement 4: 缓存和数据目录清理

**User Story:** As a user, I want to remove all opencode cache and data directories, so that no temporary files remain on my system.

#### Acceptance Criteria

1. THE Uninstaller SHALL detect opencode cache directories at standard locations:
   - Windows: `%LOCALAPPDATA%\opencode\cache`, `%TEMP%\opencode`
   - macOS: `~/Library/Caches/opencode`
   - Linux: `~/.cache/opencode`
2. THE Uninstaller SHALL detect opencode data directories at standard locations:
   - Windows: `%LOCALAPPDATA%\opencode\data`
   - macOS: `~/Library/Application Support/opencode`
   - Linux: `~/.local/share/opencode`
3. WHEN cache or data directories are found, THE Uninstaller SHALL remove them without additional confirmation
4. IF deletion fails, THEN THE Uninstaller SHALL report the failure reason and continue

### Requirement 5: 项目目录清理选项

**User Story:** As a user, I want the option to remove `.opencode` directories from my projects, so that I can completely clean up opencode traces.

#### Acceptance Criteria

1. THE Uninstaller SHALL ask the user if they want to scan for project `.opencode` directories
2. WHEN the user agrees to scan, THE Uninstaller SHALL prompt for a root directory to scan
3. WHEN scanning, THE Uninstaller SHALL find all `.opencode` directories under the specified root
4. WHEN `.opencode` directories are found, THE Uninstaller SHALL list them and ask for confirmation before deletion
5. WHEN the user confirms, THE Uninstaller SHALL remove the selected `.opencode` directories
6. WHEN the user declines, THE Uninstaller SHALL skip project directory cleanup

### Requirement 6: 清理报告

**User Story:** As a user, I want to see a summary of what was cleaned up, so that I know the uninstallation was complete.

#### Acceptance Criteria

1. WHEN the uninstallation completes, THE Uninstaller SHALL display a summary report
2. THE summary report SHALL include:
   - Number of executable files removed
   - Package managers that successfully uninstalled opencode
   - Configuration directories removed
   - Cache and data directories removed
   - Project directories removed (if applicable)
   - Any failures encountered
3. THE Uninstaller SHALL indicate whether the uninstallation was complete or partial

### Requirement 7: 跨平台支持

**User Story:** As a user on any operating system, I want the uninstaller to work correctly on my platform.

#### Acceptance Criteria

1. THE Uninstaller SHALL detect the current operating system (Windows, macOS, Linux)
2. THE Uninstaller SHALL use platform-appropriate paths and commands
3. WHEN running on Windows, THE Uninstaller SHALL handle Windows-specific paths and file extensions
4. WHEN running on macOS or Linux, THE Uninstaller SHALL handle Unix-style paths and permissions

### Requirement 8: 安全确认机制

**User Story:** As a user, I want to confirm before any destructive operations, so that I don't accidentally delete important data.

#### Acceptance Criteria

1. WHEN starting the uninstallation, THE Uninstaller SHALL display a warning about the operation
2. THE Uninstaller SHALL require explicit user confirmation before proceeding
3. THE Uninstaller SHALL provide a "dry run" option to preview what will be deleted without actually deleting
4. WHEN in dry run mode, THE Uninstaller SHALL list all items that would be deleted but not delete them
