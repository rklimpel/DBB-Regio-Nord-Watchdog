from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


class DBBRegioCrawler():

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-dev-shm-usage') 
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def handle_possible_accept_button(self):
        try:
            button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'AKZEPTIEREN')]")
            button.click()
        except:
            print("There is no accept button to click.")

    def read_webpage(self, url):
        self.driver.get(self.url)
        time.sleep(0.1)
        self.handle_possible_accept_button()
        time.sleep(0.1)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()
        return soup

    def read_table_from_page(self, url):
        soup = self.read_webpage(self.url)
        table = soup.find("table")
        rows = table.find_all("tr")
        table_data = []
        for row in rows:
            row_data = []
            cells = row.find_all("td")
            for cell in cells:
                row_data.append(cell.text.lstrip().rstrip().replace("\xa0",""))
            table_data.append(row_data)
        table_data = [row for row in table_data if row]
        return table_data

class TableCrawler(DBBRegioCrawler):

    url = "https://www.basketball-bund.net/static/#/liga/36563/tabelle"

    def get_teams(self):
        table_data = self.read_table_from_page(self.url)
        teams = [row[1] for row in table_data]
        teams.sort()
        return teams

    def get_table(self):
        table_data = self.read_table_from_page(self.url)
        standings = []
        for row in table_data:
            standings.append({
                "position": row[0],
                "team": row[1],
                "games": row[2],
                "wins": row[3],
                "loses": row[4],
                "points": str(int(row[5].split(":")[0]) - int(row[5].split(":")[1])),
                "points_made": row[5].split(":")[0],
                "points_against": row[5].split(":")[1],
                "points_difference": str(int(row[6].split(":")[0]) - int(row[6].split(":")[1])),
            })
        return standings

class GameCrawler(DBBRegioCrawler):

    url = "https://www.basketball-bund.net/static/#/liga/36563/spielplan"

    def get_all_games(self):

        def remove_duplicated_teams(game):
            if game[2] in game[4] and game[4].replace(game[2],"") != "":
                game[4] = game[4].replace(game[2], "")
            elif game[4] in game[2] and game[2].replace(game[4],"") != "":
                game[2] = game[2].replace(game[4], "")
            return game

        games = self.read_table_from_page(self.url)
        pretty_games = []
        for game in games:
            print(game)
            if len(game) > 1:
                remove_duplicated_teams(game)
                pretty_games.append({
                    "date": game[0].split(" ")[0],
                    "time": game[0].split(" ")[1],
                    "id": game[1],
                    "team_home": game[2],
                    "team_away": game[4],
                    "team_home_score": game[3].split(":")[0].lstrip().rstrip(),
                    "team_away_score": game[3].split(":")[1].lstrip().rstrip(),
                })
        return pretty_games

    def get_recent_games(self, count=10):
        games = self.get_all_games()
        for i, game in enumerate(games):
            if game["team_home_score"] == "" and game["team_away_score"] == "":
                games = games[:i]
                break
        games = games[-count:]
        games.reverse()
        return games

    def get_upcoming_games(self, count=10):
        games = self.get_all_games()
        for i, game in enumerate(games):
            if game["team_home_score"] == "" and game["team_away_score"] == "":
                games = games[i:]
                break
        return games[:count]