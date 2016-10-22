import json
import datetime


class Config:
    __file_name = ""
    __config = {}

    def __init__(self, file_name):
        self.__file_name = file_name
        self.__get_config()

    def __get_config(self):
        self.__config = json.load(open(self.__file_name))
        today = datetime.date.today()
        for blind, settings in self.__config["blinds"].items():
            for event, values in settings["actions"].items():
                min_time = list(map(int, values["min_time"].split(":")))
                values["min_time"] = datetime.datetime(year=today.year,
                                                       month=today.month,
                                                       day=today.day,
                                                       hour=min_time[0],
                                                       minute=min_time[1])
                max_time = list(map(int, values["max_time"].split(":")))
                values["max_time"] = datetime.datetime(year=today.year,
                                                       month=today.month,
                                                       day=today.day,
                                                       hour=max_time[0],
                                                       minute=max_time[1])

    def __getitem__(self, index):
        return self.__config[index]

    def __str__(self):
        return str(self.__config)
