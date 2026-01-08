# 肥料特性模块
# 跨区域功能：施肥策略和感染管理
from consts import FERTILIZER_MIN_STOCK, CARROT_LOW_WATERMARK, FERTILIZER_USE_THRESHOLD
from core_debug import debug_print


def maybe_use_fertilizer(target_entity):
	# 肥料策略
	if target_entity not in [Entities.Carrot, Entities.Cactus]:
		return

	if get_entity_type() != target_entity:
		return

	if can_harvest():
		return

	fertilizer = num_items(Items.Fertilizer)
	if fertilizer < FERTILIZER_MIN_STOCK:
		return

	# 胡萝卜：库存低或肥料多时施肥
	if target_entity == Entities.Carrot:
		if num_items(Items.Carrot) < CARROT_LOW_WATERMARK or fertilizer >= FERTILIZER_USE_THRESHOLD:
			use_item(Items.Fertilizer)
			debug_print("Fertilizer: Used on Carrot (stock:", fertilizer, ")")
		return

	# 仙人掌：肥料多时施肥
	if target_entity == Entities.Cactus:
		if fertilizer >= FERTILIZER_USE_THRESHOLD:
			use_item(Items.Fertilizer)
			debug_print("Fertilizer: Used on Cactus (stock:", fertilizer, ")")
