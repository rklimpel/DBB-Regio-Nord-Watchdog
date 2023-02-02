import json

class Game():
    date = ""
    time = ""
    game_id = ""
    team_home = ""
    team_away = ""
    team_home_score = ""
    team_away_score = ""

    def __init__(self, game):
        self.date = game["date"]
        self.time = game["time"]
        self.game_id = game["id"]
        self.team_home = game["team_home"]
        self.team_away = game["team_away"]
        self.team_home_score = game["team_home_score"]
        self.team_away_score = game["team_away_score"]

    def to_JSON(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))

class TableEntry():
    rank = ""
    team = ""
    games = ""
    wins = ""
    losses = ""
    points = ""

    def __init__(self, entry):
        self.rank = entry["rank"]
        self.team = entry["team"]
        self.games = entry["games"]
        self.wins = entry["wins"]
        self.losses = entry["losses"]
        self.points = entry["points"]
    
    def to_JSON(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))

class User():
    name=""
    chat_id = ""
    subscribed_teams = []

    def __init__(self, user):
        if 'name' in user.keys(): self.name = user["name"]
        if 'chat_id' in user.keys(): self.chat_id = user["chat_id"]
        if 'subscribed_teams' in user.keys(): self.subscribed_teams = user["subscribed_teams"] 

    def to_JSON(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))