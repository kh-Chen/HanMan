import os
import shutil
import requests
import time
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from concurrent.futures import ThreadPoolExecutor
from zhconv import convert
import utils
# 需要额外安装brotli，lxml

class Ikanhm():
    def __init__(self):
        self.domain = 'http://www.mxshm.top/'
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
            'dnt': '1',
            'pragma': 'no-cache',
            'referer': self.domain
        }
        self.proxies={
            # 'http':'http://chenkh:6659968@192.168.100.150:10087/',
            # 'https':'http://chenkh:6659968@192.168.100.150:10087/',
        }
        
    def do_book(self, bookname, book_img_path):
        print(f"running book with ikanhm: {bookname}")
        link = self.get_book_link(bookname)
        if link is None:
            print(f"bookname {bookname} not found.")
            return 
        
        chapters = self.get_chapters(link)
        
        folders=[]
        ready_chapters = os.listdir(book_img_path)
        for chapter in reversed(chapters):
            num = chapter['index']
            
            chapter_name = chapter['name']
            chapter_link = chapter['link'].strip()

            chapter_name_full = f"{num}. {chapter_name}"
            chapter_path = os.path.join(book_img_path, chapter_name_full)

            for ready_chapter in ready_chapters:
                if chapter_name == ready_chapter[5:]:
                    if ready_chapter != chapter_name_full:
                        ready_chapter_path = os.path.join(book_img_path, ready_chapter)
                        print(f"rename: {ready_chapter_path} -> {chapter_path}")
                        os.rename(ready_chapter_path, chapter_path)

            if not os.path.exists(chapter_path):
                os.mkdir(chapter_path)
            folders.append(chapter_path)
            try:
                self.get_chapter_pic(chapter_link, chapter_path)
                # time.sleep(1)
            except Exception as e:
                print(e)
                

        all_folders = os.listdir(book_img_path)
        for _f in all_folders:
            dirpath = os.path.join(book_img_path,_f)
            if dirpath not in folders:
                print("delete dir: " + dirpath)
                shutil.rmtree(dirpath)


    def get_book_link(self, bookname):
        url = f"{self.domain}/search?keyword={bookname}"
        # print(f"request to: {url}")
        try:
            res = requests.get(url=url, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            print(e)
            return None
        
        res.encoding = 'utf-8'
        if res.status_code != 200:
            print(f"request to {url} error! code:{res.status_code}")
            return None
        text = res.text
        
        soup = BeautifulSoup(text, 'lxml')
        a_list = soup.select('ul.mh-list > li > div.mh-item > a')
        
        for a_tag in a_list:
            link = a_tag.attrs["href"]
            title = a_tag.attrs["title"]
            if title == bookname:
                return link
        
        return None


    def get_chapters(self, link):
        url = f"{self.domain}{link}"
        # print(f"request to: {url}")
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
        soup = BeautifulSoup(text, 'lxml')
        a_list = soup.select('div#chapterlistload > ul#detail-list-select > li > a')
        chapters=[]
        name_set = []
        name_repeats = []
        for index, a_tag in enumerate(a_list):
            c_name = convert(a_tag.get_text().strip(),'zh-cn')
            if c_name in name_set:
                name_repeats.append(c_name)
            else:
                name_set.append(c_name)

            chapters.append({
                "index":str(index + 1).zfill(3),
                "name":c_name,
                "link":a_tag.attrs["href"]
            })

        for name_repeat in name_repeats:
            num = 0
            for chapter_item in chapters:
                if chapter_item["name"] == name_repeat:
                    num = num + 1
                    chapter_item["name"] = chapter_item["name"] + str(num)

        return chapters


    def get_chapter_pic(self, link, chapter_path):
        full_url = f'{self.domain}{link}'
        # print(f"request to: {full_url}")
        res = requests.get(url=full_url, headers=self.headers, proxies=self.proxies)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            print(f"request to {full_url} error! code:{res.status_code}")
            return []
        text = res.text
        
        soup = BeautifulSoup(text, 'lxml')
        img_tags = soup.select('div.comiclist > div.comicpage > div > img')
        
        pool = ThreadPoolExecutor(max_workers=4)
        for index, img_tag in enumerate(img_tags):
            if img_tag.has_attr("data-original"):
                img_link = img_tag.attrs["data-original"]
            else:
                img_link = img_tag.attrs["src"]
            
            img_path = os.path.join(chapter_path, str(index + 1).zfill(3)+".jpg")
            if not os.path.exists(img_path):
                pool.submit(utils.download, img_link.strip(), img_path, self.headers, self.proxies)
                
        pool.shutdown()


# if __name__ == '__main__':
    # spider = Ikanhm()
    # spider.do_book(406,"偷窺（全集无删减）", "/var/www/HanMan/images/偷窺（全集无删减）")


    # books = os.listdir('/var/www/HanMan/images')
    # for dir in books:
    #     dir = os.path.join('/var/www/HanMan/images',dir)
    #     ready_chapters = os.listdir(dir)
    #     for ready_chapter in ready_chapters:
    #         # if "&" in ready_chapter:
    #         #     print(f"{dir}/{ready_chapter}")
    #         a = ready_chapter.replace("&hellip;", "…").replace("&ldquo;", "“").replace("&rdquo;", "”").replace("&hearts;", "♥")\
    #         .replace("&mdash;", "—").replace("&#40;", "(").replace("&#41;", ")").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            
    #         # a = convert(ready_chapter,'zh-cn')#
    #         if ready_chapter != a:
    #             print(f"rename: {dir}/{ready_chapter} -> {a}")
    #             os.rename(os.path.join(dir,ready_chapter), os.path.join(dir,a))
            


    
    
