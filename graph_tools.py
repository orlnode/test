class graph_tools:


    def __init__(self,data):
        """bordel_from_master 
            ici data = {'sommets' :      sommets,
                        'arretes' :      arretes 
                        }
        sommet = [nom] un tableau de string
        arrete = [nom_1,nom_2, id] 
        j'utilise le caractere "__" pour separer des infos donc
            faut pas que des les noms y'a ce caractère  

        """

        self.sommets = data['sommets']
        self.arretes = data['arretes']

        self.index = {}
        
        for sommet in range(len(self.sommets)):
            self.index[self.sommets[sommet]] = sommet


        # variable pour un anneau de polynôme 

        variables_name = []
        
        for arrete in self.arretes:
            
            nom_1, nom_2,  id = arrete

            name = f"{nom_1}__{id}__{nom_2}"
            
            variables_name.append(name)
        
        # ajout d'une variable one qui va représenter un enchange vide 
        # ca va permettre de recupérer les chemins de longeur =< n

        variables_name.append("one")

        self.variables_name = variables_name
        
        #  Anneau de polynôme non commutatif avec ces variables je mets QQ mais c'est sur ZZ
        #  pas besoin d'inverser quoi que ce soit mais sage préfère avoir un corps a la base,
        # il doit avoir peur que la formule de la multiplication des matrice change sur un anneau :D 

        
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
        for nom_1__id__nom_2 in self.variables_name:
            if nom_1__id__nom_2 == "one":
                continue
            nom_1,id,nom_2 = nom_1__id__nom_2.split('__')
            try:
                # faudrait analyser les erreurs potentielles ?  
                i = self.index[nom_1]
                j = self.index[nom_2]

                M[i,j] = M[i,j] + self.X[nom_1__id__nom_2]
            except:
                continue
        self.matrix = M + self.X['one']


    def parse_polynomial(self,P):
        
        # je récupère les monômes du polynome, ca revient a split + 
        # le signe + désignant deux chemins différents 
        # ex :  P = A__1__B*B__3__A  +  A__7__B * B__3__A 
        
        monomials = P.monomials()
        
        routes = []
        
        for monomial in monomials:
            
            route = self.parse_monomial(monomial)
            ids   = [arrete[2] for arrete in route]

            # là je ne veux pas qu'on passe par le même chemin ayant le même id 
            
            if not len(set(ids)) == len(ids):
                continue
            
            if route not in routes and route != []:
                routes.append(route)
        return routes


    def parse_monomial(self,monomial):

        #monomial = monomial.subs({self.X['one'] : 1})
        # exemple 
        # monomial = A__1__B*B__3__A 
        
        expression = str(monomial)
        route_to_parse = expression.split("*")

        # routes_to_parse = ['A__1__B', 'B__3__A']
        
        route = []
        
        for arrete in route_to_parse:
            if "one" not in arrete: 
                nom_1 , id , nom_2 = arrete.split("__")
                route.append([nom_1,nom_2,id])
        return route

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

On calcul la matrice M**3 et on parse les coefficients pour avoir les chemins avec les id 
des pools.  

Bon c'est peut être lourd a calculer (certainement) mais on peux pre-calculer la matrice M**4 et faire un
tableau routter qu'on stocke en dur (je pense que ça demande pas mal de calcul)
mais j'ai pas essayé. 

J'ai fais un petit parser (mais faudrait réfléchir un peu plus, si y'a des carrés (des sous-cycles) 
ca risque de foiré) : 

P = test.matrix**4
### faut faire ça avec tous les coefficients 
sage: router = test.parse_polynomial(P[0,1])
sage: router
[[['A', 'B', '1'], ['B', 'A', '3'], ['A', 'B', '4']],
 [['A', 'B', '1'], ['B', 'A', '3'], ['A', 'B', '5']],
 [['A', 'B', '4'], ['B', 'A', '3'], ['A', 'B', '1']],
 [['A', 'B', '4'], ['B', 'A', '3'], ['A', 'B', '5']],
 [['A', 'B', '5'], ['B', 'A', '3'], ['A', 'B', '1']],
 [['A', 'B', '5'], ['B', 'A', '3'], ['A', 'B', '4']],
 [['A', 'B', '1']],
 [['A', 'B', '4']],
 [['A', 'B', '5']]]

# je fais joujou 
data = {}
sommets = ["Paris","Chigago","Amsterdam","Lille","Lescale","Gap","Aix"]
arretes = [["Paris","Chigago","avion"],["Paris","Lille","train"],["Paris","Gap","Velo"],
            ["Gap","Lescale","Pied"],["Gap","Amsterdam",'Trotinette'],
            ["Chigago","Aix","Avion"],['Lille','Lescale','Bateau'] ]
for s in sommets:
    for g in sommets:
        arretes.append([s,g,'Velo'])
        arretes.append([g,s,'Trotinette'])
data['sommets'] = sommets
data['arretes'] = arretes
Voyage = graph_tools(data)
M = Voyage.matrix
### un peu long tout de même chez moi 1 minute
P = M**4
router = Voyage.parse_polynomial(P[5,6])
router[33]


"""