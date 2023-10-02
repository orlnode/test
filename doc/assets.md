J'explique un peu plus les histoires d'assets. 

Donc concrétement on va jouer sur deux trucs, des assets et des blockchains. Remarque : asset = crypto = token ! 

Chaque blockchains a un ou plusieurs asset natif, par exemple pour la blockchain COSMOSHUB l'asset natif c'est atom ou uatom (convention les blockchains en majuscule et les assets en minuscule). 

Dans la fonction __init__ de la  classe Asset, j'ai plusieurs variables :  

- name : c'est le nom donc uatom par exemple.
- native_chain : c'est la chaine native de l'asset
- host_chain   : c'est la chaîne où est l'asset. (par exemple, je peux bouger des atoms sur OSMOSIS et dans ce cas, le name sera toujours uatom, native_chain sera COSMOSHUB et host_chain sera OSMOSIS : tu as accès à tes atoms qui sont sur OSMOSIS par la commande sage : atom(OSMOSIS).

Le truc, c'est que pour OSMOSIS, atom(OSMOSIS) a un nom de code qui est construit a partir d'un processus un peu complexe  : le non de code (l'ibc_denom) est 
' ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2 ' 

C'est de la forme ibc/ + HASH. Le HASH est construit à partir du name uatom et du channel de communication de OSMOSIS ---> COSMOSHUB 

Ce channel tu peux le récupérer via 
```channel = Blockchain.channels[OSMOSIS.name][COSMOSHUB.name]```

ici channel-0 (ça provient de la base de donnée) et donc  
```HASH = sha256("transfer/"+channel+"/"+uatom) #(qu'il faut mettre en majuscule).```  

Dans la classe Blockchain, y'a une petite fonction qui permet à partir d'un ibc_denom d'un asset de OSMOSIS de récupérer l'objet asset en question : 
OSMOSIS.cold_denom_trace(ibc_denom) donc en clair si tu fais 
```
OSMOSIS.cold_denom_trace('ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2') 
```
tu te retrouve avec atom(OSMOSIS)

(pourquoi cold ? c'est pour dire qu'il n'y a pas de requete rpc ici, y'a également une fonction denom_trace qui elle fait un appel rpc à la blockchaine et qui donne des informations). 

Dans le fichier asset.py : y'a des commentaires qui explique une problèmatique avec les ibc_denom, on ne peut pas s'en servir d'identifiant unique, c'est la construction de HASH qui me semble un peu étrange (mais y'a certainement une raison), du coup j'ai un peu bidoulé le truc pour fabriquer un identifiant unique pas trop éloigner de l'ibc_denom (j'ai juste remplacer ibc/ par osmosis/ (le name de host_chain)). Du coup, j'ai un dictionnaire : 

Asset.instances_by_id : identifiant ---> asset 

dont la réciproque est la fonction : 

asset --- >(asset.denom()).replace('ibc',asset.host_chain.name)  

D'un coup, pour nous on peut utiliser atom(OSMOSIS) dans une fonction et avoir facilement le nom de code pour la chaine OSMOSIS en faisant atom(OSMOSIS).denom(). Et lorsque OSMOSIS te revoit un 

ibc_denom tu peux récupéré l'asset en faisant OSMOSIS.cold_denom_trace(ibc_denom)