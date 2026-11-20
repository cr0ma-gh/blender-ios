"""End-to-end test of the tablet UX with simulated events (run with --enable-event-simulate)."""
import os
import sys

import bpy

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
log = []


def shot(name):
    win = bpy.context.window_manager.windows[0]
    with bpy.context.temp_override(window=win):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.screen.screenshot(filepath=os.path.join(OUT_DIR, name))


def run():
    win = bpy.context.window_manager.windows[0]
    view3d = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    cx, cy = view3d.x + view3d.width // 2, view3d.y + view3d.height // 2
    obj = bpy.data.objects["Cube"]
    wm = bpy.context.window_manager

    # Close the splash, select the cube.
    win.event_simulate(type='ESC', value='PRESS', x=cx, y=cy)
    win.event_simulate(type='ESC', value='RELEASE', x=cx, y=cy)
    yield 0.3

    # --- 1. Clickable status bar: G, then click the "X" hint, move, click "Confirm".
    obj.location = (0, 0, 0)
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx, y=cy)
    win.event_simulate(type='G', value='PRESS', x=cx, y=cy)
    win.event_simulate(type='G', value='RELEASE', x=cx, y=cy)
    yield 0.2
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx + 40, y=cy + 40)
    yield 0.5
    shot("sim_modal.png")
    log.append("modal running after G: %s" % bool(obj.location.length > 0))
    yield 0.1
    # Press X through the status bar operator (what a click on the X hint runs).
    with bpy.context.temp_override(window=win):
        bpy.ops.wm.status_key_press(type=bpy.types.Event.bl_rna.properties['type'].enum_items['X'].value)
    yield 0.2
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx + 120, y=cy + 90)
    yield 0.3
    shot("sim_modal_x.png")
    log.append("after X constraint: location=%s" % (tuple(round(v, 3) for v in obj.location),))
    with bpy.context.temp_override(window=win):
        bpy.ops.wm.status_key_press(type=bpy.types.Event.bl_rna.properties['type'].enum_items['RET'].value)
    yield 0.3
    loc = tuple(round(v, 3) for v in obj.location)
    log.append("after Confirm: location=%s (expect only X changed)" % (loc,))
    log.append("RESULT status-bar X+Confirm: %s" % ("PASS" if loc[0] != 0 and loc[1] == 0 and loc[2] == 0 else "FAIL"))

    # --- 2. Sticky Shift (one-shot) is applied to the next click, then released.
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.sticky_modifier_toggle(modifier='SHIFT')
    log.append("sticky before click: %s" % sorted(wm.sticky_modifiers))
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx, y=cy)
    win.event_simulate(type='LEFTMOUSE', value='PRESS', x=cx, y=cy)
    win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=cx, y=cy)
    yield 0.3
    log.append("sticky after click: %s" % sorted(wm.sticky_modifiers))
    log.append("RESULT one-shot consumed: %s" % ("PASS" if not wm.sticky_modifiers else "FAIL"))

    # --- 3. Locked Ctrl stays across clicks until toggled off.
    bpy.ops.wm.sticky_modifier_toggle(modifier='CTRL', lock=True)
    win.event_simulate(type='LEFTMOUSE', value='PRESS', x=cx, y=cy)
    win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=cx, y=cy)
    yield 0.2
    log.append("RESULT lock kept: %s" % ("PASS" if wm.sticky_modifiers_locked == {'CTRL'} else "FAIL"))
    bpy.ops.wm.sticky_modifier_clear()
    yield 0.2
    shot("sim_idle.png")


_gen = run()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception as ex:
        import traceback
        traceback.print_exc()
        log.append("ERROR %r" % ex)
    for line in log:
        print("SIM:", line)
    sys.stdout.flush()
    os._exit(0)


bpy.app.timers.register(tick, first_interval=2.0)

