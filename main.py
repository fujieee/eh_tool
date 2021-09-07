import requests
import os
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from config import *


def main():
    LOGGER.info('処理開始')
    # 定義ファイルから読み込み
    save_path = SAVE_PATH
    target_url = TARGET_URL

    # 対象のディレクトリの存在チェック
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 画像一覧の1ページ目のURLを読み込み
    soup = get_soup(target_url)
    # 画像一覧の全ページのURLを取得
    arr_url = get_page_url_list(soup)
    LOGGER.info(arr_url)

    LOGGER.info('画像一覧ページのループ開始')
    for list_url in arr_url:
        # 画像のURLを取得
        arr_pics_url = get_pics_url_list(list_url)

        for url in arr_pics_url:
            save_images(save_path, url)
    LOGGER.info('画像一覧ページのループ終了')
    LOGGER.info('処理終了')


def request_get(url: str) -> requests:
    return requests.get(url, headers=CONFIG_HEADER)


def get_soup(url: str) -> BeautifulSoup:
    LOGGER.info('TOPページ情報取得開始')
    req = request_get(url)
    LOGGER.info('TOPページ情報取得完了')
    return BeautifulSoup(req.text, 'lxml')


def get_page_url_list(soup: BeautifulSoup) -> list:
    LOGGER.info('一覧ページのURL取得開始')
    # print(soup.prettify())
    # ページングのtdタグを取得
    arr_page_div = soup.find_all("div", class_="gtb")
    print(arr_page_div)
    arr_page_td = arr_page_div[0].select('table.ptt tr td')
    print('table.ptt: ')
    print(arr_page_div[0].select('table.ptt'))
    print('table.ptt tr: ')
    print(arr_page_div[0].select('table.ptt tr'))
    print(arr_page_td)
    # arr_page_td = soup.select('table.ptt tbody tr td')
    # 配列には"<"と">"を含む、また0から始まるので">"と0の分の2を引く
    page_max = arr_page_td[len(arr_page_td) - 2].select("a")[0].string

    # ベースとなる1ページ目のURLを取得
    base_url = arr_page_td[1].find('a').get('href')
    LOGGER.info("ページ数の最大:" + page_max)

    # 画像一覧の全ページのURLを格納
    arr_url = [base_url]
    for num in range(1, int(page_max)):
        arr_url.append('{}?p={}'.format(base_url, num))
    LOGGER.info('一覧ページのURL取得終了')
    return arr_url


def get_pics_url_list(list_url: str) -> list:
    LOGGER.info("対象のURL：" + list_url)
    req = request_get(list_url)
    soup = BeautifulSoup(req.text, 'lxml')

    # ページングのtdタグを取得
    arr_pics_td = soup.find('div', id='gdt')
    arr_pics_url = []
    for div in arr_pics_td:
        if div.select_one('div > div > a') is not None:
            arr_pics_url.append(div.select_one('div > div > a')['href'])
    return arr_pics_url


def save_images(save_path: str, url: str) -> bool:
    LOGGER.info(url)

    res = request_get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    arr_div = soup.find('div', id='i3')
    img_tag = arr_div.select_one('a > img')
    img_url = img_tag['src']
    LOGGER.info(img_url)

    file_name = img_url.split('/')[-1]
    LOGGER.info(file_name)
    file_path = '{}/{}'.format(save_path, file_name)
    LOGGER.info(file_path)
    if os.path.isfile(file_path):
        LOGGER.info('already exists')
    else:
        response = request_get(img_url)

        LOGGER.info("https status code: {}".format(response.status_code))
        if response.status_code == 200:
            i = Image.open(BytesIO(response.content))
            i.save(file_path, 'JPEG', quality=100)


if __name__ == '__main__':
    main()
