import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import schedule
import time
import json

with open('config.json') as config_file:
    config = json.load(config_file)
    TWITTER_USERNAME = config['twitter_username']
    TWITTER_PASSWORD = config['twitter_password']


def connect_to_google_sheet(sheet_url, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/KIIT/Desktop/KIIT/MCP/service_account.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    return sheet


def fetch_tweets(sheet):
    tweets_to_post = []
    rows = sheet.get_all_records()
    for index, row in enumerate(rows):
        if row.get("Status", "").lower() != "posted":
            tweets_to_post.append({
                "content": row.get("Tweet Content", ""),
                "row_number": index + 2,
            })
    return tweets_to_post


def post_tweet(tweet_content):
    driver = webdriver.Chrome() 
    driver.get("https://twitter.com/login")
    
    time.sleep(5) 
    
    username_field = driver.find_element(By.NAME, "text")
    username_field.send_keys("TWITTER_USERNAME")
    username_field.send_keys(Keys.RETURN)
    
    time.sleep(5) 
    
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys("TWITTER_PASSWORD")
    password_field.send_keys(Keys.RETURN)
    
    time.sleep(5) 
    tweet_box = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div/div/div")  # Update this line with your new XPath
    print("found")
    tweet_box.send_keys(tweet_content)
    print("gsge")
    
    tweet_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/div/button/div/span")
    tweet_button.click()
    
    time.sleep(5) 
    driver.quit()

def update_status(sheet, row_number):
    sheet.update_cell(row_number, sheet.find("Status").col, "Posted")

def process_tweets(sheet_url, sheet_name):
    sheet = connect_to_google_sheet(sheet_url, sheet_name)
    
    tweets = fetch_tweets(sheet)
    
    for tweet in tweets:
        post_tweet(tweet['content'])
        update_status(sheet, tweet['row_number'])

def schedule_tweets(sheet_url, sheet_name):
    schedule.every(1).minutes.do(process_tweets, sheet_url=sheet_url, sheet_name=sheet_name)

if __name__ == "__main__":
    GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/d/1mtPhq9GQPkTYPhOCBDzhYeSR6xEstMyVMn6ASlcr-FM/edit?gid=0#gid=0' # Replace with your Google Sheet URL
    SHEET_NAME = 'Sheet1' 
    schedule_tweets(GOOGLE_SHEET_URL, SHEET_NAME)

    while True:
        schedule.run_pending()
        time.sleep(1)