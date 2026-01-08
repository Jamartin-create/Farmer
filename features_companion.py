# 伴生植物特性模块
# 跨区域功能：记录和满足伴生植物需求
import state_manager
from core_plant_executor import replant_as
from core_debug import debug_print


def record_companion_need(x, y, m):
	# 记录当前位置植物的伴生需求
	# 南瓜区内不记录
	if x < m and y < m:
		return

	entity = get_entity_type()
	if entity not in [Entities.Grass, Entities.Bush, Entities.Tree, Entities.Carrot]:
		return

	companion = get_companion()
	if companion == None:
		return

	plant_type, (tx, ty) = companion
	n = state_manager.companion_memo_n

	# 归一化坐标
	while tx < 0:
		tx = tx + n
	while ty < 0:
		ty = ty + n
	while tx >= n:
		tx = tx - n
	while ty >= n:
		ty = ty - n

	# 目标落在南瓜区：忽略
	if tx < m and ty < m:
		return

	# 冲突解决：高优先级覆盖
	current = state_manager.companion_need_map[tx][ty]
	if current == None or _get_priority(plant_type) > _get_priority(current):
		state_manager.companion_need_map[tx][ty] = plant_type
		debug_print("Companion: (", x, ",", y, ") requests", plant_type, "at (", tx, ",", ty, ")")


def handle_companion_tile(x, y):
	# 检查当前格子是否被标记为伴生需求点位
	need = state_manager.companion_need_map[x][y]
	if need == None:
		return False

	replant_as(need)
	state_manager.companion_need_map[x][y] = None
	debug_print("Companion: Fulfilled", need, "at (", x, ",", y, ")")
	return True


def _get_priority(entity):
	# 伴生植物优先级
	if entity == Entities.Tree:
		return 40
	if entity == Entities.Bush:
		return 30
	if entity == Entities.Carrot:
		return 20
	if entity == Entities.Grass:
		return 10
	return 0
