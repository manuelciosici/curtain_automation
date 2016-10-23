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
    parser = argparse.ArgumentParser(description="Manually control Somfy curtains")
    parser.add_argument("curtain", help="name of curtain to control")
    parser.add_argument("action", help="name of action to perform")
    parser.add_argument("--wd", dest="wd", help="working directory (where the config file and history are located)",
                        default="")
    args = parser.parse_args()
    if len(args.wd) > 0 and args.wd[-1] != "/":
        args.wd += "/"
    curtain = args.curtain
    action = args.action
    print("Curtain system started")
    config = Config(args.wd + "config.json")
    print(args)

    somfy = Protocol(config["credentials"]["user"], config["credentials"]["pass"])
    somfy.getSetup()
    print("Turning {0} {1}".format(curtain, action))
    action_dict = {"deviceURL": config["blinds"][curtain]["id"],
                   "commands": [{"name": action}]
                   }
    execution_id = somfy.applyActions("ManualCurtains", [Action(action_dict)])
    print("Executing ID : {0}".format(execution_id))
    print("DONE")


if __name__ == "__main__":
    main()
