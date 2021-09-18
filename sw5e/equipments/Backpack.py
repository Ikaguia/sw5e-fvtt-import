import sw5e.Equipment, utils.text
import re, json

class Backpack(sw5e.Equipment.Equipment):
	def __init__(self, raw_item, old_item, uid, importer):
		super().__init__(raw_item, old_item, uid, importer)

		self.type = 'backpack'

		self.uses, self.recharge = utils.text.getUses(self.description, self.name)
		self.action = utils.text.getActivation(self.description, self.uses, self.recharge)

	def getImg(self):
		kwargs = {
			# 'item_type': self.equipmentCategory,
			# 'no_img': ('Unknown',),
			'default_img': 'systems/sw5e/packs/Icons/Storage/Crate.webp',
			# 'plural': False
		}
		return super().getImg(**kwargs)

	def getDescription(self, importer):
		text = self.description
		return utils.text.markdownToHtml(text)
