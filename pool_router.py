class Pool_router(graph_tools):


	def __init__(self,blockchain,white_list,max_lenght):
		"""
			
			Dans l'exemple : on va prendre : 

white_list = [atom,osmo,axlusdc,axlusdt,axlwbtc,axlweth]


			white_list : list d'asset natif que l'on souhaites intégrer
			max_lenght : la longeur max des paths


			Ici on va faire un requete a la base de donnée pour nous récupérer les 
			pool intéressant i.e celle qui concernent les asset dans white_list. 

			Ensuite on crée un objet graph_tools et on initialise la matrice 
			qui contrôle les chemins de longeur =< max_lenght.  Ceux-ci 
			seront récupéré par la fonction routing. 

			Todo : il faudrait travailler la forme des données dans les chemins, 
				   pour avoir directement le message osmosis. 

			Todo : swap_matrix d'un chemin. 


			Todo : netoyage encore de la base de donnée pour les pools 
				   au moins y'a de pool parasite au plus cette efficase. 

			Todo : tester sur un autre dex que osmosis.  

		"""

		self.blockchain = blockchain

		sommets = []
		
		arretes = []

		### recupération des pools dans la base de donnée

		with Database(DATABASE) as database:

			pools = database.get_pools_from(self.blockchain,white_list)

		for pool in pools:

			# ici on récupére des ibc  
			
			id, Type, asset_1, asset_2 = pool

			### recupération des assets 
			
			### a voir comment gérer les datas

			asset_1 = self.blockchain.cold_denom_trace(asset_1).nickname

			asset_2 = self.blockchain.cold_denom_trace(asset_2).nickname


			### creation du graphe 

			### sommets

			for asset in [asset_1,asset_2]:
				if asset not in sommets:
					sommets.append(asset)

			### arretes

			arretes.append([asset_1,asset_2,id])
			arretes.append([asset_2,asset_1,id])
		

		data = {'sommets' : sommets , 'arretes' : arretes}

		### initialisation de la classe graph_tools

		graph_tools.__init__(self,data)
		
		
		self.max_lenght = max_lenght
		

		### ici ca demande du calcul 
		
		self.routing_matrix   = self.matrix**max_lenght


	def routing(self,asset_in,asset_out):

		_asset_in  = self.index[asset_in.nickname]
		_asset_out = self.index[asset_out.nickname]
		
		# y'a un petit travail ici 

		return self.parse_polynomial(self.routing_matrix[_asset_in,_asset_out])