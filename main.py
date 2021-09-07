import requests
import os
import shutil
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
    if not os.path.exists(TEMP_DIR_PATH):
        os.makedirs(TEMP_DIR_PATH)

    # 画像一覧の1ページ目のURLを読み込み
    soup = get_soup(target_url)
    # 画像一覧の全ページのURLを取得
    arr_url = get_page_url_list(soup)
    pp.pprint(arr_url)

    LOGGER.info('画像一覧ページのループ開始')
    for index, list_url in enumerate(arr_url):
        # 一覧に対象のURLがある場合は対象のURLの処理をスキップ
        if is_exist_url_in_file(list_url, TEMP_LIST_PATH, False):
            continue
        # 画像ファイルがDL済みか判定するファイル
        temp_file = TEMP_DIR_PATH + '/' + str(index+1) + '.csv'

        # 画像のURLを取得
        arr_pics_url = get_pics_url_list(list_url)

        for url in arr_pics_url:
            if is_exist_url_in_file(url, temp_file, True):
                continue

            # 保存先のパス、画像ページのURL、画像一覧の番号
            save_images(save_path, url, temp_file)

        with open(TEMP_LIST_PATH, 'a') as f:
            f.write(list_url + '\n')

    LOGGER.info('画像一覧ページのループ終了')
    after_exec()
    LOGGER.info('処理終了')


def request_get(url: str) -> requests:
    return requests.get(url, headers=CONFIG_HEADER)


def get_soup(url: str) -> BeautifulSoup:
    req = request_get(url)
    return BeautifulSoup(req.text, 'lxml')


def get_page_url_list(soup: BeautifulSoup) -> list:
    # ページングのtdタグを取得
    arr_page_div = soup.find_all("div", class_="gtb")
    arr_page_td = arr_page_div[0].select('table.ptt tr td')
    # 配列には"<"と">"を含む、また0から始まるので">"と0の分の2を引く
    page_max = arr_page_td[len(arr_page_td) - 2].select("a")[0].string

    # ベースとなる1ページ目のURLを取得
    base_url = arr_page_td[1].find('a').get('href')
    LOGGER.info("ページ数の最大:" + page_max)

    # 画像一覧の全ページのURLを格納
    arr_url = [base_url]
    for num in range(1, int(page_max)):
        arr_url.append('{}?p={}'.format(base_url, num))
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


def is_exist_url_in_file(list_url: str, path: str, isFile: bool) -> bool:
    chk = False
    if os.path.isfile(path):
        # すでに読み込み済みのURLかどうかチェック
        with open(path, 'r') as ro_files:
            for file_url in ro_files:
                file_url = file_url.strip()
                # 既に一覧全ての画像をDL済みの場合は次のループへ
                if list_url == file_url:
                    chk = True
                    message = 'skipped：' + file_url
                    if isFile:
                        # ログを見やすくするためにインデント追加
                        message = '  ' + message
                    LOGGER.info(message)

                    break
    return chk


def save_images(save_path: str, url: str, temp_file: str) -> bool:
    # LOGGER.info('url: ' + url)
    res = request_get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    arr_div = soup.find('div', id='i3')
    img_tag = arr_div.select_one('a > img')
    img_url = img_tag['src']
    # LOGGER.info(img_url)

    file_name = img_url.split('/')[-1]
    file_path = '{}/{}'.format(save_path, file_name)
    if os.path.isfile(file_path):
        LOGGER.info('exist: ' + file_path)
    else:
        response = request_get(img_url)
        if response.status_code == 200:
            i = Image.open(BytesIO(response.content))
            i.save(file_path, 'JPEG', quality=100)
            with open(temp_file, 'a') as f:
                f.write(url + '\n')
            LOGGER.info('Saved! ' + file_name)


def after_exec():
    dir = TEMP_DIR_PATH + '/'
    LOGGER.info('削除します: ' + dir)
    shutil.rmtree(dir)
    with open(SAVE_PATH + '/done', 'a') as f:
        f.write('')


if __name__ == '__main__':
    main()
