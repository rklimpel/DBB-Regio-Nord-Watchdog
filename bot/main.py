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
from database import UserPersistenceHandler, GamePersistenceHandler, TablePersistenceHandler
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
        self.job_queue.run_repeating(self.periodic_update_checker, interval=30, first=5)

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
        await update.message.reply_text('\n'.join(TablePersistenceHandler().get_teams()))

    async def table_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        messages = commands.get_table_message()
        await self.send_messages_to_user(messages, update)

    async def team_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) == 0:
            await update.message.reply_text("Bitte gib einen Teamnamen an.")
            return
        team_name = ' '.join(context.args)
        messages = commands.get_team_games_message(team_name)
        await self.send_messages_to_user(messages, update)

    async def recent_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) > 0:
            team_name = ' '.join(context.args)
            messages = commands.get_recent_games_message(team_name)
        else:
            messages = commands.get_recent_games_message()
        await self.send_messages_to_user(messages, update)

    async def next_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) > 0:
            team_name = ' '.join(context.args)
            messages = commands.get_upcoming_games_message(team_name=team_name)
        else:
            messages = commands.get_upcoming_games_message()
        await self.send_messages_to_user(messages, update)

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
        await self.send_messages_to_user(messages, update)

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) == 0:
            await update.message.reply_text("Bitte gib einen Teamnamen an.")
            return
        messages = commands.unsubscribe(update.message.chat_id, ' '.join(context.args))
        await self.send_messages_to_user(messages, update)

    async def periodic_update_checker(self, context: ContextTypes.DEFAULT_TYPE):

        # Handle Game Updates:
        games = GameCrawler().get_all_games()
        gamePersistenceHandler = GamePersistenceHandler()
        games_up_to_date = gamePersistenceHandler.check_games_up_to_date(games)
        if not games_up_to_date:
            print("Games changed.")
            changes = gamePersistenceHandler.get_changed_games(games)
            userPersistenceHandler = UserPersistenceHandler()
            users = userPersistenceHandler.get_users()
            for user in users:
                messages = commands.get_user_subscribed_changed_games_message(changes, user)
                if len(messages) > 0:
                    for message in messages:
                        await context.bot.send_message(chat_id=user.chat_id, text=message)
            gamePersistenceHandler.update_games(games)

        # Handle Table Updates:
        table = TableCrawler().get_table()
        tablePersistenceHandler = TablePersistenceHandler()
        table_up_to_date = tablePersistenceHandler.check_table_up_to_date(table)
        if not table_up_to_date:
            print("Table changed.")
            changes = tablePersistenceHandler.get_changed_table_entries(table)
            userPersistenceHandler = UserPersistenceHandler()
            users = userPersistenceHandler.get_users()
            for user in users:
                messages = commands.get_user_subscribed_changed_table_message(changes, user)
                if len(messages) > 0:
                    for message in messages:
                        await context.bot.send_message(chat_id=user.chat_id, text=message)
            tablePersistenceHandler.update_table(table)

    async def send_messages_to_user(self, messages, update):
        for message in messages:
            await update.message.reply_text(message)

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