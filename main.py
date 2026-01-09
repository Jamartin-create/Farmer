import map_manage

import do_move



def energy_drones():
	while True:
		entity = get_entity_type()
		for i in range(get_world_size()):
			move(North)
			do_a_flip()
		move(East)

print(num_drones(), max_drones())

if num_drones() < max_drones():
	spawn_drone(energy_drones)

# 程序入口：初始化本地地图缓存后，启动自动移动/种植循环
map_manage.init_map()
do_move.lets_move()


