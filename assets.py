class Asset:
    
    instances_by_id = {}
    
    ### ici by_denom ne peut pas être un dictionnaire ! ibc_denom 
    ###  ne peux pas retrouver complétement l'asset et sa chain 
    ###  faut utiliser by_id où j'ai remplacé ibc/ par blockchain.name+'/' 

    instances_by_denom = {}
    """
    sage: atom(JUNO).denom()
        'ibc/C4CFF46FD6DE35CA4CF4CE031E643C8FDC9BA4B99AE598E9B0ED98FE3A2319F9'
    sage: atom(OSMOSIS).denom()
        'ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2'
    sage: atom(CRESCENT).denom()
        'ibc/C4CFF46FD6DE35CA4CF4CE031E643C8FDC9BA4B99AE598E9B0ED98FE3A2319F9'
    par exemple, atom(JUNO) et atom(CRESCENT) ont le même ibc_denom mais c'est pas les même
    asset : 
        Blockchain.channels['juno']['cosmoshub'] == Blockchain.channels['crescent']['cosmoshub']
        
        La construction ibc_denom depend du channel pour renvoyer atom(JUNO) chez cosmoshub 
        et pas du channel qui a permis son envoie, rien n'interdit 
        Blockchain.channels['juno']['cosmoshub'] == Blockchain.channels['crescent']['cosmoshub']

        Par contre, on peut pas avoir 
        Blockchain.channels['cosmoshub']['juno'] == Blockchain.channels['cosmoshub']['crescent']
        Les channels partant de cosmoshub sont tous différents mais ceux arrivant peuvent être les 
        même. 
        
        y'a certainement une histoire de sécurité dérière ce truc.  



    """


    """
        Initialisation de tous les assets ! bouh c'est degeux ! 
        principe : 
           1. Pour tout les assets je créer un variable globals : 
              par ex :  atom désigne atom chez cosmoshub
           2. Je crée tout les transfer d'asset 
            J'ai accés à cette instance via atom(OSMOSIS)   
    """

    @classmethod
    def init(cls):
        with Database(DATABASE) as database:
            assets = database.get_assets()
        for asset in assets:
            name,blockchain,decimals, symbol = asset
            try:
                blockchain = Blockchain.instances_by_name[blockchain]
                globals()[blockchain.prefix+symbol.lower()] = cls(name,blockchain,blockchain,symbol,decimals)
            except:
                continue
        for asset in assets:
            for host_chain in Blockchain.instances_by_name.values():
                name,blockchain,decimals, symbol = asset
                try:
                    blockchain = Blockchain.instances_by_name[blockchain]
                    if not(host_chain.name == blockchain.name):
                        cls(name,host_chain,blockchain,symbol,decimals)
                except:
                    continue


    def __init__(self,name,host_chain,native_chain,symbol,decimals):
        """
            name : uatom par exemple
            host_chain : type Blockchain, c'est la blockchain où l'asset est 
            native_chain :  blockchain native de l'asset
            decimals : nombre de décimals de l'asset pour atom 6.
        """
        self.name           = name
        self.host_chain     = host_chain
        self.native_chain   = native_chain
        self.symbol         = symbol
        self.decimals       = decimals
        self.nickname       = self.native_chain.prefix + self.symbol.lower()

        
        if self.is_native():
            self.id = self.name 
        
        else:
            denom = self.denom()
            ibc,denom = denom.split("/")
            ibc = self.host_chain.name 
            self.id  = ibc+"/"+denom
        
        # dictionnaire id ---> asset 

        self.__class__.instances_by_id[self.id] = self

        ###  je laisse instances_by_denom pour l'instant mais c'est pas bon comme identifiant 

        self.__class__.instances_by_denom[self.denom()] = self


    def __repr__(self):
        return self.nickname + f"({self.host_chain.name.upper()})"


    def is_native(self):
        return self.host_chain.name == self.native_chain.name

    def balance(self):
        try:
            return self.host_chain.balances()[self.denom()]
        except:
            return '0'

            
    def denom(self):
        if self.is_native():
            return self.name
        path = {'path' : "transfer/"+Blockchain.channels[self.host_chain.name][self.native_chain.name] , 'base_denom' : self.name }
        return ibc_denom(path)


    def transfer(self,to_chain):
        if to_chain == self.native_chain:
            return self.instances_by_id[self.name]
        channel = Blockchain.channels[to_chain.name][self.native_chain.name]
        path = {
            'path' : "transfer/"+channel, 'base_denom' : self.name 
        }
        ibc = ibc_denom(path)
        id = ibc.replace('ibc/',f'{to_chain.name}/')
        return self.instances_by_id[id]


    def __call__(self,to_chain):
        return self.transfer(to_chain)