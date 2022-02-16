from asyncio import sleep
from threading import Thread


class BaseThread(Thread):
    async def checkException(self):
        await sleep(1)
        if self.ex:
            raise self.ex

    def run(self):
        self.ex = None
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as ex:
            self.ex = ex
        finally:
            del self._target, self._args, self._kwargs
