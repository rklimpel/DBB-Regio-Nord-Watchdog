from tinydb import TinyDB, Query
from models import User, Game, TableEntry, Changes

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
        db_users = self.get_all()
        return [User(user) for user in db_users]

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

    def get_game_by_game_id(self, game_id):
        db_game = self.db.get(Query().game_id == game_id)
        if db_game is not None:
            return Game(db_game)
        return None

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
        for i in range(len(games)):
            found = False
            for j in range(len(db_games)):
                if games[i] == db_games[j]:
                    found = True
            if not found:
                changed_games.append(
                    Changes(
                        self.get_game_by_game_id(games[i].game_id), 
                        games[i]
                    )
                )
        return changed_games

    def get_upcoming_games(self, team_name=None, count=6):
        if team_name is None:
            db_games = self.db.search(
                Query().team_home_score == ""
                and Query().team_away_score == ""
            )
        else:
            db_games = self.db.search(
                (Query().team_home == team_name 
                or Query().team_away == team_name)
                and Query().team_home_score == ""
                and Query().team_away_score == ""
            )
        db_games = db_games[:count]
        return [Game(game) for game in db_games]     

    def get_recent_games(self, team_name=None, count=6):
        if team_name is None:
            db_games = self.db.search(
                (Query().team_home_score != "")
                & (Query().team_away_score != "")
            )
        else:
            db_games = self.db.search(
                (Query().team_home == team_name 
                or Query().team_away == team_name)
                and Query().team_home_score != ""
                and Query().team_away_score != ""
            )
        db_games.reverse()
        db_games = db_games[:count]
        return [Game(game) for game in db_games]

    def get_games_by_team(self, team_name):
        db_games = self.db.search(
            Query().home_team == team_name 
            or Query().away_team == team_name
        )
        return [Game(game) for game in db_games]
