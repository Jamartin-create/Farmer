# 仙人掌区模块
# 利用仙人掌排序连锁机制
from core_plant_executor import replant_as
from core_debug import debug_print


def handle_cell(x, y, m, n):
	# 处理仙人掌区的单个格子
	entity = get_entity_type()

	if entity == Entities.Dead_Pumpkin:
		replant_as(Entities.Cactus)
		debug_print("Cactus zone (", x, ",", y, "): Replaced dead pumpkin")
		return

	if entity == None:
		replant_as(Entities.Cactus)
		return

	if entity == Entities.Cactus:
		if can_harvest():
			harvest()
			replant_as(Entities.Cactus)
		return

	if can_harvest():
		harvest()
		replant_as(Entities.Cactus)
