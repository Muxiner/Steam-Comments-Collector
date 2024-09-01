'''
Author: 阿朝
Date: 2023/8/25
https://cloud.tencent.com/developer/article/1085988 解决办法
https://github.com/Chaobs/Steam-Comments-Collector 原来的解决方法
'''

import time
import random
import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin
import xlwt
import re
from selenium.webdriver.common.action_chains import ActionChains

def steam_review_spider(store_link, comment_count, language):
    '''这个函数是核心爬虫逻辑'''
    
    headers = {
        # 这一部分处理评论语言的问题
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
    } 
    # 游戏商店 Link
    game_link = store_link

    comments_language = 'english' if language == 1 else 'schinese'
    if language == 1:
        headers = {
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        }
    else:
        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        } 
    # 获取游戏ID
    game_id = re.search(r"https://store.steampowered.com/app/(\d+)/", game_link).group(1) 
    # print(headers, '---', comments_language)
    
    # 评论首页
    reviews_home_url = 'https://steamcommunity.com/app/' + game_id + '/reviews'
    html = requests.get(reviews_home_url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    reviews = soup.find_all('div', {'class': 'apphub_Card'})
    # 第一个 userreviewscursor
    user_reviews_cursor = soup.find('input', {'name': 'userreviewscursor'})['value']

    comment_number = comment_count

    review_content = [] #初始化游戏测评内容的二维数组

    if comment_number % 10 == 0:
        comment_page = comment_number // 10 #一页10条
    else:
        comment_page = comment_number // 10 + 1 #还多一页
    
    base_url = 'http://steamcommunity.com/app/'

    for i in range(1, comment_page + 1):
        #根据游戏ID生成游戏评论页面的位置
        query_params = {
            'userreviewscursor': user_reviews_cursor,
            'userreviewsoffset': str(10 * (i - 1)),
            'p': str(i),
            'workshopitemspage': str(i),
            'readytouseitemspage': str(i),
            'mtxitemspage': str(i),
            'itemspage': str(i),
            'screenshotspage': str(i),
            'videospage': str(i),
            'artpage': str(i),
            'allguidepage': str(i),
            'webguidepage': str(i),
            'integratedguidepage': str(i),
            'discussionspage': str(i),
            'numperpage': '10',
            'browsefilter': 'toprated',
            'appid': game_id,
            'appHubSubSection': '10',
            # 'l': 'schinese',
            'l': comments_language,
            'filterLanguage': 'default',
            'searchText': '',
            'forceanon': '1'
        }
        url = urljoin(base_url, f'{game_id}/homecontent/') + '?' + urlencode(query_params)
        # print(url)
        # 爬取网页
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')
        reviews = soup.find_all('div', {'class': 'apphub_Card'})
        user_reviews_cursor = soup.find('input', {'name': 'userreviewscursor'})['value']
        for review in reviews:
            ###  解析评论
            ## 评论ID
            nick = review.find('div', {'class': 'apphub_CardContentAuthorName'})
            ## 推荐 or 不推荐
            title = review.find('div', {'class': 'title'}).text
            ## 游戏时长/小时数(hrs)
            hour = review.find('div', {'class': 'hours'}).text.split(' ')[0]
            ## 评论链接
            link = nick.find('a').attrs['href']
            ## 评论正文
            # comment = review.find('div', {'class': 'apphub_CardTextContent'}).text.split('\n')[2].strip('\t')
            # 查找<div>元素
            div_content = soup.find('div', {'class': 'apphub_CardTextContent'})

            # 初始化一个空列表来存储分割后的内容
            content_list = []

            # 遍历<div>内部的所有内容，包括文字和标签
            for element in div_content.children:
                if element.name == 'br':
                    # 如果是<br>标签，表示换行，插入空字符串表示新行
                    content_list.append('')
                elif isinstance(element, str):
                    # 如果是文本，追加到当前行的内容
                    if content_list:
                        content_list[-1] += element.strip()
                    else:
                        content_list.append(element.strip())
                elif element.name == 'a' or element.name == 'b':
                    # 如果是链接<a>或<b>标签，获取其文本内容
                    if content_list:
                        content_list[-1] += element.get_text().strip()
                    else:
                        content_list.append(element.get_text().strip())

            # 移除空行
            content_list = [line for line in content_list if line]

            # 使用列表推导式和join()方法来拼接内容
            comment = "\n".join(f"\t{line}" for line in content_list)


            cell = []
            cell.append(nick.text)
            cell.append(title)
            cell.append(hour)
            cell.append(link)
            cell.append(comment) # 一个人的评论信息

            review_content.append(cell)
    return review_content


def creat_xls(file_name, content):

    # 游戏名称
    game_name = "wukong"
    # game_name = file_name
    # 文件保存到当前目录
    book_name_xls = game_name + '_评论.xls' 
    # 创建一个工作簿
    workbook = xlwt.Workbook()

    # 创建工作表
    sheet_p = workbook.add_sheet("好评")
    sheet_n = workbook.add_sheet("差评")

    # 定义样式
    # 前三项样式
    first_three_items_alignment = xlwt.Alignment()
    first_three_items_alignment.horz = xlwt.Alignment.HORZ_CENTER # 水平居中对齐
    first_three_items_alignment.vert = xlwt.Alignment.VERT_CENTER # 垂直居中对齐
    first_three_items_style = xlwt.XFStyle()
    first_three_items_style.alignment = first_three_items_alignment

    # 后两项样式
    last_two_items_alignment = xlwt.Alignment()
    last_two_items_alignment.horz = xlwt.Alignment.HORZ_LEFT   # 水平靠左对齐
    last_two_items_alignment.vert = xlwt.Alignment.VERT_CENTER # 垂直居中对齐
    last_two_items_style = xlwt.XFStyle()
    last_two_items_style.alignment = last_two_items_alignment
    last_two_items_style.alignment.wrap = 1 # 自动换行


    # 设置列宽和对齐
    column_widths = [100*30, 140*30, 150*30, 200*30, 1300*30]  # 这里的单位是1/256字符宽度
    for col, width in enumerate(column_widths):
        sheet_p.col(col).width = width
        sheet_n.col(col).width = width

    # 设置标题行样式
    # 前四列标题样式
    first_four_items_header_style = xlwt.XFStyle()
    first_four_items_header_font = xlwt.Font()
    first_four_items_header_font.bold = True
    first_four_items_header_style.font = first_four_items_header_font
    first_four_items_header_style.alignment.vert = xlwt.Alignment.VERT_CENTER # 垂直居中对齐
    first_four_items_header_style.alignment.horz = xlwt.Alignment.HORZ_CENTER # 水平居中对齐

    # 内容列标题样式
    comment_item_header_style = xlwt.XFStyle()
    commnent_item_header_font = xlwt.Font()
    commnent_item_header_font.bold = True
    comment_item_header_style.font = commnent_item_header_font
    comment_item_header_style.alignment.vert = xlwt.Alignment.VERT_CENTER # 垂直居中对齐
    comment_item_header_style.alignment.horz = xlwt.Alignment.HORZ_LEFT   # 水平靠左对齐

    # 写入表头
    headers = ["ID", "推荐/不推荐", "游戏时长/小时数(hrs)", "链接", "评论"]
    for col, header in enumerate(headers):
        if  col < 4:
            sheet_p.write(0, col, header, first_four_items_header_style)
            sheet_n.write(0, col, header, first_four_items_header_style)
        else:
            sheet_p.write(0, col, header, comment_item_header_style)
            sheet_n.write(0, col, header, comment_item_header_style)

    # 好评表序号
    sheet_p_line = 1
    # 差评表序号
    sheet_n_line = 1
    for row, item in enumerate(content, start=1):
        if item[1] == "推荐" or item[1] == "Recommended":
            for col, value in enumerate(item):
                if col < 3:
                    sheet_p.write(sheet_p_line, col, value, first_three_items_style)
                else:
                    sheet_p.write(sheet_p_line, col, value, last_two_items_style)
            sheet_p_line += 1
        else:
            for col, value in enumerate(item):
                if col < 3:
                    sheet_n.write(sheet_n_line, col, value, first_three_items_style)
                else:
                    sheet_n.write(sheet_n_line, col, value, last_two_items_style)
            sheet_n_line += 1

    workbook.save(book_name_xls) # 写入并保存表格
    messagebox.showinfo("结果", "完成咯！")

def creat_GUI():
    """创建和运行GUI的函数"""

    # 创建处理按钮
    def handle_button():
        # store_link = tk_store_link.get()
        # game_name = tk_game_name.get()
        # comments_number = tk_number.get()
        language = selected_value.get()
        # print(language)
        store_link = "https://store.steampowered.com/app/2358720/_/"
        game_name = "Black Myth: Wukong"
        comments_number = 40
        comments = steam_review_spider(store_link, comments_number, language)
        creat_xls(game_name, comments)

    # 创建主窗口
    root = tk.Tk()
    root.title("Steam 评论爬取工具")
    # root.geometry("370x350")
    # 设置窗口的尺寸
    window_width = 370
    window_height = 350

    # 获取屏幕的宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口居中的位置
    position_x = int((screen_width - window_width) / 2)
    position_y = int((screen_height - window_height) / 2)

    # 设置窗口的尺寸和位置
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    root.resizable(False, False)

    # 创建标签和文本框
    tk.Label(root, text="游戏商店链接：").place(x=50, y=20)
    tk_store_link = tk.Entry(root).place(x=170, y=22)
    tk.Label(root, text="游戏名称：").place(x=50, y=45)
    tk_game_name = tk.Entry(root).place(x=170, y=47)
    tk.Label(root, text="需要的评论数量：").place(x=50, y=70)
    tk_number = tk.Entry(root).place(x=170, y=72)
    tk.Button(root, text="开始获取", command=handle_button).pack(side='bottom', pady=20, ipadx=120)
    tk.Label(root, text="注意：请勿短时间内频繁爬取！").pack(side="bottom", pady=20)
    # 定义变量
    selected_value = tk.IntVar()
    selected_value.set(1)  # 默认选中第一个选项

    # 创建Radiobutton控件
    tk.Label(root, text="选择评论语言种类：").place(x=50, y=95)
    r_l_english = tk.Radiobutton(root, text="English", variable=selected_value, value=1).place(x=170, y=95)
    r_l_schinese = tk.Radiobutton(root, text="简体中文", variable=selected_value, value=2).place(x=250, y=95)
    
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    
    creat_GUI()
