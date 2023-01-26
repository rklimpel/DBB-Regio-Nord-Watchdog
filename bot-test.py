import logging
from pathlib import Path
from telegram import __version__ as TG_VER
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import time

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TableCrawler():

    url = "https://www.basketball-bund.net/static/#/liga/36563/tabelle"

    def get_teams(self):

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        # Start the webdriver
        driver = webdriver.Chrome(options=options)

        # Navigate to the webpage
        driver.get(self.url)

        # Find and click on the button with the text "AKZEPTIEREN"
        try:
            button = driver.find_element(By.XPATH, "//button[contains(text(), 'AKZEPTIEREN')]")
            button.click()
        except:
            print("There is no accept button to click.")

        # Wait for the page to load
        time.sleep(1)

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")

        # Find all rows in the table
        rows = table.find_all("tr")

        teams = []
        # Iterate over the rows and extract the data
        for row in rows:
                cells = row.find_all("td")
                data = []
                for cell in cells:
                    data.append(re.sub(r'[^\x00-\x7F]+', ' ', cell.text).lstrip().rstrip())
                if len(data) > 1:
                    teams.append(data[1])

        # Close the webdriver
        driver.quit()

        return teams


class GameCrawler():

    url = "https://www.basketball-bund.net/static/#/liga/36563/spielplan"

    def crawl(self):

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        # Start the webdriver
        driver = webdriver.Chrome(options=options)

        # Navigate to the webpage
        driver.get(self.url)

        # Find and click on the button with the text "AKZEPTIEREN"
        try:
            button = driver.find_element(By.XPATH, "//button[contains(text(), 'AKZEPTIEREN')]")
            button.click()
        except:
            print("There is no accept button to click.")

        # Wait for the page to load
        time.sleep(1)

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")

        # Find all rows in the table
        rows = table.find_all("tr")

        # Iterate over the rows and extract the data
        for row in rows:
            cells = row.find_all("td")
            data = []
            for cell in cells:
                data.append(re.sub(r'[^\x00-\x7F]+', ' ', cell.text).lstrip().rstrip())
            print(data)

        # Close the webdriver
        driver.quit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def teams_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('\n'.join(TableCrawler().get_teams()))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

def main() -> None:
    application = Application.builder().token(Path('token').read_text()).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("teams", teams_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()


if __name__ == "__main__":
    main()