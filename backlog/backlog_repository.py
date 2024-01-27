from inspect import currentframe, getframeinfo
from pybacklogpy.Issue import Issue
from pybacklogpy.BacklogConfigure import BacklogJpConfigure
import json

from datetime import datetime
import sys
sys.path.append("./teams")
import teams_notification

from dotenv import load_dotenv
import os

class BacklogRepository:
    # ライブラリの取得と保存
    # $ pip freeze > requirements.txt
    # $ pip install -r requirements.txt

    def get_issue(self, today: datetime) -> any:
        # configをsecretsファイルから呼び出したかったけど404になるので一旦ここにハードコーディング
        load_dotenv()
        api_key = os.getenv("API_KEY")
        config = BacklogJpConfigure(space_key=os.getenv('SPACE_KEY'),
                                 api_key=os.getenv('API_KEY'))
        issue_api = Issue(config)

        d = BacklogRepository.__dateFormat(today)
        
        search_keyword = d 
        # # Y年M月D日（曜）で取得
        response = issue_api.get_issue_list(keyword=search_keyword)

        if not response.ok:
            frame = getframeinfo(currentframe())
            teams_notification.TeamsNotification().notify_error(fileName=frame.filename, line=frame.lineno, response=response.text)
            
            raise ValueError('課題 ページ情報の取得に失敗')

        decoded_issue = BacklogRepository.__decodeIssue(response)

        if decoded_issue == []:
            frame = getframeinfo(currentframe())
            teams_notification.TeamsNotification().notify_error(fileName=frame.filename, line=frame.lineno, response=search_keyword)
            
            raise ValueError('課題 ページ情報の取得に失敗')
        
        return decoded_issue

    def __decodeIssue(response) -> any:
        issue_data = json.loads(response.text)
        return issue_data
    
    def __dateFormat(date: datetime) -> str:
        d_week = {'Sun': '日', 'Mon': '月', 'Tue': '火', 'Wed': '水',
          'Thu': '木', 'Fri': '金', 'Sat': '土'}
        key = date.strftime('%a')
        w = d_week[key]
        d = date.strftime('%Y年%m月%d日') + f'（{w}曜）'
        print(d)
        return d