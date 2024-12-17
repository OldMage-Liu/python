from pynput import mouse, keyboard
import os
import sys
import ctypes

if sys.platform.startswith('win'):
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def on_click(x, y, button, pressed):
    if button == mouse.Button.x2 and pressed:
        os.system("explorer.exe")  # 打开资源管理器
    if button == mouse.Button.x1 and pressed:
        # 模拟按下 Ctrl + S 快捷键
        controller = keyboard.Controller()
        controller.press(keyboard.Key.ctrl)
        controller.press('s')
        controller.release('s')
        controller.release(keyboard.Key.ctrl)

with mouse.Listener(on_click=on_click) as listener:
    listener.join()
