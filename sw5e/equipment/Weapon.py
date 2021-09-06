import sw5e.Equipment, utils.text
import re, json, copy

class Weapon(sw5e.Equipment.Equipment):
	def __init__(self, raw_item, old_item, importer):
		super().__init__(raw_item, old_item, importer)

		self.type = 'weapon'

		self.uses, self.recharge = 0, ''
		self.action = 'action'

		self.weapon_type = self.getWeaponType()
		self.ammo_type = self.getAmmoType()

	def getImg(self):
		kwargs = {
			'item_type': self.weaponClassification,
			# 'no_img': ('Unknown',),
			'default_img': 'systems/sw5e/packs/Icons/Simple%20Blasters/Holdout%20Blaster.webp',
			'plural': True
		}
		return super().getImg(**kwargs)

	def getDescription(self):
		properties = map(lambda prop: prop.capitalize(), self.properties)
		properties = list(filter(lambda prop: not prop.startswith('Ammunition'), properties))
		text = ', '.join(properties)
		if 'Special' in self.properties: text += '\n' + self.description
		return utils.text.markdownToHtml(text)

	def getRange(self):
		short_range, long_range = None, None
		if rang := (self.getProperty('Ammunition') or self.getProperty('Range')):
			if rang == 'special': short_range = 'special'
			elif type(rang) == list: short_range, long_range = rang
			else: short_range = rang
		elif self.getProperty('Reach'):
			short_range = 10
		return {
			'value': short_range,
			'long': long_range,
			'units': 'ft'
		}

	def getUses(self):
		if self.ammo_type and self.ammo_type != 'Power Cell':
			rload = self.getProperty('Reload')
			return {
				"value": rload,
				"max": rload,
				"per": 'charges'
			}
		return {}

	def getConsume(self):
		if self.ammo_type == 'Power Cell': return {
			"type": 'charges',
			"target": '',
			"amount": 480 // self.getProperty('Reload')
		}
		elif self.ammo_type: return {
			"type": 'ammo',
			"target": '',
			"amount": 1
		}
		return {}

	def getActionType(self):
		if self.weapon_type in ('simpleB', 'martialB'):
			return 'rwak'
		else:
			return 'mwak'

	def getDamage(self):
		if (not self.damageNumberOfDice) or (not self.damageDieType):
			return {}

		die = f'{self.damageNumberOfDice}d{self.damageDieType} + @mod'
		damage_type = self.damageType.lower() if self.damageType != 'Unknown' else ''
		versatile = self.getProperty('Versatile') or ''
		return {
			"parts": [[ die, damage_type ]],
			"versatile": versatile
		}

	def getWeaponType(self):
		w_class = self.weaponClassification

		simple = w_class.startswith('Simple')
		martial = not simple and w_class.startswith('Martial')

		blaster = w_class.endswith('Blaster') or self.getProperty('Ammunition') or self.getProperty('Reload')
		vibro = (not blaster) and w_class.endswith('Vibroweapon')
		light = (not blaster) and (not vibro) and w_class.endswith('Lightweapon')

		if simple and blaster: return 'simpleB'
		if simple and vibro: return 'simpleVW'
		if simple and light: return 'simpleLW'
		if martial and blaster: return 'martialB'
		if martial and vibro: return 'martialVW'
		if martial and light: return 'martialLW'
		return 'natural'

		return weapon_types[self.weaponClassificationEnum]

	def getAmmoType(self):
		if not self.getProperty('Reload'): return None
		if self.damageType in ('Energy', 'Ion', 'Acid', 'Fire', 'Sonic', 'Lightning'): return 'Power Cell'
		else: return 'Cartridge' #TODO: detect other types of ammo (flechete, missile...)

	def getProperties(self):
		weapon_properties = {
			"amm": "Ammunition",
			"aut": "Auto",
			"bur": "Burst",
			"con": "Constitution",
			"def": "Defensive",
			"dex": "Dexterity",
			"dgd": "Disguised",
			"dir": "Dire",
			"dis": "Disintegrate",
			"dou": "Double",
			"dpt": "Disruptive",
			"drm": "Disarming",
			"exp": "Explosive",
			"fin": "Finesse",
			"fix": "Fixed",
			"foc": "Focus",
			"hid": "Hidden",
			"hom": "Homing",
			"hvy": "Heavy",
			"ion": "Ionizing",
			"ken": "Keen",
			"lgt": "Light",
			"lum": "Luminous",
			"mig": "Mighty",
			"mlt": "Melt",
			"ovr": "Overheat",
			"pic": "Piercing",
			"pow": "Power",
			"ran": "Range",
			"rap": "Rapid",
			"rch": "Reach",
			"rel": "Reload",
			"ret": "Returning",
			"sat": "Saturate",
			"shk": "Shocking",
			"sil": "Silent",
			"spc": "Special",
			"str": "Strength",
			"thr": "Thrown",
			"two": "Two-Handed",
			"ver": "Versatile",
			"vic": "Vicious",
			"zon": "Zone",
		}
		return { prop: weapon_properties[prop] in self.propertiesMap for prop in weapon_properties }

	def getProperty(self, prop_name):
		if prop_name not in self.propertiesMap: return None

		def opt(p): return f'(?:{p})?'
		def capt(p, name): return f'(?P<{name}>{p})'

		prop = self.propertiesMap[prop_name]

		if re.search('special', prop): return 'special'

		it = re.finditer(r'(\d+(?:,\d+)?)|(\d+d\d+)', prop)
		vals = [int(re.sub(',', '', val.group(1))) or val.group(2) for val in it]
		if len(vals) == 0: return True
		if len(vals) == 1: return vals[0]
		return vals

	def getAutoTargetData(self, data):
		if type(auto := self.getProperty('Auto')) == list:
			mod = (auto[0] - 10) // 2
			prof = auto[1]
			data["data"]["ability"] = 'str'
			data["data"]["attackBonus"] = f'{mod} - @abilities.str.mod + {prof} - @attributes.prof'
			data["data"]["damage"]["parts"][0][0] = f'{self.damageNumberOfDice}d{self.damageDieType} + {mod}'
			data["data"]["proficient"] = True
		return data

	def getItemVariations(self, original_data, importer):
		data = []

		if self.modes:
			# data.append(original_data)
			for mode in self.modes:
				wpn = copy.deepcopy(self)
				wpn.modes = []

				no = ([], {}, (), 0, '0', None, 'None', 'none', 'Unknown', 'unknown')

				if (var := utils.text.clean(mode, "Description")) not in no: wpn.description = var
				if (var := utils.text.raw(mode, "Cost")) not in no: wpn.cost = var
				if (var := utils.text.clean(mode, "Weight")) not in no: wpn.weight = var
				if (var := utils.text.raw(mode, "EquipmentCategoryEnum")) not in no: wpn.equipmentCategoryEnum = var
				if (var := utils.text.clean(mode, "EquipmentCategory")) not in no: wpn.equipmentCategory = var
				if (var := utils.text.raw(mode, "DamageNumberOfDice")) not in no: wpn.damageNumberOfDice = var
				if (var := utils.text.raw(mode, "DamageTypeEnum")) not in no: wpn.damageTypeEnum = var
				if (var := utils.text.clean(mode, "DamageType")) not in no: wpn.damageType = var
				if (var := utils.text.raw(mode, "DamageDieModifier")) not in no: wpn.damageDieModifier = var
				if (var := utils.text.raw(mode, "WeaponClassificationEnum")) not in no: wpn.weaponClassificationEnum = var
				if (var := utils.text.clean(mode, "WeaponClassification")) not in no: wpn.weaponClassification = var
				if (var := utils.text.raw(mode, "ArmorClassificationEnum")) not in no: wpn.armorClassificationEnum = var
				if (var := utils.text.clean(mode, "ArmorClassification")) not in no: wpn.armorClassification = var
				if (var := utils.text.raw(mode, "DamageDiceDieTypeEnum")) not in no: wpn.damageDiceDieTypeEnum = var
				if (var := utils.text.raw(mode, "DamageDieType")) not in no: wpn.damageDieType = var
				if (var := utils.text.cleanJson(mode, "Properties")) not in no: wpn.properties += var
				if (var := utils.text.cleanJson(mode, "PropertiesMap")) not in no: wpn.propertiesMap.update(var)

				wpn.weapon_type = wpn.getWeaponType()
				wpn.ammo_type = wpn.getAmmoType()

				wpn_data = wpn.getData(importer)[0]
				wpn_data["name"] = f'{self.name} ({mode["Name"]})'
				data.append(wpn_data)
		else:
			if not (self.getProperty('Auto') == True): data.append(original_data)
			if burst := self.getProperty('Burst'):
				burst_data = copy.deepcopy(original_data)
				burst_data["name"] = f'{self.name} (Burst)'

				burst_data["data"]["target"]["value"] = '10'
				burst_data["data"]["target"]["units"] = 'ft'
				burst_data["data"]["target"]["type"] = 'cube'
				if self.ammo_type:
					burst_data["data"]["consume"]["amount"] *= burst
					if self.ammo_type != 'Power Cell':
						burst_data["data"]["uses"]["value"] //= burst
						burst_data["data"]["uses"]["max"] //= burst

				burst_data["data"]["actionType"] = 'save'
				burst_data["data"]["save"] = {
					"ability": 'dex',
					"dc": None,
					"scaling": 'dex'
				}
				data.append(burst_data)
			if rapid := self.getProperty('Rapid'):
				rapid_data = copy.deepcopy(original_data)
				rapid_data["name"] = f'{self.name} (Rapid)'

				if self.ammo_type:
					rapid_data["data"]["consume"]["amount"] *= rapid
					if self.ammo_type != 'Power Cell':
						rapid_data["data"]["uses"]["value"] //= rapid
						rapid_data["data"]["uses"]["max"] //= rapid

				rapid_data["data"]["actionType"] = 'save'
				rapid_data["data"]["damage"]["parts"][0][0] = re.sub(r'^(\d+)d', lambda m: f'{int(m[1])*2}d', rapid_data["data"]["damage"]["parts"][0][0])
				rapid_data["data"]["save"] = {
					"ability": 'dex',
					"dc": None,
					"scaling": 'dex'
				}
				data.append(rapid_data)

		return data

	def getData(self, importer):
		data = super().getData(importer)[0]

		data["data"]["target"]["value"] = 1
		data["data"]["target"]["width"] = None
		data["data"]["target"]["units"] = ''
		data["data"]["target"]["type"] = 'enemy'

		data["data"]["range"] = self.getRange()
		data["data"]["uses"] = self.getUses()
		data["data"]["consume"] = self.getConsume()
		data["data"]["actionType"] = self.getActionType()
		data["data"]["damage"] = self.getDamage()
		data["data"]["weaponType"] = self.weapon_type
		data["data"]["properties"] = self.getProperties()

		data = self.getAutoTargetData(data)
		return self.getItemVariations(data, importer)

	def matches(self, *args, **kwargs):
		if not super().matches(*args, **kwargs): return False

		# if len(args) >= 1:
		# 	new_item = args[0]
		# 	if new_item["type"] != 'weapon': return False

		return True
