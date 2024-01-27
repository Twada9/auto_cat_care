import requests
import json

from dotenv import load_dotenv
import os

class TeamsNotification:
    # 正しいチャンネルに置き換える
    WEBHOOK_URL = os.getenv('WEBHOOK_URL') 
    def notify_teams(title: str, text: str):
        requests.post(
            TeamsNotification.WEBHOOK_URL, 
            json.dumps({
                'title': title,
                'text': text,
            })
        )

    def notify_error(self, fileName: str, line: str, response: str=''):
            error_msg = 'Log: fileName: {} line: {} {}'.format(fileName, line, response)
            requests.post(
            TeamsNotification.WEBHOOK_URL, 
            json.dumps({
                'title': 'エラーが発生しました。',
                'text': error_msg
            })
        )

# crontab -eに記述
# * * * * * cd /Users/qnote/project/python/auto_cat_care; env/bin/python3.11 teams/teams_repository.py
# 0 18 * * 1　cd /Users/qnote/project/python/auto_cat_care; .env/bin/python3.11 main.py