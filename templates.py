TEMPLATE_BOOKS=\
'''
<html>
    <head>
        <title>目录</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style>
            body {
                background-color: #2b2b2c;
            }
            a {
                color: gray;
                text-decoration:none;
            }
            .condiv {
                font-size: 48px;
                border-bottom: 2px solid gray;
                margin-left: 20px;
            }
            .condiv>div {
                display: inline-block;
            }
            .moveabtn {
                border-left: 1px solid gray;
                border-right: 1px solid gray;
                display: inline-block;
                text-align: center;
                width:100px;
            }
        </style>
    </head>
    <body>
        <li_here />
    </body>
</html>
'''

TEMPLATE_BOOK_LINK=\
'''
    <div class="condiv" >
        <div style="width: calc(100% - 120px);">
            <a href="{url}">
                <div>
                    <span>
                        【<object><a href="{set_status}" >{status}</a></object>】
                    </span>
                    <span style="color: {font_color}">{name}</span>
                </div>
                <div>已读至 {read_at} 章，共 {total} 章</div>
            </a>
        </div>
        <div style="width: 100px">
            <a class="moveabtn" href="{moveup}" > ↑ </a>
            <div style="border-top:1px solid gray"></div>
            <a class="moveabtn" href="{movedown}" > ↓ </a>
        </div>
    </div>
'''

TEMPLATE_BOOK_CHAPTERS=\
'''
<html>
    <head>
        <title>{title}</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style>
            body {
                background-color: #2b2b2c;
            }
            a {
                color: gray;
                text-decoration:none;
            }
            .condiv {
                font-size: 48px;
                border-bottom: 2px solid gray;
                margin-left: 20px;
            }
            .condiv>a>div {
                height: 100px;
                display: flex;
                align-items: center;
            }
            .a-btn {
                text-decoration: none;
                font-size: 48px;
                background-color: white;
                margin: 10px 10px;
                color: blue;
            }
        </style>
    </head>
    <body>
        <div class="condiv">
            <a href="booklist.html"><div> 返回 </div></a>
        </div>
        <li_here />
    </body>
</html>
'''

TEMPLATE_CHAPTER_LINK=\
'''
    <div class="condiv" >
        <a href="{url}">
            <div >{chapter_name}</div>
        </a>
    </div>
'''

TEMPLATE_CHAPTER_IMGS=\
'''
<html>
    <head>
        <title>{chapter}</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style>
            body {
                background: #2b2b2c;
                padding: 0px 0px 0px 0px;
            }
            .read-container {
                
                text-align: -webkit-center;
            }
            .rd-article-wr {
                display: flex;
                flex-direction: column;
                max-width: 1080px;
            }
            .a-btn {
                text-decoration: none;
                font-size: 48px;
                background-color: white;
                margin: 10px 10px;
                color: blue;
            }
        </style>
    </head>
    <body>
        <div class="read-container">
            <div style="margin-bottom: 20px">
                <span><a class="a-btn" href="{last}"> 上一章 </a></span>
                <span><a class="a-btn" href="{chapter_list}"> 目录 </a></span>
                <span><a class="a-btn" href="{next}"> 下一章 </a></span>
            </div>
            <div class="rd-article-wr">
                <img_here />
            </div>
            <div style="margin-top: 20px">
                <span><a class="a-btn" href="{last}"> 上一章 </a></span>
                <span><a class="a-btn" href="{chapter_list}"> 目录 </a></span>
                <span><a class="a-btn" href="{next}"> 下一章 </a></span>
            </div>
        </div>
    </body>
</html>
'''
