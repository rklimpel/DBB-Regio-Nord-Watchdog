from tinydb import TinyDB
from models import User, Game, TableEntry

class PersistenceHandler():

    def __init__(self):
        self.games_db = TinyDB('data/games.json')
        self.table_db = TinyDB('data/table.json')
        self.user_db = TinyDB('data/users.json')

    def get_games(self):
        return self.games_db.all()

    def get_table(self):
        return self.table_db.all()  

    def get_user(self, user_id):
        return self.user_db.get(doc_id=user_id)

    def get_users(self):
        return self.user_db.all()

    def insert_user(self, user: User):
        self.user_db.insert(user.to_JSON())


