# 混合区模块
# 使用棋盘格分配：树 + 向日葵 + 草
import map_manage
import state_manager
from core_plant_executor import replant_as
from consts import SUNFLOWER_MIN_COUNT_FOR_8X
from core_debug import debug_print


def handle_cell(x, y, m, n):
	# 处理混合区的单个格子
	# 优先处理伴生植物需求
	import features_companion
	if features_companion.handle_companion_tile(x, y):
		return

	# 树点位：棋盘格偶数格
	if (x + y) % 2 == 0:
		_handle_tree_spot(x, y)
		return

	# 向日葵点位：棋盘格奇数格
	if (x + y) % 2 == 1:
		_handle_sunflower_spot(x, y)
		return

	# 兜底：草
	_handle_generic_cell(Entities.Grass, x, y)


def _handle_tree_spot(x, y):
	# 树点位：检查邻居，避免相邻减速
	if map_manage.check_neighbor_has(Entities.Tree):
		_handle_generic_cell(Entities.Grass, x, y)
		debug_print("Mixed zone (", x, ",", y, "): Tree neighbor detected, plant grass")
	else:
		_handle_generic_cell(Entities.Tree, x, y)


def _handle_sunflower_spot(x, y):
	# 向日葵点位：8倍能量策略
	entity = get_entity_type()

	# 更新花瓣缓存
	_update_sunflower_petals(x, y)

	# 枯萎南瓜或空地：补种向日葵
	if entity == Entities.Dead_Pumpkin or entity == None:
		replant_as(Entities.Sunflower)
		_update_sunflower_petals(x, y)
		return

	# 是向日葵：检查是否满足收割条件
	if entity == Entities.Sunflower:
		count, max_petals = _count_sunflowers_and_max()

		# 数量不足 10，先攒
		if count < SUNFLOWER_MIN_COUNT_FOR_8X:
			return

		# 只收最大花瓣数
		if can_harvest():
			current_petals = state_manager.sunflower_petals_map[x][y]
			if current_petals == max_petals:
				harvest()
				replant_as(Entities.Sunflower)
				_update_sunflower_petals(x, y)
				debug_print("Mixed zone (", x, ",", y, "): Harvested max-petal sunflower (", max_petals, ")")
		return

	# 其他作物：换种向日葵
	if can_harvest():
		harvest()
		replant_as(Entities.Sunflower)
		_update_sunflower_petals(x, y)


def _handle_generic_cell(target_entity, x, y):
	# 通用处理
	entity = get_entity_type()

	if entity == Entities.Dead_Pumpkin or entity == None:
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


def _update_sunflower_petals(x, y):
	# 更新当前位置向日葵花瓣缓存
	if get_entity_type() == Entities.Sunflower:
		petals = measure()
		if petals != None:
			state_manager.sunflower_petals_map[x][y] = petals
		else:
			state_manager.sunflower_petals_map[x][y] = 0
	else:
		state_manager.sunflower_petals_map[x][y] = 0


def _count_sunflowers_and_max():
	# 统计向日葵数量和最大花瓣数
	count = 0
	max_petals = 0
	n = state_manager.sunflower_memo_n
	for x in range(n):
		for y in range(n):
			p = state_manager.sunflower_petals_map[x][y]
			if p > 0:
				count = count + 1
				if p > max_petals:
					max_petals = p
	return (count, max_petals)
