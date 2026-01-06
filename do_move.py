import map_manage
from do_plant import plant_something
from consts import WATER_THRESHOLD

def _update_maps_at_current_pos():
	# 将当前位置的实体/地面信息写入本地缓存地图，方便后续逻辑使用
	x = get_pos_x()
	y = get_pos_y()
	map_manage.type_map[x][y] = get_entity_type()
	map_manage.ground_map[x][y] = get_ground_type()


def move_and_scan(direction):
	# “移动 + 扫描/记录当前位置”作为唯一入口（提高可读性）
	move(direction)
	_update_maps_at_current_pos()


def my_move(direction):
	# 兼容旧调用：保留原函数名
	move_and_scan(direction)

def lets_move():
	def _ensure_water():
		# 每一步先检查水量，不足则补水
		if get_water() < WATER_THRESHOLD:
			use_item(Items.Water)

	def _tick():
		# 单步要做的事：补水 + 种植/收获
		_ensure_water()
		plant_something()

	def _traverse_one_column():
		# 沿着 North 方向走完一整列
		for _ in range(get_world_size()):
			_tick()
			move_and_scan(North)

	while True:
		_traverse_one_column()
		move_and_scan(East)