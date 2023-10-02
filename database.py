import sqlite3

class Database:

    def __init__(self,name):

        self.name       = name
        self.conn       = None
        self.cursor     = None

    def __enter__(self):
        
        self.conn = sqlite3.connect(self.name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        if self.conn:
            self.conn.commit()
            self.conn.close()

    def get_attrs_of_table(self,table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        column_names = [column[1] for column in self.cursor.fetchall()]
        return column_names

    def get(self,attr,name):
        
        self.cursor.execute(
            f'SELECT {attr} FROM blockchain WHERE name=?',(name,))
        
        data = self.cursor.fetchone()
        return data[0]

    def get_names(self):
        self.cursor.execute(
            'SELECT name FROM blockchain')
        datas = self.cursor.fetchall()
        return [data[0] for data in datas]

    def insert_blockchain(self,name,chain,node,fee_token,command,gas_price):
        self.cursor.execute(
            'INSERT OR IGNORE INTO blockchain values (?,?,?,?,?,?)',(name, chain,node,fee_token,command,gas_price))

    def insert_blockchains(self,datas):
        self.cursor.executemany('INSERT OR IGNORE INTO blockchain VALUES (?, ?, ?, ?, ?, ?)',datas)

    def insert_ibc(self,in_blockchain,out_blockchain,channel):
        self.cursor.execute(
            'INSERT INTO ibc VALUES (?, ?, ?)', (in_blockchain,out_blockchain,channel)
            ) 


    def get_channels(self,name):
        self.cursor.execute(
            'SELECT blockchain_out_name, channel FROM channel where blockchain_in_name=?',(name,))
        datas = self.cursor.fetchall()
        return {data[0] : data[1] for data in datas}

        
    def insert_channels(self,datas):
        self.cursor.executemany(
            'INSERT OR IGNORE INTO channel VALUES (?,?,?)',datas)
        


    def get_assets(self):
        self.cursor.execute(
            'SELECT * FROM asset')
        datas = self.cursor.fetchall()
        return datas


"""
Quelques fonction pour les pools 
"""