# проигрывать звук
# двигать кукуху

# озвучивать голосом
# принимать команды

# железо
# Orange Pi Zero LTS
# http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-LTS.html

import vlc
import random
import logging
import datetime
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.blocking import BlockingScheduler

# Включаем логирование. Пишем логи в файл cuckoo_clock.log
rfh = RotatingFileHandler(
    filename="cuckoo_clock.log",
    mode="a",
    maxBytes=1*1024*1024,
    backupCount=2,
    encoding=None,
    delay=0
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-25s %(levelname)-8s %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    handlers=[
        rfh
    ]
)
logger = logging.getLogger(__name__)

sounds = [
    "clock_cuckoo_strike_1_broke.mp3",
    "clock_cuckoo_strike_1.mp3",
    "train_choo_choo.mp3",
    "train_choo.mp3",
]

# Час срабатывания таски
work_hour_schedule = {
    0: (10, 22),
    1: (10, 22),
    2: (10, 22),
    3: (10, 22),
    4: (10, 22),
    5: (11, 22),
    6: (11, 22),
}

# День срабатывания таски
weekday = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

# Тип планировщика
scheduler = BlockingScheduler()


def some_job(text=None):
    print(f"Do job: {text}")
    logger.debug(f"Do job: {text}")


def get_start_task_hours() -> list[datetime.datetime]:
    """
    Возвращает список с временем запуска задач

    """
    today_datetime = datetime.datetime.now()

    # Создаем список из времени запуска задачи
    task_time = []
    today_weekday = today_datetime.weekday()
    start_hour = work_hour_schedule[today_weekday][0]
    end_hour = work_hour_schedule[today_weekday][1]
    for hour in range(start_hour, end_hour + 1):
        tsk_time = datetime.datetime.combine(
            today_datetime.date(),
            datetime.time(hour, 0)
        )
        # Добавляем если задача будет в будущем
        if tsk_time > today_datetime:
            task_time.append(tsk_time)

    print("Time to start tasks:")
    [print(task) for task in task_time]
    return task_time


def add_tasks_to_scheduler() -> None:
    """Создаем начальное расписание и заполняем его"""
    logger.info("Added tasks time to scheduler")
    tasks_time = get_start_task_hours()
    for time in tasks_time:
        scheduler.add_job(
            some_job,
            'date',
            ["test text"],
            run_date=time,
            id=str(time.time())
        )
    logger.debug(scheduler.print_jobs())


def make_sound(text=None) -> None:
    """Воспроизводит звук"""
    print(f"Cuckoo-Cuckoo {text}")
    logger.info(f"Make sound Cuckoo-Cuckoo {text}")
    filename = f"audio/{random.choice(sounds)}"
    p = vlc.MediaPlayer(filename)
    p.play()


def run__scheduler():
    """Запускаем Кукушку в работу"""

    # Создаем начальное расписание и заполняем его
    add_tasks_to_scheduler()

    # Запускаем повтор заполнения расписания в 00:01
    scheduler.add_job(add_tasks_to_scheduler, 'cron', hour=0, minute=1)

    scheduler.add_job(make_sound, 'interval', ["test text"], seconds=10)

    # Запускаем scheduler
    logger.info("Start scheduler")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    run__scheduler()
