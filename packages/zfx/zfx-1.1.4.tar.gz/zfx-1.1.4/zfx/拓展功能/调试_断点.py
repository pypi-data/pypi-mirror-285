import sys
import traceback


class SimpleDebugger:
    def __init__(self):
        self.breakpoints = []

    def set_breakpoint(self, line, message=""):
        self.breakpoints.append((line, message))

    def start(self):
        frame = sys._getframe(1)  # 获取调用者的frame
        while frame:
            lineno = frame.f_lineno
            for bp in self.breakpoints:
                if bp[0] == lineno:
                    print(f"调试信息: {bp[1]} (在第 {lineno} 行)，指令提示：输入c将继续执行，输入q将退出代码运行")
                    self.interactive_console(frame)
            frame = frame.f_back

    def interactive_console(self, frame):
        local_vars = frame.f_locals
        global_vars = frame.f_globals
        while True:
            try:
                command = input("指令：")
                if command.strip() in ["c", "continue"]:
                    return
                elif command.strip() in ["q", "quit"]:
                    sys.exit(0)
                else:
                    exec(command, global_vars, local_vars)
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()


# 创建一个全局的调试器实例
global_debugger = SimpleDebugger()


def 调试_断点(信息="自定义断点信息"):
    """
    设置一个断点并启动调试器。

    参数:
        - 信息 (str): 自定义的调试信息，默认是"自定义断点信息"。
    """
    frame = sys._getframe(1)
    global_debugger.set_breakpoint(frame.f_lineno, 信息)
    global_debugger.start()