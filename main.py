#!/usr/bin/python3

from asyncio import get_event_loop as loop

from bot_instance import BotInstance

if __name__ == "__main__":
    client = BotInstance(loop())
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
