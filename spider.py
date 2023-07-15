import os
import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from concurrent.futures import ThreadPoolExecutor
# 需要额外安装brotli，lxml

class HanmanSpider():
    def __init__(self):
        self.domain = 'https://se8.us'
        self.store_dir_path = "/var/www/HanMan"
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'cookie': 'X_CACHE_KEY=afc7c522b3cde8f5882694c13f3e8940; _pk_id.1.273b=288cf48e88223fcd.1679723595.; mc_comic_read=6ec2xj9mCXm4JpMpSOy6Q4jMbaXcjBbzWANrbl94FortU-8DpKN2So0%2F1Q0uUGZG2t-dctsgLqKdB4ppQkR9Jg7oetmbhpUCJCWAvVvQrvU5dhXbqaUsFi5h2A; pid=1007533; _pk_ref.1.273b=%5B%22%22%2C%22%22%2C1680923860%2C%22https%3A%2F%2Fwww.google.com.hk%2F%22%5D; _pk_ses.1.273b=1',
            'dnt': '1',
            'pragma': 'no-cache',
            'referer': 'https://se8.us/'
        }
        self.proxies={
            'http':'192.168.100.150:10087',
            'https':'192.168.100.150:10087'
        }
        self.book_img_path = self.init_dir()

    def init_dir(self):
        book_img_path = os.path.join(self.store_dir_path, 'images')
        if not os.path.exists(book_img_path):
            os.makedirs(book_img_path)

        return book_img_path


    def run(self, id=''):
        print(f' run at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} --------------------------')
        jsonfile = os.path.join(self.store_dir_path, "books.json")
        with open(jsonfile, "r") as f:
            books = json.load(f)

        # self.do_book(books[4])
        for bookitem in books:
            if id == '' or id == bookitem["id"].strip():
                self.do_book(bookitem)
                time.sleep(1)
        print("end.")
        print(f'stop at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} -------------------------')
    

    def do_book(self, bookitem):

        bookmid = bookitem["mid"].strip()
        bookid = bookitem["id"].strip()
        bookname = bookitem["name"].strip()
        print(f"running book: {bookname}")

        book_img = os.path.join(self.book_img_path, bookname)
        if not os.path.exists(book_img):
            os.makedirs(book_img)
        elif bookitem["end"] == 1:
            print(f"skip end book {bookname}")
            return

        if bookmid == '':
            bookmid = self.get_book_mid(bookid)
        
        chapters = self.get_chapters(bookmid)
        
        for index, chapter in enumerate(chapters):
            num = str(index + 1).zfill(3)
            pnum = chapter['pnum']
            chapter_name = chapter['name'].strip()
            chapter_link = chapter['link'].strip()

            chapter_name_full = f"{num}. {chapter_name}"
            chapter_path = os.path.join(book_img, chapter_name_full)

            ready_chapters = os.listdir(book_img)
            downloaded = False
            for ready_chapter in ready_chapters:
                if chapter_name == ready_chapter[5:]:
                    if ready_chapter != chapter_name_full:
                        ready_chapter_path = os.path.join(book_img, ready_chapter)
                        print(f"rename: {ready_chapter_path} -> {chapter_path}")
                        os.rename(ready_chapter_path, chapter_path)

                    files = os.listdir(chapter_path)
                    if len(files) >= int(pnum):
                        downloaded = True
                        break
            
            if downloaded:
                print(f"skip: {chapter_path}")
                continue

            if not os.path.exists(chapter_path):
                os.mkdir(chapter_path)

            try:
                print(f"downloading: {bookname} - {chapter_name_full}")
                self.get_chapter_pic(chapter_link, chapter_path)
            except Exception as e:
                print(e)
                # os.rmdir(chapter_path)


    def get_book_mid(self, bookid):
        catalogue_link = f'{self.domain}/index.php/comic/{bookid}'
        print(f"request to: {catalogue_link}")
        res = requests.get(url=catalogue_link, headers=self.headers, proxies=self.proxies)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            print(f"request to {catalogue_link} error! code:{res.status_code}")
            return []
        text = res.text
        # print(text)
        soup = BeautifulSoup(text, 'lxml')
        a_tag = soup.select('div.comic-handles.clearfix > a.btn--collect.j-user-collect')[0]
        mid = a_tag.attrs['data-id']
        jsonfile = os.path.join(self.store_dir_path, "books.json")
        with open(jsonfile, "r+") as f:
            books = json.load(f)
            for bookitem in books:
                if bookitem["id"] == bookid:
                    bookitem["mid"] = mid
                    break
            jsonstr = json.dumps(books, ensure_ascii=False)
            jsonstr = jsonstr.replace("}, {","}, \n    {").replace("[{","[\n    {").replace("}]","} \n]");
            f.seek(0)
            f.truncate()
            f.write(jsonstr)


        return mid


    def get_chapters(self, mid):
        url = f"{self.domain}/index.php/api/comic/chapter?mid={mid}"
        time.sleep(1)
        print(f"request to: {url}")
        try:
            res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            print(e)
            return []
        
        res.encoding = 'utf-8'
        if res.status_code != 200:
            print(f"request to {url} error! code:{res.status_code}")
            return []
        text = res.text
        return json.loads(text)["data"]


    def get_chapter_pic(self, link, chapter_path):
        time.sleep(1)
        full_url = f'{link}'
        print(f"request to: {full_url}")
        res = requests.get(url=full_url, headers=self.headers, proxies=self.proxies)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            print(f"request to {full_url} error! code:{res.status_code}")
            return []
        text = res.text
        soup = BeautifulSoup(text, 'lxml')
        img_tags = soup.select('div.rd-article-wr.clearfix>div>img')
        pool = ThreadPoolExecutor(max_workers=4)
        for img_tag in img_tags:
            img_link = img_tag.attrs["data-original"]
            img_no = img_tag.attrs["alt"].zfill(7)
            img_path = os.path.join(chapter_path, img_no)
            if not os.path.exists(img_path):
                pool.submit(self.download, img_link.strip(), img_path)
                
        pool.shutdown()


    def download(self, link, filepath):
        for i in range(3):
            try:
                r = requests.get(url=link, headers=self.headers, proxies=self.proxies)
                if r.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(r.content)
                    break
                else:
                    print(f'获取失败。code: {r.status_code} link: {link}')
            except Exception as e:
                print(f'获取失败。code: {r.status_code} link: {link} error: {e}')
        # print(filepath + " end.")


def timer():
    while True:
        now = time.localtime()
        if now.tm_hour == 4 and now.tm_min == 0 and now.tm_sec == 0:
            spider = HanmanSpider()
            spider.run()
        else:
            time.sleep(1)


if __name__ == '__main__':
    spider = HanmanSpider()
    spider.run()