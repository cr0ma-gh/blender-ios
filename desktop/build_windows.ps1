# Build Blender 5.3 for Windows with the Tablet UX patch.
#
# Prerequisites (one time, e.g. with winget):
#   winget install Microsoft.VisualStudio.2022.BuildTools --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
#   winget install Kitware.CMake
#   winget install GitHub.GitLFS
#
# Usage (PowerShell):   .\desktop\build_windows.ps1 [-Root C:\blender-git]
# Result:               <Root>\build_windows_x64_vc17_Release\bin\blender.exe
param(
    [string]$Root = "C:\blender-git"
)
$ErrorActionPreference = "Stop"

$Patch = Join-Path $PSScriptRoot "patches\tablet-ux-blender-5.3.patch"
$Src = Join-Path $Root "blender"
$Ninja = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja"
$env:Path = "$Ninja;" + [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
            [Environment]::GetEnvironmentVariable('Path', 'User')

git lfs install --skip-repo | Out-Null
New-Item -ItemType Directory -Force $Root | Out-Null

if (-not (Test-Path $Src)) {
    # Blender 5.3.0 release (the 'blender-v5.3-release' branch).
    git clone --depth 1 --branch blender-v5.3-release https://projects.blender.org/blender/blender.git $Src
}

# Apply the patch once (skip if it is already applied).
git -C $Src apply --check $Patch 2>$null
if ($LASTEXITCODE -eq 0) {
    git -C $Src apply $Patch
    Write-Host "Tablet UX patch applied."
} else {
    git -C $Src apply --reverse --check $Patch 2>$null
    if ($LASTEXITCODE -ne 0) { throw "The patch neither applies nor is already applied to $Src" }
    Write-Host "Tablet UX patch already applied."
}

# Precompiled Windows libraries (several GB, git LFS).
python "$Src\build_files\utils\make_update.py" --no-blender

# '2022b' = Visual Studio 2022 *Build Tools* edition; 'ninja' = faster builds.
cmd /c "cd /d $Src && $Src\make.bat 2022b ninja nobuildinfo"
if ($LASTEXITCODE -ne 0) { throw "Build failed" }
Write-Host "Done: $Root\build_windows_x64_vc17_Release\bin\blender.exe"
