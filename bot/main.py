from pathlib import Path
import re
import logging
import datetime
import threading
from telegram import __version__ as TG_VER
from telegram import *
from telegram.ext import *
from typing import Union, List

from scraper import TableCrawler, GameCrawler
import stringify
import commands
from database import UserPersistenceHandler, GamePersistenceHandler, TablePersistenceHandler
from models import Game, TableEntry, User

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramHandler:

    def __init__(self, token: str) -> None:
        self.application = Application.builder().token(token).build()
        self.register_commands()
        self.setup_job_queue()
        self.token = token
        self.subscribed_chat_ids = []

    def setup_job_queue(self):
        self.job_queue = self.application.job_queue
        self.job_queue.run_repeating(self.periodic_update_checker, interval=900, first=30)

    def register_commands(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("hilfe", self.help_command))
        self.application.add_handler(CommandHandler("teams", self.teams_command))
        self.application.add_handler(CommandHandler("tabelle", self.table_command))
        self.application.add_handler(CommandHandler("team_spiele", self.team_games_command))
        self.application.add_handler(CommandHandler("team_letzte_spiele", self.team_recent_games_command))
        self.application.add_handler(CommandHandler("team_naechste_spiele", self.team_next_games_command))
        self.application.add_handler(CommandHandler("letzte_spiele", self.recent_games_command))
        self.application.add_handler(CommandHandler("naechste_spiele", self.next_games_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.application.add_handler(CallbackQueryHandler(self.button_pressed))
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
        await self.send_messages_to_user(messages, context, update)

    async def team_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        teams = TablePersistenceHandler().get_teams()
        await self.show_selection_buttons(
            update,
            "Wähle ein Team aus, dessen Spiele du sehen möchtest:",
            teams,
            "team_spiele"
        )

    async def team_recent_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        teams = TablePersistenceHandler().get_teams()
        await self.show_selection_buttons(
            update,
            "Wähle ein Team aus, dessen letzten Spielergebnisse du sehen möchtest:",
            teams,
            "team_letzte_spiele"
        )

    async def team_next_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        teams = TablePersistenceHandler().get_teams()
        await self.show_selection_buttons(
            update,
            "Wähle ein Team aus, dessen nächsten Spiele du sehen möchtest:",
            teams,
            "team_naechste_spiele"
        )

    async def recent_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) > 0:
            team_name = ' '.join(context.args)
            messages = commands.get_recent_games_message(team_name)
        else:
            messages = commands.get_recent_games_message()
        await self.send_messages_to_user(messages, context, update)

    async def next_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if len(context.args) > 0:
            team_name = ' '.join(context.args)
            messages = commands.get_upcoming_games_message(team_name=team_name)
        else:
            messages = commands.get_upcoming_games_message()
        await self.send_messages_to_user(messages, context, update)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        help_text = Path('help.txt').read_text()
        await update.message.reply_text(help_text)

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(update.message.text)

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        teams = TablePersistenceHandler().get_teams()
        teams = ["all"] + teams 
        await self.show_selection_buttons(
            update, 
            "Wähle ein Team aus, für das du Benachrichtigungen bekommen möchtest:",
            teams, 
            "subscribe"
        )

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = UserPersistenceHandler().get_user_by_chat_id(chat_id=update.message.chat_id)
        subscribed_teams = user.subscribed_teams
        subscribed_teams = ["all"] + subscribed_teams 
        await self.show_selection_buttons(
            update, 
            "Wähle ein Team aus, für das du die Benachrichtigungen deaktivieren möchtest:", 
            subscribed_teams,
            "unsubscribe"
        )

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

    async def show_selection_buttons(self, update: Update, text, select_options, callback_str: str) -> None:
        keyboard = []
        for option in select_options:
            keyboard.append([InlineKeyboardButton(option, callback_data=callback_str + "#" + option)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    async def button_pressed(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        callback_str, callback_data = query.data.split("#")

        if callback_str == "subscribe":
            messages = commands.subscribe(update.effective_chat.id, update.effective_user.name, callback_data)
            await self.send_messages_to_user(messages, context, update)
        elif callback_str == "unsubscribe":
            messages = commands.unsubscribe(update.effective_chat.id, callback_data)
            await self.send_messages_to_user(messages, context, update)
        elif callback_str == "team_naechste_spiele":
            messages = commands.get_upcoming_games_message(team_name=callback_data)
            await self.send_messages_to_user(messages, context, update)
        elif callback_str == "team_letzte_spiele":
            messages = commands.get_recent_games_message(team_name=callback_data)
            await self.send_messages_to_user(messages, context, update)
        elif callback_str == "team_spiele":
            messages = commands.get_team_games_message(team_name=callback_data)
            await self.send_messages_to_user(messages, context, update)
        # await query.edit_message_text(text=f"Selected option: {query.data}")

    async def send_messages_to_user(self, messages, context, update):
        for message in messages:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main() -> None:
    telegram_app_token = Path('token').read_text()
    app = TelegramHandler(telegram_app_token)
    app.start()
    
if __name__ == "__main__":
    main()