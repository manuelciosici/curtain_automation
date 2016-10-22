import json
import datetime
import copy


class History:
    __file_name = ""
    __all_history = {}

    def __init__(self, file_name):
        self.__file_name = file_name
        self.__get_history()

    def __get_history(self):
        try:
            self.__all_history = json.load(open(self.__file_name, "rt"))
            for blind, history in self.__all_history.items():
                for command, time_value in history.items():
                    d = datetime.datetime.strptime(time_value, "%Y%m%d %H:%M")
                    history[command] = d
        except FileNotFoundError:
            print("File {} does not exist. Will load empty history".format(self.__file_name))

    def save(self):
        history_to_save = copy.deepcopy(self.__all_history)
        for blind, history in history_to_save.items():
            for command, time_value in history.items():
                history[command] = time_value.strftime("%Y%m%d %H:%M")
        json.dump(history_to_save, open(self.__file_name, 'wt'), indent=2)

    def get_last_action_time(self, blind_id, action):
        last_action_date = datetime.datetime(year=1900, month=1, day=1)
        if blind_id in self.__all_history.keys():
            if action in self.__all_history[blind_id].keys():
                last_action_date = self.__all_history[blind_id][action]
        return last_action_date

    def set_last_action_time(self, blind_id, action, time):
        if blind_id not in self.__all_history.keys():
            self.__all_history[blind_id] = {}
        self.__all_history[blind_id][action] = time
        self.save()
