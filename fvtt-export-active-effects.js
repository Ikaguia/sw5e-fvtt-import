let types = [
	"adventuringgear",
	"archetypes",
	"armor",
	"backgrounds",
	"classes",
	"classfeatures",
	"enhanceditems",
	"feats",
	"fightingstyles",
	"fightingmasteries",
	"forcepowers",
	"gamingset",
	"lightsaberform",
	"species",
	"speciestraits",
	"techpowers",
	"weapons"
]
// types = [
// 	"species"
// ]

let verbose = false;

function clean(str){
	str = str || '';
	str = str.toLowerCase();
	str = str.replaceAll(/[^\w\s-]/g, '');
	str = str.replaceAll(/[\s-]+/g, '_');
	str = str.replaceAll(/^[-_]+/g, '');
	str = str.replaceAll(/[-_]+$/g, '');
	return str;
}

function getUID(item){
	uid = clean(item.type)
	uid += `.name-${clean(item.name)}`

	category = item.data.weaponType || item.data.consumableType || item.data.armor?.type;
	if (category) uid += `.equipmentCategory-${clean(category)}`;

	if (item.data.requirements) uid += `.sourceName-${clean(item.data.requirements)}`

	return uid
}

for (let type of types){
	let foundry_effects = {};

	console.log(`Extracting AEs from ${type} compendium`)

	let pack = await game.packs.get(`sw5e.${type}`);
	if (!pack){
		console.log(`Compendium pack sw5e.${type} not found`);
		continue;
	}

	let was_locked = pack.locked;
	await pack.configure({locked: false})

	let pack_docs = await pack.getDocuments();
	for(let pack_doc of pack_docs){
		let pack_item = pack_doc.data;

		uid = getUID(pack_item);
		if (pack_item.effects && pack_item.effects.size) foundry_effects[uid] = pack_item.effects;
	}

	await pack.configure({locked: was_locked})

	if (Object.keys(foundry_effects).length) {
		console.log('Foundry Effects:')
		console.log(foundry_effects);
	}
}
