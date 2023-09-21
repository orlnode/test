import hashlib
import subprocess

def command_exists(command):
    try:
        # On exécute la commande "which" suivie du nom de la commande à vérifier
        subprocess.check_output(["which", command])
        return True
    except subprocess.CalledProcessError:
        return False


def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def ibc_denom(path):
    # path = {'path' : path, 'base_denom' : base_denom}
    to_hash = f"{path['path']}/{path['base_denom']}"
    return f"ibc/{sha256(to_hash).swapcase()}"