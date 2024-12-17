import pygame
import pygame.joystick
from 鼠标模拟 import 转换操作1, 转换操作2  # 直接从模块导入所需函数
import 鼠标模拟
# 初始化 pygame
pygame.init()

# 初始化 Joystick 子系统
pygame.joystick.init()

# 获取第一个可用的 Joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# 打印 Joystick 的名称（用于调试）
# print(f"Connected Joystick: {joystick.get_name()}")
AXIS_LEFT_RIGHT = 0
AXIS_UP_DOWN = 1
# 假设扳机是轴的一部分，这取决于您的手柄
AXIS_RT = 5  # 右扳机轴（示例值，根据您的手柄调整）
AXIS_LT = 4  # 左扳机轴（示例值，根据您的手柄调整）

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            # 检查哪个按钮被按下
            button_index = event.button
            if button_index == 0:
                鼠标模拟.转换操作3()
            elif button_index == 1:
                鼠标模拟.转换操作4('z')
            elif button_index == 2:
                鼠标模拟.转换操作4('x')
            elif button_index == 3:
                鼠标模拟.转换操作4('c')
            elif button_index == 4:
                print("右扳机被按下")
            elif button_index == 5:
                print("左扳机被按下")

    # 查询扳机的状态（这里假设扳机是模拟轴）
    rt_value = joystick.get_axis(AXIS_RT)
    lt_value = joystick.get_axis(AXIS_LT)
    if rt_value > 0.5:  # 设置一个阈值来判断 RT 是否被按下
        鼠标模拟.转换操作('左')
        # 可以在这里调用鼠标模拟函数，例如：鼠标模拟.某个函数(rt_value)
    if lt_value > 0.5:  # 设置一个阈值来判断 LT 是否被按下
        鼠标模拟.转换操作('右')
        # 可以在这里调用鼠标模拟函数，例如：鼠标模拟.某个函数(lt_value)

    # 查询其他轴的状态，并处理它们
    axes_left_right = joystick.get_axis(AXIS_LEFT_RIGHT)
    axes_up_down = joystick.get_axis(AXIS_UP_DOWN)
    mouse_x = 转换操作1(axes_up_down)  # 处理垂直轴
    mouse_y = 转换操作2(axes_left_right)  # 处理水平轴
    # 注意：这里需要实际使用 mouse_x 和 mouse_y 来移动鼠标或执行其他操作

    pygame.time.delay(100)  # 控制帧率

pygame.quit()
