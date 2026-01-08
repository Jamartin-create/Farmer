# The Farmer Was Replaced — 自动化脚本文档

本目录是 `The Farmer Was Replaced` 的脚本存档（入口：`main.py`）。本文档包含游戏规则速查和代码架构说明。

## 代码架构

### 模块化设计（前缀组织）

由于游戏不支持文件夹结构，代码通过文件名前缀进行逻辑分组：

#### 核心模块（core_）
- `core_plant_controller.py`：主控制器，`plant_something()` 入口
- `core_zone_classifier.py`：区域分类器，判断坐标属于哪个区域
- `core_zone_config.py`：区域配置，支持动态调整区域边界/优先级
- `core_plant_executor.py`：底层种植动作（ensure_soil, plant_xxx）
- `core_debug.py`：调试工具，统一的 debug_print 和开关控制

#### 状态管理（state_）
- `state_manager.py`：所有全局状态变量集中管理
- `state_resource_monitor.py`：资源监控，为动态配置提供决策依据

#### 区域模块（zones_）
- `zones_pumpkin_zone.py`：南瓜区，合并策略 + 成熟度检测
- `zones_support_zone.py`：供给区，胡萝卜环带
- `zones_cactus_zone.py`：仙人掌区，排序连锁收获
- `zones_mixed_zone.py`：混合区，树 + 向日葵 + 草（棋盘格）
- `zones_maze_zone.py`：迷宫区，生成 + DFS 导航

#### 特性模块（features_）
- `features_companion.py`：伴生植物系统，跨区域需求管理
- `features_fertilizer.py`：肥料策略，施肥时机 + 感染管理

#### 原有文件
- `main.py`：程序入口
- `do_move.py`：移动控制器（普通模式 + 迷宫模式）
- `map_manage.py`：本地地图缓存
- `utils.py`：工具函数
- `consts.py`：常量配置

### 动态区域配置

支持根据资源情况动态调整区域：

```python
# 在 core_zone_config.py 中修改配置
zone_enabled['maze'] = False  # 禁用迷宫区
zone_size_factor['support_ring_width'] = 2  # 扩大供给环带
```

每 100 步自动调用 `apply_dynamic_adjustments()` 根据资源情况调整。

### 调试模式

在 `core_debug.py` 中设置 `DEBUG_MODE = True` 开启调试输出：

```python
# 所有模块使用 debug_print() 替代 quick_print()
from core_debug import debug_print
debug_print("Zone:", zone, "at", x, y)
```

## 文档目录（docs）

- `docs/pumpkin_strategy.md`：南瓜策略（动态合并区，含 \(m=n-\lfloor n/2\rfloor\)）
- `docs/farm_layout.md`：农场分区策略（南瓜 + 多作物混种）
- `docs/water_fertilizer_sunflower.md`：水 / 肥料 / 向日葵（规则与实战建议）
- `docs/companion_mixed_planting.md`：混合种植 / 伴生植物（Companion）
- `docs/cactus_strategy.md`：仙人掌策略（排序连锁）
- `docs/maze_strategy.md`：迷宫策略（生成与导航）

---

# 游戏规则速查

## 胡萝卜（Carrot）

- **种植方式**：调用 `plant(Entities.Carrot)` 种植胡萝卜。
- **必须先耕地**：在种植胡萝卜之前必须先调用 `till()`。
  - 调用 `till()` 会将地块变为 `Grounds.Soil`。
  - **再次**调用 `till()` 会将地块变回 `Grounds.Grassland`（耕地是“开关”行为）。
- **耗材消耗**：种植胡萝卜会消耗 **干草** 与 **木材**（数量以游戏内胡萝卜专属页面为准）。

## 南瓜（Pumpkin）

- **生长地面**：与胡萝卜一样，需要在 **耕过的土地**（`Grounds.Soil`）上种植。
- **种植消耗**：种植南瓜需要消耗 **胡萝卜**。

### 合并为巨型南瓜

- 当一个**方形区域**内的南瓜都**完全成熟**时，会合并成 **1 个巨型南瓜**。
- 南瓜在完全成熟后有 **20%** 概率枯死，变为 **枯萎南瓜**：
  - 枯萎南瓜 **不会参与合并**，并且会**阻止**合并行为。
  - 若想让周围南瓜继续合并，需要**重新种植新的南瓜**替代枯萎南瓜。
- **枯萎南瓜收获**：
  - 枯萎南瓜收获不会掉落任何东西。
  - `can_harvest()` 在枯萎南瓜上**始终返回 `False`**。
  - 在枯萎南瓜位置上种植新植物会**自动移除**枯萎南瓜（无需单独“收获/清理”枯萎南瓜）。

### 巨型南瓜产量

巨型南瓜产量取决于合并的大小（\(n \times n\)）：

- \(1\times1\)：产出 \(1\times1\times1=1\) 个南瓜
- \(2\times2\)：产出 \(2\times2\times2=8\) 个
- \(3\times3\)：产出 \(27\) 个
- \(4\times4\)：产出 \(64\) 个
- \(5\times5\)：产出 \(125\) 个
- \(n\times n\)，当 \(n \ge 6\)：产出 \(n\times n\times 6\) 个

因此，**最佳南瓜合并大小是 \(6\times6\)**（单位面积产量最大）。注意：如果在方形区域每个地块都种南瓜，只要出现**任意一个**枯萎南瓜，就会阻止该区域的合并。

## 向日葵（Sunflower）

- **种植方式**：与胡萝卜/南瓜相同（同样需要耕地后种植；收获产出是“能量”而不是果实）。
- **收获产出**：收获一株成熟的向日葵会产出能量。
- **8 倍能量加成**：
  - 如果农场上至少有 **10** 株向日葵，并且你收获的是 **花瓣数量最多** 的那一株，就能获得 **8 倍** 能量。
  - 如果你收获一株向日葵时，农场上还有另一株花瓣更多的向日葵，那么你**接下来**收获的向日葵也只能获得普通数量的能量（没有 8 倍加成）。
- **测量花瓣**：
  - `measure()` 返回无人机下方那株向日葵的花瓣数量。
  - 花瓣数最少 **7**、最多 **15**。
  - 向日葵完全成熟之前就可以测量花瓣数量。
  - 可能存在多株向日葵花瓣数并列“最多”，收获任意一株都等价。

### 能量与加速

- 只要有能量，无人机会以 **两倍速度** 运行。
- 无人机每 **30 次行动**（移动、收获、种植……）消耗 **1 点能量**。
- 执行其他代码语句也会消耗能量，但比无人机行动少得多。
- 总体：在不考虑速度倍率的情况下，任何“用能量加速”的东西消耗的能量都与执行时间成正比。

## 树（Tree）

- **效率**：树比灌木获取木材效率更高；每棵树能提供 **5 份木材**。
- **可种植地面**：与灌木一样，可种在 **草地** 或 **耕过的土地** 上。
- **相邻减速**：树喜欢保持空间，相邻树会降低生长速度：
  - 每在其正北/正东/正西/正南的地块上种植一棵树，都会使其生长时间**翻倍**。
  - 如果每个地块都种树，生长时间将是原来的 \(2\times2\times2\times2 = 16\) 倍。

## 代码实现要点

### 区域划分逻辑

- **南瓜区**（左上角 m×m）：等待全区成熟后收割巨型南瓜，快速补种枯萎南瓜
- **供给环带**（贴着南瓜区外沿）：种植胡萝卜供给南瓜消耗，宽度可动态调整
- **仙人掌区**（南瓜区右侧）：利用排序连锁机制收获
- **迷宫区**（右下角）：生成迷宫并使用 DFS 导航至宝藏
- **混合区**（其他区域）：棋盘格分配树/向日葵/草

区域优先级：南瓜 > 迷宫 > 供给 > 仙人掌 > 混合

### 关键机制

- **耕地开关**：`till()` 会在 Grassland ↔ Soil 之间切换，必须先检查 `get_ground_type()`
- **枯萎南瓜处理**：直接 `plant()` 覆盖，不要尝试 `harvest()`
- **向日葵 8 倍能量**：维护花瓣缓存，只收最大花瓣数（需 ≥10 株）
- **伴生植物**：跨区域收集需求，按优先级分配（避免占用南瓜区）
- **肥料感染**：只对 Carrot/Cactus 施肥，获取 Weird_Substance 用于迷宫

### 添加新区域

1. 在 `zones_xxx.py` 创建新模块，实现 `handle_cell(x, y, m, n)` 函数
2. 在 `core_zone_classifier.py` 添加区域判断逻辑
3. 在 `core_zone_config.py` 添加启用开关和优先级
4. 在 `core_plant_controller.py` 添加分发逻辑

### 调试技巧

- 开启调试模式查看每格的区域分类和操作
- 使用 `state_resource_monitor.py` 查看资源统计
- 通过 `core_zone_config.py` 临时禁用某些区域进行测试
