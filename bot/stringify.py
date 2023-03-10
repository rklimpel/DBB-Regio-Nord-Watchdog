from datetime import datetime
from models import User, Game, TableEntry, Changes

def upcoming_game_as_string(game) -> str:
    return f"{game.date}  {game.time}:\n{game.team_home} vs. {game.team_away}\n"

def played_game_as_string(game) -> str:
    string = f"{game.date}  {game.time}:\n"
    string += f"{game.team_home_score} | {game.team_home}\n"
    string += f"{game.team_away_score} | {game.team_away}\n"
    return string

def current_data_time_as_string() -> str:
    return datetime.now().strftime("%d.%m.%Y  %H:%M")

def table_entry_as_string(table_entry: TableEntry) -> str:
    return f"{table_entry.position}.  {table_entry.team}  ({table_entry.points})"