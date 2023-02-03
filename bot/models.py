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
    position = ""
    team = ""
    games = ""
    wins = ""
    loses = ""
    points = ""
    points_made = ""
    points_against = ""
    points_difference = ""

    def __init__(self, entry):
        if 'position' in entry.keys(): self.position = entry["position"]
        if 'team' in entry.keys(): self.team = entry["team"]
        if 'games' in entry.keys(): self.games = entry["games"]
        if 'wins' in entry.keys(): self.wins = entry["wins"]
        if 'loses' in entry.keys(): self.loses = entry["loses"]
        if 'points' in entry.keys(): self.points = entry["points"]
        if 'points_made' in entry.keys(): self.points_made = entry["points_made"]
        if 'points_against' in entry.keys(): self.points_against = entry["points_against"]
        if 'points_difference' in entry.keys(): self.points_difference = entry["points_difference"]

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "team": self.team,
            "games": self.games,
            "wins": self.wins,
            "loses": self.loses,
            "points": self.points,
            "points_made": self.points_made,
            "points_against": self.points_against,
            "points_difference": self.points_difference,
        }

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return str(self.to_dict())

    def __eq__(self, other) -> str:
        return self.to_dict() == other.to_dict()

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
