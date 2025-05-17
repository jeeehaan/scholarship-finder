import logging
from huey.contrib.djhuey import task

from .methods import scrape_and_insert_scholarships
logging.basicConfig(level=logging.INFO)

@task()
def scrape_scholarships():
    import asyncio
    asyncio.run(scrape_and_insert_scholarships())