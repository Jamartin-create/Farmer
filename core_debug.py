# 调试工具模块
# 提供统一的调试输出接口，支持全局开关控制

# 全局调试开关（改为 True 开启调试输出）
DEBUG_MODE = False

def debug_print(a1, a2=None, a3=None, a4=None, a5=None, a6=None, a7=None, a8=None, a9=None, a10=None, a11=None, a12=None):
	# 封装 quick_print，通过 DEBUG_MODE 控制输出
	# 用法：debug_print("Zone:", zone, "at", x, y)
	# 注意：最多支持12个参数
	if DEBUG_MODE:
		if a2 == None:
			quick_print(a1)
		elif a3 == None:
			quick_print(a1, a2)
		elif a4 == None:
			quick_print(a1, a2, a3)
		elif a5 == None:
			quick_print(a1, a2, a3, a4)
		elif a6 == None:
			quick_print(a1, a2, a3, a4, a5)
		elif a7 == None:
			quick_print(a1, a2, a3, a4, a5, a6)
		elif a8 == None:
			quick_print(a1, a2, a3, a4, a5, a6, a7)
		elif a9 == None:
			quick_print(a1, a2, a3, a4, a5, a6, a7, a8)
		elif a10 == None:
			quick_print(a1, a2, a3, a4, a5, a6, a7, a8, a9)
		elif a11 == None:
			quick_print(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10)
		elif a12 == None:
			quick_print(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11)
		else:
			quick_print(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12)

def set_debug_mode(enabled):
	# 动态切换调试模式
	# 用法：set_debug_mode(True)
	global DEBUG_MODE
	DEBUG_MODE = enabled
	if enabled:
		quick_print("Debug mode: ENABLED")
	else:
		quick_print("Debug mode: DISABLED")
