#!/usr/bin/env python3
"""
Fix Mach-O binaries in Blender.app for iOS.

Upstream precompiled NumPy (and potentially other third-party C-extensions in lib/ios_arm64)
contain Mach-O binaries tagged with platform=1 (macOS) and linking to macOS framework paths
like '/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate'.
On iOS/iPadOS, dyld rejects them with:
  "mach-o file, but is for macOS (which is not this platform)"
and Accelerate is located at '/System/Library/Frameworks/Accelerate.framework/Accelerate'.

This script traverses the app bundle and:
1. Replaces macOS framework paths with standard iOS framework paths.
2. Updates LC_BUILD_VERSION platform from 1 (macOS) to 2 (iOS) via vtool.
3. Ad-hoc codesigns every .dylib and .so binary so iOS installd and sideloading signers accept them.
"""

import os
import sys
import subprocess

def fix_binaries(app_path):
    if not os.path.isdir(app_path):
        print(f"Error: app bundle not found at {app_path}", file=sys.stderr)
        sys.exit(1)

    print(f"==> Fixing Mach-O binaries in {app_path} for iOS...")
    count = 0

    for root, _, files in os.walk(app_path):
        for f in files:
            if f.endswith(".dylib") or f.endswith(".so"):
                path = os.path.join(root, f)
                count += 1

                # 1. Fix Accelerate framework path (macOS Versions/A -> iOS direct path)
                subprocess.run([
                    "install_name_tool",
                    "-change",
                    "/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate",
                    "/System/Library/Frameworks/Accelerate.framework/Accelerate",
                    path
                ], capture_output=True)

                # 2. Fix Mach-O platform tag to iOS (platform 2, minos 16.0, sdk 18.5)
                subprocess.run([
                    "vtool",
                    "-set-build-version", "2", "16.0", "18.5",
                    "-replace", "-output", path, path
                ], capture_output=True)

                # 3. Ad-hoc codesign binary
                subprocess.run([
                    "codesign", "--force", "--sign", "-", path
                ], capture_output=True)

    print(f"==> Successfully fixed and signed {count} dynamic libraries and Python C-extensions.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fix_macho.py <path-to-Blender.app>", file=sys.stderr)
        sys.exit(1)
    fix_binaries(sys.argv[1])
