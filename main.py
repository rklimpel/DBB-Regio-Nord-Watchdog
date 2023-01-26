from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import time


class TableCrawler():

    url = "https://www.basketball-bund.net/static/#/liga/36563/tabelle"

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


def main():
    print("Welcome to the Basketball Regionalliga Nord Watchdog!")
    TableCrawler().crawl();
    GameCrawler().crawl();

if __name__ == "__main__":
    main()