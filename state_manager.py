# 状态管理模块
# 集中管理所有全局状态变量，提供统一的初始化和重建接口

# ===== 南瓜区状态 =====
pumpkin_ready_map = None          # 2D bool：每格是否成熟
pumpkin_ready_to_harvest = False  # bool：全区成熟标记
pumpkin_ready_m = None            # int：当前合并区大小

# ===== 向日葵状态 =====
sunflower_petals_map = None  # 2D int：每格花瓣数
sunflower_memo_n = None      # int：缓存对应的世界大小

# ===== 伴生植物状态 =====
companion_need_map = None    # 2D Entity|None：每格被请求的伴生植物
companion_memo_n = None      # int：缓存对应的世界大小

# ===== 迷宫状态 =====
maze_generated = False       # bool：是否已生成迷宫
maze_size = None             # int：迷宫大小
maze_substance_needed = None # int：生成迷宫所需的 Weird_Substance 数量
maze_visited = None          # 2D bool：DFS 访问标记
maze_path = None             # list：DFS 路径栈
maze_navigating = False      # bool：是否正在导航
maze_nav_direction = None    # Direction|None：导航建议方向
maze_memo_n = None           # int：缓存对应的世界大小
is_in_maze = False           # bool：当前是否在迷宫中


def init_pumpkin_state(n, m):
	# 初始化南瓜状态缓存
	global pumpkin_ready_map
	global pumpkin_ready_m
	global pumpkin_ready_to_harvest

	pumpkin_ready_m = m
	pumpkin_ready_to_harvest = False

	pumpkin_ready_map = []
	for _ in range(n):
		row = []
		for _ in range(n):
			row.append(False)
		pumpkin_ready_map.append(row)


def init_sunflower_state(n):
	# 初始化向日葵状态缓存
	global sunflower_petals_map
	global sunflower_memo_n

	sunflower_memo_n = n
	sunflower_petals_map = []
	for _ in range(n):
		row = []
		for _ in range(n):
			row.append(0)
		sunflower_petals_map.append(row)


def init_companion_state(n):
	# 初始化伴生植物状态缓存
	global companion_need_map
	global companion_memo_n

	companion_memo_n = n
	companion_need_map = []
	for _ in range(n):
		row = []
		for _ in range(n):
			row.append(None)
		companion_need_map.append(row)


def init_maze_state(n):
	# 初始化迷宫状态缓存
	global maze_visited
	global maze_path
	global maze_memo_n
	global maze_navigating
	global maze_generated

	global maze_size
	global maze_substance_needed

	maze_memo_n = n
	maze_generated = False
	maze_size = None
	maze_substance_needed = None
	maze_navigating = False

	maze_visited = []
	for _ in range(n):
		row = []
		for _ in range(n):
			row.append(False)
		maze_visited.append(row)

	maze_path = []


def check_and_rebuild_all(n, m):
	# 检查世界大小变化，自动重建所有缓存
	# 在每次 plant_something() 开始时调用
	global pumpkin_ready_map
	global pumpkin_ready_m
	
	global sunflower_petals_map
	global sunflower_memo_n
	
	global companion_need_map
	global companion_memo_n
	
	global maze_visited
	global maze_memo_n
	

	# 南瓜缓存：m 变化时重建
	if pumpkin_ready_map == None or pumpkin_ready_m != m:
		init_pumpkin_state(n, m)

	# 向日葵缓存：n 变化时重建
	if sunflower_petals_map == None or sunflower_memo_n != n:
		init_sunflower_state(n)

	# 伴生缓存：n 变化时重建
	if companion_need_map == None or companion_memo_n != n:
		init_companion_state(n)

	# 迷宫缓存：n 变化时重建
	if maze_visited == None or maze_memo_n != n:
		init_maze_state(n)
