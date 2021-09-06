import sw5e.Equipment, utils.text
import re, json

class Equipment(sw5e.Equipment.Equipment):
	def __init__(self, raw_item, old_item, importer):
		super().__init__(raw_item, old_item, importer)

		self.type = 'equipment'

		self.uses, self.recharge = utils.text.getUses(self.description, self.name)
		self.action = utils.text.getAction(self.description, self.uses, self.recharge)

	def getImg(self):
		kwargs = {
			'item_type': self.equipmentCategory,
			'no_img': ('Unknown', 'Clothing'),
			'default_img': 'systems/sw5e/packs/Icons/Storage/Crate.webp',
			# 'plural': False
		}
		if self.equipmentCategory == 'Armor': kwargs["item_type"] += '/' + self.contentSource
		return super().getImg(**kwargs)

	def getDescription(self):
		text = self.description
		return utils.text.markdownToHtml(text)

	def matches(self, *args, **kwargs):
		if not super().matches(*args, **kwargs): return False

		# if len(args) >= 1:
		# 	new_item = args[0]
		# 	if new_item["type"] != 'equipment': return False

		return True
