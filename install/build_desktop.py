#!/usr/bin/env python3
"""
OpenCode Desktop Build Script
=============================

This script provides a convenient way to build the OpenCode desktop application
with various configuration options.

Usage:
    python build_desktop.py [options]

Options:
    --release           Build in release mode (default)
    --debug             Build in debug mode
    --bundle-type       Bundle type: nsis, msi, app, dmg, deb, rpm (default: nsis for Windows)
    --clean             Clean build artifacts before building
    --skip-frontend     Skip frontend build
    --open-devtools     Open devtools in release build
    --help              Show this help message

Examples:
    python build_desktop.py
    python build_desktop.py --clean
    python build_desktop.py --bundle-type dmg
    python build_desktop.py --debug --open-devtools
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
import platform
from pathlib import Path
from typing import Optional, List

# Project paths
SCRIPT_DIR = Path(__file__).parent.absolute()
# install 目录的父目录是 openCode 根目录
ROOT_DIR = SCRIPT_DIR.parent
# opencode-dev 项目目录
OPENCODE_DEV_DIR = ROOT_DIR / "opencode-dev" / "opencode-dev"
DESKTOP_DIR = OPENCODE_DEV_DIR / "packages" / "desktop"
TAURI_DIR = DESKTOP_DIR / "src-tauri"
TAURI_CONF = TAURI_DIR / "tauri.conf.json"
LIB_RS = TAURI_DIR / "src" / "lib.rs"


def run_command(cmd: List[str], cwd: Optional[Path] = None, env: Optional[dict] = None) -> int:
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    
    result = subprocess.run(cmd, cwd=cwd, env=merged_env, shell=platform.system() == "Windows")
    return result.returncode


def clean_build_artifacts():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    
    # Clean Tauri target directory
    target_dir = TAURI_DIR / "target"
    if target_dir.exists():
        print(f"Removing {target_dir}")
        shutil.rmtree(target_dir, ignore_errors=True)
    
    # Clean frontend dist
    dist_dir = DESKTOP_DIR / "dist"
    if dist_dir.exists():
        print(f"Removing {dist_dir}")
        shutil.rmtree(dist_dir, ignore_errors=True)
    
    print("Clean complete.")


def set_devtools(enable: bool):
    """Enable or disable devtools in release builds."""
    if not LIB_RS.exists():
        print(f"Warning: {LIB_RS} not found, skipping devtools configuration")
        return
    
    with open(LIB_RS, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check current state
    has_release_devtools = '#[cfg(not(debug_assertions))]\n            window.open_devtools();' in content
    
    if enable and not has_release_devtools:
        # Add devtools for release
        old_code = '''            // Open devtools only in debug builds
            #[cfg(debug_assertions)]
            window.open_devtools();'''
        new_code = '''            // Open devtools in all builds
            #[cfg(debug_assertions)]
            window.open_devtools();
            
            #[cfg(not(debug_assertions))]
            window.open_devtools();'''
        content = content.replace(old_code, new_code)
        with open(LIB_RS, "w", encoding="utf-8") as f:
            f.write(content)
        print("Enabled devtools for release builds.")
    elif not enable and has_release_devtools:
        # Remove devtools for release
        old_code = '''            // Open devtools in all builds
            #[cfg(debug_assertions)]
            window.open_devtools();
            
            #[cfg(not(debug_assertions))]
            window.open_devtools();'''
        new_code = '''            // Open devtools only in debug builds
            #[cfg(debug_assertions)]
            window.open_devtools();'''
        content = content.replace(old_code, new_code)
        with open(LIB_RS, "w", encoding="utf-8") as f:
            f.write(content)
        print("Disabled devtools for release builds.")


def get_default_bundle_type() -> str:
    """Get default bundle type based on OS."""
    system = platform.system()
    if system == "Windows":
        return "nsis"
    elif system == "Darwin":
        return "dmg"
    else:
        return "deb"


def build_desktop(
    release: bool = True,
    bundle_type: Optional[str] = None,
    skip_frontend: bool = False,
    open_devtools: bool = False
) -> int:
    """Build the desktop application."""
    
    if bundle_type is None:
        bundle_type = get_default_bundle_type()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║            OpenCode Desktop Build Configuration              ║
╠══════════════════════════════════════════════════════════════╣
║  Mode:              {'Release' if release else 'Debug':<40} ║
║  Bundle Type:       {bundle_type:<40} ║
║  Open DevTools:     {'Yes' if open_devtools else 'No':<40} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Set devtools
    set_devtools(open_devtools)
    
    # Build command
    cmd = ["bun", "run", "tauri", "build"]
    
    if not release:
        cmd.append("--debug")
    
    cmd.extend(["--bundles", bundle_type])
    
    # Add cargo path for Windows
    env = {}
    if platform.system() == "Windows":
        cargo_bin = Path.home() / ".cargo" / "bin"
        env["PATH"] = f"{cargo_bin};{os.environ.get('PATH', '')}"
    
    # Run build
    print(f"\nBuilding desktop application...")
    result = run_command(cmd, cwd=DESKTOP_DIR, env=env)
    
    if result == 0:
        print("\n✅ Build successful!")
        
        # Show output location
        if release:
            bundle_dir = TAURI_DIR / "target" / "release" / "bundle"
        else:
            bundle_dir = TAURI_DIR / "target" / "debug" / "bundle"
        
        if bundle_dir.exists():
            print(f"\n📦 Output location: {bundle_dir}")
            for item in bundle_dir.iterdir():
                if item.is_dir():
                    for file in item.iterdir():
                        print(f"   - {file.name}")
    else:
        print("\n❌ Build failed!")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="OpenCode Desktop Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--release", action="store_true", default=True,
                        help="Build in release mode (default)")
    parser.add_argument("--debug", action="store_true",
                        help="Build in debug mode")
    parser.add_argument("--bundle-type", type=str, default=None,
                        choices=["nsis", "msi", "app", "dmg", "deb", "rpm", "appimage"],
                        help="Bundle type (default: nsis for Windows, dmg for macOS, deb for Linux)")
    parser.add_argument("--clean", action="store_true",
                        help="Clean build artifacts before building")
    parser.add_argument("--skip-frontend", action="store_true",
                        help="Skip frontend build")
    parser.add_argument("--open-devtools", action="store_true",
                        help="Open devtools in release build")
    
    args = parser.parse_args()
    
    # Change to project directory
    os.chdir(OPENCODE_DEV_DIR)
    
    # Clean if requested
    if args.clean:
        clean_build_artifacts()
    
    # Build
    release = not args.debug
    
    result = build_desktop(
        release=release,
        bundle_type=args.bundle_type,
        skip_frontend=args.skip_frontend,
        open_devtools=args.open_devtools
    )
    
    sys.exit(result)


if __name__ == "__main__":
    main()

