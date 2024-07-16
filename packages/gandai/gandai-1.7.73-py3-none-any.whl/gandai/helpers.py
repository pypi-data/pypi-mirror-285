import re

import pandas as pd
import requests
import tldextract
from bs4 import BeautifulSoup


def get_homepage_text(domain: str) -> str:
    print(f"getting homepage text for {domain}")
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Accept": "text/html",
        "Referer": "https://www.google.com",
    }
    try:
        resp = requests.get(f"http://www.{domain}", headers=HEADERS, timeout=5)
    except:
        print(f"failed on www.{domain}\ntrying without www")
        resp = requests.get(f"http://{domain}", headers=HEADERS, timeout=5)

    soup = BeautifulSoup(resp.text, "html.parser")
    homepage_text = soup.text.strip()
    homepage_text = re.sub(r"\s+", " ", homepage_text)
    print(homepage_text[:500])
    return homepage_text


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.lower().replace(" ", "_").replace(".", "") for col in df.columns]
    return df


def clean_domain(url: str) -> str:
    if url:
        ext = tldextract.extract(url.strip())  # handled uk.co, and high stars
        return ext.registered_domain
    return None


def domain_is_none(url: str) -> bool:
    return url is None or url == ""
