import asyncio

class LocalQueueService:

    def __init__(self):

        self.queue = asyncio.Queue()

    async def publish(
        self,
        message: dict
    ):

        await self.queue.put(message)

    async def consume(self):

        message = await self.queue.get()

        return message


queue_service = LocalQueueService()