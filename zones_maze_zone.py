# 迷宫区模块
# 负责迷宫生成和DFS导航
# import state_manager
from core_plant_executor import plant_bush
from utils import get_x_y
from core_debug import debug_print
import state_manager


def handle_cell(x, y, m, n):
	# 处理迷宫区的单个格子
	_check_and_update_maze_status()

	entity = get_entity_type()

	# 如果还没有生成迷宫，尝试生成
	if entity != Entities.Hedge and entity != Entities.Treasure:
		if not _generate_maze_if_needed():
			return

	# 如果在宝藏位置，收获
	if entity == Entities.Treasure:
		harvest()
		state_manager.maze_generated = False
		_reset_maze_navigation()
		_check_and_update_maze_status()
		debug_print("Maze zone (", x, ",", y, "): Harvested treasure!")
		return

	# 如果在迷宫中但不是宝藏，计算导航方向
	if entity == Entities.Hedge:
		_navigate_to_treasure()
		return

	_generate_maze_if_needed()


def _generate_maze_if_needed():
	# 检查是否已有迷宫，如果没有则尝试生成
	entity = get_entity_type()

	# 如果已经在迷宫中
	if entity == Entities.Hedge or entity == Entities.Treasure:
		if not state_manager.maze_generated:
			state_manager.maze_generated = True
			n = get_world_size()
			state_manager.maze_size = n
			state_manager.maze_substance_needed = n * (2 ** (num_unlocked(Unlocks.Mazes) - 1))
			debug_print("Maze zone: Detected existing maze")
		return True

	if state_manager.maze_generated:
		return True

	# 计算所需资源
	n = get_world_size()
	substance_needed = n * (2 ** (num_unlocked(Unlocks.Mazes) - 1))

	# 检查资源是否充足
	if num_items(Items.Weird_Substance) < substance_needed:
		debug_print("Maze zone: Insufficient Weird_Substance (", num_items(Items.Weird_Substance), "/", substance_needed, ")")
		return False

	# 确保当前位置是灌木
	if entity != Entities.Bush:
		plant_bush()
		return False

	# 生成迷宫
	use_item(Items.Weird_Substance, substance_needed)
	state_manager.maze_generated = True
	state_manager.maze_size = n
	state_manager.maze_substance_needed = substance_needed
	debug_print("Maze zone: Generated maze with", substance_needed, "Weird_Substance")
	return True


def _reset_maze_navigation():
	# 重置导航状态
	state_manager.maze_navigating = False
	state_manager.maze_path = []
	state_manager.maze_nav_direction = None

	n = state_manager.maze_memo_n
	if state_manager.maze_visited == None:
		return
	for x in range(n):
		for y in range(n):
			state_manager.maze_visited[x][y] = False


def _navigate_to_treasure():
	# 使用 DFS 导航到宝藏
	treasure_pos = measure()
	if treasure_pos == None:
		state_manager.maze_nav_direction = None
		return

	treasure_x, treasure_y = treasure_pos
	[current_x, current_y] = get_x_y()

	# 如果已经在宝藏位置
	if current_x == treasure_x and current_y == treasure_y:
		_reset_maze_navigation()
		state_manager.maze_nav_direction = None
		return

	# 初始化导航状态
	if not state_manager.maze_navigating:
		state_manager.maze_navigating = True
		state_manager.maze_path = [[current_x, current_y]]
		n = state_manager.maze_memo_n
		if state_manager.maze_visited == None:
			state_manager.init_maze_state(n)
		for x in range(n):
			for y in range(n):
				state_manager.maze_visited[x][y] = False
		state_manager.maze_visited[current_x][current_y] = True

	# DFS 单步
	directions = [North, South, East, West]

	for direction in directions:
		if not can_move(direction):
			continue

		# 计算目标位置
		if direction == North:
			next_x, next_y = current_x, current_y + 1
		elif direction == South:
			next_x, next_y = current_x, current_y - 1
		elif direction == East:
			next_x, next_y = current_x + 1, current_y
		else:  # West
			next_x, next_y = current_x - 1, current_y

		# 边界检查
		n = state_manager.maze_memo_n
		if next_x < 0 or next_x >= n or next_y < 0 or next_y >= n:
			continue

		# 如果已访问，跳过
		if state_manager.maze_visited[next_x][next_y]:
			continue

		# 找到未访问的相邻格子
		state_manager.maze_path.append([next_x, next_y])
		state_manager.maze_visited[next_x][next_y] = True
		state_manager.maze_nav_direction = direction
		return

	# 需要回溯
	if len(state_manager.maze_path) > 1:
		state_manager.maze_path.pop()
		prev_pos = state_manager.maze_path[-1]
		prev_x, prev_y = prev_pos[0], prev_pos[1]

		dx = prev_x - current_x
		dy = prev_y - current_y

		if dx == 1:
			state_manager.maze_nav_direction = East
		elif dx == -1:
			state_manager.maze_nav_direction = West
		elif dy == 1:
			state_manager.maze_nav_direction = North
		elif dy == -1:
			state_manager.maze_nav_direction = South
		else:
			_reset_maze_navigation()
			state_manager.maze_nav_direction = None
		return

	_reset_maze_navigation()
	state_manager.maze_nav_direction = None


def _check_and_update_maze_status():
	# 检查当前位置是否在迷宫中
	entity = get_entity_type()

	if entity == Entities.Hedge or entity == Entities.Treasure:
		if not state_manager.is_in_maze:
			state_manager.is_in_maze = True
			debug_print("Maze zone: Entered maze")
		return True

	if state_manager.is_in_maze:
		state_manager.is_in_maze = False
		_reset_maze_navigation()
		debug_print("Maze zone: Exited maze")

	return False


# ===== 导出函数（供 do_move.py 使用）=====

def get_nav_direction():
	# 获取迷宫导航建议的移动方向
	return state_manager.maze_nav_direction


def is_in_maze_mode():
	# 获取当前是否在迷宫模式
	return state_manager.is_in_maze
