import os
import sys
import time
import json
import requests
from spider_ikanhm_top import Ikanhm
from spider_se8_us import Se8us

class Spider():
    def __init__(self):
        self.store_dir_path = "/var/www/HanMan"
        self.book_img_folder = self.init_dir()

    def init_dir(self):
        book_img_folder = os.path.join(self.store_dir_path, 'images')
        if not os.path.exists(book_img_folder):
            os.makedirs(book_img_folder)
        # print(os.path.abspath(book_img_path))
        return book_img_folder


    def run(self, id=''):
        
        print(f' run at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} --------------------------')
        # jsonfile = os.path.abspath("book_spider.json")
        json_path = os.path.join(self.store_dir_path, 'books.json')
        with open(json_path, "r") as f:
            books = json.load(f)

        for bookitem in books:
            if id == '' or id == bookitem["id"].strip():
                self.spider_book(bookitem)
                if id == '':
                    time.sleep(10)
        print("end.")
        print(f'stop at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} -------------------------')


    def spider_book(self, bookitem):
        bookname = bookitem["name"].strip()
        spiderby = bookitem["spiderby"].strip()
        book_img_path = os.path.join(self.book_img_folder, bookname)
        if not os.path.exists(book_img_path):
            os.makedirs(book_img_path)
        
        if spiderby == 'ikan':
            ikan = Ikanhm()
            ikan.do_book(bookitem["name"].strip(), book_img_path)
        elif spiderby == 'se8':
            bookid = bookitem["id"].strip()
            Se8us().do_book(bookid,bookname,book_img_path)


def timer():
    while True:
        now = time.localtime()
        if now.tm_hour == 4 and now.tm_min == 0 and now.tm_sec == 0:
            Spider().run()
        else:
            time.sleep(1)

if __name__ == '__main__':
    id = sys.argv[1]
    spider = Spider()
    spider.run(id)

