#!/bin/bash
# Make a built Blender.app installable/usable on iPad, in place, keeping Blender's original
# branding (name, bundle identifier, file types and the official icon from upstream).
#
# Why this exists: the iOS build references the icon via CFBundleIconFile -> a .icns file,
# but iOS ignores .icns for the home-screen icon — it needs PNG icons declared under
# CFBundleIcons. So after the build we render PNG icons from Blender's own blender_icon.icns
# and declare them, enable the iOS Files app integration, and ship a binary Info.plist.
#
# Usage: bash prepare_ios_bundle.sh <path-to-Blender.app> [icon.icns|icon.png]
#        (icon defaults to the official <Blender.app>/Assets/blender_icon.icns)
set -euo pipefail

APP="${1:?usage: prepare_ios_bundle.sh <Blender.app> [icon.icns|icon.png]}"
ICON="${2:-$APP/Assets/blender_icon.icns}"
PL="$APP/Info.plist"
PB=/usr/libexec/PlistBuddy

test -f "$ICON" || { echo "!! icon not found: $ICON"; exit 1; }
# Blender stores the .icns in git LFS; a ~130-byte file means the LFS object was not pulled.
if [ "$(wc -c < "$ICON")" -lt 1024 ]; then
  echo "!! $ICON looks like a git-lfs pointer (run 'git lfs pull' in the Blender checkout)"
  exit 1
fi

# Render a 1024px PNG master from the icon (sips picks the largest representation of an .icns).
MASTER="$(mktemp -d)/icon_1024.png"
sips -s format png "$ICON" --out "$MASTER" >/dev/null
sips -z 1024 1024 "$MASTER" >/dev/null

# iOS PNG app icons (sizes for iPad: 76@1x, 76@2x=152, 83.5@2x=167; plus 60@2x=120 fallback).
sips -z 120 120 "$MASTER" --out "$APP/AppIcon60x60@2x.png"          >/dev/null
sips -z 76  76  "$MASTER" --out "$APP/AppIcon76x76~ipad.png"        >/dev/null
sips -z 152 152 "$MASTER" --out "$APP/AppIcon76x76@2x~ipad.png"     >/dev/null
sips -z 167 167 "$MASTER" --out "$APP/AppIcon83.5x83.5@2x~ipad.png" >/dev/null

# iOS icon keys (replace any existing).
$PB -c "Delete :CFBundleIcons" "$PL" 2>/dev/null || true
$PB -c "Delete :CFBundleIcons~ipad" "$PL" 2>/dev/null || true
$PB -c "Add :CFBundleIcons dict" "$PL"
$PB -c "Add :CFBundleIcons:CFBundlePrimaryIcon dict" "$PL"
$PB -c "Add :CFBundleIcons:CFBundlePrimaryIcon:CFBundleIconFiles array" "$PL"
$PB -c "Add :CFBundleIcons:CFBundlePrimaryIcon:CFBundleIconFiles: string AppIcon60x60" "$PL"
$PB -c "Add :CFBundleIcons~ipad dict" "$PL"
$PB -c "Add :CFBundleIcons~ipad:CFBundlePrimaryIcon dict" "$PL"
$PB -c "Add :CFBundleIcons~ipad:CFBundlePrimaryIcon:CFBundleIconFiles array" "$PL"
$PB -c "Add :CFBundleIcons~ipad:CFBundlePrimaryIcon:CFBundleIconFiles: string AppIcon60x60" "$PL"
$PB -c "Add :CFBundleIcons~ipad:CFBundlePrimaryIcon:CFBundleIconFiles: string AppIcon76x76" "$PL"
$PB -c "Add :CFBundleIcons~ipad:CFBundlePrimaryIcon:CFBundleIconFiles: string AppIcon83.5x83.5" "$PL"

# File sharing and in-place document opening for iOS Files app ("On My iPad" folder).
$PB -c "Set :UIFileSharingEnabled true" "$PL" 2>/dev/null \
  || $PB -c "Add :UIFileSharingEnabled bool true" "$PL"
$PB -c "Set :LSSupportsOpeningDocumentsInPlace true" "$PL" 2>/dev/null \
  || $PB -c "Add :LSSupportsOpeningDocumentsInPlace bool true" "$PL"
$PB -c "Set :UISupportsDocumentBrowser true" "$PL" 2>/dev/null \
  || $PB -c "Add :UISupportsDocumentBrowser bool true" "$PL"

# Real iOS apps ship a BINARY Info.plist. This Blender build emits XML, which some
# installers (e.g. iLoader / isideload) fail to parse — convert to binary for compatibility.
plutil -convert binary1 "$PL"

echo "    iOS icons ($(basename "$ICON")) + Files integration applied to $APP"
echo "    bundle id: $($PB -c 'Print :CFBundleIdentifier' "$PL")  name: $($PB -c 'Print :CFBundleName' "$PL")"
