# 多无人机架构设计方案

## 问题分析

### 当前架构的限制
1. **全局变量隔离**：每个无人机有独立的变量空间，无法直接共享状态
2. **状态分散**：状态分布在 `state_manager.py` 和 `map_manage.py` 中
3. **关键共享需求**：
   - `pumpkin_ready_map`：南瓜成熟状态（需要全局协调收获）
   - `type_map/ground_map`：地图缓存（可以独立维护）
   - `sunflower_petals_map`：向日葵花瓣数（需要协调以保持8x能量）
   - `maze_generated`：迷宫状态（需要全局协调）
   - `companion_need_map`：伴生需求（可以局部化）

## 推荐方案：混合架构

### 核心思想
**"地图即数据库 + 区域分工 + 状态分层"**

- **共享层**：通过地图位置存储全局状态
- **独立层**：每个无人机维护自己区域的局部状态
- **协调层**：特定位置作为"信号旗"进行协调

---

## 实现方案

### 1. 地图状态存储系统

#### 设计原则
使用地图左上角作为"状态存储区"，通过特定实体编码状态信息。

```python
# shared_state_storage.py
# 共享状态存储模块 - 使用地图特定位置作为"数据库"

# ===== 状态存储位置定义 =====
# 使用 (0, 0) ~ (0, 4) 作为状态存储区
STATE_STORAGE_ROW = 0
STATE_POSITION = {
    'pumpkin_harvest_ready': (0, 0),  # 南瓜是否可收获
    'maze_generated': (0, 1),         # 迷宫是否已生成
    'sunflower_count': (0, 2),        # 向日葵数量（用花瓣数编码）
    'coordination_lock': (0, 3),      # 协调锁
    'drone_heartbeat_base': (0, 4),   # 无人机心跳基址
}

# ===== 状态编码规则 =====
# Bool 状态：Grass=False, Bush=True
# 数值状态：通过测量花瓣数、测量次数等编码

def write_bool_state(key, value):
    """写入布尔状态到地图"""
    pos = STATE_POSITION[key]
    move_to(pos[0], pos[1])

    current = get_entity_type()
    target = Entities.Bush if value else Entities.Grass

    if current != target:
        # 确保是土壤
        if get_ground_type() != Grounds.Soil:
            till()
        # 收获现有作物
        if can_harvest():
            harvest()
        # 种植目标状态
        if target == Entities.Bush:
            plant(Entities.Bush)
        # Grass 不需要种植，保持空地即可

def read_bool_state(key):
    """从地图读取布尔状态"""
    pos = STATE_POSITION[key]
    # 可以在任意位置调用 measure() 来读取指定位置
    # 或者移动到目标位置读取
    old_x, old_y = get_pos_x(), get_pos_y()
    move_to(pos[0], pos[1])
    result = get_entity_type() == Entities.Bush
    move_to(old_x, old_y)
    return result

def write_int_state(key, value):
    """写入整数状态（0-15 通过向日葵花瓣数）"""
    pos = STATE_POSITION[key]
    move_to(pos[0], pos[1])

    # 种植向日葵并等待到目标花瓣数
    if get_entity_type() != Entities.Sunflower:
        if can_harvest():
            harvest()
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Sunflower)

    # 等待向日葵长到目标花瓣数
    while measure() != value:
        do_a_flip()  # 消耗时间

def read_int_state(key):
    """读取整数状态"""
    pos = STATE_POSITION[key]
    old_x, old_y = get_pos_x(), get_pos_y()
    move_to(pos[0], pos[1])

    if get_entity_type() == Entities.Sunflower:
        result = measure()
    else:
        result = 0

    move_to(old_x, old_y)
    return result

def acquire_lock(key='coordination_lock', timeout=100):
    """获取协调锁"""
    pos = STATE_POSITION[key]
    attempts = 0

    while attempts < timeout:
        move_to(pos[0], pos[1])

        # 检查锁是否空闲（Grass=空闲，Bush=占用）
        if get_entity_type() != Entities.Bush:
            # 锁空闲，尝试获取
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Bush)
            # 再次确认（防止竞态）
            if get_entity_type() == Entities.Bush:
                return True

        attempts += 1
        do_a_flip()  # 等待

    return False

def release_lock(key='coordination_lock'):
    """释放协调锁"""
    pos = STATE_POSITION[key]
    move_to(pos[0], pos[1])

    if can_harvest():
        harvest()
    # 保持 Grass 状态表示空闲
```

---

### 2. 无人机角色分工

#### 方案 A：主从架构

```python
# drone_coordinator.py
# 无人机协调器 - 定义角色和任务分配

DRONE_ROLES = {
    'master': 0,      # 主无人机 ID
    'pumpkin': 1,     # 南瓜区专员
    'cactus': 2,      # 仙人掌区专员
    'maze': 3,        # 迷宫探索者
    'support': 4,     # 辅助资源采集
}

def get_my_role():
    """获取当前无人机的角色"""
    my_id = get_drone_id()  # 假设游戏提供此 API

    for role, drone_id in DRONE_ROLES.items():
        if my_id == drone_id:
            return role

    return 'worker'  # 默认工作者

def get_assigned_zone():
    """获取当前无人机负责的区域"""
    role = get_my_role()
    n = get_world_size()
    m = get_pumpkin_zone_size(n)

    if role == 'master':
        # 主无人机负责协调和南瓜区
        return {
            'type': 'pumpkin',
            'bounds': (0, 0, m, m)
        }
    elif role == 'pumpkin':
        return {
            'type': 'pumpkin',
            'bounds': (0, 0, m, m)
        }
    elif role == 'cactus':
        return {
            'type': 'cactus',
            'bounds': (m+1, 0, min(2*m+1, n), m)
        }
    elif role == 'maze':
        maze_start = n // 2
        return {
            'type': 'maze',
            'bounds': (maze_start, maze_start, n, n)
        }
    elif role == 'support':
        # 支持环和混合区
        return {
            'type': 'support',
            'bounds': (m, 0, m+1, m)  # 支持环
        }
    else:
        # 默认工作者：遍历所有区域
        return {
            'type': 'all',
            'bounds': (0, 0, n, n)
        }

def is_in_my_zone(x, y):
    """检查坐标是否在我负责的区域"""
    zone = get_assigned_zone()
    bounds = zone['bounds']

    return (bounds[0] <= x < bounds[2] and
            bounds[1] <= y < bounds[3])
```

#### 方案 B：完全分布式架构

```python
# drone_distributed.py
# 分布式架构 - 每个无人机独立工作，通过地图协调

def claim_territory():
    """动态声明领地（启动时调用）"""
    n = get_world_size()
    my_id = get_drone_id()
    num_drones = num_unlocked_drones()

    # 按 ID 均分地图列
    cols_per_drone = n // num_drones
    my_start_col = my_id * cols_per_drone
    my_end_col = my_start_col + cols_per_drone if my_id < num_drones - 1 else n

    return {
        'x_range': (my_start_col, my_end_col),
        'y_range': (0, n)
    }

def coordinate_pumpkin_harvest():
    """协调南瓜收获（所有无人机都可以调用）"""
    # 1. 检查是否有无人机已在协调
    if read_bool_state('pumpkin_harvest_ready'):
        # 已经有人标记为可收获，执行收获
        return True

    # 2. 尝试获取锁
    if not acquire_lock():
        return False

    # 3. 检查南瓜区是否全部成熟
    n = get_world_size()
    m = get_pumpkin_zone_size(n)
    all_ready = True

    for x in range(m):
        for y in range(m):
            move_to(x, y)
            if get_entity_type() == Entities.Pumpkin:
                if not can_harvest():
                    all_ready = False
                    break
        if not all_ready:
            break

    # 4. 如果全部成熟，设置状态
    if all_ready:
        write_bool_state('pumpkin_harvest_ready', True)

    # 5. 释放锁
    release_lock()

    return all_ready
```

---

### 3. 状态管理重构

#### 修改 state_manager.py

```python
# state_manager_v2.py
# 状态管理器 v2 - 支持多无人机

# ===== 配置：哪些状态需要共享 =====
SHARED_STATES = {
    'pumpkin_ready_to_harvest',  # 南瓜全区成熟标记
    'maze_generated',            # 迷宫已生成
}

LOCAL_STATES = {
    'pumpkin_ready_map',         # 每个无人机维护自己区域的
    'sunflower_petals_map',
    'companion_need_map',
    'maze_visited',
}

# ===== 本地状态（和之前一样） =====
pumpkin_ready_map = None
sunflower_petals_map = None
companion_need_map = None
maze_visited = None
# ... 其他状态

# ===== 共享状态访问器 =====
def get_pumpkin_harvest_ready():
    """获取南瓜收获就绪状态（从地图读取）"""
    return shared_state_storage.read_bool_state('pumpkin_harvest_ready')

def set_pumpkin_harvest_ready(value):
    """设置南瓜收获就绪状态（写入地图）"""
    shared_state_storage.write_bool_state('pumpkin_harvest_ready', value)

def get_maze_generated():
    """获取迷宫生成状态（从地图读取）"""
    return shared_state_storage.read_bool_state('maze_generated')

def set_maze_generated(value):
    """设置迷宫生成状态（写入地图）"""
    shared_state_storage.write_bool_state('maze_generated', value)

# ===== 初始化函数保持不变 =====
# init_pumpkin_state(), init_sunflower_state() 等保持原样
```

---

### 4. 主程序入口修改

```python
# main_multi_drone.py
# 多无人机主程序

import map_manage
import do_move
import drone_coordinator
import shared_state_storage

def master_drone_main():
    """主无人机：负责协调和全局决策"""
    # 初始化共享状态存储区
    shared_state_storage.init_storage_area()

    # 初始化本地地图缓存
    map_manage.init_map()

    # 启动主循环
    do_move.lets_move()

def worker_drone_main():
    """工作无人机：负责特定区域"""
    # 获取我的角色和区域
    role = drone_coordinator.get_my_role()
    zone = drone_coordinator.get_assigned_zone()

    # 初始化本地地图缓存
    map_manage.init_map()

    # 启动区域循环
    if zone['type'] == 'pumpkin':
        do_move.pumpkin_zone_loop(zone['bounds'])
    elif zone['type'] == 'cactus':
        do_move.cactus_zone_loop(zone['bounds'])
    elif zone['type'] == 'maze':
        do_move.maze_zone_loop(zone['bounds'])
    else:
        do_move.lets_move()  # 默认全局遍历

def energy_drone_main():
    """能量无人机：专门收集能量"""
    while True:
        for i in range(get_world_size()):
            move(North)
            do_a_flip()
        move(East)

# ===== 启动逻辑 =====
print("Drones:", num_drones(), "/", max_drones())

# 根据无人机 ID 分配任务
my_id = get_drone_id() if num_drones() > 0 else 0

if my_id == 0:
    # 主无人机（默认无人机）
    if num_drones() < max_drones():
        # 生成能量无人机
        spawn_drone(energy_drone_main)

        # 生成工作无人机
        if max_drones() >= 3:
            spawn_drone(worker_drone_main)
        if max_drones() >= 4:
            spawn_drone(worker_drone_main)

    master_drone_main()
else:
    # 工作无人机
    worker_drone_main()
```

---

## 关键设计决策

### 1. 为什么使用地图存储？
- **唯一的共享媒介**：游戏不提供其他跨无人机通信方式
- **持久化**：即使无人机重启，状态也能恢复
- **原子性**：地图操作是原子的，天然防止竞态条件

### 2. 哪些状态需要共享？
**必须共享：**
- `pumpkin_ready_to_harvest`：需要所有无人机协调收获
- `maze_generated`：避免重复生成迷宫

**可以本地：**
- `pumpkin_ready_map`：每个无人机只需知道自己区域的
- `sunflower_petals_map`：可以每个无人机独立维护
- `type_map/ground_map`：完全可以本地缓存

### 3. 锁机制的必要性
当多个无人机需要协调全局操作时（如南瓜收获、迷宫生成），需要锁来防止冲突。

---

## 性能考虑

### 开销分析
1. **状态读取**：移动到状态存储区 + 读取实体类型（~2-5 tick）
2. **状态写入**：移动 + 收获 + 种植（~5-10 tick）
3. **锁竞争**：最坏情况下等待其他无人机释放锁（~100 tick）

### 优化策略
1. **缓存读取**：本地缓存共享状态，定期刷新（每100步）
2. **延迟写入**：批量更新状态，减少移动次数
3. **无锁设计**：大部分操作应该是无锁的，只有关键协调点需要锁

---

## 实施路线图

### Phase 1：基础设施（1-2天）
1. 实现 `shared_state_storage.py`
2. 测试状态读写的正确性和性能

### Phase 2：角色系统（2-3天）
1. 实现 `drone_coordinator.py`
2. 修改 `main.py` 支持角色分配

### Phase 3：状态迁移（3-5天）
1. 修改 `state_manager.py` 支持共享/本地状态分离
2. 更新所有使用状态的模块

### Phase 4：区域循环（3-5天）
1. 实现 `do_move.py` 的区域循环版本
2. 测试多无人机协同工作

### Phase 5：优化和调试（持续）
1. 性能调优
2. 处理边界情况
3. 添加监控和调试工具

---

## 测试策略

### 单无人机回归测试
确保新架构在单无人机下和原来行为一致。

### 双无人机协调测试
- 测试南瓜收获协调
- 测试迷宫生成协调
- 测试锁机制

### 多无人机压力测试
- 4+ 无人机同时工作
- 检查资源竞争
- 监控效率提升

---

## 备选方案

如果地图存储方案性能不佳，可以考虑：

### 方案：完全独立架构
- 每个无人机完全独立工作
- 放弃全局协调（如南瓜不等全部成熟就收获）
- 优点：零协调开销
- 缺点：可能损失一些优化策略

### 方案：时间片轮转
- 无人机按时间片轮流工作
- 在自己的时间片内完全控制
- 优点：简化协调逻辑
- 缺点：并行度低

---

## 总结

**推荐：混合架构（地图状态存储 + 区域分工）**

### 优势
- 充分利用多无人机并行能力
- 最小化共享状态，减少协调开销
- 保留关键全局协调能力（南瓜、迷宫）

### 实施优先级
1. **高优先级**：状态存储系统、角色分配
2. **中优先级**：南瓜收获协调、迷宫协调
3. **低优先级**：性能优化、监控工具

### 预期收益
- 多无人机效率提升：2-3倍（取决于无人机数量）
- 代码复杂度：中等（新增约500行代码）
- 维护成本：可控（状态管理更清晰）
