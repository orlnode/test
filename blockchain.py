import asyncio
import subprocess
import json

#  base de donnée pour l'initialisation des blockchains, channels ibc et assets


"""
    Ici un objet blockchain est construit pour chaque blockchain.
    les attributs sont stokés dans une base de donnée (qui a juste vocation à contenir 
    les données qui sont assez statiques) ! 

    il y a un attribut self.controllable qui est un bool vallant true si 
    et seulement si le logiciel de la chaine est installer (via command_exist) et si une
    clef est stokée dans le logiciel. 
    
    il y a un incovenient à ce modèle car si j'ai besoin d'implémenter des méthodes sur
    une chaine spécifique je vais devoir créer une seconde classe ? 
    ou alors faire quelques choses avec des modules 

    class module:
        def __init__(self,blockchain_name )
            self.blockchain = Blockchain.instance_by_name[blockchain_name]
            self.execute = self.blockchain.exectute
            self.request = self.blockchain.request
            self.sign    = sel

    class crescent_dex(module):
        def __init__(self):
            module.__init__(self,"crescent")



"""








DATABASE = "blockchain.db"

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
                # si le logiciel de la chaine est installer 
                self.is_controlable   = command_exists(self.command)

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

        assert self.is_controlable

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

    
    # requete asynchrone 

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

        tx = f"echo {password} | {self.command} {tx}  {self.node} --chain-id {self.chain} {self.gas} {self.mode} --output json"
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

    @controlable
    def balances(self,address):
        request = " q bank balances {address}"
        result  = self.request(request)
        return result['balance']

def controlable(function):
    def wrapper(obj,*args, **kwargs):
        if not obj.is_controlable():
            return "Action impossible"
        else:
            return obj.function(*args,**kargs)
    return wrapper 