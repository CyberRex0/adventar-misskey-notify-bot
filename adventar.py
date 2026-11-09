from libs.adventar_calendar import fetch_calendar
from classes import DummyConfig, ArgT
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

calendar, calTitle = fetch_calendar(int(CALENDAR_ID))

print(calTitle)
for date, info in calendar.items():
    print(f'12/{date}: {info["user"]} - {info["title"]} ({info["url"]})')

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
