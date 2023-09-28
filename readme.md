``` 
git clone https://github.com/orlnode/test/
cd test
```
ensuite entrer dans le terminal python (ou sage)
```attach('init.py')```
déclarer une variable password = TON_PASSWORD (celui pour accéder au keyring) 

```
Blockchain.init()
Asset.init()
```

Donc là y'a plein de nouvelles variables, par exemple une variable atom, osmo ou encore ion (donc les assets en minuscule et les blockchain en majuscule). Ces variables sont des objets de la classe Asset qui contiennent les informations des assets en question + quelques fonctions ! 

Par exemple :

```
atom.balance()
```

doit te renvoyer le nombre d'uatom que tu as sur la blockchain COSMOSHUB. 
Y'a une fonction transfer qui permet d'obtenir l'asset chez une autre blockchain par exemple. Ce n'est pas une transaction ! 

```
atom(OSMOSIS) # pareil que atom.transfer(OSMOSIS)
```

c'est atom sur la blockchain osmosis et tu peux demander ta balance

```
atom(OSMOSIS).balance()
```

Du coup, ça doit te renvoyer le nombre d'atom que tu as sur osmosis.

----------------------------------------------------------
Quelques petites modification + j'ai ajouté un fichier testswap.py où y'a une fonction qui teste les matrices de swap sur un exemple. 

```
attach('testswap.py') 
```
Peut être que from testswap import * fonctionne ? je pige pas trop le systéme de module en python

la fonction swap_test va faire une transaction via ton compte : ca échange 100uatom de ton compte osmosis contre du umee

```
swap_test()
```

qui doit faire une tx et afficher quelques datas. Mais faut regarder un peu le code : j'ai mis un truc "----> truc préliminaire " ligne 45 de testswap.py car tu n'a pas d'osmo pour payer les frais de transaction sur osmosis donc faut faire 2 commandes en terminal qui sont indiquées, ca envoie un peu d'atom vers osmosis et ensuite ca achete un peu osmo avec de l'atom en payant les frais en atom.  (faut attendre quelques seconde entre les deux transactions, le temps que le transfer ibc se fasse normalement 20 secondes maxi). 

