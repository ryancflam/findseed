from asyncio import new_event_loop as loop
from logging import StreamHandler, getLogger
from sys import stdout

from src.bot_instance import BotInstance


def main():
    handler = StreamHandler(stream=stdout)
    handler.setLevel(20)
    getLogger().addHandler(handler)
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


if __name__ == "__main__":
    main()
