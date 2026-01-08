# 资源监控模块
# 统计当前物资情况，为动态区域配置提供决策依据
from core_debug import debug_print


def get_current_resources():
	# 获取当前所有资源数量
	# 返回：dict {item_name: count}
	return {
		'carrot': num_items(Items.Carrot),
		'pumpkin': num_items(Items.Pumpkin),
		'wood': num_items(Items.Wood),
		'hay': num_items(Items.Hay),
		'power': num_items(Items.Power),
		'fertilizer': num_items(Items.Fertilizer),
		'weird_substance': num_items(Items.Weird_Substance),
		'cactus': num_items(Items.Cactus),
		'water': num_items(Items.Water),
	}


def analyze_resource_pressure():
	# 分析资源压力，返回建议的区域调整
	# 返回：dict {suggestion_key: bool}
	resources = get_current_resources()
	suggestions = {
		'expand_support': False,
		'expand_trees': False,
		'shrink_sunflower': False,
		'disable_maze': False,
		'enable_maze': False,
	}

	# 胡萝卜短缺 -> 建议扩大供给区
	if resources['carrot'] < 500:
		suggestions['expand_support'] = True
		debug_print("Resource: Carrot low (", resources['carrot'], "), suggest expand support zone")

	# 木材短缺 -> 建议增加树区
	if resources['wood'] < 1000:
		suggestions['expand_trees'] = True
		debug_print("Resource: Wood low (", resources['wood'], "), suggest expand tree zone")

	# 能量充足 -> 建议缩小向日葵区
	if resources['power'] > 5000:
		suggestions['shrink_sunflower'] = True
		debug_print("Resource: Power high (", resources['power'], "), suggest shrink sunflower zone")

	# Weird_Substance 充足 -> 可以启用迷宫区
	n = get_world_size()
	maze_level = num_unlocked(Unlocks.Mazes)
	if maze_level > 0:
		substance_needed = n * (2 ** (maze_level - 1))
		if resources['weird_substance'] >= substance_needed:
			suggestions['enable_maze'] = True
			debug_print("Resource: Weird_Substance sufficient (", resources['weird_substance'], "/", substance_needed, "), can enable maze")
		else:
			suggestions['disable_maze'] = True
			debug_print("Resource: Weird_Substance insufficient (", resources['weird_substance'], "/", substance_needed, "), should disable maze")

	return suggestions


def should_prioritize_zone(zone_name):
	# 判断某个区域是否应该优先执行（基于资源情况）
	suggestions = analyze_resource_pressure()

	if zone_name == 'support' and suggestions['expand_support']:
		return True

	if zone_name == 'mixed' and suggestions['expand_trees']:
		return True

	if zone_name == 'maze' and suggestions['enable_maze']:
		return True

	return False
