"""
OpenCode 安装/卸载工具

提供 opencode 和 oh-my-opencode 的安装和彻底删除功能。
"""

import subprocess
import os
import sys
import json
import platform

# 添加 uninstaller 模块到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
install_dir = os.path.dirname(script_dir)  # install 目录
uninstaller_dir = os.path.join(install_dir, 'uninstaller')
sys.path.insert(0, uninstaller_dir)

from main import OpenCodeUninstaller


def set_permanent_env_var(name, value):
    """设置永久环境变量（Windows）"""
    if platform.system() == 'Windows':
        try:
            # 使用 setx 命令设置用户级环境变量
            subprocess.run(['setx', name, value], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f'setx 命令失败: {e}')
    else:
        # Linux/macOS 需要手动添加到 shell 配置文件
        print(f'请手动将以下行添加到你的 shell 配置文件 (~/.bashrc 或 ~/.zshrc):')
        print(f'export {name}="{value}"')
        return False


def remove_permanent_env_var(name):
    """删除永久环境变量（Windows）"""
    if platform.system() == 'Windows':
        try:
            # 使用 reg 命令删除用户环境变量
            subprocess.run([
                'reg', 'delete', 
                'HKEY_CURRENT_USER\\Environment', 
                '/v', name, '/f'
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            # 环境变量可能不存在，这是正常的
            return False
    else:
        print(f'请手动从 shell 配置文件中删除: export {name}=...')
        return False


def get_opencode_env_vars():
    """获取 OpenCode 相关的环境变量列表"""
    # 常见的 AI API 环境变量
    common_env_vars = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY', 
        'GOOGLE_GENERATIVE_AI_API_KEY',
        'NVIDIA_API_KEY',
        'CUSTOM_OPENAI_API_KEY',
        'CUSTOM_API_KEY',
        'OLLAMA_API_KEY',
        'CLAUDE_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    # 从配置文件中读取自定义环境变量
    try:
        home_dir = os.path.expanduser('~')
        config_path = os.path.join(home_dir, '.config', 'opencode', 'opencode.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'provider' in config:
                    for provider_config in config['provider'].values():
                        if 'env' in provider_config:
                            common_env_vars.extend(provider_config['env'])
    except:
        pass
    
    # 去重并返回
    return list(set(common_env_vars))


def check_opencode_installed():
    """检查 opencode 是否已安装"""
    try:
        result = subprocess.run(['opencode', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            return version
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None


def check_oh_my_opencode_installed():
    """检查 oh-my-opencode 是否已安装"""
    try:
        # 检查全局安装
        result = subprocess.run(['bun', 'pm', 'ls', '-g'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'oh-my-opencode' in result.stdout:
            return True
        
        # 检查配置文件中的插件
        home_dir = os.path.expanduser('~')
        config_path = os.path.join(home_dir, '.config', 'opencode', 'opencode.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'plugin' in config and 'oh-my-opencode' in config['plugin']:
                    return True
    except:
        pass
    return False


def get_source_version(source_dir):
    """获取源码版本"""
    package_json = os.path.join(source_dir, 'package.json')
    if os.path.exists(package_json):
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', 'unknown')
        except:
            pass
    return 'unknown'


def get_script_dir():
    """获取脚本所在目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 返回 install 目录


def get_install_dir():
    """获取 install 目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_dir():
    """获取配置文件目录"""
    install_dir = get_install_dir()
    return os.path.join(install_dir, 'config')


def fix_bun_global_package_json():
    """确保 bun 全局目录有有效的 package.json"""
    home_dir = os.path.expanduser('~')
    bun_global_dir = os.path.join(home_dir, '.bun', 'install', 'global')
    package_json_path = os.path.join(bun_global_dir, 'package.json')
    
    # 确保目录存在
    os.makedirs(bun_global_dir, exist_ok=True)
    
    # 检查 package.json 是否存在且有效
    needs_fix = False
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'name' not in data:
                    needs_fix = True
        except:
            needs_fix = True
    else:
        needs_fix = True
    
    if needs_fix:
        package_data = {
            "name": "bun-global",
            "version": "1.0.0",
            "private": True,
            "dependencies": {}
        }
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2)
        print('✓ 已修复 bun 全局 package.json')


def install_opencode_exe(opencode_dev_dir):
    """将构建好的 opencode.exe 安装到 bun bin 目录"""
    import shutil
    import platform
    
    home_dir = os.path.expanduser('~')
    bun_bin_dir = os.path.join(home_dir, '.bun', 'bin')
    
    # 确保目录存在
    os.makedirs(bun_bin_dir, exist_ok=True)
    
    # 确定平台对应的构建目录
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == 'windows':
        platform_name = 'windows'
        exe_name = 'opencode.exe'
    elif system == 'darwin':
        platform_name = 'darwin'
        exe_name = 'opencode'
    else:
        platform_name = 'linux'
        exe_name = 'opencode'
    
    if arch in ('amd64', 'x86_64'):
        arch_name = 'x64'
    elif arch in ('arm64', 'aarch64'):
        arch_name = 'arm64'
    else:
        arch_name = 'x64'
    
    dist_dir = os.path.join(opencode_dev_dir, 'packages', 'opencode', 'dist')
    build_name = f'opencode-{platform_name}-{arch_name}'
    exe_src = os.path.join(dist_dir, build_name, 'bin', exe_name)
    exe_dst = os.path.join(bun_bin_dir, exe_name)
    
    if not os.path.exists(exe_src):
        # 尝试查找任何可用的构建
        for item in os.listdir(dist_dir):
            item_path = os.path.join(dist_dir, item, 'bin', exe_name)
            if os.path.exists(item_path):
                exe_src = item_path
                break
    
    if os.path.exists(exe_src):
        shutil.copy2(exe_src, exe_dst)
        print(f'✓ 已安装 {exe_name} 到 {bun_bin_dir}')
        
        # 检查 bun bin 是否在 PATH 中
        path_env = os.environ.get('PATH', '')
        if bun_bin_dir.lower() not in path_env.lower():
            print(f'\n⚠ 注意: {bun_bin_dir} 可能不在 PATH 中')
            print(f'  请将以下目录添加到系统 PATH 环境变量:')
            print(f'  {bun_bin_dir}')
    else:
        raise FileNotFoundError(f'未找到构建的可执行文件: {exe_src}')


def fix_git_issue(opencode_dev_dir):
    """修复非 git 仓库的构建问题"""
    script_path = os.path.join(opencode_dev_dir, 'packages', 'script', 'src', 'index.ts')
    
    if not os.path.exists(script_path):
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修复过
    if 'try { return await $`git branch' in content:
        return True
    
    # 备份
    backup_path = script_path + '.backup'
    if not os.path.exists(backup_path):
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 修复 git 命令，使其在非 git 仓库中也能工作
    old_code = 'return await $`git branch --show-current`.text().then((x) => x.trim())'
    new_code = 'try { return await $`git branch --show-current`.text().then((x) => x.trim()) } catch { return "main" }'
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✓ 已修复 git 仓库检测问题')
        return True
    
    return False


def fix_parser_worker_path(opencode_dev_dir):
    """修复 parser.worker.js 路径问题（monorepo 结构）"""
    script_path = os.path.join(opencode_dev_dir, 'packages', 'opencode', 'script', 'build.ts')
    
    if not os.path.exists(script_path):
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 备份
    backup_path = script_path + '.parser-backup'
    if not os.path.exists(backup_path):
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 修复 parserWorker 路径查找
    old_parser_code = 'const parserWorker = fs.realpathSync(path.resolve(dir, "./node_modules/@opentui/core/parser.worker.js"))'
    new_parser_code = '''let parserWorker: string
  try {
    parserWorker = fs.realpathSync(path.resolve(dir, "./node_modules/@opentui/core/parser.worker.js"))
  } catch {
    // Fall back to root node_modules (monorepo structure)
    parserWorker = fs.realpathSync(path.resolve(dir, "../../node_modules/@opentui/core/parser.worker.js"))
  }'''
    
    if old_parser_code in content:
        content = content.replace(old_parser_code, new_parser_code)
        modified = True
        print('✓ 已修复 parser.worker.js 路径问题')
    elif 'let parserWorker: string' in content:
        print('✓ parser.worker.js 路径已修复')
    
    if modified:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return modified or 'let parserWorker: string' in content


def restore_fixes(opencode_dev_dir):
    """恢复所有修复"""
    # 恢复 git 修复
    script_path = os.path.join(opencode_dev_dir, 'packages', 'script', 'src', 'index.ts')
    backup_path = script_path + '.backup'
    if os.path.exists(backup_path):
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        os.remove(backup_path)
    
    # 恢复 parser 修复
    parser_script = os.path.join(opencode_dev_dir, 'packages', 'opencode', 'script', 'build.ts')
    parser_backup = parser_script + '.parser-backup'
    if os.path.exists(parser_backup):
        with open(parser_backup, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(parser_script, 'w', encoding='utf-8') as f:
            f.write(content)
        os.remove(parser_backup)


def install_opencode(force=False):
    """安装 opencode"""
    install_dir = get_install_dir()
    # opencode-dev 目录在 install 目录的上级目录
    root_dir = os.path.dirname(install_dir)
    opencode_dev_dir = os.path.join(root_dir, 'opencode-dev')
    
    if not os.path.exists(opencode_dev_dir):
        print(f'错误: 未找到 opencode-dev 目录: {opencode_dev_dir}')
        return False
    
    # 检查是否已安装
    installed_version = check_opencode_installed()
    source_version = get_source_version(opencode_dev_dir)
    
    if installed_version and not force:
        print(f'OpenCode 已安装 (版本: {installed_version})')
        print(f'源码版本: {source_version}')
        
        if installed_version == source_version:
            print('✓ 版本一致，无需重新安装')
            choice = input('是否强制重新安装? (y/N): ').strip().lower()
            if choice not in ('y', 'yes', '是'):
                return True
        else:
            print('版本不一致，建议更新')
            choice = input('是否更新安装? (Y/n): ').strip().lower()
            if choice in ('n', 'no', '否'):
                return True
    
    print(f'正在从 {opencode_dev_dir} 安装 opencode...')
    
    original_dir = os.getcwd()
    fixes_applied = False
    
    try:
        os.chdir(opencode_dev_dir)
        
        # 修复构建问题
        print('预处理: 修复构建脚本...')
        fix_git_issue(opencode_dev_dir)
        fix_parser_worker_path(opencode_dev_dir)
        fixes_applied = True
        
        print('步骤 1: 安装依赖...')
        subprocess.run(['bun', 'install'], check=True)
        print('✓ 依赖安装完成')
        
        print('步骤 2: 构建 opencode...')
        # 设置环境变量避免 git 问题
        # 使用 --single 只构建当前平台，--skip-install 跳过跨平台依赖下载
        env = os.environ.copy()
        env['OPENCODE_CHANNEL'] = 'latest'
        
        # 先安装当前平台的依赖（不使用 --os="*" --cpu="*"）
        print('  安装构建依赖...')
        subprocess.run(['bun', 'install'], cwd='packages/opencode', check=True, env=env)
        
        # 使用 --single --skip-install 避免下载其他平台的 bun 可执行文件
        subprocess.run(['bun', 'run', 'build', '--', '--single', '--skip-install'], cwd='packages/opencode', check=True, env=env)
        print('✓ 构建完成')
        
        print('步骤 3: 安装到全局...')
        # 直接复制构建好的 exe 到 bun bin 目录
        install_opencode_exe(opencode_dev_dir)
        print('✓ 全局安装完成')
        
        print('\n✓ opencode 安装完成！')
        print('你现在可以在任何地方使用 `opencode` 命令')
        
        os.chdir(original_dir)
        
        # 恢复修改
        if fixes_applied:
            restore_fixes(opencode_dev_dir)
        
        return True
        
    except FileNotFoundError:
        print('错误: 未找到 bun，请先安装 bun (https://bun.sh)')
        os.chdir(original_dir)
        if fixes_applied:
            restore_fixes(opencode_dev_dir)
        return False
    except subprocess.CalledProcessError as e:
        print(f'安装失败: {e}')
        os.chdir(original_dir)
        if fixes_applied:
            restore_fixes(opencode_dev_dir)
        return False
    except Exception as e:
        print(f'发生错误: {e}')
        os.chdir(original_dir)
        if fixes_applied:
            restore_fixes(opencode_dev_dir)
        return False


def find_oh_my_opencode_dir():
    """查找 oh-my-opencode 目录"""
    install_dir = get_install_dir()
    root_dir = os.path.dirname(install_dir)
    
    # 可能的路径
    possible_paths = [
        os.path.join(root_dir, '..', 'oh-my-opencode-dev', 'oh-my-opencode-dev'),
        os.path.join(root_dir, '..', 'oh-my-opencode-dev', 'oh-my-opencode-test'),
        os.path.join(root_dir, 'oh-my-opencode'),
        os.path.join(root_dir, '..', 'oh-my-opencode'),
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, 'package.json')):
            return abs_path
    
    return None


def install_oh_my_opencode():
    """安装 oh-my-opencode 插件"""
    oh_my_opencode_dir = find_oh_my_opencode_dir()
    
    if not oh_my_opencode_dir:
        print('错误: 未找到 oh-my-opencode 目录')
        print('请确保 oh-my-opencode 源码目录存在')
        return False
    
    print(f'正在从 {oh_my_opencode_dir} 安装 oh-my-opencode...')
    
    try:
        original_dir = os.getcwd()
        os.chdir(oh_my_opencode_dir)
        
        print('步骤 1: 安装依赖...')
        subprocess.run(['bun', 'install'], check=True)
        print('✓ 依赖安装完成')
        
        print('步骤 2: 构建 oh-my-opencode...')
        subprocess.run(['bun', 'run', 'build'], check=True)
        print('✓ 构建完成')
        
        print('步骤 3: 链接到全局...')
        subprocess.run(['bun', 'link', '--global'], check=True)
        print('✓ 全局链接完成')
        
        # 配置 opencode 使用 oh-my-opencode 插件
        print('步骤 4: 配置 opencode 插件...')
        configure_oh_my_opencode_plugin()
        
        os.chdir(original_dir)
        
        print('\n✓ oh-my-opencode 安装完成！')
        print('\n使用方法:')
        print('  1. 运行 opencode 启动')
        print('  2. 在提示中包含 "ultrawork" 或 "ulw" 关键字即可启用所有功能')
        
        return True
        
    except FileNotFoundError:
        print('错误: 未找到 bun，请先安装 bun (https://bun.sh)')
        return False
    except subprocess.CalledProcessError as e:
        print(f'安装失败: {e}')
        return False
    except Exception as e:
        print(f'发生错误: {e}')
        return False


def configure_custom_models():
    """配置自定义大模型 - 从 JSON 文件读取配置"""
    print('\n' + '=' * 50)
    print('自定义大模型配置')
    print('=' * 50)
    
    config_dir = get_config_dir()
    config_file = os.path.join(config_dir, 'model-config.json')
    template_file = os.path.join(config_dir, 'model-config.template.json')
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f'\n❌ 未找到配置文件: {config_file}')
        print(f'📝 请复制模板文件并修改配置:')
        print(f'   1. 复制 {os.path.basename(template_file)} 为 model-config.json')
        print(f'   2. 编辑 model-config.json 中的配置项')
        print(f'   3. 重新运行此命令')
        
        if os.path.exists(template_file):
            print(f'\n✅ 模板文件位置: {template_file}')
        else:
            print(f'\n⚠ 模板文件不存在，正在创建...')
            create_model_config_template(template_file)
            print(f'✅ 已创建模板文件: {template_file}')
        
        return False
    
    # 读取配置文件
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            # 移除 JSON 注释（更完善的处理）
            content = f.read()
            # 移除 // 注释行和行内注释
            lines = content.split('\n')
            clean_lines = []
            for line in lines:
                # 移除 // 注释（但保留字符串中的 //）
                in_string = False
                escaped = False
                clean_line = ""
                i = 0
                while i < len(line):
                    char = line[i]
                    if escaped:
                        clean_line += char
                        escaped = False
                    elif char == '\\' and in_string:
                        clean_line += char
                        escaped = True
                    elif char == '"':
                        clean_line += char
                        in_string = not in_string
                    elif char == '/' and i + 1 < len(line) and line[i + 1] == '/' and not in_string:
                        # 找到注释，停止处理这一行
                        break
                    else:
                        clean_line += char
                    i += 1
                
                clean_line = clean_line.rstrip()
                if clean_line:  # 保留非空行
                    clean_lines.append(clean_line)
            
            clean_content = '\n'.join(clean_lines)
            model_config = json.loads(clean_content)
    except json.JSONDecodeError as e:
        print(f'\n❌ JSON 格式错误: {e}')
        print(f'请检查 {config_file} 的格式是否正确')
        return False
    except Exception as e:
        print(f'\n❌ 读取配置文件失败: {e}')
        return False
    
    # 验证必需字段
    required_fields = ['api_url', 'api_key', 'model_name']
    missing_fields = [field for field in required_fields if not model_config.get(field)]
    
    if missing_fields:
        print(f'\n❌ 缺少必需字段: {", ".join(missing_fields)}')
        print(f'请在 {config_file} 中配置这些字段')
        return False
    
    # 获取配置值
    api_url = model_config['api_url']
    api_key = model_config['api_key']
    model_name = model_config['model_name']
    
    # 可选配置
    provider_name = model_config.get('provider_name', 'Custom OpenAI Compatible')
    env_var_name = model_config.get('env_var_name', 'CUSTOM_OPENAI_API_KEY')
    model_display_name = model_config.get('model_display_name', model_name)
    
    # 模型功能配置
    features = model_config.get('model_features', {})
    temperature = features.get('temperature', True)
    tool_call = features.get('tool_call', True)
    attachment = features.get('attachment', False)
    reasoning = features.get('reasoning', False)
    
    # 模型限制
    limits = model_config.get('model_limits', {})
    context_limit = limits.get('context', 128000)
    output_limit = limits.get('output', 4096)
    
    # 成本配置
    cost = model_config.get('model_cost', {})
    input_cost = cost.get('input', 0)
    output_cost = cost.get('output', 0)
    
    print(f'\n📖 读取配置文件: {config_file}')
    print(f'🔗 API 地址: {api_url}')
    print(f'🤖 模型名称: {model_name}')
    print(f'📝 显示名称: {model_display_name}')
    
    # 获取 OpenCode 配置目录
    home_dir = os.path.expanduser('~')
    opencode_config_dir = os.path.join(home_dir, '.config', 'opencode')
    opencode_config_path = os.path.join(opencode_config_dir, 'opencode.json')
    
    # 确保配置目录存在
    os.makedirs(opencode_config_dir, exist_ok=True)
    
    # 读取现有 OpenCode 配置
    opencode_config = {}
    if os.path.exists(opencode_config_path):
        try:
            with open(opencode_config_path, 'r', encoding='utf-8') as f:
                opencode_config = json.load(f)
        except:
            opencode_config = {}
    
    # 生成提供商配置
    provider_id = 'custom-openai'
    
    # 更新 OpenCode 配置
    if 'provider' not in opencode_config:
        opencode_config['provider'] = {}
    
    opencode_config['provider'][provider_id] = {
        'name': provider_name,
        'api': api_url,
        'npm': '@ai-sdk/openai-compatible',
        'env': [env_var_name],
        'models': {
            model_name: {
                'name': model_display_name,
                'temperature': temperature,
                'tool_call': tool_call,
                'attachment': attachment,
                'reasoning': reasoning
            }
        }
    }
    
    # 添加限制和成本信息（如果提供）
    if context_limit or output_limit:
        opencode_config['provider'][provider_id]['models'][model_name]['limit'] = {
            'context': context_limit,
            'output': output_limit
        }
    
    if input_cost or output_cost:
        opencode_config['provider'][provider_id]['models'][model_name]['cost'] = {
            'input': input_cost,
            'output': output_cost
        }
    
    # 设置默认模型
    opencode_config['model'] = f'{provider_id}:{model_name}'
    
    # 设置环境变量（当前会话）
    os.environ[env_var_name] = api_key
    
    # 设置永久环境变量（Windows）
    try:
        set_permanent_env_var(env_var_name, api_key)
        print(f'✓ 已设置永久环境变量: {env_var_name}')
    except Exception as e:
        print(f'⚠ 设置永久环境变量失败: {e}')
        print(f'  请手动设置环境变量 {env_var_name}')
    
    # 保存配置
    save_config(opencode_config, opencode_config_path)
    
    print(f'\n✅ 配置完成!')
    print(f'   提供商: {provider_name}')
    print(f'   API 地址: {api_url}')
    print(f'   模型: {model_display_name} ({model_name})')
    print(f'   环境变量: {env_var_name}')
    print(f'   功能: 温度={temperature}, 工具调用={tool_call}, 附件={attachment}, 推理={reasoning}')
    
    if context_limit or output_limit:
        print(f'   限制: 上下文={context_limit}, 输出={output_limit}')
    
    if input_cost or output_cost:
        print(f'   成本: 输入=${input_cost}/1k tokens, 输出=${output_cost}/1k tokens')
    
    print(f'\n💡 重要提示:')
    print(f'   1. 环境变量已设置，重启命令行后生效')
    print(f'   2. 或者运行: set {env_var_name}={api_key[:10]}...')
    print(f'   3. 验证设置: echo %{env_var_name}%')
    
    return True


def create_model_config_template(template_path):
    """创建模型配置模板文件"""
    template_content = """{
  // OpenCode 自定义模型配置模板
  // 复制此文件为 model-config.json 并修改以下配置
  
  // API 连接地址 - 支持任何 OpenAI 兼容的 API 端点
  "api_url": "https://api.openai.com/v1",
  
  // API Key - 你的 API 密钥
  "api_key": "sk-your-api-key-here",
  
  // 模型名称 - 要使用的具体模型
  "model_name": "gpt-4o",
  
  // 可选配置项：
  
  // 提供商名称 - 显示名称（可选，默认为 "Custom OpenAI Compatible"）
  "provider_name": "Custom OpenAI Compatible",
  
  // 环境变量名 - API Key 的环境变量名（可选，默认为 "CUSTOM_OPENAI_API_KEY"）
  "env_var_name": "CUSTOM_OPENAI_API_KEY",
  
  // 模型显示名称 - 在界面中显示的名称（可选，默认使用 model_name）
  "model_display_name": "GPT-4o",
  
  // 模型功能配置（可选）
  "model_features": {
    // 是否支持温度参数
    "temperature": true,
    // 是否支持工具调用
    "tool_call": true,
    // 是否支持附件
    "attachment": false,
    // 是否支持推理
    "reasoning": false
  },
  
  // 模型限制（可选）
  "model_limits": {
    // 上下文长度限制
    "context": 128000,
    // 输出长度限制
    "output": 4096
  },
  
  // 成本配置（可选，用于成本估算）
  "model_cost": {
    // 输入 token 成本（每千 token）
    "input": 0.005,
    // 输出 token 成本（每千 token）
    "output": 0.015
  }
}"""
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    print(f'  配置文件: {template_path}')
    
    return True


def save_config(config, config_path):
    """保存配置文件"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f'✓ 配置已保存到: {config_path}')
    except Exception as e:
        print(f'✗ 保存配置失败: {e}')



def configure_oh_my_opencode_plugin():
    """配置 opencode 使用 oh-my-opencode 插件"""
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, '.config', 'opencode')
    config_path = os.path.join(config_dir, 'opencode.json')
    
    # 确保配置目录存在
    os.makedirs(config_dir, exist_ok=True)
    
    # 读取或创建配置
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
    
    # 添加 oh-my-opencode 插件
    if 'plugin' not in config:
        config['plugin'] = []
    
    if 'oh-my-opencode' not in config['plugin']:
        config['plugin'].append('oh-my-opencode')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f'✓ 已将 oh-my-opencode 添加到配置: {config_path}')
    else:
        print('✓ oh-my-opencode 已在配置中')


def install_with_config():
    """安装 OpenCode 并询问是否配置自定义模型"""
    print('=' * 50)
    print('开始安装 OpenCode...')
    print('=' * 50)
    
    # 安装 opencode
    if not install_opencode():
        print('\n✗ opencode 安装失败')
        return False
    
    # 安装 oh-my-opencode
    print('\n' + '=' * 50)
    print('开始安装 oh-my-opencode 插件...')
    print('=' * 50)
    
    if not install_oh_my_opencode():
        print('\n✗ oh-my-opencode 安装失败')
        print('但 opencode 已安装成功，你可以稍后手动安装 oh-my-opencode')
    
    print('\n' + '=' * 50)
    print('✓ OpenCode 安装完成！')
    print('=' * 50)
    
    # 询问是否配置自定义模型
    print('\n是否配置自定义大模型? (Y/n): ', end='')
    try:
        choice = input().strip().lower()
        if choice in ('', 'y', 'yes', '是'):
            configure_custom_models()
        else:
            print('\n你可以稍后运行以下命令配置模型:')
            print('  py create_doc.py config')
    except (EOFError, KeyboardInterrupt):
        print('\n跳过模型配置')
    
    print('\n现在你可以:')
    print('  1. 运行 `opencode` 启动 AI 编程助手')
    print('  2. 使用 "ultrawork" 关键字启用 oh-my-opencode 的所有功能')
    
    return True


def uninstall_opencode_complete():
    """彻底删除 OpenCode，确保删除干净"""
    print('=' * 50)
    print('彻底删除 OpenCode')
    print('=' * 50)
    
    print('\n⚠ 警告: 这将完全删除 OpenCode 及其所有数据')
    print('包括: 配置文件、缓存、会话数据、插件等')
    
    try:
        confirm = input('\n确认删除? (y/N): ').strip().lower()
        if confirm not in ('y', 'yes', '是'):
            print('已取消删除')
            return False
    except (EOFError, KeyboardInterrupt):
        print('\n已取消删除')
        return False
    
    print('\n开始删除...')
    
    # 创建一个自动确认的输入函数，跳过 uninstaller 的二次确认
    def auto_confirm_input(prompt):
        if '确定要继续吗' in prompt or 'continue' in prompt.lower():
            print(prompt + 'y')  # 显示提示和自动回答
            return 'y'
        elif '是否删除这些配置目录' in prompt:
            print(prompt + 'y')
            return 'y'
        elif '是否扫描项目中的' in prompt:
            print(prompt + 'n')  # 默认跳过项目扫描
            return 'n'
        else:
            # 对于其他提示，尝试从标准输入读取
            try:
                return input(prompt)
            except (EOFError, KeyboardInterrupt):
                return 'n'
    
    # 使用 uninstaller 删除，传入自动确认函数
    uninstaller = OpenCodeUninstaller(dry_run=False, input_func=auto_confirm_input)
    report = uninstaller.run()
    
    # 额外清理步骤，确保删除干净
    additional_cleanup()
    
    if report.is_complete:
        print('\n✓ OpenCode 已完全删除')
    else:
        print('\n⚠ 删除过程中遇到一些问题，但主要组件已删除')
        if report.total_failed > 0:
            print('未能删除的项目:')
            # 显示各类失败的项目
            for path, reason in report.executables_failed:
                print(f'  - 可执行文件 {path}: {reason}')
            for name, reason in report.package_managers_failed:
                print(f'  - 包管理器 {name}: {reason}')
            for path, reason in report.config_dirs_failed:
                print(f'  - 配置目录 {path}: {reason}')
            for path, reason in report.cache_dirs_failed:
                print(f'  - 缓存目录 {path}: {reason}')
            for path, reason in report.data_dirs_failed:
                print(f'  - 数据目录 {path}: {reason}')
            for path, reason in report.project_dirs_failed:
                print(f'  - 项目目录 {path}: {reason}')
    
    return report.is_complete


def additional_cleanup():
    """额外的清理步骤，确保删除干净"""
    import shutil
    import stat
    
    def handle_remove_readonly(func, path, exc):
        """处理只读文件删除"""
        if os.path.exists(path):
            # 移除只读属性
            os.chmod(path, stat.S_IWRITE)
            func(path)
    
    cleanup_paths = [
        # Bun 相关
        os.path.join(os.path.expanduser('~'), '.bun', 'bin', 'opencode.exe'),
        os.path.join(os.path.expanduser('~'), '.bun', 'bin', 'opencode'),
        os.path.join(os.path.expanduser('~'), '.bun', 'install', 'global', 'node_modules', 'opencode'),
        os.path.join(os.path.expanduser('~'), '.bun', 'install', 'global', 'node_modules', 'oh-my-opencode'),
        
        # 配置和缓存目录
        os.path.join(os.path.expanduser('~'), '.config', 'opencode'),
        os.path.join(os.path.expanduser('~'), '.cache', 'opencode'),
        os.path.join(os.path.expanduser('~'), '.local', 'share', 'opencode'),
        
        # Windows 特定路径
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'opencode'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'opencode'),
        
        # 临时文件
        os.path.join(os.path.expanduser('~'), '.opencode'),
    ]
    
    removed_count = 0
    failed_count = 0
    
    for path in cleanup_paths:
        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    # 处理只读文件
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWRITE)
                    os.remove(path)
                    print(f'✓ 删除文件: {path}')
                    removed_count += 1
                elif os.path.isdir(path):
                    # 使用 onerror 处理只读文件
                    shutil.rmtree(path, onerror=handle_remove_readonly)
                    print(f'✓ 删除目录: {path}')
                    removed_count += 1
        except PermissionError as e:
            print(f'⚠ 权限不足，跳过: {path}')
            failed_count += 1
        except Exception as e:
            print(f'✗ 删除失败 {path}: {e}')
            failed_count += 1
    
    if removed_count > 0:
        print(f'\n✓ 额外清理了 {removed_count} 个项目')
    if failed_count > 0:
        print(f'⚠ {failed_count} 个项目因权限问题无法删除')
    
    # 清理环境变量
    print('\n清理环境变量...')
    env_vars_to_clear = get_opencode_env_vars()
    cleared_count = 0
    failed_env_count = 0
    
    for env_var in env_vars_to_clear:
        try:
            # 清理当前会话的环境变量
            if env_var in os.environ:
                del os.environ[env_var]
                cleared_count += 1
            
            # 清理永久环境变量
            if remove_permanent_env_var(env_var):
                print(f'✓ 删除永久环境变量: {env_var}')
            
        except Exception as e:
            print(f'⚠ 清理环境变量失败 {env_var}: {e}')
            failed_env_count += 1
    
    if cleared_count > 0:
        print(f'✓ 清理了 {cleared_count} 个会话环境变量')
    if failed_env_count > 0:
        print(f'⚠ {failed_env_count} 个环境变量清理失败')
    
    # 提示用户重启以生效
    if platform.system() == 'Windows':
        print('\n💡 提示: 环境变量更改需要重启命令行或重新登录才能完全生效')


def main():
    """主入口函数"""
    print('=' * 50)
    print('OpenCode 安装/卸载工具')
    print('=' * 50)
    print('\n请选择操作:')
    print('  1. 安装 OpenCode (包含 opencode + oh-my-opencode)')
    print('  2. 彻底删除 OpenCode')
    print('  0. 退出')
    
    try:
        choice = input('\n请输入选项 (0-2): ').strip()
    except (EOFError, KeyboardInterrupt):
        print('\n已取消')
        return
    
    if choice == '1':
        install_with_config()
    elif choice == '2':
        uninstall_opencode_complete()
    elif choice == '0':
        print('已退出')
    else:
        print('无效的选项')


# 支持命令行参数
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ('install', '安装'):
            install_with_config()
        elif arg in ('uninstall', 'remove', '删除', '卸载'):
            uninstall_opencode_complete()
        elif arg in ('config', 'configure', '配置'):
            configure_custom_models()
        elif arg in ('--help', '-h', 'help'):
            print('用法: python create_doc.py [命令]')
            print('')
            print('命令:')
            print('  install           安装 OpenCode (包含 opencode + oh-my-opencode)')
            print('  uninstall         彻底删除 OpenCode')
            print('  config            配置自定义大模型')
            print('')
            print('示例:')
            print('  python create_doc.py install     # 安装 OpenCode')
            print('  python create_doc.py uninstall   # 删除 OpenCode')
            print('  python create_doc.py config      # 配置模型')
        else:
            print(f'未知命令: {arg}')
            print('使用 --help 查看帮助')
    else:
        main()
