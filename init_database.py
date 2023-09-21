import os
directory 	= "cosmos/chain-registry"
content 	= os.listdir(directory)
### on va filter pour récupérer tous les dossiers 
sub_directory = [d for d in content if os.path.isdir(os.path.join(directory, d)) and not d.startswith(('.', '_'))    ]



datas = []
for bc_name in sub_directory:
	with open(os.path.join(directory,bc_name,'chain.json'),"r+") as file:
	 	data    = json.load(file)
	 	try:
	 		command = data['daemon_name']
	 	except:
	 		command = ""
	 	chain   = data['chain_id']
	 	name    = data['chain_name']
	 	nodes   = data['apis']['rpc']
	 	### selection du noeud
	 	print(name)
	 	try:
	 		nodes[0]['provider'] = 'Polkachu'
	 	except:
	 		continue
	 	for _node in nodes:
	 		if _node['provider'] == 'Polkachu':
	 			node = " --node " + _node['address']
	 	if not('443' in node):
	 		node = node + ":443"
	 	fees = data['fees']['fee_tokens'][0]
	 	fee_token = fees['denom']
	 	if "average_gas_price" in fees.keys():
	 		### faire mieux ! 
	 		gas_price = fees['average_gas_price']
	 	else:
	 		gas_price = 0
	datas.append((name,chain,node,fee_token,command,gas_price))

with Database('blockchain.db') as database:
 	database.insert_blockchains(datas)

