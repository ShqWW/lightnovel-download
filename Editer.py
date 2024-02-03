#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests  # 用来抓取网页的html源码
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import time  # 时间相关操作
import os
from rich.progress import track as tqdm
from utils import *
import zipfile
import shutil
import re
import pickle
from PIL import Image
import time
import threading
from concurrent.futures import ThreadPoolExecutor, wait
import pickle

lock = threading.RLock()

class Editer(object):
    def __init__(self, root_path, book_no='0000', volume_no=1):
        self.url_head = 'https://www.wenku8.net' 
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47', 'referer': self.url_head}

        self.main_page = f'{self.url_head}/book/{book_no}.htm'
        self.color_chap_name = '插图'
        self.color_page_name = '彩页'
        self.html_buffer = dict()
        
        main_html = self.get_html(self.main_page ,is_gbk=True)
        self.cata_page = self.url_head + re.search(r'<a href=\"(.*?)\">小说目录</a>', main_html).group(1)
        cata_html = self.get_html(self.cata_page ,is_gbk=True)
        bf = BeautifulSoup(cata_html, 'html.parser')
        self.title = bf.find('div', {"id": "title"}).text
        self.author = bf.find('div', {"id": "info"}).text[3:]
        self.cover_url = re.findall(r'<img src=\"(.*?)\"', main_html)[1]
    
            
        self.img_url_map = dict()
        self.volume_no = volume_no

        self.epub_path = root_path
        self.temp_path = check_chars(os.path.join(self.epub_path,  'temp_'+ self.title + '_' + str(self.volume_no)))
    
        self.missing_last_chap_list = []
        self.is_color_page = True
        self.page_url_map = dict()
        self.ignore_urls = []
        self.url_buffer = []
        self.max_thread_num = 8
        self.pool = ThreadPoolExecutor(self.max_thread_num)
        
    # 获取html文档内容
    def get_html(self, url, is_gbk=False):
        time.sleep(1)
        while True:
            req = requests.get(url, headers=self.header)
            if is_gbk:
                req.encoding = 'GBK'       #这里是网页的编码转换，根据网页的实际需要进行修改，经测试这个编码没有问题
            if '<title>Access denied | www.wenku8.net used Cloudflare to restrict access</title>' in req.text:
                time.sleep(3)
            else:
                break
        req = req.text
        return req
    
    def get_html_img(self, url, is_buffer=False):
        if is_buffer:
            while not url in self.html_buffer.keys():
                time.sleep(0.1) 
        if url in self.html_buffer.keys():
            return self.html_buffer[url]
        while True:
            try:
                req=requests.get(url, headers=self.header)
                break
            except Exception as e:
                pass
        lock.acquire()
        self.html_buffer[url] = req.content
        lock.release()
        return req.content
    
    def make_folder(self):
        os.makedirs(self.temp_path, exist_ok=True)

        self.text_path = os.path.join(self.temp_path, 'OEBPS/Text')
        os.makedirs(self.text_path, exist_ok=True)

        self.img_path = os.path.join(self.temp_path,  'OEBPS/Images')
        os.makedirs(self.img_path, exist_ok=True)
    
    def get_index_url(self):
        self.volume = {}
        self.volume['chap_urls'] = []
        self.volume['chap_names'] = []
        volume_title_list, chap_names_list, chap_urls_list = self.get_chap_list(is_print=False)
        if len(volume_title_list)<self.volume_no:
            print('输入卷号超过实际卷数！')
            return False
        volume_array = self.volume_no - 1
        self.volume['chap_names'] = chap_names_list[volume_array]
        self.volume['chap_urls'] = chap_urls_list[volume_array]
        self.volume['book_name'] = volume_title_list[volume_array]
        return True
        
    def get_chap_list(self, is_print=True):
        cata_html = self.get_html(self.cata_page, is_gbk=True)
        bf = BeautifulSoup(cata_html, 'html.parser')
        # print(bf)
        chap_html = str(bf.find('table', {'class', 'css'}))
        volume_title_list = []
        chap_urls_list = []
        chap_names_list = []
        # chap_num = 0
        for line in chap_html.split('\n'):
            bf = BeautifulSoup(line, 'html.parser')
            if line.startswith('<td class=\"vcss\"'):
                volume_title = bf.text
                volume_title_list.append(volume_title)
                chap_urls_list.append([])
                chap_names_list.append([])
            elif line.startswith('<td class=\"ccss\"'):
                chap_name = bf.text
                if chap_name != '' and chap_name!= ' ':
                    chap_names_list[-1].append(chap_name)
                    chap_urls_list[-1].append(self.cata_page.replace('index.htm', bf.find('a')['href']))
        if is_print:
            for volume_no, volume_title in enumerate(volume_title_list):
                print(f'[{volume_no+1}]', volume_title)
        return volume_title_list, chap_names_list, chap_urls_list 
    
    def get_chap_text(self, url, chap_name, is_color=False):
        print(chap_name)
        content_html = self.get_html(url, is_gbk=True)
        bf = BeautifulSoup(content_html, 'html.parser')
        text_with_head = bf.find('div', {'id': 'content'}) 
        text_chap = ''
        if is_color:
            img_url_htmls = text_with_head.find_all('img', {'class': 'imagecontent'})
            img_urls = [img_url_html.get('src') for img_url_html in img_url_htmls]
            for img_url in img_urls:
                self.img_url_map[img_url] = str(len(self.img_url_map)).zfill(2)
                img_symbol = f'[img:{self.img_url_map[img_url]}]'
                if '00' not in img_symbol:
                    text_chap += (img_symbol+'\n')
        else:
            text_html = str(text_with_head)
            for line in text_html.split('\n'):
                if not line.startswith('<ul id="contentdp">') and not line.startswith('<br/>'):
                    text_chap += (line+'\n')
            text_chap = BeautifulSoup(text_chap, 'html.parser').get_text()
        return text_chap
    
    def get_text(self):
        self.make_folder()   
        img_strs = []   #记录后文中出现的所有图片位置
        text_no=0   #text_no正文章节编号(排除插图)   chap_no 是所有章节编号
        for chap_no, (chap_name, chap_url) in enumerate(zip(self.volume['chap_names'], self.volume['chap_urls'])):
            if chap_name == self.color_chap_name:
                text = self.get_chap_text(chap_url, chap_name, True)
                text_html_color = text2htmls(self.color_page_name, text)
            else:
                text = self.get_chap_text(chap_url, chap_name)
                text_html = text2htmls(chap_name, text)
                textfile = self.text_path + f'/{str(text_no).zfill(2)}.xhtml'
                with open(textfile, 'w+', encoding='utf-8') as f:
                    f.writelines(text_html)
                for text_line in text_html:
                    img_str = re.search(r"<img(.*?)\/>", text_line)
                    if img_str is not None:
                        img_strs.append(img_str.group(0))
                text_no += 1
            
        # 将彩页中后文已经出现的图片删除，避免重复
        if self.is_color_page: #判断彩页是否存在
            text_html_color_new = []
            textfile = self.text_path + '/color.xhtml'
            for text_line in text_html_color: 
                is_save = True
                for img_str in img_strs:
                    if img_str in text_line:
                        is_save = False
                        break
                if is_save:
                   text_html_color_new.append(text_line) 
        
            with open(textfile, 'w+', encoding='utf-8') as f:
                f.writelines(text_html_color_new)
        

    def get_image(self, is_gui=False, signal=None):
        for url in self.img_url_map.keys():
            self.pool.submit(self.get_html_img, url)
        img_path = self.img_path
        if is_gui:
            len_iter = len(self.img_url_map.items())
            signal.emit('start')
            for i, (img_url, img_name) in enumerate(self.img_url_map.items()):
                content = self.get_html_img(img_url, is_buffer=True)
                with open(img_path+f'/{img_name}.jpg', 'wb') as f:
                    f.write(content) #写入二进制内容 
                signal.emit(int(100*(i+1)/len_iter))
            signal.emit('end')
        else:
            for img_url, img_name in tqdm(self.img_url_map.items()):
                content = self.get_html_img(img_url)
                with open(img_path+f'/{img_name}.jpg', 'wb') as f:
                    f.write(content) #写入二进制内容

    def get_cover(self, is_gui=False, signal=None):
        textfile = os.path.join(self.text_path, 'cover.xhtml')
        img_w, img_h = 300, 300
        try:
            imgfile = os.path.join(self.img_path, '00.jpg')
            img = Image.open(imgfile)
            img_w, img_h = img.size
            signal_msg = (imgfile, img_h, img_w)
            if is_gui:
                signal.emit(signal_msg)
        except Exception as e:
            print(e)
            print('没有封面图片，请自行用第三方EPUB编辑器手动添加封面')
        img_htmls = get_cover_html(img_w, img_h)
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(img_htmls)

    def check_volume(self, is_gui=False, signal=None, editline=None):
         #没有检测到插图页，手动输入插图页标题
        if self.color_chap_name not in self.volume['chap_names']:
            self.is_color_page = False
            self.img_url_map[self.cover_url] = str(len(self.img_url_map)).zfill(2)
            print('**************')
            print('提示：没有彩页，但主页封面存在，将使用主页的封面图片作为本卷图书封面')
            print('**************')
    
    def hand_in_msg(self, error_msg='', is_gui=False, signal=None, editline=None):
        if is_gui:
            print(error_msg)
            signal.emit('hang')
            time.sleep(1)
            while not editline.isHidden():
                time.sleep(1)
            content = editline.text()
            editline.clear()
        else:
            content = input(error_msg)
        return content
            
    def hand_in_url(self, chap_name, is_gui=False, signal=None, editline=None):
        error_msg = f'章节\"{chap_name}\"连接失效，请手动输入该章节链接(手机版“{self.url_head}”开头的链接):'
        return self.hand_in_msg(error_msg, is_gui, signal, editline)
    
    def hand_in_color_page_name(self, is_gui=False, signal=None, editline=None):
        if is_gui:
            error_msg = f'插图页面不存在，需要下拉选择插图页标题，若不需要插图页则保持本栏为空直接点确定：'
            editline.addItems(self.volume['chap_names'])
            editline.setCurrentIndex(-1)
        else:
            error_msg = f'插图页面不存在，需要手动输入插图页标题，若不需要插图页则不输入直接回车：'
        return self.hand_in_msg(error_msg, is_gui, signal, editline) 
    
    def get_toc(self):
        if self.is_color_page:
            ind = self.volume["chap_names"].index(self.color_chap_name)
            self.volume["chap_names"].pop(ind)
        toc_htmls = get_toc_html(self.title, self.volume["chap_names"])
        textfile = self.temp_path + '/OEBPS/toc.ncx'
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(toc_htmls)

    def get_content(self):
        num_chap = len(self.volume["chap_names"])
        num_img = len(os.listdir(self.img_path))
        content_htmls = get_content_html(self.title + '-' + self.volume['book_name'], self.author, num_chap, num_img, self.is_color_page)
        textfile = self.temp_path + '/OEBPS/content.opf'
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(content_htmls)

    def get_epub_head(self):
        mimetype = 'application/epub+zip'
        mimetypefile = self.temp_path + '/mimetype'
        with open(mimetypefile, 'w+', encoding='utf-8') as f:
            f.write(mimetype)
        metainf_folder = os.path.join(self.temp_path, 'META-INF')
        os.makedirs(metainf_folder, exist_ok=True)
        container = metainf_folder + '/container.xml'
        container_htmls = get_container_html()
        with open(container, 'w+', encoding='utf-8') as f:
            f.writelines(container_htmls)

    def get_epub(self):
        epub_file = check_chars(self.epub_path + '/' + self.title + '-' + self.volume['book_name'] + '.epub')
        with zipfile.ZipFile(epub_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, filenames in os.walk(self.temp_path):
                fpath = dirpath.replace(self.temp_path,'') #这一句很重要，不replace的话，就从根目录开始复制
                fpath = fpath and fpath + os.sep or ''
                for filename in filenames:
                    zf.write(os.path.join(dirpath, filename), fpath+filename)
        shutil.rmtree(self.temp_path)
        return epub_file