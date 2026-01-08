import map_manage
from core_plant_controller import plant_something
import zones_maze_zone
from consts import WATER_THRESHOLD

def _update_maps_at_current_pos():
	# 将当前位置的实体/地面信息写入本地缓存地图，方便后续逻辑使用
	x = get_pos_x()
	y = get_pos_y()
	map_manage.type_map[x][y] = get_entity_type()
	map_manage.ground_map[x][y] = get_ground_type()


def move_and_scan(direction):
	# "移动 + 扫描/记录当前位置"作为唯一入口（提高可读性）
	move(direction)
	_update_maps_at_current_pos()


def lets_move():
	def _ensure_water():
		# 每一步先检查水量，不足则补水
		if get_water() < WATER_THRESHOLD:
			use_item(Items.Water)

	def _tick():
		# 单步要做的事：补水 + 种植/收获
		_ensure_water()
		plant_something()

	def _maze_navigation_step():
		# 迷宫导航模式：使用导航算法计算的方向
		_tick()
		maze_dir = zones_maze_zone.get_nav_direction()
		if maze_dir != None:
			# 有导航方向，按导航方向移动
			move_and_scan(maze_dir)
		else:
			# 没有导航方向（可能已到达宝藏或出错），保持当前位置
			# 这种情况应该很少发生，但为了安全起见，不移动
			pass

	def _normal_traverse_one_column():
		# 普通模式：沿着 North 方向走完一整列
		# 注意：在遍历过程中如果进入迷宫，会通过模式切换自动处理
		for _ in range(get_world_size()):
			# 每次移动前检查是否进入迷宫
			if zones_maze_zone.is_in_maze_mode():
				# 进入迷宫，切换到导航模式
				return
			_tick()
			move_and_scan(North)

	# 主循环：根据是否在迷宫中切换运动模式
	while True:
		if zones_maze_zone.is_in_maze_mode():
			# 迷宫模式：使用导航算法
			_maze_navigation_step()
		else:
			# 普通模式：按列遍历
			_normal_traverse_one_column()
			# 检查是否在遍历过程中进入了迷宫
			if zones_maze_zone.is_in_maze_mode():
				# 如果进入了迷宫，继续使用迷宫模式
				continue
			# 继续普通遍历：向东移动一列
			move_and_scan(East)
