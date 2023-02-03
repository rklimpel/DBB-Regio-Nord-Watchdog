from database import UserPersistenceHandler, GamePersistenceHandler, TablePersistenceHandler
from scraper import TableCrawler, GameCrawler
import stringify
from models import User, Game, TableEntry, Changes

def subscribe(chat_id, user_name, arg):

    persistenceHandler = UserPersistenceHandler()
    new_user = False

    if persistenceHandler.check_user_exists(chat_id):
        user = persistenceHandler.get_user_by_chat_id(chat_id)
    else:
        user = User({
            'chat_id': chat_id, 
            'name': user_name, 
            'subscribed_teams': []
        })
        new_user = True
    
    teams = TableCrawler().get_teams()
    subscribed_team = None

    for team in teams:
        if arg.lower() in team.lower() or arg.lower() == "all":
            if not (team in user.subscribed_teams):
                user.subscribed_teams.append(team)
                subscribed_team = team
            elif arg.lower() != "all":
                return ["Du bist bereits auf das Team '" + team +"' subscribed"]

    if subscribed_team is None:
        return ["Team nicht gefunden"]

    if new_user:
        persistenceHandler.insert_user(user)
    else:
        persistenceHandler.update_user(user)

    messages = []
    if arg.lower() == "all":
        messages.append("Du hast Benachrichtigungen aktiviert für alle Teams")
    else:
        messages.append("Du hast Benachrichtigungen aktiviert für das Team '" + subscribed_team +"'")
    subscriptions_string = "Aktuell bist du auf folgende Teams subscribed:\n"
    for team in user.subscribed_teams:
        subscriptions_string += team + "\n"
    messages.append(subscriptions_string)
    return messages

def unsubscribe(chat_id, arg):
    
        persistenceHandler = UserPersistenceHandler()
        user = persistenceHandler.get_user_by_chat_id(chat_id)
    
        if user is None:
            return ["Du bist noch nicht auf ein Team subscribed"]
    
        teams = TableCrawler().get_teams()
        unsubscribed_team = None
    
        for team in teams:
            if arg.lower() in team.lower() or arg.lower() == "all":
                if team in user.subscribed_teams:
                    user.subscribed_teams.remove(team)
                    unsubscribed_team = team
                elif arg.lower() != "all":
                    return ["Du bist nicht auf das Team '" + team +"' subscribed"]
    
        if unsubscribed_team is None:
            return ["Team nicht gefunden"]
    
        persistenceHandler.update_user(user)
    
        messages = []
        if arg.lower() == "all":
            messages.append("Du hast Benachrichtigungen deaktiviert für alle Teams")
        else:
            messages.append("Du hast Benachrichtigungen deaktiviert für das Team '" + unsubscribed_team +"'")
        subscriptions_string = "Aktuell bist du noch auf folgende Teams subscribed:\n"
        for team in user.subscribed_teams:
            subscriptions_string += team + "\n"
        messages.append(subscriptions_string)
        return messages

def get_user_subscribed_changed_games_message(changes, user):
    messages = []
    for change in changes:
        if change.new.team_home in user.subscribed_teams or change.new.team_away in user.subscribed_teams:
            if change.new.is_played() and change.old.is_played() == False:
                messages.append("Ergebnis eingetragen!\n" + stringify.played_game_as_string(change.new))
            elif change.new.date != change.old.date or change.new.time != change.old.time:
                messages.append("Spiel verlegt!\n" + stringify.upcoming_game_as_string(change.new))
            else:
                messages.append("Nicht kategorisierte Änderung am!\n" + stringify.upcoming_game_as_string(change.new))
    return messages

def get_upcoming_games_message(team_name=None, count=None):  
    games = GamePersistenceHandler().get_upcoming_games(team_name=team_name, count=count)
    games_string = "Nächste Spiele, Stand vom " + stringify.current_data_time_as_string() + ":\n\n"
    for game in games:
        games_string += stringify.upcoming_game_as_string(game) + "\n"
    return [games_string]

def get_recent_games_message(team_name=None, count=None):
    if count is None:
        games = GamePersistenceHandler().get_recent_games(team_name=team_name)
    else:
        games = GamePersistenceHandler().get_recent_games(team_name=team_name, count=count)
    games_string = "Letzte Spiele, Stand vom " + stringify.current_data_time_as_string() + ":\n\n"
    for game in games:
        games_string += stringify.played_game_as_string(game) + "\n"
    return [games_string]

def get_team_games_message(team_name):
    games = GamePersistenceHandler().get_games_by_team(team_name)
    games_string = "Spiele " + team_name + ", Stand vom " + stringify.current_data_time_as_string() + ":\n\n"
    for game in games:
        if not game.is_played():
            games_string += stringify.upcoming_game_as_string(game) + "\n"
        else:
            games_string += stringify.played_game_as_string(game) + "\n"
    return [games_string]

def get_table_message():
    table = TablePersistenceHandler().get_table()
    table_string = "Tabelle, Stand vom " + stringify.current_data_time_as_string() + ":\n\n"
    for table_entry in table:
        table_string += stringify.table_entry_as_string(table_entry) + "\n"
    return [table_string]

def get_user_subscribed_changed_table_message(changes, user):
    messages = []
    for change in changes:
        if change.new.team in user.subscribed_teams:
            change_message = ""
            change_message += "Tabellenänderung für " + change.new.team + ":\n"
            if change.new.points != change.old.points:
                change_message += "Punkte dazugewonnen!\n"
            if change.new.position != change.old.position:
                change_message += "Tabellenposition hat sich verändert!\n"
            if change.new.games != change.old.games \
                and change.new.position == chhange.old.position \
                and change.new.points == change.old.points:
                change_message += "Keine Veränderung nach Eintrag des neuen Spiels!\n"
            change_message += "\n" + stringify.table_entry_as_string(change.new)
            messages.append(change_message)
    return messages