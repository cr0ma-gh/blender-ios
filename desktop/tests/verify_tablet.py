import addon_utils
import bpy

results = []


def check(name, cond):
    results.append(("PASS" if cond else "FAIL", name))


wm = bpy.context.window_manager

# Core (C++) additions.
check("RNA WindowManager.sticky_modifiers", hasattr(wm, "sticky_modifiers"))
check("RNA WindowManager.sticky_modifiers_locked", hasattr(wm, "sticky_modifiers_locked"))
for op in ("sticky_modifier_toggle", "sticky_modifier_clear", "status_key_press"):
    check("operator wm." + op, hasattr(bpy.ops.wm, op) and bpy.ops.wm.__getattribute__(op).idname() != "")

# Sticky modifier cycle: off -> one-shot -> locked -> off.
bpy.ops.wm.sticky_modifier_clear()
check("initially no sticky modifiers", wm.sticky_modifiers == set())
bpy.ops.wm.sticky_modifier_toggle(modifier='SHIFT')
check("toggle 1: SHIFT one-shot", wm.sticky_modifiers == {'SHIFT'} and wm.sticky_modifiers_locked == set())
bpy.ops.wm.sticky_modifier_toggle(modifier='SHIFT')
check("toggle 2: SHIFT locked", wm.sticky_modifiers_locked == {'SHIFT'})
bpy.ops.wm.sticky_modifier_toggle(modifier='SHIFT')
check("toggle 3: SHIFT off", wm.sticky_modifiers == set())
bpy.ops.wm.sticky_modifier_toggle(modifier='CTRL', lock=True)
check("lock=True: CTRL locked", wm.sticky_modifiers_locked == {'CTRL'})
bpy.ops.wm.sticky_modifier_clear()
check("clear releases all", wm.sticky_modifiers == set())

# Add-on: enabled by default in factory preferences, classes registered.
loaded_default, loaded_state = addon_utils.check("tablet_ux")
check("tablet_ux enabled by default", loaded_state)
for cls in ("VIEW3D_PT_tablet_display", "VIEW3D_PT_tablet_sculpt", "WM_MT_tablet_modifier_wheel"):
    check("class " + cls, hasattr(bpy.types, cls))
for op in ("search", "context_menu", "touch_keyboard", "touch_scale_toggle"):
    check("operator tablet." + op, hasattr(bpy.ops.tablet, op))
check("header draw hook", any(getattr(f, "__name__", "") == "draw_view3d_header"
                              for f in bpy.types.VIEW3D_HT_header._dyn_ui_initialize()))
check("status bar draw hook", any(getattr(f, "__name__", "") == "draw_statusbar_modifiers"
                                  for f in bpy.types.STATUSBAR_HT_header._dyn_ui_initialize()))

# Touch scale toggle.
view = bpy.context.preferences.view
before = view.ui_scale
bpy.ops.tablet.touch_scale_toggle()
check("touch scale on", abs(view.ui_scale - 1.3) < 1e-3)
bpy.ops.tablet.touch_scale_toggle()
check("touch scale off", abs(view.ui_scale - 1.0) < 1e-3)
view.ui_scale = before

for status, name in results:
    print(f"[{status}] {name}")
print("SUMMARY:", sum(s == "PASS" for s, _ in results), "passed,",
      sum(s == "FAIL" for s, _ in results), "failed")
