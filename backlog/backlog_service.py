from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import jpholiday
from inspect import currentframe, getframeinfo
import sys
sys.path.append("backlog")
sys.path.append("./teams")
import backlog_repository
import teams_notification

# export PYTHONPATH="/Users/qnote/project/python/auto_cat_care:$PYTHONPATH" .zshrcに記入 他ディレクトリからimportできないため
# https://qiita.com/yokohama4580/items/466a483ae022d264c8ee#2-%E8%A6%AA%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E3%82%92%E7%92%B0%E5%A2%83%E5%A4%89%E6%95%B0pythonpath%E3%81%AB%E9%80%9A%E3%81%99
class BacklogService :
    TODAY: datetime
    BACKLOG_REPOSITORY: backlog_repository.BacklogRepository

    def __init__(self):
        self.TODAY: datetime = BacklogService.__get_today()
        self.BACKLOG_REPOSITORY = backlog_repository.BacklogRepository()

    def do(self):
        nearest_holiday = BacklogService.__calc_nearest_holiday(self)

        issue = self.__get_issue(nearest_holiday)
        description = issue[0]["description"]
        # 課題からそれぞれの休日と、その休日の担当者を１行ずつ分割する。
        description_list = description.splitlines()

        self.__find_holiday_assignee(description_list, nearest_holiday)

    def __get_issue(self, nearest_holiday: datetime) -> any:
        issue = self.BACKLOG_REPOSITORY.get_issue(self.TODAY)
        # 直近の休みが来月だった場合、来月分の課題を取得し再度findWeekendInを呼び出す。
        if nearest_holiday.month != self.TODAY.month:
            nextMonth = self.TODAY + relativedelta(months=1)
            nextMonthIssue = self.BACKLOG_REPOSITORY.get_issue(nextMonth)
            return nextMonthIssue
        
        return issue

    def __find_holiday_assignee(self, description_list, nearest_holiday: datetime, is_first_time: bool = True):
        # ゼロ埋めした日付でないと複数日付が取得してしまう。ex. 4日が欲しくても１の位が4であれば14、24も取得される。
        # holiday_lineはbacklogから取得した指定の日付に合致した１行　例えば|2023年06月10日（土曜）|担当者名1|担当者名2||。
        holiday_line = [s for s in description_list if nearest_holiday.strftime("%d")+'日' in s]

        print(holiday_line)

        if holiday_line == []:
            if is_first_time:
                frame = getframeinfo(currentframe())
                print("Filename:", frame.filename, "Line Number:", frame.lineno)
                teams_notification.TeamsNotification().notify_error(fileName=frame.filename, line=frame.lineno)
                raise ValueError('休日の行取得に失敗')
            else:
                return

        holiday = holiday_line[0].split("|")[1]
        has_morning_assignee = holiday_line[0].split("|")[2] == ''
        has_afternoon_assignee = holiday_line[0].split("|")[3] == ''
        print(has_afternoon_assignee)
        self.__notify_teams_on_condition(holiday, has_morning_assignee, has_afternoon_assignee)

        tomorrow = nearest_holiday + timedelta(days=1)

        # 再起で翌日の担当者を取得
        self.__find_holiday_assignee(description_list, tomorrow, False)
        return 

    def __notify_teams_on_condition(self, this_holiday, has_morning_assignee, has_afternoon_assignee):
        # 条件分岐へらせそうだけど...
        if has_afternoon_assignee and has_afternoon_assignee:
            title = '休日猫世話 ' + this_holiday
            text = '午前午後両方埋まっていません。'
            teams_notification.TeamsNotification.notify_teams(title=title, text=text)
            return
            
        elif has_morning_assignee:
            title = '休日猫世話 ' + this_holiday
            text = '午前埋まっていません。'
            teams_notification.TeamsNotification.notify_teams(title=title, text=text)
            return

        elif has_afternoon_assignee:
            title = '休日猫世話 ' + this_holiday
            text = '午後埋まっていません。'
            teams_notification.TeamsNotification.notify_teams(title=title, text=text)
            return

    def __get_today() -> datetime:
        return datetime.today()

    def __calc_nearest_holiday(self) -> datetime:
        # 週の初めの日を取得
        start_day = self.TODAY - timedelta(days=self.TODAY.weekday())

        # 祝日のリストを作成
        holidays = BacklogService.__get_holidays_in_week(self)

        # 週末の土曜日と日曜日を祝日リストに追加
        for i in range(0, 7):
            day = start_day + timedelta(days=i)
            if day.weekday() == 5 or day.weekday() == 6:
                holidays.append(day.date())

        return min(holidays)

    def __get_holidays_in_week(self) -> list[datetime]:
        # 現在の日付から1週間後の日付を計算
        week_later = self.TODAY + timedelta(days=7)

        # 1週間分の日付を取得
        dates = [self.TODAY + timedelta(days=i) for i in range(7)]
        # 祝日のリストを作成
        holidays: list[datetime] = []
        for date in dates:
            if jpholiday.is_holiday(date):
                holidays.append(date.date())
        return holidays