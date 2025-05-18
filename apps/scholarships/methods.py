from crawl4ai import AsyncWebCrawler, CacheMode
from core.ai.chroma import openai_ef
from core.ai.structured_output import ScholarshipDetail, ScholarshipList
from core.ai.prompts import SYSTEM_PROMPT
from core.ai.prompt_manager import PromptManager
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig, ProxyConfig
from .models import Scholarship
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from chromadb import AsyncHttpClient, HttpClient
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()

logger = logging.getLogger(__name__)


def parse_date(date_str):
    if date_str == "N/A" or not date_str:
        return None

    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        logger.error(f"Unexpected date format: {date_str}")
        return None


@sync_to_async
def scholarship_exists(url):
    return Scholarship.objects.filter(source_url=url).exists()


@sync_to_async
def create_scholarship(data):
    return Scholarship.objects.create(**data)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def scrape_and_insert_scholarships():
    proxy_config = ProxyConfig(
        server=os.getenv("PROXY_SERVER"),
        username=os.getenv("PROXY_USERNAME"),
        password=os.getenv("PROXY_PASSWORD"),
    )
    run_config = CrawlerRunConfig(
        wait_for="css:body",
        magic=True,
        cache_mode=CacheMode.BYPASS,
        simulate_user=True,
        override_navigator=True,
    )
    browser_config = BrowserConfig(proxy_config=proxy_config)
    client = await AsyncHttpClient(host="localhost", port=8001)
    collection = await client.get_or_create_collection(name="scholarship_finder", embedding_function=openai_ef)
    p = PromptManager()

    max_limit = 2
    n = 1
    while True:
        if n == max_limit:
            break

        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    f"https://opportunitiescorners.com/category/scholarships-in-europe/page/{n}/",
                    config=run_config,
                )
                
                messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": result.markdown},
                ]
                
                p.set_messages(messages)
                response = p.generate_structured(ScholarshipList)
                logger.info(f"Found {len(response.scholarships)} scholarships")

                if len(response.scholarships) == 0:
                    logger.info("No scholarships found")
                    continue

                for r in response.scholarships:
                    if await scholarship_exists(r.url):
                        logger.info(f"Scholarship {r.url} already exists, skipping")
                        continue
                    try:               
                        async with AsyncWebCrawler() as crawler:
                            logger.info(f"Scraping {r.url}")
                            scrape = await crawler.arun(r.url, config=run_config)
                            messages=[
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": scrape.markdown},
                            ]
                            p.set_messages(messages)
                            scholarship_data = p.generate_structured(ScholarshipDetail)
                            
                            if not scholarship_data:
                                logger.info(f"Failed to scrape {r.url}, skipping")
                                continue
                                
                            cleaned_data = {
                                "title": scholarship_data.title,
                                "description": scholarship_data.description,
                                "degree": scholarship_data.degree,
                                "deadline": parse_date(scholarship_data.deadline),
                                "registration_start_date": parse_date(scholarship_data.registration_start_date),
                                "country": scholarship_data.country,
                                "type": scholarship_data.type,
                                "benefits": scholarship_data.benefits,
                                "requirements": scholarship_data.requirements,
                                "official_url": scholarship_data.url,
                                "source_url": r.url
                            }
                                
                            saved_scholarship = await create_scholarship(cleaned_data)
                            logger.info(f"Scholarship {cleaned_data['source_url']} successfully inserted to Postgres")
                            
                            doc_string = (
                                    f"Title: {cleaned_data['title']}, "
                                    f"Description: {cleaned_data['description']}, "
                                    f"Degree: {cleaned_data['degree']}, "
                                    f"Deadline: {cleaned_data['deadline']}, "
                                    f"Registration Start Date: {cleaned_data['registration_start_date']}, "
                                    f"Country: {cleaned_data['country']}, "
                                    f"Type: {cleaned_data['type']}, "
                                    f"Benefits: {', '.join(cleaned_data['benefits']) if cleaned_data['benefits'] else 'None'}, "
                                    f"Requirements: {', '.join(cleaned_data['requirements']) if cleaned_data['requirements'] else 'None'}, "
                                    f"Official URL: {cleaned_data['official_url']}"
                                    f"Source URL: {cleaned_data['source_url']}"
                            )
                            await collection.add(
                                documents=[doc_string],
                                ids=[saved_scholarship.id],
                                metadatas=[{"id": saved_scholarship.id, "country": saved_scholarship.country, "type": saved_scholarship.type, "degree": saved_scholarship.degree}],
                            )
                            logger.info(f"Scholarship {cleaned_data['source_url']} successfully inserted to Chroma")
                            
                    except Exception as e:
                        logger.error(f"Failed to process {r.url}: {e}")
                        continue
                n += 1
        except Exception as e:
            logger.error(f"Failed to process page {n}: {e}")
            continue



def query_search(query):
    client = HttpClient(host="localhost", port=8001)
    collection = client.get_collection(name="scholarship_finder", embedding_function=openai_ef)
    results = collection.query(
        query_texts=[query],
        n_results=3,
    )
    search_results = []
    for metadata in results["metadatas"][0]:
        scholarship = Scholarship.objects.get(id=metadata["id"])
        search_results.append(
            {
                "id": scholarship.id,
                "title": scholarship.title,
                "degree": scholarship.degree,
                "deadline": scholarship.deadline,
                "country": scholarship.country,
                "type": scholarship.type,
            }
        )
    return search_results