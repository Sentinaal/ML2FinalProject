import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

def get_team_boxscore(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "DropDown_select__4pIg9"))
        )
        dropdown.click()
        
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//option[text()='All']"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Crom_table__p1iZz"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', class_='Crom_table__p1iZz')
        if table:
            headers = [th.text.strip() for th in table.find_all('th')]
            data = []
            for tr in table.find_all('tr')[1:]:
                cells = [td.text.strip() for td in tr.find_all('td')]
                data.append(cells)

            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            return df
        else:
            print("Table not found")
    finally:
        driver.quit()


def get_player_boxscores(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        # Wait for the dropdown to be clickable and select the 'All' option
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "DropDown_select__4pIg9"))
        ).click()

        # Select the 'All' option from the dropdown (value="-1")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select.DropDown_select__4pIg9 > option[value='-1']"))
        ).click()

        # Ensure the table is updated with all entries
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Crom_table__p1iZz"))
        )

        # After the table is updated, parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', class_='Crom_table__p1iZz')

        if table:
            headers = [th.text.strip() for th in table.find_all('th')]
            data = []
            for tr in table.find_all('tr')[1:]:  # Skip the header row
                cells = [td.text.strip() for td in tr.find_all('td')]
                data.append(cells)

            # Create DataFrame from scraped data
            df = pd.DataFrame(data, columns=headers)
            return df
        else:
            print("Table not found")
    except Exception as e:
        print(f"An error occurred while fetching player box scores: {e}")
    finally:
        driver.quit()


def get_odds(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table bg-white table-hover table-bordered table-sm')
        
        if table:
            desired_headers = ["Date", "Rot", "VH", "Team", "1st", "2nd", "3rd", "4th", "Final", "Open", "Close", "ML", "2H"]
            
            rows = []
            for tr in table.find_all('tr')[1:]:
                cells = [td.text.strip() for td in tr.find_all('td')]
                if len(cells) == len(desired_headers):
                    rows.append(cells)
                else:
                    print("Row with mismatched columns:", cells)

            df = pd.DataFrame(rows, columns=desired_headers)
            return df
        else:
            print("Table not found")
    else:
        print("Failed to retrieve the webpage, status code:", response.status_code)


def split_match_up(match_up):
    if ' vs. ' in match_up:
        team, opponent = match_up.split(' vs. ')
        location = 'Home'
    elif ' @ ' in match_up:
        team, opponent = match_up.split(' @ ')
        location = 'Visitor'
    else:
        team, opponent, location = '', '', ''
    return pd.Series([team, opponent, location])



nba_url = 'https://www.nba.com/stats/teams/boxscores?Season=2018-19'
odds_url = 'https://www.sportsbookreviewsonline.com/scoresoddsarchives/nba-odds-2018-19/'
player_url = 'https://www.nba.com/stats/players/boxscores?Season=2018-19'

df1 = get_team_boxscore(nba_url)
df2 = get_odds(odds_url)
df3 = get_player_boxscores(player_url)

#chnage the coumns of df3 so that it matches this: PLAYER,TEAM,MATCH UP,GAME DATE,W/L,MIN,PTS,FGM,FGA,FG%,ThreePM,ThreePA,ThreePP,FTM,FTA,FT%,OREB,DREB,REB,AST,STL,BLK,TOV,PF,PlusMinus,FP
df3.columns = ['PLAYER','TEAM','MATCH UP','GAME DATE','WL','MIN','PTS','FGM','FGA','FGP','ThreePM','ThreePA','ThreePP','FTM','FTA','FTP','OREB','DREB','REB','AST','STL','BLK','TOV','PF','PlusMinus','FP']
df1.columns = ['Team', 'Match Up', 'Game Date', 'WL', 'MIN', 'PTS', 'FGM', 'FGA',
       'FGP', 'ThreePM', 'ThreePA', 'ThreePP', 'FTM', 'FTA', 'FTP', 'OREB', 'DREB', 'REB',
       'AST', 'STL', 'BLK', 'TOV', 'PF', 'PlusMinus']


#save to csv in the data folder
df1.to_csv('data/nba2019_boxscore.csv', index=False)
df2.to_csv('data/nba2019_odds.csv', index=False)
df3.to_csv('data/nba2019_player_boxscore.csv', index=False)


