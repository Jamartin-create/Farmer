# 区域配置模块
# 动态调整区域边界、优先级、启用状态
# 支持根据物资情况运行时修改配置
import state_resource_monitor
from core_debug import debug_print


# ===== 动态配置全局变量 =====

# 区域启用开关
zone_enabled = {
	'pumpkin': True,
	'support': True,
	'cactus': True,
	'maze': True,
	'mixed': True,
}

# 区域优先级
zone_priority = {
	'pumpkin': 100,
	'maze': 90,
	'support': 80,
	'cactus': 70,
	'mixed': 60,
}

# 区域大小系数
zone_size_factor = {
	'support_ring_width': 1,
	'cactus_multiplier': 1.0,
	'maze_multiplier': 1.0,
}


def _floor_half(n):
	# 计算 floor(n/2)
	half = 0
	while (half + 1) * 2 <= n:
		half = half + 1
	return half


def get_pumpkin_zone_size(n):
	# 计算南瓜区大小：m = n - floor(n/2)
	return n - _floor_half(n)


def get_support_ring_width():
	# 获取当前供给环带厚度
	return zone_size_factor['support_ring_width']


def get_cactus_zone_bounds(m, n):
	# 计算仙人掌区边界
	multiplier = zone_size_factor['cactus_multiplier']
	x_min = m + 1
	x_max_raw = m + m * multiplier + 1
	if x_max_raw > n:
		x_max = n
	else:
		x_max = x_max_raw
	y_min = 0
	y_max = m
	return (x_min, x_max, y_min, y_max)


def get_maze_zone_start(n):
	# 计算迷宫区起始坐标
	return n - _floor_half(n)


def apply_dynamic_adjustments():
	# 根据资源监控结果动态调整区域配置
	suggestions = state_resource_monitor.analyze_resource_pressure()

	# 扩大供给区
	if suggestions['expand_support']:
		zone_size_factor['support_ring_width'] = 2
		debug_print("Config: Expanded support ring to width 2")
	else:
		zone_size_factor['support_ring_width'] = 1

	# 提高混合区优先级
	if suggestions['expand_trees']:
		zone_priority['mixed'] = 85
		debug_print("Config: Increased mixed zone priority for trees")
	else:
		zone_priority['mixed'] = 60

	# 启用/禁用迷宫区
	if suggestions['enable_maze']:
		zone_enabled['maze'] = True
		debug_print("Config: Enabled maze zone")
	elif suggestions['disable_maze']:
		zone_enabled['maze'] = False
		debug_print("Config: Disabled maze zone (resource insufficient)")


def disable_zone(zone_name):
	# 临时禁用某个区域
	zone_enabled[zone_name] = False
	debug_print("Config: Disabled", zone_name, "zone")


def enable_zone(zone_name):
	# 重新启用某个区域
	zone_enabled[zone_name] = True
	debug_print("Config: Enabled", zone_name, "zone")
