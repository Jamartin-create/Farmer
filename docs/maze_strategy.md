# 迷宫策略

本文用于《The Farmer Was Replaced》脚本策略记录，目标是：正确理解并实现迷宫的生成、导航和收获机制。

## 基本规则

### 生成迷宫

- **前提**：在灌木（`Entities.Bush`）上使用 `Items.Weird_Substance` 可以生成迷宫
- **调用方式**：`use_item(Items.Weird_Substance, amount)`（无人机需位于灌木上方）
- **迷宫大小**：使用 `n` 份 `Items.Weird_Substance` 将生成一个 `n×n` 的迷宫
- **升级影响**：每次解锁 `Unlocks.Mazes` 升级，所需数量翻倍，但宝藏中的金币数量也会翻倍

### 全场迷宫公式

若要生成一个覆盖整个世界的迷宫：

```python
plant(Entities.Bush)
substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
use_item(Items.Weird_Substance, substance)
```

### 迷宫结构

- **树篱（Hedge）**：迷宫中的墙壁，无人机无法飞过
- **宝藏（Treasure）**：迷宫中隐藏的唯一宝藏
- **无循环**：初始生成的迷宫不包含循环（除非重复使用，见下文）

## 导航与探索

### 检测墙壁

- `move(direction)`：尝试移动，成功返回 `True`，失败（撞墙）返回 `False`
- `can_move(direction)`：在不移动的情况下检查是否有墙

### 获取宝藏位置

- `measure()`：在迷宫中的任何位置调用，都会返回宝藏的坐标 `(x, y)`
- 可用于导航算法（如深度优先搜索、广度优先搜索等）

### 实体类型判断

- `get_entity_type() == Entities.Treasure`：无人机在宝藏上方
- `get_entity_type() == Entities.Hedge`：无人机在树篱上（墙壁位置）

## 收获宝藏

### 基本收获

- 对宝藏使用 `harvest()` 可以获得等于**迷宫面积**的金币
- 例如：5×5 的迷宫产出 25 份金币（`Items.Gold`）

### 重要警告

- **如果在迷宫的其他任何地方使用 `harvest()`，迷宫将直接消失**
- 因此必须确保只在宝藏位置收获

## 重复使用迷宫（可选挑战）

### 机制

- 在宝藏上再次使用**相同数量**的 `Items.Weird_Substance` 可以重复使用迷宫
- 效果：
  - 收集当前宝藏
  - 在迷宫中随机位置生成新宝藏
  - 随机移除一些墙壁（可能产生循环）

### 限制与权衡

- **循环增加难度**：重复使用后可能产生循环，使导航更复杂
- **金币不增加**：重复使用得到的金币不会比直接收获并生成新迷宫更多
- **最多 300 次**：宝藏最多可以被重新定位 300 次，之后不再移动且金币不再增加
- **建议**：这是一个可跳过的额外挑战，只有当额外信息和捷径能帮助更快破解迷宫时才值得重复使用

## 实现策略建议

### 1. 生成时机

- 确保有足够的 `Items.Weird_Substance` 库存
- 灌木可以种在草地或土壤上，不需要耕地
- 建议在固定位置（如地图中心或角落）生成迷宫，便于管理

### 2. 导航算法

由于初始迷宫无循环，可以使用简单的算法：

- **深度优先搜索（DFS）**：使用栈记录路径，回溯时标记已访问
- **广度优先搜索（BFS）**：使用队列，找到最短路径
- **右手法则**：沿着墙壁走，适合简单迷宫

### 3. 收获流程

```python
# 伪代码示例
def harvest_maze_treasure():
    # 1. 生成迷宫（如果还没有）
    if get_entity_type() != Entities.Hedge and get_entity_type() != Entities.Treasure:
        plant(Entities.Bush)
        substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
        if num_items(Items.Weird_Substance) >= substance:
            use_item(Items.Weird_Substance, substance)
    
    # 2. 导航到宝藏（使用 measure() 获取位置，使用 move/can_move 导航）
    treasure_x, treasure_y = measure()
    # ... 导航逻辑 ...
    
    # 3. 确认在宝藏位置后收获
    if get_entity_type() == Entities.Treasure:
        harvest()
```

### 4. 资源管理

- `Items.Weird_Substance` 通过给植物施肥后收获获得（一半产量转化为奇异物质）
- 需要平衡施肥策略，确保有足够库存生成迷宫
- 全场迷宫消耗较大，建议在资源充足时进行

### 5. 与其他策略的协调

- 迷宫占用空间，需要考虑与南瓜区、仙人掌区等布局的协调
- 建议将迷宫区域独立出来，避免与其他作物冲突
- 可以在地图边缘或特定区域专门用于迷宫

## 注意事项

1. **收获位置必须准确**：在非宝藏位置使用 `harvest()` 会导致迷宫消失
2. **导航效率**：初始迷宫无循环，但重复使用后可能变复杂
3. **资源消耗**：全场迷宫需要大量 `Items.Weird_Substance`，需要提前规划
4. **升级影响**：每次升级所需数量翻倍，但收益也翻倍
5. **无人机限制**：无法飞过树篱，必须通过路径导航

