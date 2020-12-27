#!/usr/bin/python3

from os import path, makedirs
from json import dump
from time import time
from asyncio import get_event_loop as loop

import config
from bot import Bot
from other_utils.funcs import getPath


def generateJson():
    if not path.exists(f"{getPath()}/data"):
        makedirs(f"{getPath()}/data")
        print("Generated directory 'data'")
    if not path.exists(f"{getPath()}/data/blacklist.json"):
        f = open(f"{getPath()}/data/blacklist.json", "w")
        dump({"servers": [], "users": []}, f, sort_keys=True, indent=4)
        f.close()
        print("Generated file 'blacklist.json'")
    if not path.exists(f"{getPath()}/data/findseed.json"):
        f = open(f"{getPath()}/data/findseed.json", "w")
        dump({
            "calls": 0,
            "highest": {
                "found": 0,
                "number": 0,
                "time": int(time())
            }
        }, f, sort_keys=True, indent=4)
        f.close()
        print("Generated file 'findseed.json'")


def botInstance():
    generateJson()
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
