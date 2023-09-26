Je t'expliques un peu plus mon projet. Ca te permettra de voir si tu peux m'aider un peu, c'est assez délicat d'expliquer car je dois en dire suffisament mais pas me noyer dans les détails. En écrivant, je me rend compte que j'ai vraiment été me percher :D


 L'idée c'est de créer un programme qui fait les liquidations sur Umee. Je pense qu'il y a de l'argent a se faire (y'a déjà quelques personnes sur le coup, j'ai repéré 7 addresses dont une liquide beaucoup : il a pas mal de fond pour liquider de grosse position, faut faire avec).


Qu'est ce qu'il faut ? 
======================

- Sur Osmosis.
- Ibc transfer général.
- sur Umee. 


1. Une bonne fonction de swap sur osmosis. Là sérieux j'ai du mal car c'est un véritable bordel, y'a plus de 1000 pools de liquidité. Le truc, c'est que si tu swap dans une pool, il faut faire attention à la liquidité de la pool le L_A et L_B dans mon fichier doc/dex.txt en gros faut sélection les pools qui ont le plus de liquidité : sinon tu peux te retrouver à échanger 1 atom pour 1$ (c'est un peu critique ici). (y'a des gars qui ont vraiment perdu beaucoup en swappant n'importe comment !!!)

Remarques : 

 a. pas besoin des 1000 pools donc une idée serai de récupérer les pools importantes en base de  donnée, en gros faire une préselection pour viré toutes les petites pools inutilisables. 


 b. y'a également un problème de chemin : par exemple pour échanger ATOM contre du USDC, il n'y a pas de pool direct ATOM / USDC  et donc faut selectionner un chemin du genre :

      ATOM ---> OSMO ---> USDC 

   Y'a un truc certain c'est que tous les assets ont une pool avec OSMO (le token de osmosis)

   Avec mes histoires de matrices, y'a moyen de faire des calculs mais avec un trop grand nombre de pool les algorithmes de chemins sont trop lent chez moi ! 

 c. y'a un problème également sur les datas. Lorsque tu récupères les pools de liquidité  tu récupére un dictionnaire python avec des clefs embriquées du coup c'est pénible pour récupérer l'information dont tu as besoin : 

```
sage: p = OSMOSIS.request("q poolmanager all-pools")['pools']
sage: pool = p[16]
 typiquement : 
pool = 
 {'@type': '/osmosis.gamm.v1beta1.Pool',
 'address': 'osmo1l45a67tujfxl99qt39a09cqf9ep0vtqyn8xnuua66yvjtc7e8lvsua2hjn',
 'id': '17',
 'pool_params': {'swap_fee': '0.003000000000000000',
  'exit_fee': '0.000000000000000000',
  'smooth_weight_change_params': None},
 'future_pool_governor': '24h',
 'total_shares': {'denom': 'gamm/pool/17', 'amount': '100000000000000000000'},
 'pool_assets': [{'token': {'denom': 'ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2',
    'amount': '2831'},
   'weight': '536870912000000'},
  {'token': {'denom': 'ibc/9712DBB13B9631EDFA9BF61B55F1B2D290B2ADB67E3A4EB3A875F3B6081B3B84',
    'amount': '47338259'},
   'weight': '536870912000000'}],
 'total_weight': '1073741824000000'}
```
```
pool['pool_assets'][0]['token']['denom'] # pour récupérer un asset 
```

Ya quelques info statique importante : 

(i). id
(ii). contrôler le 'type' (je t'ai parlé que d'un type de pool mais il y a plusieurs algos d'échanges)
(iii). contrôler les weights. 

l'info dynamique importante c'est : 

(iv). pool_assets  les parties amounts  ... ici vu les chiffres la pool doit être vraiment toute pourrie typiquement si tu échanges 1$ de valeur dans cette pool tu perds 90% de valeur :D





 c. Pour la génération de la commande de swap, je sais a peu près faire (disons que j'ai quelques problème avec certain asset) ... 


-------->>  Y'a du boulot pour faire un truc clean ... faut réfléchir avant de coder ! 


2. Une bonne gestion des transfer ibc. (là c'est a peu près clean pour moi, j'y ai passé pas mal de temps). (jexplique un peu après). J'ai mis à jour le github en incluant tout les assets. 


3. Une bonne gestion sur umee (gros chantier, j'arrive a liquider des positions mais quand je suis devant l'ordinateur, c'est pas automatique). 


--------------------------------------------------------------

Je parle du point 2. . 

Donc transfer ibc pour déplacer une crypto d'une chain A vers une chaine B. Donc a priori, il suffit d'installer osmosis et umee, vu que c'est le deux blockchaine dont je parle. Ici c'est pas vrai car y'a un truc technique sur ibc a comprendre. 

Imaginons que tu as des atoms sur osmosis, si tu veux les transferer sur umee, tu dois absolument repasser par la case cosmoshub : 
  
    OSMOSIS ---> COSMOSHUB ----> UMEE 

Si tu fais directement OSMOSIS ---> UMEE, les fonds ne seront pas perdu mais UMEE ne reconnaîtra pas les atom venant de osmosis, umee te dira ok je vois un truc mais  c'est pas des atoms venant de cosmoshub donc tu peux pas les utiliser chez moi, a priori c'est un systéme de protection un peu  chiant en pratique , car il faut installer plein de logiciel de chaîne  (bon en gros j'en ai une dizaine). 

Ensuite, un autre point c'est que tes atoms sur osmosis ne s'appelle pas atom il s'appelle 
"ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2" donc un truc du style 
ibc/ + HASH. 

Le hash est construit de la manière suivante : 
   hash = sha256(path)  avec path = "transfer/"+ channel+base_denom
   - channel qui est le channels ibc pour renvoyer tes assets a domicile. 
   - base_denom c'est le nom de l'asset dans sa blockchain d'origine : uatom 


Je refais le truc pour tes atoms chez osmosis. 

sage: #  le channel 
sage: channel = Blockchain.channels['osmosis']['cosmoshub']
 # c'est pas le même channel que tu as utiliser hier c'est normal car ici on veut le channel 
 # pour renvoyer a domicile
channel-0
sage: # donc path = 
sage: path = "transfer/"+channel+"/"+"uatom"
sage: "ibc/"+sha256(path).upper()

La fonction sha256 c'est la fonction qui est codée dans tools.py. Mais y'a également une fonction ibc_denom qui fait le job complet. 

---->   Le truc c'est que si tu connais que ibc_denom d'un asset tu peux pas retrouver de qui il s'agit car tu peux pas remonter sha256. 

Donc y'a deux possibilités : 

1. demander a la blockchain osmosis 
(avec sage: OSMOSIS.request('q ibc-transfer denom-trace ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2')   )

denom_trace:
  base_denom: uatom
  path: transfer/channel-0

il retrouve bien uatom Mais ca fait un appel rpc. 

2.  Comprendre comment osmosis fait pour te fournir cette réponse ? car ils sont pas capable de remonter sha256 non plus. Beh le truc c'est que comme on dispose de tous les channels dans ma base de donnée et qu'a priori on connais également tous les actifs natifs d'une blockchain, et bien on connait tous les ibc_denom possible, on peut faire un dictionnaire (hum, c'est un petit plus complexe !) 


- il y a une fonction denom() qui te renvoie l'ibc-denom de l'asset en question. Et une fonction transfer  atom.transfer(OSMOSIS) = ATOM chez OSMOSIS (c'est pas une vrai transaction, ca donne juste l'objet de la classe Asset qui contient les informations de l'actif ATOM transferer chez osmosis). 