from crawl4ai import AsyncWebCrawler
from core.ai.chroma import openai_ef
from core.ai.openai import openai
from core.ai.structured_output import ScholarshipOutput, ScholarshipList
from core.ai.prompts import SYSTEM_PROMPT
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig, ProxyConfig
from .models import Scholarship
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from chromadb import AsyncHttpClient

load_dotenv()

logger = logging.getLogger(__name__)


proxy_config = ProxyConfig(
    server=os.getenv("PROXY_SERVER"),
    username=os.getenv("PROXY_USERNAME"),
    password=os.getenv("PROXY_PASSWORD"),
)
run_config = CrawlerRunConfig(wait_for="css:body")

browser_config = BrowserConfig(proxy_config=proxy_config)

def parse_date(date_str):
    if not date_str or date_str.strip().lower() in ('', 'n/a', 'na'):
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return None

@sync_to_async
def scholarship_exists(url):
    return Scholarship.objects.filter(url=url).exists()

@sync_to_async
def create_scholarship(data):
    return Scholarship.objects.create(**data)


async def scrape_and_insert_scholarships():
    client = await AsyncHttpClient(host="localhost", port=8001)
    collection = await client.get_or_create_collection(name="scholarship_finder", embedding_function=openai_ef)
    n = 1
    while True:
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(f"https://beasiswa.id/category/beasiswa-magister/page/{n}/", config=run_config)
                logger.info(f"Scraping page {n}")
                res = openai.beta.chat.completions.parse(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": result.markdown},
                    ],
                    response_format=ScholarshipList,
                )
                response = res.choices[0].message.parsed
                '''
                coba dulu scrape 3 halaman untuk development.
                
                method yang serius: liat dulu len(response.scholarships), kalau 0 break loop
                
                if(len(response.scholarships) == 0):
                    break
                '''
                if(n == 3):
                    break
                logger.info(f"Found {len(response.scholarships)} scholarships on page {n}")
                n += 1
                
                for scholarship in response.scholarships:
                    logger.info(f"Scraping scholarship {scholarship.url}")
                    try:
                        async with AsyncWebCrawler() as crawler:
                            result = await crawler.arun(scholarship.url, config=run_config)
                            res = openai.beta.chat.completions.parse(
                                model="gpt-4.1-mini",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": SYSTEM_PROMPT,
                                    },
                                    {"role": "user", "content": result.markdown},
                                ],
                                response_format=ScholarshipOutput,
                            )
                            scholarship_data = res.choices[0].message.parsed
                            
                            if await scholarship_exists(scholarship_data.url):
                                logger.info(f"Scholarship {scholarship_data.url} already exists, skipping")
                                continue
                            
                            await create_scholarship(scholarship_data.model_dump())
                            logger.info(f"Created scholarship {scholarship_data.url}")
                            
                            await collection.add(
                                documents=[str(scholarship_data.model_dump())],
                                ids=[scholarship_data.url],
                                metadatas=[{"country": scholarship_data.country, "type": scholarship_data.type}],
                            )

                            logger.info(f"Added scholarship {scholarship_data.url} to collection")
                    except Exception as e:
                        logger.warning(f"Error parsing date for scholarship {scholarship.url}: {e}")
        except Exception as e:
            logger.error(f"Error on page {n}: {e}")
            break
        
           
              