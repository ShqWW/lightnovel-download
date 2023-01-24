#!/usr/bin/python
# -*- coding:utf-8 -*-

from codecs import charmap_encode
from operator import index, itemgetter
from turtle import down
from typing import Container
import requests  # 用来抓取网页的html源码
import random  # 取随机数
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import time  # 时间相关操作
import os
from rich.progress import track as tqdm
from utils import *
import cv2
import zipfile
import shutil
import numpy as np

import argparse

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='config')
    parser.add_argument('--color_page', default=1, type=int)
    parser.add_argument('--book_no', default='0000', type=str)
    parser.add_argument('--book_cls', default='1', type=str)
    parser.add_argument('--volumn_no', default='1', type=int)
    args = parser.parse_args()
    return args


class Editer(object):
    def __init__(self, root_path, book_no='0000', book_cls='1', volume_no=1):
        
        self.book  = 'https://www.wenku8.net/novel/'+ book_cls +'/' + book_no
        self.index = self.book + '/index.htm'
        self.rootpath = root_path
        self.volume_no = volume_no

        self.temp_path = os.path.join(self.rootpath,  'temp')
        os.makedirs(self.temp_path, exist_ok=True)
        self.epub_path = os.path.join(self.rootpath,  'epub')
        os.makedirs(self.epub_path, exist_ok=True)

        self.text_path = os.path.join(self.temp_path, 'OEBPS/Text')
        os.makedirs(self.text_path, exist_ok=True)
        self.img_path = os.path.join(self.temp_path,  'OEBPS/Images')
        os.makedirs(self.img_path, exist_ok=True)
        
        self.title='xxx'
        self.author='xxx'

        # 设置headers是为了模拟浏览器访问 否则的话可能会被拒绝 可通过浏览器获取，这里不用修改
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'}

        # self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}


    """
    获取html文档内容
    """

    def get_html(self, url, is_gbk=True):
        # 设置一个超时时间 取随机数 是为了防止网站被认定为爬虫，不用修改
        timeout = random.choice(range(80, 180))

        while True:
            try:
                req = requests.get(url=url, headers=self.header)
                if is_gbk:
                    req.encoding = 'GBK'       #这里是网页的编码转换，根据网页的实际需要进行修改，经测试这个编码没有问题
                # else:
                #     req.decode('utf-8')
                break
            except Exception as e:
                print('3', e)
                time.sleep(random.choice(range(5, 10)))
        return req.text

    def get_index_url(self):
        html = self.get_html(self.index)
        # print(html)
        bf = BeautifulSoup(html, 'html.parser')
        self.title = bf.find('div', {'id': 'title'}).text
        self.author = bf.find('div', {'id': 'info'}).text.replace('作者：', '')
        index_url_find = bf.findAll('tr')
        volume_names = []
        img_urls = []
        chap_names = []
        chap_urls = []
        chap_strips = []
        chap_strip = 0
        for index_url in index_url_find:
            volume = index_url.find('td', {'class': 'vcss'})
            chaps = index_url.findAll('td', {'class': 'ccss'})
            if volume != None:
                chap_strips.append(chap_strip)
                volume_name = volume.text
                volume_names.append(volume_name)         
            else:
                for chap in chaps:
                    if chap.find('a') != None:
                        chap_url = self.book + '/'+  chap.find('a').get('href')
                        chap_name = chap.text
                        chap_names.append(chap_name)
                        chap_urls.append(chap_url)
                        chap_strip += 1
        chap_strips.append(chap_strip)
        if len(chap_strips)>1:
            volumes = []
            for i in range(len(volume_names)):
                volume = {'name': volume_names[i], 'chap_names': chap_names[chap_strips[i]:chap_strips[i+1]], 'chap_urls': chap_urls[chap_strips[i]:chap_strips[i+1]]}
                volumes.append(volume)
            volume = volumes[self.volume_no-1]
            if '插图' in volume['chap_names']:
                img_index = volume['chap_names'].index('插图')
                volume['chap_names'].pop(img_index)
                volume['img_urls'] = volume['chap_urls'].pop(img_index)
            self.title += (' ' + volume['name'])
            print(self.title, self.author)
            return volume
        else:
            return

    def get_text(self, volume):
        text_path = self.text_path
        chap_names, chap_urls = volume["chap_names"], volume["chap_urls"]

        for chap_no, (chap_name, chap_url) in enumerate(zip(chap_names, chap_urls)):
            print(chap_name)
            html = self.get_html(chap_url)
            bf = BeautifulSoup(html, 'html.parser')
            text = bf.find('div', {'id': 'content'}).text[34:-51]
            text = text.replace('\r', '').replace('\xa0', '').replace('\n\n', '\n')
            text_htmls = text2htmls(chap_name, text)
            textfile = text_path + '/'+str(chap_no).zfill(2)+'.xhtml'
            with open(textfile, 'w+', encoding='utf-8') as f:
                f.writelines(text_htmls)

    def get_image(self, volume):
        url = volume["img_urls"]
        if url=='':
            return
        img_path = self.img_path
        html = self.get_html(url)
        bf = BeautifulSoup(html, 'html.parser')
        img_url_find = bf.findAll('div', {'class': 'divimage'})
        img_url_list = []
        for img_url_txt in img_url_find:
            img_url = img_url_txt.find('a').get('href')
            img_url_list.append(img_url)
        
        for img_no, img_url in enumerate(tqdm(img_url_list)):
            r=requests.get(img_url, headers=self.header)
            with open(img_path+'/'+str(img_no).zfill(2)+'.jpg', 'wb') as f:
                f.write(r.content) #写入二进制内容

    def get_cover(self, volume):
        textfile = os.path.join(self.text_path, 'cover.xhtml')
        url = volume["img_urls"]
        if url=='':
            img_htmls = get_cover_html(0, 0)
            with open(textfile, 'w+', encoding='utf-8') as f:
                f.writelines(img_htmls)
            return
        
        imgfile = os.path.join(self.img_path, '00.jpg')
        img = cv2.imread(imgfile)
        img_htmls = get_cover_html(img.shape[1], img.shape[0])
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(img_htmls)

    def get_color_page(self, color_num=0):

        if color_num>0:
            colorimg_htmls = get_color_html(color_num)
            textfile = self.text_path + '/color.xhtml'
            with open(textfile, 'w+', encoding='utf-8') as f:
                f.writelines(colorimg_htmls)


    def get_toc(self, volume):
        toc_htmls = get_toc_html(self.title, volume["chap_names"])
        textfile = self.temp_path + '/OEBPS/toc.ncx'
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(toc_htmls)

    def get_content(self, volume):
        num_chap = len(volume["chap_names"])
        num_img = len(os.listdir(self.img_path))
        content_htmls = get_content_html(self.title, self.author, num_chap, num_img)
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
        epub_file = self.epub_path + '/' + self.title + '.epub'
        with zipfile.ZipFile(epub_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(self.temp_path):
                fpath = dirpath.replace(self.temp_path,'') #这一句很重要，不replace的话，就从根目录开始复制
                fpath = fpath and fpath + os.sep or ''#这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
                for filename in filenames:
                    zf.write(os.path.join(dirpath, filename), fpath+filename)
        shutil.rmtree(self.temp_path)
        return epub_file

        

if __name__=='__main__':
    args = parse_args()
    color_page_num = args.color_page
    editer = Editer(root_path='out', book_no=args.book_no, book_cls=args.book_cls, volume_no=args.volumn_no)

    print('正在获取书籍信息....')
    volume = editer.get_index_url()

    print('正在下载文本....')
    editer.get_text(volume)

    print('正在下载插图....')
    editer.get_image(volume)

    print('正在编辑元数据....')
    editer.get_cover(volume)
    editer.get_color_page(color_page_num)
    editer.get_toc(volume)
    editer.get_content(volume)
    editer.get_epub_head()

    print('正在生成电子书....')
    epub_file = editer.get_epub()
    print('生成成功！', '电子书路径【', epub_file, '】')
    