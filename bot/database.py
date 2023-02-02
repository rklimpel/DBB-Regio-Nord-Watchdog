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