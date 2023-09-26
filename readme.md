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
