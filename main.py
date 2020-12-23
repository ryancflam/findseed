#!/usr/bin/python3

from os import path
from json import dump
from time import time
from asyncio import get_event_loop as loop

import info
from bot import Bot
from other_utils.funcs import getPath


def generateJson():
    if not path.exists(f"{getPath()}/blacklist.json"):
        f = open(f"{getPath()}/blacklist.json", "w")
        dump({"servers": [], "users": []}, f, sort_keys=True, indent=4)
        f.close()
    if not path.exists(f"{getPath()}/data.json"):
        f = open(f"{getPath()}/data.json", "w")
        dump({
            "calls": 0,
            "highest": {
                "found": 0,
                "number": 0,
                "time": int(time())
            }
        }, f, sort_keys=True, indent=4)
        f.close()


def generateClient():
    return Bot(
        loop=loop(),
        prefix="b" * (not info.production) + info.prefix,
        path=getPath(),
        token=info.botToken,
        activity={
            "name": info.activityName,
            "type": info.activityType,
            "status": info.status
        }
    )


if __name__ == "__main__":
    generateJson()
    client = generateClient()
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
