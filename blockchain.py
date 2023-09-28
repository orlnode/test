import asyncio
import subprocess
import json

from tools import command_exists


class Blockchain:


    # base de donnée

    database     =  DATABASE
    table        = 'blockchain'



    instances_by_name       = {}

    # les blockchains controlable i.e le logiciel installé

    controlable_instance    = []


    # channel ibc pour la comminucation entre blockchain

    channels     = {}



    @classmethod
    def reset(cls):
        cls.instances_by_name    = {}
        cls.controlable_instance = []
        cls.channels             = {}


    @classmethod
    def add(cls,name):
        globals()[name.upper()] = cls(name)



    @classmethod
    def init(cls):

        # fonction pour initialiser toutes les blockchains 

        cls.reset()


        with Database(cls.database) as database:

            # nom des différentes blockchaines
            
            names = database.get_names()

        for name in names:

            # une variable nom en majuscule 
            
            globals()[name.upper()] = cls(name)


    def __init__(self,name):

        

        self.__class__.instances_by_name[name] = self
        
        # name est la valeur de l'attribut name dans la base de donnée 

        with Database(self.__class__.database) as database:

            """
                Les attributs de l'objet blockchain sont stokés dans la table 
                blockchain de la base de donnée blockchain.db

            """
            
            attrs = database.get_attrs_of_table(self.__class__.table)
            
            for attr in attrs:

                # la fonction database.get(attr,name)
                # renvoie les valeurs des attributs de la ligne dans la table 
                # blockchain dont le 'name'  est name

                setattr(self,attr,database.get(attr,name))

            # creation des channels ibc

            self.__class__.channels[name] = database.get_channels(name)

            # j'ai un logiciel qui s'appele sommelier, qui ne correspond pas à la bc 

            if name == 'sommelier':

                self.is_controlable = False

            else:
                # si le logiciel de la chaine est installer et si y'a wallet
                if command_exists(self.command):

                    is_wallet_ok, address = self.get_address()
                    
                    if is_wallet_ok:
                    
                        self.is_controlable = True
                        self.address        = address
                        self.__class__.controlable_instance.append(self)
                else:
                    self.is_controlable = False
                    self.address        = None

            # pour les transactions 
            # ici gas-adjustment 1.7 c'est peut être un peu trop mais 
            # y'a un bordel sur certain chain donc soit gérer au cas par cas, soit laisser à 1.7
            # Disons que c'est pas trop grave sauf sur cosmoshub ou les frais de transaction ne 
            # sont pas négligeable 0.03$ (je suis un radin :D 

            self.gas          = f" --gas auto --gas-adjustment 1.7  --gas-prices {self.gas_price}{self.fee_token}"

            # prefix servira pour les assets 
            # casse pied :::  en gros ici j'ajoute un prefix pour différencier certain asset
            # par exemple il y a plusieurs type d'usdc chez l'univers cosmos
            # y'a du vrai usdc qui vient de noble
            # y'a du axl usdc qui vient du bridge axelar d'eth 
            # y'a du g usdc qui vient du bridge gravity 
            # y'a du avax usdc  qui vient du vrai usdc de la blockchain avanlance et ramené 
            # pour un raison  certainement débile par axelar (ils sont con con chez axelar, 
            # il ramene plein de merde de partout). 

            self.prefix = ""
            if name =='axelar':
                self.prefix ="axl"
            if name == 'gravitybridge':
                self.prefix = 'g'
            if name == 'nolus':
                self.prefix = 'n'
            if name =='quasar':
                self.prefix = 'qua'
            if name =='carbon':
                self.prefix ='c'


    """
        Requete RPC. 

        C'est une source de problème donc objectif limiter au maximum les requètes. 

        Pour chaque transaction  :  

        1.  J'ai besoin d'avoir mes balances avant la transaction, que je peux stoker 
            en dur mais faut être certain que la mise à jour est ok. 
            Je peux update les balances après les transactions. 1 appel RPC.

        2. J'ai également besoin de savoir si la transaction a bien été inclus dans le block. 
           donc mininum 1 requète. 

        Ensuite des appels rpc pour mettre à jours les prix ou autre truc. (c'est moins grave). 

    """


    def __repr__(self):
        return self.name.upper()


    def request(self,request):
        request = f"{self.command} {request} {self.node} --chain-id {self.chain} -o json"       
        process = os.popen(request)
        
        stdout = process.read()
        stderr = process.close()
        
        if stderr:
            return 'error'
        
        else:
            try:
                return json.loads(stdout)
            except:
                return 'error'


    """
        Ici on recupère les adresses du wallet. 

    """
    def get_address(self):
        ### changement 
        request = f" echo {password} | {self.command} keys list --output json"
        process = os.popen(request)
        stdout = process.read()
        stderr = process.close()
        if stderr:
            return False, None
        else:
            try:
                # ici y'a un truc avec certain chain par exmeple marsd
                # normalement ça doit me renvoyer un tableau vide []
                # mais mars me renvoie un message : No records were found in keyring
                wallets = json.loads(stdout)
            except:
                return False, None 
            wallet  = [w for w in wallets if w['name'] == 'wallet']
            if wallet ==[]:
                return False, None
            else:
                return True, wallet[0]['address']



    async def async_request(self,request):
        return False


    def cold_denom_trace(self,ibc_denom):
        id = ibc_denom.replace("ibc/",self.name+'/')
        return Asset.instances_by_id[id]

    def denom_trace(self,ibc_denom):
        return self.request(f"q ibc-transfer denom-trace {ibc_denom}")




    """
        Pour l'envoie de message 
            sign        : signer une transaction hors ligne
            broadcast   : envoyé la transaction
        
        Pour executer une commande cli directement
            execute     : executer une transaction cli   
        
        Attention : il faut vérifie que la transaction est bien enregistrée dans
                     le block. 
    """



    def execute(self,tx):
        tx = f"echo {password} | {self.command} {tx}  {self.node} --chain-id {self.chain} {self.gas}  --output json --from wallet"

        process  = os.popen(f"{tx} -y")
        
        stdout   = process.read()
        stderr   = process.close()
        
        if stderr:
            
            # si besoin je peux envoyer l'erreur

            return "error"

        # stdout renvoie un dictionnaire avec le txhash de la transaction
        
        txhash =  json.loads(stdout)['txhash']
        
        error = True 
        
        while error:
            # ici vaut mieux réfléchir à un compteur a la place de while qui fait tourner
            # a l'infini au cas où y'a un problème
            # et que la transaction ne soit pas enregistrer dans le block
            time.sleep(6) #temps de validation du block
            result  = self.request(f' q tx {txhash}')
            if not(result == 'error'):
                return result


    def balances(self):
        request = f" q bank balances {self.address}"
        result  = self.request(request)['balances']
        balances = {}
        for coin in result:
            balances[coin['denom']] = coin['amount']
        return balances





        """
        Il y a un timeout par default qui est de 10min. Si y'a un problème les fonds retournent 
        à la casse départ 10 minutes plus tard, faudrait voir comment réduire le timeout 
        (d'expérience) 1min c'est suffisant 
        """

    def ibc_transfer(self,asset,amount,to_chain):



        # asset     :  Asset
        # amount    :  int 
        # to_chain  :  Blockchain 


        # 1. il faut que to_chain et self soit controlable 
        # is_controlable = le logiciel de la chain est installé + wallet est enregistré 

        assert self.is_controlable
        assert to_chain.is_controlable

        # ensuite on veut pas transférer n'importe quoi 
        # on veut transferer soit un asset natif de self, ou soit un asset native de to_chain
        
        assert (asset.is_native or asset(to_chain).is_native)

        # recupération du channel ibc
        # Blockchain.channels est un dictionnaire a double entrée 
        # Blockchain[A.name][B.name] donne le channel ibc pour transférer de la 
        # blockchain A vers la blockchain B 
        try:

            channel = Blockchain.channels[self.name][to_chain.name]

        except:

            print("transfer impossible pas de connection ibc")
            return False

        # ici je regarde les balances
        
        to_balance = asset(to_chain).balance()
        to_address = to_chain.address

        # on balance la transaction 
        
        tx = f" tx ibc-transfer transfer transfer {channel} {to_address} {amount}{asset.denom()} "
        
        # ici a la sorti de execute on est certain que la transaction est validé 
        # dans la blockchain self

        self.execute(tx)

        # maintenant faut attendre la validation chez to_chain donc je regarde la balance

        received = False 
        while not received:
            time.sleep(6)
            new_balance = asset(to_chain).balance() # c'est la balance de l'asset qui doit arriver chez to_chain
            if to_balance == new_balance:
                continue
            else:
                received = True
        return True