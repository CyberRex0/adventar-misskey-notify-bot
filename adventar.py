from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_binary
import time
import config
from misskey import Misskey
import datetime

EOL = '\n'

CALENDAR_ID = config.CALENDAR_ID
CALENDAR_URL = f"https://adventar.org/calendars/{CALENDAR_ID}"

mi = Misskey(i=config.TOKEN, address=config.DOMAIN)

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = Chrome(options=options)

# wait to load explicitly
driver.get(CALENDAR_URL)
time.sleep(6)

calendar = {}

# get calendar
days = driver.find_elements(By.CLASS_NAME, "cell")
for day in days:
    try:
        inner = day.find_element(By.CLASS_NAME, "inner")
    except:
        continue
    if len(inner.text.split('\n')) == 2:
        date, user = inner.text.split('\n')
        calendar[int(date)] = {'user': user}

# get entry list
entry_list = driver.find_element(By.CLASS_NAME, "EntryList")

entries_day = driver.find_elements(By.XPATH, "//div[@class='head']/div[@class='date']")
entries = driver.find_elements(By.XPATH, "//ul[@class='EntryList']/li[@class='item']")

for dayEl, itemEl in zip(entries_day, entries):
    date = int(dayEl.text.split('/')[1])
    t = itemEl.text
    title = None
    url = None
    if len(t.split('\n')) >= 2:
        _x = t.split('\n')
        title = _x[1]
    try:
        linkEl = itemEl.find_element(By.XPATH, ".//div[@class='article']/div[@class='left']/div[@class='link']/a")
        url = linkEl.get_attribute('href')
    except:
        pass
    calendar[date]['title'] = title
    calendar[date]['url'] = url

for date, info in calendar.items():
    print(f'12/{date}: {info["user"]} - {info["title"]} ({info["url"]})')

driver.quit()

today = datetime.datetime.now()
if today.month == 12:
    if today.day >= 1 and today.day <= 25:
        if calendar.get(today.day):
            if calendar[today.day]['user'] != '登録':
                entry_title = calendar[today.day]['title']
                entry_url = calendar[today.day]['url']
                entry_user = calendar[today.day]['user']
                mi.notes_create(**{
                    'text': f'Misskey Advent Calendar {today.year}\nDay {today.day} 「{entry_title or "(タイトル未設定)"}」 by {entry_user}\n{entry_url or "(URL未設定)"+EOL+CALENDAR_URL}',
                    'visibility': config.NOTE_VISIBILITY
                })