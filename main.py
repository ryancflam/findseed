#!/usr/bin/python3

from os import path, makedirs
from sys import exit
from time import time
from asyncio import get_event_loop as loop

from bot import Bot
from other_utils.funcs import getPath, generateJson

try:
    import config
except ModuleNotFoundError:
    f = open(f"{getPath()}/config.py", "w")
    template = open(f"{getPath()}/config.py.template", "r")
    f.write(template.read())
    template.close()
    f.close()
    print("Generated file 'config.py', please modify it before using.")
    exit()


def generateFiles():
    if not path.exists(f"{getPath()}/data"):
        makedirs(f"{getPath()}/data")
        print("Generated directory 'data'.")
    generateJson("blacklist", {"servers": [], "users": []})
    generateJson("dream", {"iteration": 0, "mostPearls": 0, "mostRods": 0})
    generateJson(
        "findseed", {
            "calls": 0,
            "highest": {
                "found": 0,
                "number": 0,
                "time": int(time())
            }
        }
    )


def botInstance():
    generateFiles()
    return Bot(
        loop=loop(),
        prefix="b" * (not config.production) + config.prefix,
        path=getPath(),
        token=config.botToken,
        activity={
            "name": config.activityName,
            "type": config.activityType,
            "status": config.status
        }
    )


if __name__ == "__main__":
    client = botInstance()
    try:
        task = loop().create_task(client.startup())
        loop().run_until_complete(task)
        loop().run_forever()
    except (KeyboardInterrupt, RuntimeError):
        print(f"Shutting down - {client.kill()}")
    except Exception as ex:
        print(f"Error - {ex}")
    finally:
        loop().close()
