"""
table database comdex_pool 
"""

request = request = "query liquidity pools  -o json"
crescent_pools = CRESCENT.request(request)['pools']
datas = []

for pool in crescent_pools:
	if not pool['disabled']:
		balance 	= pool['balances']
		asset_1 	= balance['base_coin']['denom']
		asset_2 	= balance['quote_coin']['denom']
		pool_type 	= pool['type']
		id = pool['id']
		data = [id,pool_type,asset_1,asset_2]
		datas.append(data)
with Database(DATABASE) as database:
	database.insert_crescent_pools(datas)