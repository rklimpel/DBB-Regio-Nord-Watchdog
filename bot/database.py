from tinydb import TinyDB, Query
from models import User, Game, TableEntry

class PersistenceHandler():

    def __init__(self, db_path):
        self.db = TinyDB(db_path)

    def get_all(self):
        return self.db.all()

    def get_by_id(self, doc_id):
        return self.db.get(doc_id=doc_id)

    def insert(self, data):
        self.db.insert(data)

    def insert_all(self, data):
        self.db.insert_multiple(data)

    def clear_db(self):
        self.db.truncate()

    def update(self, data, doc_ids):
        self.db.update(data, doc_ids=doc_ids)

    def delete(self, doc_ids):
        self.db.remove(doc_ids=doc_ids)


class UserPersistenceHandler(PersistenceHandler):

    def __init__(self):
        super().__init__('data/users.json')

    def check_user_exists(self, chat_id):
        return self.get_user_id_by_chat_id(chat_id=chat_id) is not None

    def get_user(self, user_id):
        return self.get_by_id(user_id)

    def get_user_by_chat_id(self, chat_id):
        db_user = self.db.get(Query().chat_id == chat_id)
        if db_user is not None:
            return User({
                "chat_id": db_user["chat_id"],
                "name": db_user["name"],
                "subscribed_teams": db_user["subscribed_teams"]
            })
        return None

    def get_user_id_by_chat_id(self, chat_id):
        user = self.db.get(Query().chat_id == chat_id)
        if user is not None:
            return user.doc_id
        return None

    def get_users(self):
        return self.get_all()

    def insert_user(self, user: User):
        self.insert(user.to_dict())

    def update_user(self, user: User):
        self.update(
            user.to_dict(), 
            doc_ids=[self.get_user_id_by_chat_id(chat_id=user.chat_id)]
        )

    def delete_user(self, user_id):
        self.delete(doc_ids=[self.get_user_id_by_chat_id(chat_id=user.chat_id)])

class GamePersistenceHandler(PersistenceHandler):

    def __init__(self):
        super().__init__('data/games.json')

    def get_games(self):
        db_games = self.get_all()
        if db_games is not None:
            return [Game(game) for game in db_games]

    def insert_games(self, games):
        dict_games = [game.to_dict() for game in games]
        self.insert_all(dict_games)

    def update_games(self, games):
        self.clear_db()
        self.insert_games(games)

    def check_dv_up_to_date(self, games):
        return len(self.get_changed_games(games)) == 0

    def get_changed_games(self, games):
        db_games = self.get_games()
        if db_games is None:
            return games
        changed_games = []
        for i in range(len(db_games)):
            match = False
            for j in range(len(games)):
                if db_games[i] == games[j]:
                    match = True
            if not match:
                changed_games.append(games[i])
        return changed_games

        

       