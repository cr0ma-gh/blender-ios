"""Click the status bar for real (simulated mouse events) during a Move: X hint, then Confirm."""
import os
import sys

import bpy

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
log = []
STATUS_Y = 11          # Status bar row, window coordinates (origin bottom-left).
X_HINT_X = 446         # "X" key of the "X Y Z Axis" hint.
CONFIRM_X = 140        # "Confirm" button.


def click(win, x, y):
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
    win.event_simulate(type='LEFTMOUSE', value='PRESS', x=x, y=y)
    win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=x, y=y)


def shot(name):
    win = bpy.context.window_manager.windows[0]
    with bpy.context.temp_override(window=win):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.screen.screenshot(filepath=os.path.join(OUT_DIR, name))


def modal_running(win):
    return len(win.modal_operators) > 0


def run():
    win = bpy.context.window_manager.windows[0]
    view3d = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    cx, cy = view3d.x + view3d.width // 2, view3d.y + view3d.height // 2
    obj = bpy.data.objects["Cube"]
    win.event_simulate(type='ESC', value='PRESS', x=cx, y=cy)
    win.event_simulate(type='ESC', value='RELEASE', x=cx, y=cy)
    yield 0.3

    obj.location = (0, 0, 0)
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx, y=cy)
    win.event_simulate(type='G', value='PRESS', x=cx, y=cy)
    win.event_simulate(type='G', value='RELEASE', x=cx, y=cy)
    yield 0.2
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx + 40, y=cy + 40)
    yield 0.3
    shot("click_before.png")
    log.append("modal after G: %s" % modal_running(win))

    click(win, X_HINT_X, STATUS_Y)          # Click the X hint in the status bar.
    yield 0.3
    log.append("modal after clicking X hint (must still run): %s" % modal_running(win))
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx + 150, y=cy + 120)
    yield 0.3
    shot("click_after_x.png")
    loc_x = tuple(round(v, 3) for v in obj.location)
    log.append("location after X + move: %s" % (loc_x,))

    click(win, CONFIRM_X, STATUS_Y)         # Click Confirm in the status bar.
    yield 0.3
    loc = tuple(round(v, 3) for v in obj.location)
    log.append("modal after clicking Confirm (must be done): %s" % modal_running(win))
    log.append("final location: %s" % (loc,))
    ok = (loc[0] != 0 and loc[1] == 0 and loc[2] == 0 and not modal_running(win))
    log.append("RESULT real status-bar clicks (X hint + Confirm): %s" % ("PASS" if ok else "FAIL"))


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
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(tick, first_interval=2.0)


