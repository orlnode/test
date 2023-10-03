import time
import os 

current_directory = os.getcwd()

separator = os.path.sep
DATABASE = f"{current_directory}{separator}blockchain.db"


attach(f"{current_directory}{separator}tools.py")
attach(f"{current_directory}{separator}database.py")
attach(f"{current_directory}{separator}blockchain.py")
attach(f"{current_directory}{separator}assets.py")


### pour tester le routing 


attach(f"{current_directory}{separator}graph_tools.py")
attach(f"{current_directory}{separator}pool_router.py")