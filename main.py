import asyncio
import datetime
import logging
import random

import vlc
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-25s %(levelname)-8s %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Часы работы таски с и до часов
work_hour_schedule = {
    0: (10, 22),
    1: (10, 22),
    2: (10, 22),
    3: (10, 22),
    4: (10, 22),
    5: (11, 22),
    6: (11, 22),
}

# День работы таски
weekday = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

sounds = [
    "clock_cuckoo_strike_1_broke.mp3",
    "clock_cuckoo_strike_1.mp3",
    "train_choo_choo.mp3",
    "train_choo.mp3",
]  # Список проигрываемых звуков


class CuckooClock:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def run(self):
        """Запускает Кукушку в работу."""

        logger.info("Start CuckooClock")
        self.scheduler.start()  # Запускаем scheduler

        # Создаем начальное расписание и заполняем его
        self.add_tasks_to_scheduler()
        self.scheduler.add_job(
            func=self.add_tasks_to_scheduler, trigger="cron", hour=0, minute=1
        )  # Запускаем повтор заполнения расписания каждый день в 00:01

        # Тест интервальной таски
        self.scheduler.add_job(
            func=self.interval_task,
            trigger="interval",
            args=["*this is text*"],
            seconds=10,
        )

        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stop CuckooClock")

    def add_tasks_to_scheduler(self) -> None:
        """Создает начальное расписание и заполняем его основной таской"""

        logger.info("Add general task to scheduler")
        tasks_time = self.get_start_task_hours()
        for time in tasks_time:
            self.scheduler.add_job(
                func=self.general_task,
                trigger="date",
                args=["test text"],
                run_date=time,
                id=str(time.time()),
            )
        logger.debug(self.scheduler.print_jobs())

    @staticmethod
    def get_start_task_hours() -> list[datetime.datetime]:
        """
        Возвращает список со временем запуска задач
        :return: список со временем запуска задач
        """
        today_datetime = datetime.datetime.now()

        # Создаем список из времени запуска задачи
        tasks_time = []
        today_weekday = today_datetime.weekday()
        start_hour = work_hour_schedule[today_weekday][0]
        end_hour = work_hour_schedule[today_weekday][1]
        for hour in range(start_hour, end_hour + 1):
            tsk_time = datetime.datetime.combine(
                date=today_datetime.date(), time=datetime.time(hour=hour, minute=0)
            )
            # Добавляем если задача будет в будущем
            tasks_time.append(tsk_time) if tsk_time > today_datetime else None
        return tasks_time

    def general_task(self, text=None):
        """Основаная таска."""

        logger.debug(f"General task: {text}")
        self.make_sound()

    def interval_task(self, text=None) -> None:
        """Интервальная таска."""

        logger.info(f"Interval task: {text}")
        self.make_sound()

    @staticmethod
    def make_sound():
        """Воспроизводит звук."""

        filename = f"audio/{random.choice(sounds)}"
        p = vlc.MediaPlayer(filename)
        p.play()


if __name__ == "__main__":
    cuckoo_clock = CuckooClock()
    cuckoo_clock.run()
