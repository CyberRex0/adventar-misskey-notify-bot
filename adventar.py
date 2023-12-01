from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from classes import DummyConfig, ArgT
import chromedriver_binary
import time
try:
    import config
except:
    config = DummyConfig()
from misskey import Misskey
import datetime
import argparse
import os

def getCfgFromEnv(k: str):
    return os.environ.get('ADVMI_' + k)

EOL = '\n'

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--force', action='store_true')
parser.add_argument('--force-day', type=int)
parser.add_argument('--calendar-id', type=int)
args: ArgT = parser.parse_args()

CALENDAR_ID = config.CALENDAR_ID
if args.calendar_id:
    CALENDAR_ID = args.calendar_id

# load settings from env
if getCfgFromEnv('TOKEN'):
    config.TOKEN = getCfgFromEnv('TOKEN')
if getCfgFromEnv('DOMAIN'):
    config.DOMAIN = getCfgFromEnv('DOMAIN')
if getCfgFromEnv('CALENDAR_ID'):
    CALENDAR_ID = int(getCfgFromEnv('CALENDAR_ID'))
if getCfgFromEnv('NOTE_VISIBILITY'):
    config.NOTE_VISIBILITY = getCfgFromEnv('NOTE_VISIBILITY')
if getCfgFromEnv('SHOW_YEAR'):
    config.SHOW_YEAR = getCfgFromEnv('SHOW_YEAR') in ('1', 'true', 'True')

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
        calendar[int(date)] = {'user': user, 'title': None, 'articleTitle': None, 'url': None}

# get entry list
entry_list = driver.find_element(By.CLASS_NAME, "EntryList")

entries_day = driver.find_elements(By.XPATH, "//div[@class='head']/div[@class='date']")
entries = driver.find_elements(By.XPATH, "//ul[@class='EntryList']/li[@class='item']")

for dayEl, itemEl in zip(entries_day, entries):
    date = int(dayEl.text.split('/')[1])
    t = itemEl.text
    title = None
    url = None
    articleTitle = None
    if len(t.split('\n')) >= 2:
        _x = t.split('\n')
        title = _x[1]
    try:
        linkEl = itemEl.find_element(By.XPATH, ".//div[@class='article']/div[@class='left']/div[@class='link']/a")
        url = linkEl.get_attribute('href')
    except:
        pass
    try:
        articleTitleEl = itemEl.find_element(By.XPATH, ".//div[@class='article']/div[@class='left']/div[not(@class='link')]")
        articleTitle = articleTitleEl.text.split('|', 1)[0]
    except:
        pass
    calendar[date]['articleTitle'] = articleTitle
    calendar[date]['title'] = title
    calendar[date]['url'] = url

for date, info in calendar.items():
    print(f'12/{date}: {info["user"]} - {info["title"]} ({info["url"]})')

# get caledar title
calTitleEl = driver.find_element(By.XPATH, '//header[@class="header"]/div[@class="inner"]/h2[@class="title"]')
calTitle = calTitleEl.text

driver.quit()

today = datetime.datetime.now()
today_day = today.day
if args.force:
    if args.force_day:
        today_day = args.force_day

if today.month == 12 or args.force:
    if (today_day >= 1 and today_day <= 25) or args.force:
        if calendar.get(today_day):
            if calendar[today_day]['user'] != '登録':
                entry_title = calendar[today_day]['title']
                entry_url = calendar[today_day]['url']
                entry_user = calendar[today_day]['user']
                entry_article_title = calendar[today_day]['articleTitle']
                text = f'{calTitle}{" "+str(today.year) if config.SHOW_YEAR else ""}\nDay {today_day} 「{entry_title or "(タイトル未設定)"}」 by {entry_user}\n\n{str(entry_article_title)+EOL if entry_article_title else ""}{entry_url or "(URL未設定)"+EOL+CALENDAR_URL}'
                if not args.dry_run:
                    mi.notes_create(**{
                        'text': text,
                        'visibility': config.NOTE_VISIBILITY
                    })
                else:
                    print('---DRY RUN---')
                    print(text)
