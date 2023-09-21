import asyncio
import subprocess
import json


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


            # prefix servira pour les assets 

            self.prefix = ""


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
                print(stdout)
                return 'error'



    def get_address(self):
        request = f" echo {password} | {self.command} keys show wallet --output json"
        process = os.popen(request)
        stdout = process.read()
        stderr = process.close()
        if stderr:
            return False, None
        else:
            return True, json.loads(stdout)['address']



    async def async_request(self,request):
        return False


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

        tx = f"echo {password} | {self.command} {tx}  {self.node} --chain-id {self.chain} {self.gas}  --output json"
        process  = os.popen(f"{message} -y")
        
        stdout   = process.read()
        stderr   = process.close()
        
        if stderr:
            
            # si besoin je peux envoyer l'erreur

            return "error"

        # stdout renvoie un dictionnaire avec le txhash de la transaction
        
        txhash =  json.loads(stdout)['txhash']
        
        error = True 
        
        while error:
            # ici vaut mieux mettre un compteur 
            time.sleep(6)
            result  = self.request(f' q tx {txhash}')
            if not(result == 'error'):
                return result


    def balances(self):
        request = f" q bank balances {self.address}"
        result  = self.request(request)
        return result['balances']
