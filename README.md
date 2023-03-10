# Basketball Regio Nord (West) Watchdog

Telegram bot to retrieve information of the German Basketball Regionalliga Nord (West) and to subscribe to changes in the standings or games.
Please note that in this repo some content is written in German, as it was developed for a local sports league.

Telegram Bot supports the following commands:
```
/tabelle - Aktuelle Tabelle
/subscribe - Benachrichtigungen für Teams aktivieren
/unsubscribe - Benachrichtigungen für Teams deaktivieren
/team_spiele - Alle Spiele eines Teams
/team_letzte_spiele - Letzte Spielergebnisse eines Teams
/team_naechste_spiele - Nächste Spiele eines Teams
/letzte_spiele - Letzten Spielergebnisse der Liga
/naechste_spiele - Nächsten Spiele der Liga
/teams - Liste aller Teams in der Liga
/start - Zeigt Willkommensnachricht
/hilfe - Zeigt Bot Kommandos
```

## How does this stuff work?

Data is retrieved from the basketball league website via a web scraper, formatted and then written to the database using TinyDB. A periodic job runs every x minutes to check if there is anything new in the standings or the list of games. 
Via the Telegram bot you can get information like standings, next games or last played games. The information is then provided from the database. Furthermore, it is possible to subscribe to updates regarding specific teams. When the periodic job has run and fetched the latest information from the website, it checks if there have been any changes and then informs all users who have subscribed to the changes.

## Open Todos
- [x] deploy bot on server 
- [ ] make the ugly code beautiful
- [ ] write a fancy logfile
- [ ] support other leagues from the same website (1. Regio, 2. Regio Ost, Nord, Damen)
- [ ] uutsource web scraping to a separated process so that the bot does not block during operation.


## Screenshots

<p float="center">
  <img src="./screenshots/IMG_2586.PNG" width="30%" />
  <img src="./screenshots/IMG_2592.PNG" width="30%" /> 
  <img src="./screenshots/IMG_2588.PNG" width="30%" />
</p>

<p float="center">
  <img src="./screenshots/IMG_2589.PNG" width="30%" />
  <img src="./screenshots/IMG_2593.PNG" width="30%" /> 
  <img src="./screenshots/IMG_2595.PNG" width="30%" />
</p>