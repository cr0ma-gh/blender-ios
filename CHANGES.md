# Changes from upstream Blender

Blender is licensed under **GPL-2.0-or-later**. Per the GNU GPL (v2 §2(b): modified files must
carry prominent notices stating they were changed), this file documents that the program has been
modified and lists all changes.

## Base

- **Upstream:** Blender, official repository `https://projects.blender.org/blender/blender.git`
- **Branch:** `ios` (experimental)
- **Pinned commit:** `d9b6fe34ddce527d93b97c0bf42ad92cebac4e4e` (Blender 5.0)
  ("iOS: Correct Info.plist CFBundleVersion version string", 2025-09-10)

All modifications below are provided as [patches/blender-ipad.patch](patches/blender-ipad.patch),
which applies cleanly on top of that commit.

Two builds are produced from that base:

- **tablet** — additionally applies [patches/tablet-ui.patch](patches/tablet-ui.patch) first: the
  upstream Blender commits from branch `ios-workshop`, unmodified except for one trivial
  versioning merge, cherry-picked onto the pinned commit:
  - `c6e8abfe` — *UI: Menu Behavior Preferences #144838* (Dalai Felinto)
  - `97232b0f` — *WIP: Experimental editor dock #144945* (Dalai Felinto)
  - (`922720b9` *Touch-Capable Area Maintenance #144591* is already part of the pinned `ios`
    commit via main, so it is not re-applied.)
  - plus [patches/tablet-ui-backports.patch](patches/tablet-ui-backports.patch): later upstream
    `main` UI commits backported to 5.0 (only identifiers renamed to their 5.0 names):
    - `b5fd02b5` — *UI: Quad View Resizing* (Harley Acheson): drag the Quad View center to resize
    - `728c8624` — *UI: Fine adjusting values with arrows on number button* (Pratik Borhade)
    - `2d186b8c` — *UI: Support holding a shortcut to temporarily switch tools* (John Kiril Swenson)
- **legacy** — the pinned commit with `blender-ipad.patch` only.

The newer `ios` tip `a1de44dd` (Blender 5.1.2) is not used yet: no 5.1 precompiled
`lib-ios_arm64` exists, so it needs the iOS dependencies built from source (`make deps`).
The work-in-progress patch rebased onto it is kept in [patches/wip-5.1/](patches/wip-5.1/).

## Modified files & what changed

### Input backend (the core of this project)
- `intern/ghost/intern/GHOST_WindowIOS.mm`
  - External **mouse** (GCMouse) buttons, movement, and wheel.
  - External **keyboard** (GCKeyboard) full key events, including UTF-8 text so numeric input
    during transforms works.
  - An `IndirectPointer` `UIPanGestureRecognizer` for accurate absolute pointer positions
    (fixes box-select drift and drives orbit/pan).
  - **Orbit** (middle-drag) via a 2-finger trackpad-scroll GHOST event; **pan** (Shift+middle)
    routed to Blender's native depth-correct pan modal.
  - **Pinch / two-finger trackpad zoom** (Magic Keyboard trackpad).
  - **Apple Pencil** tablet data (pressure / tilt) wired through the pan gesture recognizer so
    the first contact is already a pressured stylus dab; hover events suppressed during a pencil
    touch.
  - Render/secondary window teardown so **`Esc` closes the render window** (toplevel `UIWindow`
    hidden + main window reactivated in the destructor).

### Editor / window-manager glue (iOS-guarded)
- `source/blender/editors/space_view3d/view3d_navigate_view_move.cc` — let a real `MIDDLEMOUSE`
  press start the native grab-pan modal (depth/zoom correct).
- `source/blender/editors/interface/view2d/view2d_ops.cc` — enable middle-click-drag pan in UV /
  2D editors.
- `build_files/cmake/platform/platform_apple.cmake` — warn instead of a fatal error when the
  macOS precompiled libs are missing.

### Branding
Blender's original branding is kept: upstream `release/ios/Blender.app/Info.plist` (name
**Blender**, bundle id `org.blenderfoundation.blender`, file types) and the official
`blender_icon.icns` are not modified.

Post-build, [build/prepare_ios_bundle.sh](build/prepare_ios_bundle.sh) only adds what iOS needs
on top of the built `.app` (no source change):
- PNG home-screen icons rendered from the official `blender_icon.icns` + `CFBundleIcons` keys
  (iOS ignores `.icns`);
- iOS Files app integration (`UIFileSharingEnabled`, `LSSupportsOpeningDocumentsInPlace`,
  `UISupportsDocumentBrowser`);
- conversion of `Info.plist` to binary format for sideloading-tool compatibility.

## Development note

These modifications were developed with substantial **AI assistance** (Anthropic's Claude) —
the input backend code, build/packaging scripts, CI, and documentation. Treat the
code as community-contributed and review it before relying on it.
