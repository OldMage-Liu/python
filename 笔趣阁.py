import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor


def get_urls_from_div(div):
    href_list = re.findall('<a href="(.*?)"', str(div))
    return ['https://www.biqg.cc' + href for href in href_list]


def fetch_and_write_urls(url, headers):
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        href_text = response.text
        html = BeautifulSoup(href_text, 'html.parser')  # Use 'html.parser' instead of 'lxml'
        href_url_list = html.find_all('dl')
        text_urls = re.findall('<dd><a href="(.*?)"', str(href_url_list))
        with open(r'D:\52bqg小说\text_href_list.txt', 'a', encoding='utf-8') as f:
            for text_url in text_urls:
                f.write('https://www.biqg.cc' + text_url + '\n')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")


def main():
    url = 'https://www.biqg.cc/top/'
    headers = {
        'Cookie': 'Hm_lvt_985c57aa6304c183e46daae6878b243b=1718874626; Hm_lpvt_985c57aa6304c183e46daae6878b243b=1718875667',
        'Referer': 'https://www.biqg.cc/top/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    }

    try:
        resp = requests.get(url=url, headers=headers)
        resp.raise_for_status()  # Raise an exception for bad status codes
        html = BeautifulSoup(resp.text, 'html.parser')  # Use 'html.parser' instead of 'lxml'
        href_divs = html.find_all('div', class_='blocks')
        url_list = sum([get_urls_from_div(div) for div in href_divs], [])

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for url in url_list:
                futures.append(executor.submit(fetch_and_write_urls, url, headers))

            for future in futures:
                future.result()  # Wait for each task to complete

    except requests.exceptions.RequestException as e:
        print(f"Error fetching main URL {url}: {e}")


if __name__ == '__main__':
    main()
