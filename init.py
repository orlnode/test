current_directory = os.getcwd()

separator = os.path.sep
DATABASE = "{current_directory}{separator}blockchain.db"

attach(f"{current_directory}{separator}tools.py")
attach(f"{current_directory}{separator}database.py")
attach(f"{current_directory}{separator}blockchain.py")
