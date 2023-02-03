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
        self.game_id = game["game_id"]
        self.team_home = game["team_home"]
        self.team_away = game["team_away"]
        self.team_home_score = game["team_home_score"]
        self.team_away_score = game["team_away_score"]

    def is_played(self):
        return self.team_home_score != "" and self.team_away_score != ""

    def to_dict(self):
        return {
            "date": self.date,
            "time": self.time,
            "game_id": self.game_id,
            "team_home": self.team_home,
            "team_away": self.team_away,
            "team_home_score": self.team_home_score,
            "team_away_score": self.team_away_score
        }

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

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

    def to_dict(self):
        return {
            "rank": self.rank,
            "team": self.team,
            "games": self.games,
            "wins": self.wins,
            "losses": self.losses,
            "points": self.points
        }
    

class User():
    name=""
    chat_id = ""
    subscribed_teams = []

    def __init__(self, user):
        if 'name' in user.keys(): self.name = user["name"]
        if 'chat_id' in user.keys(): self.chat_id = user["chat_id"]
        if 'subscribed_teams' in user.keys(): self.subscribed_teams = user["subscribed_teams"] 

    def to_dict(self):
        return {
            "name": self.name,
            "chat_id": self.chat_id,
            "subscribed_teams": self.subscribed_teams
        }

class Changes():
    def __init__(self, old, new):
        self.old = old
        self.new = new

    def to_dict(self):
        return {
            "old": self.old,
            "new": self.new,
        }

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())
