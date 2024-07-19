import asyncio
import nest_asyncio


nest_asyncio.apply()


class SingletonEventLoop:
    _instance = None

    @staticmethod
    def get_instance():
        if SingletonEventLoop._instance is None:
            SingletonEventLoop()
        return SingletonEventLoop._instance

    def __init__(self):
        if SingletonEventLoop._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SingletonEventLoop._instance = self
            self.loop = asyncio.get_event_loop()
            if not self.loop.is_running():
                self.loop.run_until_complete(self.initialize())

    async def initialize(self):
        # Any initialization if needed
        await asyncio.sleep(0)

    def get_loop(self):
        return self.loop
