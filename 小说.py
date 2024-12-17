import os
import requests
from bs4 import BeautifulSoup
import concurrent.futures

def save_novel(novel_name):
    folder_path = os.path.join("D:/52bqg小说/", str(novel_name))
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        print(f"已保存小说 {novel_name}")

def save_chapter(novel, chapter_name, chapter_content):
    file_path = os.path.join("D:/52bqg小说/", novel, f"{chapter_name}.txt")
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            print(f"正在保存小说章节 {chapter_name}")
            f.write(chapter_content)

def download_chapter(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    }
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        html = BeautifulSoup(resp.text, 'lxml')
        novel_name = html.find('div', class_="path wap_none").find_all('a')[-1].get_text()
        save_novel(novel_name)
        chapter_name = html.find('h1', class_="wap_none").get_text()
        chapter_content = html.find('div', id='chaptercontent').get_text().replace('『点此报错』『加入书签』', '').replace(
            '请收藏本站：https://www.biqg.cc。笔趣阁手机版：https://m.biqg.cc ', '')
        save_chapter(novel_name, chapter_name, chapter_content)
        print(f"章节 {chapter_name} 下载完成")
    except Exception as e:
        print(f"下载章节失败: {url}, 错误: {e}")

if __name__ == '__main__':
    with open(r'D:/52bqg小说/text_href_list.txt', encoding='utf-8') as f:
        text_url = f.read().strip()
    text_url_list = text_url.split('\n')

    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        executor.map(download_chapter, text_url_list)
