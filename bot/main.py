from pathlib import Path
import re
import logging
import datetime
from telegram import __version__ as TG_VER
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from scraper import TableCrawler, GameCrawler

class TelegramHandler:

    def __init__(self, token: str) -> None:
        self.application = Application.builder().token(token).build()
        self.register_commands()

    def register_commands(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("teams", self.teams_command))
        self.application.add_handler(CommandHandler("tabelle", self.table_command))
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
        table_string = "Tabellenstand vom " + str(datetime.date.today().day) + "." 
        table_string += str(datetime.date.today().month) + "." + str(datetime.date.today().year) + " um " 
        table_string += str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":\n\n"
        for row in TableCrawler().get_table():
            table_string += row['position'] + ". " + row['team'] + " (" + row['points'] + ")\n"
        await update.message.reply_text(table_string)

    async def team_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        game_list = GameCrawler().crawl()
        first_10_games = game_list[:10]
        await update.message.reply_text('/n'.join(first_10_games))

    async def recent_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        game_list = GameCrawler().crawl()
        first_10_games = game_list[:10]
        await update.message.reply_text('/n'.join(first_10_games))

    async def next_games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        game_list = GameCrawler().crawl()
        first_10_games = game_list[:10]
        await update.message.reply_text('/n'.join(first_10_games))    
    

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "/teams - List all teams in the league."
            + "/games - List all games in the league."
            + "/help - Show this help message."
        )

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(update.message.text)

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