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

    ### ici pool de osmsis 

    def insert_pools(self):
        datas = get_pools_data()
        self.cursor.executemany(
            'INSERT OR IGNORE INTO osmosis_pool VALUES (?,?,?,?)',datas)

    def get_assets_in_osmosis_pool(self):
        self.cursor.execute(
            'SELECT asset_1, asset_2 FROM osmosis_pool')
        datas = self.cursor.fetchall()
        assets = []
        for data in datas:
            asset_1,asset_2 = data
            assets.append(asset_1)
            assets.append(asset_2)
        return assets             


    def get_pools_(self):
        self.cursor.execute(
            'SELECT * FROM osmosis_pool')
        datas = self.cursor.fetchall()
        return datas

    def get_pools(self,white_list):
        # ici white_list est un dictionnaire d'asset
        white_list = [asset(OSMOSIS).denom() for asset in white_list]

        sql = f"SELECT id, type, asset_1, asset_2 FROM osmosis_pool WHERE asset_1 IN ({','.join(['?'] * len(white_list))}) AND asset_2 IN ({','.join(['?'] * len(white_list))})"
        matching_pools = []
        self.cursor.execute(sql, white_list + white_list)

        # Parcourez les résultats et ajoutez-les à la liste matching_pools
        for row in self.cursor.fetchall():
            matching_pools.append(row)
        return matching_pools

    def delete_pools(self,pools_id):
        sql = "DELETE FROM osmosis_pool WHERE id IN ({})".format(','.join(['?'] * len(pools_id)))

        self.cursor.execute(sql, pools_id)

    def get_pools_from(self,blockchain,white_list):
        white_list = [asset(blockchain).denom() for asset in white_list]
        table_name =f"{blockchain.name}_pool"
        sql = f"SELECT id, type, asset_1, asset_2 FROM {table_name} WHERE asset_1 IN ({','.join(['?'] * len(white_list))}) AND asset_2 IN ({','.join(['?'] * len(white_list))})"

        matching_pools = []
        self.cursor.execute(sql, white_list + white_list)

        for row in self.cursor.fetchall():
            matching_pools.append(row)

        return matching_pools