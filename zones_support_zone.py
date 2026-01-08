# 供给区模块
# 胡萝卜供给环带
# from core_plant_executor import replant_as
from core_debug import debug_print
from core_plant_executor import replant_as


def handle_cell(x, y, m):
	# 处理供给区的单个格子
	_handle_generic_cell(Entities.Carrot, x, y)


def _handle_generic_cell(target_entity, x, y):
	# 通用处理
	entity = get_entity_type()

	if entity == Entities.Dead_Pumpkin:
		replant_as(target_entity)
		debug_print("Support zone (", x, ",", y, "): Replaced dead pumpkin with", target_entity)
		return

	if entity == None:
		replant_as(target_entity)
		return

	if entity == target_entity:
		if can_harvest():
			harvest()
			replant_as(target_entity)
		return

	if can_harvest():
		harvest()
		replant_as(target_entity)
