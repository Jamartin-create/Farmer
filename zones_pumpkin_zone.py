
# 南瓜区模块
# 负责南瓜合并策略

import state_manager
from core_plant_executor import plant_pumpkin
from core_debug import debug_print


def handle_cell(x, y, m):
	# 处理南瓜区的单个格子
	entity = get_entity_type()

	# 枯萎南瓜：直接补种
	if entity == Entities.Dead_Pumpkin:
		state_manager.pumpkin_ready_map[x][y] = False
		plant_pumpkin()
		debug_print("Pumpkin zone (", x, ",", y, "): Replaced dead pumpkin")
		return

	# 空地：补种
	if entity == None:
		state_manager.pumpkin_ready_map[x][y] = False
		plant_pumpkin()
		return

	# 南瓜：更新成熟度
	if entity == Entities.Pumpkin:
		if can_harvest():
			state_manager.pumpkin_ready_map[x][y] = True
		else:
			state_manager.pumpkin_ready_map[x][y] = False

		# 检测全区成熟
		if (state_manager.pumpkin_ready_to_harvest == False) and _check_zone_all_ready(m):
			state_manager.pumpkin_ready_to_harvest = True
			debug_print("Pumpkin zone: All ", m, "x", m, " ready for harvest!")

		if state_manager.pumpkin_ready_to_harvest and can_harvest():
			harvest()
			state_manager.pumpkin_ready_to_harvest = False
			_clear_zone_ready(m)
			plant_pumpkin()
			debug_print("Pumpkin zone (", x, ",", y, "): Harvested mega pumpkin!")
		return

	# 其他异常实体
	if can_harvest():
		harvest()
	state_manager.pumpkin_ready_map[x][y] = False
	plant_pumpkin()


def _check_zone_all_ready(m):
	# 检查 m×m 南瓜区是否全部成熟
	for x in range(m):
		for y in range(m):
			if state_manager.pumpkin_ready_map[x][y] != True:
				return False
	return True


def _clear_zone_ready(m):
	# 收割后清空缓存
	for x in range(m):
		for y in range(m):
			state_manager.pumpkin_ready_map[x][y] = False
