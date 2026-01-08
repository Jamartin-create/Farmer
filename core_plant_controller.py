# 主控制器模块
# 协调所有模块，分发到对应区域处理
from utils import get_x_y
import core_zone_classifier
import core_zone_config
import state_manager
import features_companion
import zones_pumpkin_zone
import zones_support_zone
import zones_cactus_zone
import zones_mixed_zone
import zones_maze_zone
from core_debug import debug_print


# 步数计数器
_step_counter = 0


def plant_something():
	# 主入口：每个格子调用一次
	global _step_counter
	_step_counter = _step_counter + 1

	[x, y] = get_x_y()
	n = get_world_size()
	m = core_zone_config.get_pumpkin_zone_size(n)

	# 检查缓存是否需要重建
	state_manager.check_and_rebuild_all(n, m)

	# 每 100 步调用一次动态配置调整
	if _step_counter % 100 == 0:
		core_zone_config.apply_dynamic_adjustments()
		debug_print("Step", _step_counter, ": Applied dynamic config adjustments")

	# 记录伴生植物需求
	features_companion.record_companion_need(x, y, m)

	# 分类当前区域
	zone = core_zone_classifier.classify_zone(x, y, n, m)

	# 分发到对应区域
	if zone == 'pumpkin':
		zones_pumpkin_zone.handle_cell(x, y, m)
	elif zone == 'support':
		zones_support_zone.handle_cell(x, y, m)
	elif zone == 'cactus':
		zones_cactus_zone.handle_cell(x, y, m, n)
	elif zone == 'maze':
		zones_maze_zone.handle_cell(x, y, m, n)
	elif zone == 'mixed':
		zones_mixed_zone.handle_cell(x, y, m, n)
