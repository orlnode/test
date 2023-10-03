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

Test du router 
--------------

```
sage: router = test_routing.routing(atom,atom)
sage: router
[[['atom', 'osmo', '1'], ['osmo', 'atom', '1135']],
 [['atom', 'osmo', '1135'], ['osmo', 'atom', '1']],
 [['atom', 'akt', '4'], ['akt', 'osmo', '3'], ['osmo', 'atom', '1']],
 [['atom', 'akt', '4'], ['akt', 'osmo', '3'], ['osmo', 'atom', '1135']],
 [['atom', 'akt', '4'], ['akt', 'osmo', '1093'], ['osmo', 'atom', '1']],
 [['atom', 'akt', '4'], ['akt', 'osmo', '1093'], ['osmo', 'atom', '1135']],
 [['atom', 'regen', '22'], ['regen', 'osmo', '42'], ['osmo', 'atom', '1']],
 [['atom', 'regen', '22'], ['regen', 'osmo', '42'], ['osmo', 'atom', '1135']],
 [['atom', 'osmo', '1'], ['osmo', 'akt', '3'], ['akt', 'atom', '4']],
 [['atom', 'osmo', '1'], ['osmo', 'akt', '1093'], ['akt', 'atom', '4']],
 [['atom', 'osmo', '1135'], ['osmo', 'akt', '3'], ['akt', 'atom', '4']],
 [['atom', 'osmo', '1135'], ['osmo', 'akt', '1093'], ['akt', 'atom', '4']],
 [['atom', 'osmo', '1'], ['osmo', 'regen', '42'], ['regen', 'atom', '22']],
 [['atom', 'osmo', '1135'], ['osmo', 'regen', '42'], ['regen', 'atom', '22']]]
 ``` 

 Dans pool_router qui est un classe y'a trois objets Pool_router 
 ```
 white_list = [atom,osmo,axlusdc,axlweth,axlwbtc,akt,regen,evmos]
test_routing = Pool_router(OSMOSIS,white_list,3)


# test routing sur comdex  (faut surveiller les channels ibc)
white_list = [statom,stosmo,atom,cmdx,cmst,evmos,juno]
comdex_routing = Pool_router(COMDEX,white_list,4)

# testing sur crescent 
white_list = [cre,atom, bcre,evmos,axlusdc,cmst,ist]
crescent_routing = Pool_router(CRESCENT,white_list,3)
 ```

 Donc là c'est pour tester la classe en multi-chain (trois blockchain différentes)

 ```
 len(crescent_routing.routing(atom,atom))
 42

 ```

 