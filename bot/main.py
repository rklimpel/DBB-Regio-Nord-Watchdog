from pathlib import Path
import re
import logging
import datetime
import threading
from telegram import __version__ as TG_VER
from telegram import ForceReply, Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater

from scraper import TableCrawler, GameCrawler
import stringify
import commands
from database import UserPersistenceHandler, GamePersistenceHandler
from models import Game, TableEntry, User

class TelegramHandler:

    def __init__(self, token: str) -> None:
        self.application = Application.builder().token(token).build()
        self.register_commands()
        self.setup_job_queue()
        self.token = token
        self.subscribed_chat_ids = []

    def setup_job_queue(self):
        self.job_queue = self.application.job_queue
        self.job_queue.run_repeating(self.send_subscribed_games, interval=30, first=5)

    def register_commands(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("teams", self.teams_command))
        self.application.add_handler(CommandHandler("tabelle", self.table_command))
        self.application.add_handler(CommandHandler("spiele", self.team_games_command))
        self.application.add_handler(CommandHandler("letzte_spiele", self.recent_games_command))
        self.application.add_handler(CommandHandler("naechste_spiele", self.next_games_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

    def start(self) -> None:
        self.application.run_polling()

    def stop(self) -> None:
        self.application.stop()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )

    async def teams_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text('\n'.join(TableCrawler().get_teams()))

    async def table_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        table_string = "Tabellenstand vom " + stringify.current_data_time_as_string() + ":\n\n"
        for row in TableCrawler().get_table():
            table_string += row['position'] + ". " + row['team'] + " (" + row['points'] + ")\n"
        await update.message.reply_text(table_string)

    async def team_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) == 0:
            await update.message.reply_text("Bitte gib einen Teamnamen an.")
            return
        team_name = ' '.join(context.args)
        games_string = "Spiele " + team_name + ", Stand vom " + stringify.current_data_time_as_string() + ":\n\n"
        games = GameCrawler().get_all_games(team=team_name)
        for game in games:
            if game['team_home_score'] == '':
                games_string += stringify.upcoming_game_as_string(game) + "\n"
            else:
                games_string += stringify.played_game_as_string(game) + "\n"
        await update.message.reply_text(games_string)

    async def recent_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) > 0:
            team_name = ' '.join(context.args)
            game_list = GameCrawler().get_recent_games(team=team_name)
        else:
            game_list = GameCrawler().get_recent_games()
        games_string = "Letzte Spiele, Stand vom " + stringify.current_data_time_as_string() + ":\n\n"
        for game in game_list:
            games_string += stringify.played_game_as_string(game) + "\n"
        await update.message.reply_text(games_string)

    async def next_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) > 0:
            team_name = ' '.join(context.args)
            game_list = GameCrawler().get_upcoming_games(team=team_name)
        else:
            game_list = GameCrawler().get_upcoming_games()
        games_string = "Nächste Spiele, Stand vom " + stringify.current_data_time_as_string() + ":\n\n"
        for game in game_list:
            games_string += stringify.upcoming_game_as_string(game) + "\n"
        await update.message.reply_text(games_string)
    

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "/teams - List all teams in the league.\n"
            + "/tabelle - Zeigt die aktuelle Tabelle an.\n"
            + "/spiele <team> - List all games of one team.\n"
            + "/letzte_spiele - Zeigt die letzten Spiele an.\n"
            + "/naechste_spiele - Zeigt die nächsten Spiele an.\n"
            + "/help - Show this help message.\n"
        )

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(update.message.text)

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) == 0:
            await update.message.reply_text("Bitte gib einen Teamnamen an.")
            return
        messages = commands.subscribe(update.message.chat_id, update.effective_user.name, ' '.join(context.args))
        for message in messages:
             await update.message.reply_text(message)

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) == 0:
            await update.message.reply_text("Bitte gib einen Teamnamen an.")
            return
        messages = commands.unsubscribe(update.message.chat_id, ' '.join(context.args))
        for message in messages:
             await update.message.reply_text(message)

    async def send_subscribed_games(self, context: ContextTypes.DEFAULT_TYPE):
        print("periodic task")
        games = GameCrawler().get_all_games()
        gamePersistenceHandler = GamePersistenceHandler()
        games_up_to_date = gamePersistenceHandler.check_dv_up_to_date(games)
        print("Games up to date? " + str(games_up_to_date))
        if not games_up_to_date:
            print(gamePersistenceHandler.get_changed_games(games))
            gamePersistenceHandler.update_games(games)
        # database.insert_all_games(games)
        # await context.bot.send_message(chat_id='642529287', text='One message every 10 seconds')

def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    telegram_app_token = (Path('token').read_text())
    app = TelegramHandler(telegram_app_token)
    app.start()
    
    
if __name__ == "__main__":
    main()