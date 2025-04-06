from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from typing import Union

class CalendarCallbackFactory(CallbackData, prefix="calendar"):
    act: str
    year: int
    month: int
    day: int

class CalendarMarkup:
    def __init__(self):
        self.months = {
            1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
            5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
            9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень"
        }
        self.days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

    def create_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        keyboard = []

        # Додаємо рядок з місяцем і роком
        keyboard.append([
            InlineKeyboardButton(
                text="<<",
                callback_data=CalendarCallbackFactory(
                    act="PREV-MONTH",
                    year=year,
                    month=month,
                    day=1
                ).pack()
            ),
            InlineKeyboardButton(
                text=f'{self.months[month]} {str(year)}',
                callback_data=CalendarCallbackFactory(
                    act="IGNORE",
                    year=year,
                    month=month,
                    day=1
                ).pack()
            ),
            InlineKeyboardButton(
                text=">>",
                callback_data=CalendarCallbackFactory(
                    act="NEXT-MONTH",
                    year=year,
                    month=month,
                    day=1
                ).pack()
            ),
        ])

        # Додаємо дні тижня
        keyboard.append(
            [InlineKeyboardButton(text=day, callback_data=CalendarCallbackFactory(
                act="IGNORE",
                year=year,
                month=month,
                day=1
            ).pack()) for day in self.days]
        )

        month_calendar = self._get_month_calendar(year, month)

        for week in month_calendar:
            calendar_row = []
            for day in week:
                if day == 0:
                    calendar_row.append(InlineKeyboardButton(
                        text=" ",
                        callback_data=CalendarCallbackFactory(
                            act="IGNORE",
                            year=year,
                            month=month,
                            day=day
                        ).pack()
                    ))
                else:
                    calendar_row.append(InlineKeyboardButton(
                        text=str(day),
                        callback_data=CalendarCallbackFactory(
                            act="DAY",
                            year=year,
                            month=month,
                            day=day
                        ).pack()
                    ))
            keyboard.append(calendar_row)

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def _get_month_calendar(self, year: int, month: int) -> list:
        first_day = datetime(year, month, 1)
        week_day = first_day.weekday()
        days_in_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day if month != 12 \
            else (datetime(year + 1, 1, 1) - timedelta(days=1)).day

        calendar_array = [[0 for _ in range(7)] for _ in range(6)]
        day = 1

        for week in range(6):
            for weekday in range(7):
                if week == 0 and weekday < week_day:
                    continue
                if day > days_in_month:
                    break
                calendar_array[week][weekday] = day
                day += 1

        return calendar_array
