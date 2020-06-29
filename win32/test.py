import win32api
import win32gui
import win32con


# win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0,0,0)
# win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0,0,0)
win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE|win32con.MOUSEEVENTF_MOVE,28000,28000,0,0)
