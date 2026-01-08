# 种植执行器模块
# 提供底层种植动作：ensure_soil, plant_xxx, replant_as
# 所有区域模块通过这个模块执行实际种植操作

def ensure_soil():
	# 耕地是开关：只在草地时 till 一次，避免 Soil -> Grassland 的反切换
	# 这是最常见的bug来源，必须先检查地面类型！
	if get_ground_type() == Grounds.Grassland:
		till()


def plant_pumpkin():
	# 种植南瓜（需要耕地）
	ensure_soil()
	plant(Entities.Pumpkin)


def plant_carrot():
	# 种植胡萝卜（需要耕地）
	ensure_soil()
	plant(Entities.Carrot)


def plant_sunflower():
	# 种植向日葵（需要耕地）
	ensure_soil()
	plant(Entities.Sunflower)


def plant_cactus():
	# 种植仙人掌（需要耕地）
	ensure_soil()
	plant(Entities.Cactus)


def plant_tree():
	# 种植树（不需要耕地，可种在草地或土壤上）
	plant(Entities.Tree)


def plant_bush():
	# 种植灌木（不需要耕地）
	plant(Entities.Bush)


def plant_grass():
	# 种植草（不需要耕地）
	plant(Entities.Grass)


def replant_as(target_entity):
	# 统一的"收获后补种"入口
	# 在种植后自动调用相应的后处理（如施肥）
	# 导入肥料功能（延迟导入避免循环依赖）
	import features_fertilizer

	if target_entity == Entities.Carrot:
		plant_carrot()
		# 肥料在种植后立刻使用，更有效
		features_fertilizer.maybe_use_fertilizer(Entities.Carrot)
		return

	if target_entity == Entities.Pumpkin:
		plant_pumpkin()
		return

	if target_entity == Entities.Sunflower:
		plant_sunflower()
		return

	if target_entity == Entities.Cactus:
		plant_cactus()
		# 仙人掌也在种下后立刻施肥
		features_fertilizer.maybe_use_fertilizer(Entities.Cactus)
		return

	if target_entity == Entities.Tree:
		plant_tree()
		return

	if target_entity == Entities.Bush:
		plant_bush()
		return

	if target_entity == Entities.Grass:
		plant_grass()
		return
