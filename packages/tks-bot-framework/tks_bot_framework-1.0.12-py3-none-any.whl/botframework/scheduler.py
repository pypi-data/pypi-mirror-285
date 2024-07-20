# import asyncio
# import logging
# from datetime import datetime

# logger = logging.getLogger('app')


# class Scheduler:

#     def __init__(self):
#         pass

#     async def start_task(self, delay, bot_callback):
#         while True:
#             utc_now = datetime.utcnow()
#             if utc_now.hour==0 and utc_now.minute==0 and utc_now.second==0:
#                 if delay == None:
#                     pass
#                 else:
#                     await asyncio.sleep(delay*60)
#                 await bot_callback()                
#                 break

#     async def start_interval(self, interval, delay, bot_callback):
#         while True:
#             utc_now = datetime.utcnow()
#             if utc_now.hour==0 and utc_now.minute==0 and utc_now.second==0:
#                 await self.time_decision_making_interval(interval, delay, bot_callback)
#                 break

#     async def time_decision_making_interval(self, interval, delay, bot_callback):
#         while True:
#             if delay == None:
#                 pass
#             else:
#                 await asyncio.sleep(delay*60)
#             utc_now = datetime.utcnow()
#             await bot_callback()
#             # Check if more than 1 second since the end of the interval has passed; if yes, adjust the asyncio.sleep accordingly.
#             if (interval == 1 or interval == 5 or interval == 15):
#                 await asyncio.sleep(interval*60 - utc_now.second)    
#             else:
#                 await asyncio.sleep(interval*60 - (utc_now.minute*60 + utc_now.second))   


  
      
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger('app')


class Scheduler:

    def __init__(self):
        pass

    async def start_task(self, delay, bot_callback):
        logger.info("Starting task.")
        logger.info(datetime.utcnow())
        while True:
            utc_now = datetime.utcnow()
            if utc_now.second==0:
                if delay == None:
                    pass
                else:
                    await asyncio.sleep(delay*60)
                await bot_callback()                
                break

    async def start_interval(self, interval, delay, bot_callback):
        logger.info("Starting interval.")
        logger.info(datetime.utcnow())
        while True:
            utc_now = datetime.utcnow()
            if utc_now.second==0:
                await self.time_decision_making_interval(interval, delay, bot_callback)
                break

    async def time_decision_making_interval(self, interval, delay, bot_callback):
        logger.info("Starting decision making interval.")
        logger.info(datetime.utcnow())
        while True:
            if delay == None:
                pass
            else:
                await asyncio.sleep(delay*60)
            utc_now = datetime.utcnow()
            await bot_callback()
            # Check if more than 1 second since the end of the interval has passed; if yes, adjust the asyncio.sleep accordingly.
            if (interval == 1 or interval == 5 or interval == 15):
                await asyncio.sleep(interval*60 - utc_now.second)    
            else:
                await asyncio.sleep(interval*60 - (utc_now.minute*60 + utc_now.second))   


  
      
                