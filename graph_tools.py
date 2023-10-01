class graph_tools:

	def parse_monomial(monomial):
		# exemple 
		# monomial = A__1__B*B__3__A 
		expression = str(monomial)
		route_to_parse = expression.split("*")
		# routes_to_parse = ['A__1__B', 'B__3__A']
		route = []
		for arrete in route_to_parse:
			nom_1 , id , nom_2 = arrete.split("__")
			route.append([nom_1,nom_2,id])
		return route

	@classmethod
	def parse_polynomial(cls,P):
		monomials = P.monomials()
		routes = []
		for monomial in monomials:
			routes.append(cls.parse_monomial(monomial))
		return routes


	def __init__(self,data):
		"""
			ici data = {'sommets' :      sommets,
						'arretes' :      arretes 
						}
		sommet = [nom] un tableau de string
		arrete = [nom_1,nom_2, id] 
		j'utilise le caractere "__" pour separer des infos donc
			faut pas que des les noms y'a ce caractère  
 		"""
		self.data 	= data
		self.sommets = self.data['sommets']
		self.arretes = self.data['arretes']

""" 
	ici je vais fabriquer un matrice d'adjacence générique. Générique c'est pour dire
	que c'est une matrice à coeffcients dans un anneau de polynome non commutatif, 
	adjacence pour dire que ç'est une construction assez similaire à la matrice
	d'adjacence d'un graphe sauf que je peux stoker plus d'information que le nombre 
	d'arrête reliant deux chemins. 
		
	Donc d'abord construire le nom des variables. 
	
	pour chaque arrete [nom_1,nom_2,id] une variable dont le nom est :
			
		nom_1__id__nom_2   ça pemet de retrouver l'arrête en faisant split("__") 
		
"""

		variables_name = []
		
		for arrete in self.arretes:
			nom_1,nom_2,id = arrete
			name = f"{nom_1}__{id}__{nom_2}"
			variables_name.append(name)
		
		self.variables_name = variables_name
        
        #Anneau de polynôme non commutatif avec ces variables """
		
		self.polynomial =  FreeAlgebra(QQ,self.variables_name)

		"""
			La matrice d'adjacence va fonctionner de la manière suivante : 
			
			matrice M de taille len(self.sommets) 
			
			M[i,j] = la somme de toutes les variables variables_name tel que 
						nom_1 = self.sommets[i] 
						nom_2 = self.sommets[j]	

			en gros, dans la matrice d'adjacence classique, on met 1 si y'a un chemin 
			et 0 sinon. Ici c'est le même principe sauf que je stoke de l'information
			en mettant une variable qui identifie les id des chemins. 

		"""
		
		# dictionnaire donant les variables par leurs noms
		self.X =  self.polynomial.gens_dict()

		# je remplie la matrice 
		M = matrix(self.polynomial,len(self.sommets),len(self.sommets))
		for i in range(len(self.sommets)):
			for j in range(len(self.sommets)):
				m_i_j = 0
				for nom_1__id__nom_2 in self.variables_name:
					nom_1,id,nom_2 = nom_1__id__nom_2.split('__')
					if nom_1 == self.sommets[i] and nom_2 == self.sommets[j]:
						m_i_j = m_i_j + self.X[nom_1__id__nom_2]
				M[i,j] = m_i_j
		self.matrix = M


"""
	principe la puissance n de self.matrix donne les chemins de longeur n 
	dans le graphe ! 
			
Exemple 1 : 

data = {}
data['sommets'] = ["A","B","C"]
data['arretes'] = [["A","B",1],["A","C",2],["B","A",3]]
test = graph_tools(data)
test.matrix
[      0 A__1__B A__2__C]
[B__3__A       0       0]
[      0       0       0]

par exemple : les chemmins de longeur exactement 2 sont A B A  et B A B et B A C 
test.matrix**2
[A__1__B*B__3__A               0               0]
[              0 B__3__A*A__1__B B__3__A*A__2__C]
[              0               0               0]

on retrouve 3 coefficients non nul qui indique 3 chemins de longeur 2, 

le premier qui va de A vers A (car il est en position A, A de la matrice)
	A__1__B*B__3__A  : qui doit se lire comme je fais A ---> B avec id 1 puis B ---> A avec l'id 3
	B__3__A*A__2__C  : qui doit se lire comme je fais B ---> A avec l'id 3 puis A ---> C avec l'id 2

Le côté non commutatif permet de conserver l'ordre des executions des arrêtes. 

Exemple 2 : 

Avec un graphe plus complexe pour voir le rôle des + 

data = {}
data['sommets'] = ["A","B","C"]
data['arretes'] = [["A","B",1],["A","C",2],["B","A",3],["A","B",4],["A","B",5]]
test = graph_tools(data)
test.matrix**2
j'affiche c'est degeux 
[A__1__B*B__3__A + A__4__B*B__3__A + A__5__B*B__3__A                                                   0                                                   0]
[                                                  0 B__3__A*A__1__B + B__3__A*A__4__B + B__3__A*A__5__B                                     B__3__A*A__2__C]
[                                                  0                                                   0                                                   0]
Remarque : 
on retrouver la matrice d'adjacence classique : 
M = test.matrix
sage: one = {Variable : 1 for Variable in test.X.values()}
sage: M.subs(one)
[0 3 1]
[1 0 0]
[0 0 0]


donc je vais afficher simplement de coefficient A A
M = self.matrix
M**2[0,0]
A__1__B*B__3__A + A__4__B*B__3__A + A__5__B*B__3__A

Donc là on voit 3 chemins allant de A ---> A de longeur 2 avec la même desciprtion
par exemple : A__5__B*B__3__A     A  --- B  ---> A avec les pool_id 5 et 3 

Donc  idée pour le router des pools osmosis c'est de faire ça sur le graphe des pools
osmosis. 

En gros, ca va donnée un anneau de polynôme avec 1230 variables (les pools) et une matrice 
de 230 lignes et colonnes (les assets). 

On calcul les matrices M**2, M**3 et on parse les coefficients pour avoir les chemins avec les id 
des pools.  

Bon c'est peut être lourd a calculer (certainement) mais on peux pre-calculer la matrice M**4 et faire un
tableau routter qu'on stocke en dur (je pense que ça demande pas mal de calcul)
mais j'ai pas essayé. 

J'ai fais un petit parser (mais faudrait réfléchir un peu plus, si y'a des carrés (des sous-cycles) 
ca risque de foiré) : 

M = test.matrix**3
### faut faire ça avec tous les coefficients 
router = test.parse_polynomial(M[0,1])
router
[[['A', 'B', '1'], ['B', 'A', '3'], ['A', 'B', '1']],
 [['A', 'B', '1'], ['B', 'A', '3'], ['A', 'B', '4']],
 [['A', 'B', '1'], ['B', 'A', '3'], ['A', 'B', '5']],
 [['A', 'B', '4'], ['B', 'A', '3'], ['A', 'B', '1']],
 [['A', 'B', '4'], ['B', 'A', '3'], ['A', 'B', '4']],
 [['A', 'B', '4'], ['B', 'A', '3'], ['A', 'B', '5']],
 [['A', 'B', '5'], ['B', 'A', '3'], ['A', 'B', '1']],
 [['A', 'B', '5'], ['B', 'A', '3'], ['A', 'B', '4']],
 [['A', 'B', '5'], ['B', 'A', '3'], ['A', 'B', '5']]]

 donc ça renvoie 9 chemins de longeur 3 entre A et B avec la liste des arrêtes pour
 modéliser les chemins. 
### petit test :  1 minute chez moi 
sage: M = test.matrix**17
sage: router = test.parse_polynomial(M[0,1])
sage: len(router) # presque 20000 chemins de longeur 17 dans mon petit graphe 
19683
"""