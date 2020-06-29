import autopy
import time

autopy.mouse.move(966,790)
time.sleep(0.2)
autopy.mouse.toggle(down=True,button=None)
autopy.mouse.smooth_move(1037,790)
time.sleep(5)
autopy.mouse.toggle(down=True,button=None)
