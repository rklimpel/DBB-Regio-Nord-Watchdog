from database import UserPersistenceHandler
from scraper import TableCrawler, GameCrawler

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