import csv
import sys
import time
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

GEOCORDING_URL = 'https://www.geocoding.jp/api/'
ITEM_MAP = {
    '住所': 'address'
}


def get_prefectures_urls(url):
    prefectures_urls = []

    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    for td in soup.find('table', class_='ichiran_box').find_all('td'):
        if r := td.find('a'):
            prefectures_urls.append(f'{url}/{r.attrs["href"]}')
    return prefectures_urls


def get_spa_urls(prefectures_urls):
    for prefecture_url in prefectures_urls:
        soup = BeautifulSoup(requests.get(prefecture_url).text, 'html.parser')
        for table in soup.find_all('table', class_='tenpo_ichiran_box2'):
            for p in table.find_all('p', class_='res_tenmei'):
                if p is not None:
                    yield f'{"/".join(prefecture_url.split("/")[:-1])}/{p.find("a").attrs["href"]}' # NOQA


def get_coordinates(address):
    res = requests.get(
        GEOCORDING_URL,
        params={'q': address}
    )
    if res.status_code != 200:
        raise Exception

    xml = ET.fromstring(res.text).find('coordinate')
    return xml.find('lat').text, xml.find('lng').text


def get_spa_info(spa_url, items):
    response = requests.get(spa_url)
    if response.status_code != 200:
        raise Exception
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    results = {item: None for item in items}
    results['name'] = soup.find('h1').contents[0].strip()
    results['url'] = spa_url

    for tr in soup.find('table', class_='date_box4').find_all('tr'):
        tds = tr.find_all('td')
        item_name = tds[0].contents[0]
        if ITEM_MAP.get(item_name, None) in items:
            results[ITEM_MAP[item_name]] = tds[1].contents[0].strip()

    if 'coordinates' in results and 'address' in results and results['address']: # NOQA
        results['coordinates'] = ','.join(get_coordinates(results['address']))

    return results


def get_spa_infos(spa_urls, items):
    for spa_url in spa_urls:
        try:
            yield get_spa_info(spa_url, items)
        except Exception as e:
            print(
                f'Failed to get {spa_url}. {e}',
                file=sys.stderr
            )
        if 'coordinates' in items:
            time.sleep(10)


if __name__ == '__main__':
    prefectures_urls = get_prefectures_urls('https://www.supersento.com')
    spa_urls = get_spa_urls(prefectures_urls)
    items = ['name', 'url', 'address', 'coordinates']

    writer = csv.DictWriter(sys.stdout, fieldnames=items)
    writer.writeheader()
    for i, info in enumerate(get_spa_infos(spa_urls, items)):
        writer.writerow(info)
