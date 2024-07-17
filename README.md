# uNoGS RSS Feed

Generate Custom RSS feed from uNoGS using this Docker container.

Can be added to your RSS reader or any compatible service.

Specify Your RSS feed preferences according to the site query parameters.


## How Its Achieved

- Uses Selenium Chrome WebDriver to fetch JavaScript-rendered HTML content.
- Scrapes data using BeautifulSoup4.
- Generates RSS feed using Rfeed.

## Setup

Docker:
```
docker run -p 8030:8000 docker.io/randomg1/unogs-rss-feed:latest
```

- When running docker run, you can add environment variables like in docker-compose configuration.


Docker-compose:
```
version: '4'
services:
  unogs-rss-feed:
    container_name: uNoGS-RSS-Feed
    image: docker.io/randomg1/unogs-rss-feed:latest
    environment:
      BASE_URL: "https://unogs.com/search/"
      MAX_RESULTS: 50
      START_YEAR: 1900
      END_YEAR: 2024
      # START_RATING: 2
      END_RATING: 10
      # GENRELIST: 43048
      TYPE: "Movie"
      AUDIO: "English"
      SUBTITLE: "English"
      AUDIOSUBTITLE_ANDOR: "and"
      # PERSON: "Morgan Freeman"
      # FILTERBY: "New last 24 hours"
      # ORDERBY: "Date"
      COUNTRY_ANDORUNIQUE: "and"
      COUNTRYLIST: 78
    ports:
      - "8030:8000"
    restart: unless-stopped
```

- You can choose which environment variables you want.


Manually :
```
git clone https://github.com/SunLaria/uNoGS-RSS-Feed.git
cd uNoGS-RSS-Feed
python -m pip install -r requirements.txt
# Edit config.yaml according to your preferences
python app/main.py
```

## Usage

- Navigate to "http://localhost:8030" or "http://127.0.0.1:8030" to access the RSS feed.
- Monitor Docker logs for notifications and error messages Using loguru Module.

## How to Add to RSS Reader

- Add the RSS feed link to your RSS reader using "http://your-ip:8020".
