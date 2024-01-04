import os
import requests
import shutil
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import json
import utils
import base64 
import hashlib
from zhconv import convert

from PIL import Image



class Rouman():
    def __init__(self):
        self.domain = 'https://roum2.xyz/'
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

    def do_book(self, bookname, book_img_path, stop_num = 5):
        print(f"running book with rouman: {bookname}")
        link = self.get_book_link(bookname)
        if link is None:
            print(f"bookname {bookname} not found.")
            return 
        
        chapters = self.get_chapters(link)
        if chapters is None or len(chapters) == 0:
            print(f"bookname {bookname} get chapters error.")
            return 

        folders=[]
        ready_chapters = os.listdir(book_img_path)
        no_download_count = 0
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
                no_download_count = 0
            folders.append(chapter_path)

            if stop_num != 0 and no_download_count >= stop_num:
                continue

            try:
                print("load chapter: "+chapter_path)
                notdownload = self.get_chapter_pic(chapter_link, chapter_path)
                # break
                if notdownload:
                    no_download_count += 1
            except Exception as e:
                print(e)
                

        all_folders = os.listdir(book_img_path)
        for _f in all_folders:
            dirpath = os.path.join(book_img_path,_f)
            if dirpath not in folders:
                print("delete dir: " + dirpath)
                shutil.rmtree(dirpath)




    def get_book_link(self, bookname):
        url = f"{self.domain}/search?term={bookname}"
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

        a_list = soup.select('ul[class^="search_listArea"] > div > li[class^="comicBox_li"] > a')
        for a_tag in a_list:
            span_tag = a_tag.select('div[class^="comicBox_lineTit"] > span[class^="comicBox_title"]')[0]
            if convert(span_tag.text,'zh-cn') == convert(bookname,'zh-cn'):
                return a_tag.attrs["href"]

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
        a_list = soup.select('div[class^="bookid_chapterBox"] > div[class^="bookid_chapter"] > a')

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
            return True
        text = res.text
        
        soup = BeautifulSoup(text, 'lxml')
        data_tag = soup.select('script#__NEXT_DATA__')[0]
        

        data = json.loads(data_tag.get_text())["props"]["pageProps"]
        images = []
        if "images" in data.keys():
            images = data["images"]
        elif "chapterAPIPath" in data.keys():
            images = self.get_chapterAPIPath(data["chapterAPIPath"])
        


        download_list = []
        for index, item in enumerate(images):
            img_path = os.path.join(chapter_path, str(index + 1).zfill(3)+".jpg")
            if not os.path.exists(img_path):
                download_list.append({"img_link": item["src"], "img_path": img_path, "scramble":item["scramble"]})

        if len(download_list) > 0:
            pool = ThreadPoolExecutor(max_workers=4)
            for download_item in download_list:
                pool.submit(utils.download, download_item["img_link"], download_item["img_path"], self.headers, self.proxies)
            pool.shutdown()

            for download_item in download_list:
                if download_item["scramble"]:
                    part_num = parse_part_num(os.path.splitext(download_item["img_link"].split("/")[-1])[0])
                    re_cut_img(download_item["img_path"], part_num)
            return False
        return True

    def get_chapterAPIPath(self, link):
        full_url = f'{self.domain}{link}'
        res = requests.get(url=full_url, headers=self.headers, proxies=self.proxies)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            print(f"request to {full_url} error! code:{res.status_code}")
            return []
        
        data = json.loads(res.text)
        return data["chapter"]["images"]











# for (var part_num, l = height % part_num, index = 0; index < part_num; index++) {
#    var part_height = Math.floor(height / part_num)
#    var parse_h = part_height * index  
#    var cut_h = height - part_height * (index + 1) - l; 
#    0 == index ? part_height += l : cut_h += l,
#    n.drawImage(e, 0, cut_h, width, part_height, 0, parse_h, width, part_height)
#                         }
def re_cut_img(file_path, part_num):
    img = Image.open(file_path)
    width, height = img.size
    part_height = int(height/part_num)
    img_list = []
    index = 0
    while True:
        cut_h = index*part_height
        cut_to_h = (index+1)*part_height
        if (index+1)*part_height < height and (index+2)*part_height > height:
            cut_to_h = height
        cropped = img.crop((0, cut_h, width, cut_to_h))
        img_list.append(cropped)
        if cut_to_h == height:
            break
        index+=1
    # target = Image.new('RGB', (width, height))
    h = 0
    for _img in reversed(img_list):
        img.paste(_img, (0, h))
        h+=_img.size[1]
        
    img.save(file_path)


def parse_part_num(b64str):
    if(len(b64str)%3 == 1): 
        b64str += "=="
    elif(len(b64str)%3 == 2): 
        b64str += "=" 
    
    sr=base64.b64decode(bytes(b64str,'utf-8'))
    md5str = hashlib.md5(sr).hexdigest()
    hex_array = list(bytes.fromhex(md5str))
    return hex_array[-1] % 10 + 5
    

if __name__ == '__main__':
    Rouman().do_book("花店三母女","./test")

