from tinydb import TinyDB, Query
from models import User, Game, TableEntry, Changes

test_contains = lambda value, search: search.lower() in value.lower()

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

    def check_games_up_to_date(self, games):
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
        if count == None: count = 6
        if team_name is None:
            db_games = self.db.search(
                (Query().team_home_score == "")
                & (Query().team_away_score == "")
            )
        else:
            db_games = self.db.search(
                (Query().team_home.test(test_contains, team_name)
                | Query().team_away.test(test_contains, team_name))
                & (Query().team_home_score == "")
                & (Query().team_away_score == "")
            )
        print("Found Games for team: " + team_name + ": " + str(len(db_games)))
        print(db_games)
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
                (Query().team_home.test(test_contains, team_name)
                | Query().team_away.test(test_contains, team_name))
                & (Query().team_home_score != "")
                & (Query().team_away_score != "")
            )
        db_games.reverse()
        db_games = db_games[:count]
        return [Game(game) for game in db_games]

    def get_games_by_team(self, team_name):
        db_games = self.db.search(
            (Query().team_home.test(test_contains, team_name))
            | (Query().team_away.test(test_contains, team_name))
        )
        return [Game(game) for game in db_games]

class TablePersistenceHandler(PersistenceHandler):
    
        def __init__(self):
            super().__init__('data/table.json')
    
        def get_table(self):
            db_table = self.get_all()
            return [TableEntry(entry) for entry in db_table]

        def get_teams(self):
            db_table = self.get_all()
            return [entry["team"] for entry in db_table]
    
        def insert_table(self, table):
            dict_table = [entry.to_dict() for entry in table]
            self.insert_all(dict_table)
    
        def update_table(self, table):
            self.clear_db()
            self.insert_table(table)
    
        def check_table_up_to_date(self, new_table):
            return len(self.get_changed_table_entries(new_table)) == 0
    
        def get_changed_table_entries(self, table):
            db_table = self.get_table()
            changed_table = []
            for i in range(len(table)):
                found = False
                for j in range(len(db_table)):
                    if table[i] == db_table[j]:
                        found = True
                if not found:
                    changed_table.append(
                        Changes(
                            self.get_table_entry_by_team(table[i].team), 
                            table[i]
                        )
                    )
            return changed_table
    
        def get_table_entry_by_team(self, team_name):
            db_entry = self.db.get(Query().team == team_name)
            if db_entry is not None:
                return TableEntry(db_entry)
            return None
    
        def get_table_entry_by_position(self, position):
            db_entry = self.db.get(Query().position == position)
            if db_entry is not None:
                return TableEntry(db_entry)
            return None
    