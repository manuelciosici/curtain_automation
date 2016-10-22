from astral import Location
import datetime
from tahoma import Protocol, Action
from history import History
from config import Config
import argparse


def get_sunrise_sunset(date):
    current_location = Location(("Aarhus", "Denmark", 56.15, 10.216667, "Europe/Copenhagen", 100))
    sun_dict = current_location.sun(date=date, local=True)
    for k, v in sun_dict.items():
        sun_dict[k] = v.replace(tzinfo=None)
    return sun_dict


def main():
    parser = argparse.ArgumentParser(description="Automatically control Somfy curtains based on Sun and preferences")
    parser.add_argument("--wd", dest="wd", help="working directory (where the config file and history are located)", default="")
    args = parser.parse_args()
    if len(args.wd) > 0 and args.wd[-1] != "/":
        args.wd += "/"
    print("Curtain system started")
    print("Config is ")
    config = Config(args.wd + "config.json")
    print(config)
    history = History(args.wd + "history.json")
    now = datetime.datetime.now()
    sun_times = get_sunrise_sunset(now)
    somfy = Protocol(config["credentials"]["user"], config["credentials"]["pass"])
    somfy.getSetup()
    actions_to_execute = []
    for blind, settings in config["blinds"].items():
        for action, values in settings["actions"].items():
            time_min = values["min_time"]
            time_max = values["max_time"]

            last_action_date = history.get_last_action_time(settings["id"], action)
            if time_min <= now <= time_max:
                if last_action_date < time_min:
                    execute = True
                    if values["raise_by_sun"]:
                        reference_time = sun_times[values["sun_time"]]
                        if time_min <= reference_time <= time_max:
                            if now >= reference_time:
                                execute = True
                            else:
                                execute = False
                                message = "Time qualifies{0}, but not Sun time yet{1}"
                                print(message.format(now, reference_time))
                        elif reference_time < time_min:
                            # curtains should be operated immediately after min_time if
                            # the sun time is before min_time
                            execute = True
                        elif reference_time > time_max and (time_max - now).total_seconds() > 120:
                            execute = False
                            message = "Time ({0}) is good, sun ({1}) is good. Will wait until closet to time_max ({2})"
                            print(message.format(now, reference_time, time_max))
                    if execute:
                        s = "Blinds {0} (id {2}) should be {1}"
                        print(s.format(blind, action, settings["id"]))
                        action_dict = {"deviceURL": settings["id"],
                                       "commands": [{"name": action}]
                                       }
                        actions_to_execute.append(Action(action_dict))
                else:
                    message = "({2}) Time qualifies, but last run date ({0}) is after min ({1})"
                    print(message.format(last_action_date, time_min, action))
    if len(actions_to_execute) > 0:
        print("Executing {0} actions".format(len(actions_to_execute)))
        id = somfy.applyActions("AutoCurtains", actions_to_execute)
        print("Executing ID : {0}".format(id))
        for a in actions_to_execute:
            device_id = a.deviceURL
            action_name = a.commands[0].name
            history.set_last_action_time(device_id, action_name, now)
            history.save()
    else:
        print("Nothing to do")

    print("DONE")


if __name__ == "__main__":
    main()
