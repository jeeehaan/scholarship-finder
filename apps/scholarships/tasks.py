import logging
from huey import crontab
from huey.contrib.djhuey import periodic_task

from .methods import scrape_and_insert_scholarships
logging.basicConfig(level=logging.INFO)

@periodic_task(crontab(hour=15, minute=0))
def scrape_scholarships():
    import asyncio
    asyncio.run(scrape_and_insert_scholarships())