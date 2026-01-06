DIRECTION = [
	[0, 1],  # up
	[0, -1], # down
	[-1, 0], # left
	[1, 0]   # right
]

# 低于该阈值时自动喝水（提高脚本可读性：避免散落的“魔法数字”）
WATER_THRESHOLD = 0.5

# 肥料策略（阈值集中放在这里，便于调参）
# - 当前策略：主动消耗肥料来获得 `Items.Weird_Substance`（感染后收获会把一半产量转化为奇异物质）
FERTILIZER_MIN_STOCK = 10
CARROT_LOW_WATERMARK = 500

# 肥料主动使用阈值：库存高于该值时，会更积极地对“可接受感染”的作物施肥
FERTILIZER_USE_THRESHOLD = 25

# 向日葵策略
SUNFLOWER_MIN_COUNT_FOR_8X = 10