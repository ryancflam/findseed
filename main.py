#!/usr/bin/python3

from asyncio import get_event_loop as loop

import info
from other_utils.bot import Bot
from other_utils.funcs import getPath

client = Bot(
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
