import utils
from consts import DIRECTION

type_map = []
ground_map = []


def init_map():
	# 初始化本地缓存地图：记录每个格子的实体类型与地面类型
	size = get_world_size()
	for i in range(size):
		type_map.append([])
		ground_map.append([])
		for j in range(size):
			type_map[i].append(None)
			ground_map[i].append(None)

def check_out_size(position):
	# True 表示越界
	if position < 0 or position >= get_world_size():
		return True
	return False


def check_neighbor_has(entity):
	# 检查当前格子四邻域是否存在指定实体
	[cur_x, cur_y] = utils.get_x_y()
	for i in range(len(DIRECTION)):
		[dx, dy] = DIRECTION[i]
		x = cur_x + dx
		y = cur_y + dy
		
		# 超出范围
		if check_out_size(x) or check_out_size(y):
			continue
			
		if type_map[x][y] == entity:
			return True
			
	return False
	