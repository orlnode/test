"""
Ici un petit programme pour tester les formules pour l'échange de crypto. 

--------------------------------------------------------------------------------------------

Je redonne ici les maths : 

   Donnée :  une pool de liquidité entre deux actifs A et B, on notera L_A et L_B 
   les liquidités. 
   
   La phrase qui traduit l'algorithme : pendant un swap le produit L_A * L_B reste constant.
   
   On cherche la fonction a ---> nombre de B lorsque l'on swap a token A dans cette pool.
   
   new_L_A = L_A + a (on ajoute nos a token A dans la pool)
   new_L_B = L_A * L_B  / new_L_A = L_A * LB / (L_A+a)    (le produit est constant)
   b = L_B - new_L_B  (on retire les  b token B de la pool)

   d'où b = L_B a / (a + L_A)

   On introduit la matrice : 

      swap_matrix = [ L_B  0  ] 
                    [ 1   L_A ]


    pour se souvenir  le terme en haut à gauche c'est la liquidité de la pool pour l'actif 
    que l'on va récupérer.

    et on a parlé de la matrice de fee 

    fee_matrix = [997    0]
                 [0   1000]


---------------------------------------------------------------------------------------------

On va se focaliser sur une pool de liquidité où y'a pas trop d'échanges  
(si y'a des gens qui passe une transaction en même temps que nous ca va changer les valeurs et
 ça on ne peux pas le prédire). 

Donc le but c'est de calculer la matrice de swap, faire une estimation du nombre de token 
que l'on va recevoir et ensuite faire le swap et vérifier que les prédictions sont bonnes. 

----> truc préliminaire 

là on a un problème car t'as pas de osmo pour payer les frais de transaction donc 
faut d'abord acheter un peu d'osmo (on peut payer les transaction en atom sur osmosis) 
mais la fonction blockchain.execute() ne prend pas ça en charge (donc toujours avoir un peu de 
tokens des blockchains utilisée)

donc on va faire  en terminal sans python

Donc 2 transactions 

  i.    envoyer un peu d'atom sur osmosis  200000 uatom ça fait 0.2 atom ,bon tu peux changer. 
  ii.   acheter un peu d'osmo.

gaiad  tx ibc-transfer transfer transfer channel-141 osmo1zy58n4j3qlq0fs86v9t5fg90qgh08p7zuxvytp 200000uatom    --node https://rpc-cosmoshub.whispernode.com:443 --chain-id cosmoshub-4  --gas auto --gas-adjustment 1.7  --gas-prices 0.025uatom  --output json --from wallet

ii. là se te fait acheter pour 0.03 atom de osmo en payant les frais en atom 

osmosisd tx poolmanager swap-exact-amount-in 30000ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2 1  --swap-route-pool-ids 1  --swap-route-denoms uosmo  --node https://osmosis-rpc.polkachu.com:443 --chain-id osmosis-1  --fees 670ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2  
--output json --from wallet

le truc ibc/blablabla c'est l' ibc_denom du jeton atom(OSMOSIS), 
tu peux le retrouver via python avec 
atom(OSMOSIS).denom()


"""
def swap_test():
    # je récupére la balance osmosis avant

    balance = OSMOSIS.balances()

    # ici on va swapper chez osmosis 
    # On va échanger  ATOM pour  UMEE dans la pool dont l'id est 643.
    
    # Je récupère les infos de la pool chez osmosis 

    pool = OSMOSIS.request("q poolmanager pool 643") # y'a une requéte rpc

    """ 
    là faut naviguer dans le dictionnaire pool que je recopie ici 
            
                {'pool': {'@type': '/osmosis.gamm.v1beta1.Pool',
                        'address': 'osmo1m28rqxevywfn76c4lf5vws64shd0hxvxyvzazzswlj5n7q48pxrqvlgry5',
                        'id': '643',
                        'pool_params': {'swap_fee': '0.003000000000000000',
                       'exit_fee': '0.000000000000000000',
                       'smooth_weight_change_params': None},
                      'future_pool_governor': '24h',
                      'total_shares': {'denom': 'gamm/pool/643',
                       'amount': '1636713866170166649564'},
                      'pool_assets': [{'token': {'denom': 'ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2',
                         'amount': '995085334'},
                        'weight': '536870912000000'},
                       {'token': {'denom': 'ibc/67795E528DF67C5606FC20F824EA39A6EF55BA133F4DC79C90A8C47A0901E17C',
                         'amount': '2148573946988'},
                        'weight': '536870912000000'}],
                      'total_weight': '1073741824000000'}}
    
    tu vois les deux weights sont les même donc c'est bien une pool 50 /50 
    ce que je dois récupérer c'est pool_assets les denom et amount 

    les liquidité (L_A = 995085334) 

    """
    coin_A, coin_B = pool['pool']['pool_assets']

    denom_A     = coin_A['token']['denom']   # le ibc_denom 
    L_A         = int(coin_A['token']['amount'])  # ici c'est le L_A
    denom_B     = coin_B['token']['denom']   # ibc denom
    L_B         = int(coin_B['token']['amount'])  # ici le L_B

    # on va faire un petit affichage. 
    # je commence par récupérer les assets 
    # la fonction cold_denom_trace : c'est une fonction qui à partir 
    # d'une blockchain et d'un ibc_denom renvoie l'objet Asset correspondant 
    
    A = OSMOSIS.cold_denom_trace(denom_A)  
    B = OSMOSIS.cold_denom_trace(denom_B)


    print(f" Pool de liquidite : {A} vs {B}")

    # on va échanger dans le sens ATOM --> UMEE 
    # donc A ---> B 
    # A = atom(osmosis) et B = umee(OSMOSIS) 

    fee_matrix = matrix(ZZ,2,2,[997,0,0,1000])
    swap_matrix_without_fee = matrix(ZZ,2,2,[L_B,0,1,L_A])
    
    swap_matrix = swap_matrix_without_fee * fee_matrix
    
    print(swap_matrix)
    # là je vais échanger 100 uatom contre du umee
    # pour savoir combien j'en récupére 
    """ 
    j'ai   [a b]   
           [c d]
    donc une fonction f :  x ---> (ax+b)/(cx+d)
    
     je fais V = [a b]    [x]    [ax+b] 
                 [c d]    [1]  = [cx+d] 
    et donc f(x) = premiere composante de V  / seconde composante de  V

    Ici ca peut sembler casse pied, mais la multiplication de matrice est plus simple 
    que la composition de fonction pour sage, du moins je trouve que c'est un peu plus propre !

    
    """                         
    a , b = swap_matrix * vector([100,1])
    print(f"prediction : {int(a/b)} {B.name} pour 100 {A.name}") 


    # la je fais le swap faudrait faire un fonction générique de swap

    """
    Je regarde depuis un terminal l'aide la commande de swap 
    osmosisd tx poolmanager swap-exact-amount-in --help
    swap exact amount in

    Usage:
    osmosisd tx poolmanager swap-exact-amount-in [token-in] [token-out-min-amount] [flags]
    Examples: 
         
         berk c'est degeux !!! 

        osmosisd tx poolmanager swap-exact-amount-in 2000000uosmo 1 --swap-route-pool-ids 5 
       --swap-route-denoms uion --from val 
       --keyring-backend test -b=block --chain-id=localosmosis --fees 10000uosmo
    
    ici faut que je spécifie le token-out-min-amount : 
    Ca permet de te protège en cas de gros swap juste avant toi. C'est le nombre minimum de token 
    que tu veux obtenir.  

    Donc je prend ma prédiction avec une petite variation pour être certain que la transaction passe 
    (note en pratique faudrait proteger autrement en prenant une variation 
    sur le prix de la pool). Pour l'exemple, la pool a assez de liquidité et puis on échnge 100uatoms :D   
    """
    amount = int(0.99 * a/b) 
    flag = f" --swap-route-pool-ids 643  --swap-route-denoms {B.denom()}" 

    # ICI c'est une vrai transaction !!! 

    OSMOSIS.execute(f"tx poolmanager swap-exact-amount-in 100{A.denom()} {amount} {flag}")
    
    new_balance = OSMOSIS.balances()
    # la j'affiche les différences de balance 
    delta_1 = int(new_balance[A.denom()]) - int(balance[A.denom()]) 

    if B.denom() in balance.keys():
        b_2 = int(balance[B.denom()])  # faudrait gérer ça dans la fonction balance de blockchain
    else:
        b_2 = 0
    delta_2 = int(new_balance[B.denom()]) - b_2
    print(f"{delta_1}")
    print(f"{delta_2}")
    """
    # pour finir je recupére la  pool après mon swap 
    new_pool = OSMOSIS.request("q poolmanager pool 643")

    # je recupère les amounts : 
    """
    new_coin_A, new_coin_B = new_pool['pool']['pool_assets']

    new_L_A         = int(new_coin_A['token']['amount'])  # ici c'est le L_A
    new_L_B         = int(new_coin_B['token']['amount'])  # ici le L_B

    print(f"Liquidity avant le swap : {L_A} /// {L_B}")
    print(f"Liquidity apres le swap : {new_L_A} /// {new_L_B}")

    print("Token A en plus",new_L_A - L_A)
    print("Token B en moins",L_B - new_L_B )
    """
sage: swap_test()

resultat : 

Pool de liquidite : atom(OSMOSIS) vs umee(OSMOSIS)
[2151410985082003                0]
[             997     990821718000]
prediction : 217133 uumee pour 100 uatom
gas estimate: 369663 
## la y'a une erreur rpc qui à été gérée   c'est peut être ma connection internet ! 
Error: RPC error -32603 - Internal error: tx (4CC54479D2A1C4A1989FDBEE16DA071FB671B38347591F64CE2B26463ADC50F0) not found
-100
217133
Liquidity avant le swap : 990821718 /// 2157884638999
Liquidity apres le swap : 990821818 /// 2157884421866
Token A en plus 100   ### ici c'est dans la pool
Token B en moins 217133  

On voit d'une part les predictions sont bonnes et également que les 100uatoms sont partis 
de mon portefeuille vers la liquidité de la pool 
et que les 217133 sont bien sorti de la pool vers  mon portefeuille. 

Pour les 0.3% de frais, on voit qu'ils ont été ajouté directement dans la pool de liquidité. 
Comme la pool appartient au liquidity provider, c'est bien eux qui récupérent ces frais
directement ici le protocol ne prend strictement rien. Bref, on échange de la valeur en 
peer to peer via le protocol mais celui-ci est complétement neutre. Osmosis (les validateurs et stakeur) 
récupére simplement les frais de transaction de la blockchain (une poussière : 0.003$)

"""