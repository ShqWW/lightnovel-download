
<div align="center">
  <img src="resource/logo_big.png" width="300" style="margin-right: 3000px;"/> 
</div>

<h1 align="center">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;EPUB下载器
</h1>





[文库吧/轻小说文库](www.wenku8.net)(wenku8)网站小说下载，EPUB打包。

特性:

* Fluent Design风格界面，下载进度与书籍封面显示，主题切换，下载目录自定义。
* 前后端分离，同时支持命令行版本。
* EPUB格式打包，支持多种阅读器。
* 插图排版。
* 书籍批量下载。
* 图片多线程下载。
* 缺失链接自动修复。
* 自定义彩页。
* ...................


有建议或bug可以提issue，由于软件更新频繁，可以加QQ群获得更多信息：563072544

图形界面使用[PyQt-Fluent-Widgets](https://pyqt-fluent-widgets.readthedocs.io/en/latest/index.html)界面编写。

[release](https://github.com/ShqWW/lightnovel-download/releases/tag/downloader)页面发布了已经打包好的exe可执行程序，包括图形化版本和命令行版本(系统最低要求Windows 10)。

界面样例：
<div align="center">
  <img src="resource/example1.png" width="400"/>
  <img src="resource/example2.png" width="400"/>
</div>

## 使用前安装需要的包
```
pip install -r requirements.txt -i https://pypi.org/simple/
```
## 使用命令行模式运行(无需安装图形界面库，支持Linux):
```
python bilinovel.py
```

## 使用图形界面运行:
```
python bilinovel_gui.py
```

## 使用pyinstaller打包:
```
pip install pyinstaller
```
```
pyinstaller -F -w -i .\resource\logo.png --paths=C:\Users\haoru\bilinovel-download .\lightnovel_gui.py --clean
```
```
pyinstaller -F -i .\resource\logo.png --paths=C:\Users\haoru\bilinovel-download .\lightnovel.py --clean
```

## 相关项目：

* [轻小说文库EPUB下载器](https://github.com/ShqWW/lightnovel-download)

* [哔哩轻小说EPUB下载器](https://github.com/ShqWW/bilinovel-download)

* [拷贝漫画EPUB下载器](https://github.com/ShqWW/copymanga-download)



## EPUB书籍编辑和管理工具推荐：
1. [Sigil](https://sigil-ebook.com/) 
2. [Calibre](https://www.calibre-ebook.com/)

