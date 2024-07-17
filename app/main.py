from fastapi import FastAPI, status
from fastapi.responses import Response, JSONResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from rfeed import Item, Feed
from loguru import logger
from urllib.parse import urlencode
import time
import uvicorn
import yaml
import os


with open("app/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)


def get_config(param, default=None):
    if param in config['app']:
        return os.getenv(param.upper(), config['app'][param])
    elif param in config['app']['params']:
        return os.getenv(param.upper(), config['app']['params'][param])
    else:
        return default


app = FastAPI()


base_url = get_config('base_url')
max_results = int(get_config('max_results'))
start_year = get_config('start_year')
end_year = get_config('end_year')


if not base_url or not start_year or not end_year or max_results <= 0:
    logger.error("Missing mandatory configuration parameters.")
    raise ValueError("Missing mandatory configuration parameters.")


params = {
    'country_andorunique': get_config('country_andorunique'),
    'start_year': start_year,
    'end_year': end_year,
    'start_rating': get_config('start_rating'),
    'end_rating': get_config('end_rating'),
    'genrelist': get_config('genrelist'),
    'type': get_config('type'),
    'audio': get_config('audio'),
    'subtitle': get_config('subtitle'),
    'audiosubtitle_andor': get_config('audiosubtitle_andor'),
    'person': get_config('person'),
    'filterby': get_config('filterby'),
    'orderby': get_config('orderby'),
    'countrylist': get_config('countrylist'),
}

params = {k: v for k, v in params.items() if v is not None}

URL = f"{base_url}?{urlencode(params)}"
logger.info(f"Generated URL: {URL}")


@app.get("/")
async def main():
    max_attempts = 10
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    try:
        logger.debug("Starting WebDriver...")
        driver = webdriver.Chrome(options=options)
        driver.get(URL)
        time.sleep(5)
        titles = []
        logger.debug("Scraping Titles...")
        attempt = 0
        previous_count = 0
        while attempt < max_attempts:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            rendered_html = driver.page_source
            soup = BeautifulSoup(rendered_html, "html.parser")
            titles_cards_search = soup.findAll(
                "h3", attrs={"style": "font-size: 14px;margin:3px"})
            current_count = len(titles_cards_search)
            if current_count == previous_count:
                attempt += 1
            else:
                previous_count = current_count
                attempt = 0
            if current_count >= max_results:
                break

        if current_count < max_results:
            logger.info(f"Found {current_count} Titles.")

        driver.quit()
        logger.success("Titles Scrap Done!")

        if len(titles_cards_search) > 0:
            if current_count > max_results:
                titles_cards_search = titles_cards_search[:max_results]
            logger.debug("Generating RSS Feed...")
            for title_card in titles_cards_search:
                titles.append(Item(
                    title=title_card.find("span").text,
                    description=title_card.find(
                        "a").attrs["href"].split("/")[2]
                ))
            feed = Feed(
                title="uNoGS Netflix RSS",
                description="Netflix RSS Feed",
                language="en-US",
                items=titles,
                link="https://uNoGS.com/"
            )
            logger.success("RSS Feed Generated!")
            return Response(content=feed.rss(), media_type="application/xml", status_code=status.HTTP_200_OK)
        else:
            if params.get("start_year", -1) == -1:
                logger.warning(
                    '"start_year" - Must be Defined in Config.yaml file')
            logger.error("Failed to generate RSS Feed, No Titles Found.")
            return JSONResponse(content={"Error": "Failed to generate RSS Feed, No Titles Found!"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        driver.quit()
        logger.error("Failed to generate RSS Feed, Internet Connection?")
        return JSONResponse(content={"Error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8030,
                timeout_keep_alive=120)
