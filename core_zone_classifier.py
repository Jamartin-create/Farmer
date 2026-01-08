# 区域分类器模块
# 根据 core_zone_config 判断坐标 (x, y) 属于哪个区域
# 按优先级顺序检查
import core_zone_config


def classify_zone(x, y, n, m):
	# 判断坐标 (x, y) 属于哪个区域

	if core_zone_config.zone_enabled['pumpkin'] and _in_pumpkin_zone(x, y, m):
		return 'pumpkin'

	if core_zone_config.zone_enabled['maze'] and _in_maze_zone(x, y, n):
		return 'maze'

	if core_zone_config.zone_enabled['support'] and _in_support_ring(x, y, m):
		return 'support'

	if core_zone_config.zone_enabled['cactus'] and _in_cactus_zone(x, y, m, n):
		return 'cactus'

	return 'mixed'


def _in_pumpkin_zone(x, y, m):
	# 南瓜区：0 <= x < m 且 0 <= y < m
	return x >= 0 and y >= 0 and x < m and y < m


def _in_support_ring(x, y, m):
	# 供给环带
	width = core_zone_config.get_support_ring_width()

	if y < m and x >= m and x < m + width:
		return True

	if x < m and y >= m and y < m + width:
		return True

	return False


def _in_cactus_zone(x, y, m, n):
	# 仙人掌区
	x_min, x_max, y_min, y_max = core_zone_config.get_cactus_zone_bounds(m, n)
	return x >= x_min and x < x_max and y >= y_min and y < y_max


def _in_maze_zone(x, y, n):
	# 迷宫区
	maze_start = core_zone_config.get_maze_zone_start(n)
	return x >= maze_start and y >= maze_start
