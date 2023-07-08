import os
import json
import base64
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

import templates

host = ('0.0.0.0', 60003)
json_path = "/var/www/HanMan/books.json"
imgs_path = "/var/www/HanMan/images"

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        html = ""
        route_path = self.path
        if '?' in self.path:
            route_path = self.path.split('?',1)[0]

        match route_path:
            # case '/':print()
            case '/comic/booklist.html'    : html = self.get_booklist()
            case '/comic/chapterlist.html' : html = self.get_chapterlist()
            case '/comic/imglist.html' : html = self.get_imglist()
            case '/comic/switchend': 
                self.switchend()
                html = self.get_booklist()
            case '/comic/move': 
                self.move()
                html = self.get_booklist()
            case _:
                print(self.path)
                html=self.path
        
        self.send_content(html)


    def get_booklist(self):
        with open(json_path, "r") as f:
            books = json.load(f)

        book_link_htmls=""
        for bookitem in books:
            maxchapter=""
            chapter_folder = os.path.join(imgs_path, bookitem['name'])
            if os.path.exists(chapter_folder) and os.path.isdir(chapter_folder):
                chapters = os.listdir(chapter_folder)
                maxchapter = max(chapters, key=lambda chapter: int(os.path.basename(chapter)[0:3]))[0:3]
            values = {
                'url'        : f"chapterlist.html?bookname={base64.urlsafe_b64encode(bookitem['name'].encode()).decode()}",
                'status'     : "已完结" if bookitem['end'] else "连载中",
                'set_status' : f"switchend?bookid={bookitem['id']}",
                'name'       : bookitem['name'],
                'font_color' : "#e6e6e6" if bookitem['readAt'] in ["000","001",maxchapter] else "#faf572",
                'read_at'    : bookitem['readAt'],
                'total'      : maxchapter,
                'moveup'     : f"move?type=up&bookid={bookitem['id']}",
                'movedown'   : f"move?type=down&bookid={bookitem['id']}"
            }
            book_link_htmls += templates.TEMPLATE_BOOK_LINK.format(**values)
        return templates.TEMPLATE_BOOKS.replace("        <li_here />",book_link_htmls)
        

    def get_chapterlist(self):
        query = parse_qs(urlparse(self.path).query)
        bookname = str(base64.urlsafe_b64decode(query.get('bookname', [''])[0]), encoding='utf-8')
        chapter_folder = os.path.join(imgs_path, bookname)
        if not os.path.exists(chapter_folder) or not os.path.isdir(chapter_folder):
            return f"bookname:{bookname} not found"
        
        chapter_link_htmls = ""
        chapters = os.listdir(chapter_folder)
        if len(chapters) == 0:
            chapter_link_htmls = "            <li>无章节</li> \n"
        else:
            chapters.sort(key=lambda chapter: int(os.path.basename(chapter)[0:3]))
            for chapter in chapters:
                values = {
                    'url'          : f"imglist.html?bookname={encodeURLSafe(bookname)}&chapter={encodeURLSafe(os.path.basename(chapter))}",
                    'chapter_name' : os.path.basename(chapter)
                }
                chapter_link_htmls += templates.TEMPLATE_CHAPTER_LINK.format(**values)  
        
        return templates.TEMPLATE_BOOK_CHAPTERS.replace("        <li_here />",chapter_link_htmls).replace("{title}", bookname) 

    def get_imglist(self):
        query = parse_qs(urlparse(self.path).query)
        bookname = decodeURLSafe(query.get('bookname', [''])[0])
        chapter = decodeURLSafe(query.get('chapter', [''])[0])

        img_folder = os.path.join(imgs_path, bookname, chapter)
        if not os.path.exists(img_folder) or not os.path.isdir(img_folder):
            return f"bookname:{bookname} chapter:{chapter} not found"

        last = ""
        next = ""
        chapter_folder = os.path.join(imgs_path, bookname)
        chapters = os.listdir(chapter_folder)
        if len(chapters) != 0:
            chapters.sort(key=lambda _chapter: int(os.path.basename(_chapter)[0:3]))

            try:
                index = chapters.index(chapter)
                if index == 0:
                    next = chapters[1]
                elif index == len(chapters) - 1:
                    last = chapters[index - 1]
                else:
                    last = chapters[index - 1]
                    next = chapters[index + 1]
            except BaseException:
                print("chapters.index(chapter) error")

        imgs = os.listdir(img_folder)
        img_link_htmls = ""
        if len(imgs) == 0:
            img_link_htmls = "            <li>无图片</li> \n"
        else:
            imgs.sort(key=lambda img: int(os.path.basename(img)[0:3]))
            for img in imgs:
                img_link_htmls += f"            <img src=\"/hanman/images/{replaceURLSafe(bookname)}/{replaceURLSafe(chapter)}/{img}\" /> \n"


        with open(json_path, "r+") as f:
            books = json.load(f)
            target_index = -1
            for index,bookitem in enumerate(books):
                if bookitem["name"] == bookname:
                    bookitem["readAt"] = chapter[0:3]
                    target_index = index
                    break
            
            if next == '' and books["end"]:
                books.append(books[target_index])
                books.remove(books[target_index])

            jsonstr = json.dumps(books, ensure_ascii=False)
            jsonstr = jsonstr.replace("}, {","}, \n    {").replace("[{","[\n    {").replace("}]","} \n]");
            f.seek(0)
            f.truncate()
            f.write(jsonstr)


        return templates.TEMPLATE_CHAPTER_IMGS\
                .replace("                <img_here />", img_link_htmls)\
                .replace("{chapter}", chapter)\
                .replace("{chapter_list}", f"chapterlist.html?bookname={encodeURLSafe(bookname)}")\
                .replace("{last}", "" if "" == last else f"imglist.html?bookname={encodeURLSafe(bookname)}&chapter={encodeURLSafe(last)}")\
                .replace("{next}", "" if "" == next else f"imglist.html?bookname={encodeURLSafe(bookname)}&chapter={encodeURLSafe(next)}")


    def switchend(self):
        query = parse_qs(urlparse(self.path).query)
        bookid = query.get('bookid', [''])[0]

        with open(json_path, "r+") as f:
            books = json.load(f)
            for bookitem in books:
                if bookitem["id"] == bookid:
                    bookitem["end"] = not bookitem["end"]
                    break
            jsonstr = json.dumps(books, ensure_ascii=False)
            jsonstr = jsonstr.replace("}, {","}, \n    {").replace("[{","[\n    {").replace("}]","} \n]");
            f.seek(0)
            f.truncate()
            f.write(jsonstr)

    def move(self):
        query = parse_qs(urlparse(self.path).query)
        type = query.get('type', [''])[0]
        bookid = query.get('bookid', [''])[0]
        with open(json_path, "r+") as f:
            books = json.load(f)
            target_index = -1
            for index,bookitem in enumerate(books):
                if bookitem["id"] == bookid:
                    target_index = index
                    break

            if target_index == -1 :
                print("cannot move 1")
            else:
                if target_index == 0 and "up" == type:
                    print("cannot move 2")
                elif target_index == len(books)-1 and "down" == type:
                    print("cannot move 3")
                else:
                    if "up" == type:
                        books[target_index-1], books[target_index] = books[target_index], books[target_index-1]
                    elif "down" == type:
                        books[target_index], books[target_index+1] = books[target_index+1], books[target_index]

                    jsonstr = json.dumps(books, ensure_ascii=False)
                    jsonstr = jsonstr.replace("}, {","}, \n    {").replace("[{","[\n    {").replace("}]","} \n]");
                    f.seek(0)
                    f.truncate()
                    f.write(jsonstr)


    def send_content(self, page):
        # page = page.encode()
        # print(type(page))
        b_page = bytes(page, encoding='utf-8')
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.send_header("Content-Length", str(len(b_page)))
        self.end_headers()
        self.wfile.write(b_page)

def encodeURLSafe(_str):
    return base64.urlsafe_b64encode(_str.encode()).decode()
def decodeURLSafe(_str):
    return str(base64.urlsafe_b64decode(_str), encoding='utf-8')
def replaceURLSafe(_str):
    return _str.replace("&", "&amp;").replace("\\?", "%3F")