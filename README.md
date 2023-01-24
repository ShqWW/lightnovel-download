

# 轻小说文库 EPUB格式下载

## 简介
&ensp; &ensp; [轻小说文库](https://www.wenku8.net)下载小脚本，只需要根据网址填入小说信息即可下载并打包成EPUB格式小说。

&ensp; &ensp; 由python语言编写，按Sigil提供的默认EPUB模板打包。

&ensp; &ensp; 不足：由于轻小说文库没有提供插图在正文中的位置，所以目前只能下载并打包插图到EPUB的图片文件夹，并需要网友们手动指明彩页的页数，对于正文中的黑白插图，需要手动使用EPUB编辑器自行插入到正文中，如果不插入也不会影响正文阅读。目前没有想到针对这一点的解决方法，欢迎网友们提供改进方法。

## 安装

&ensp; &ensp; 自行使用pip命令， 安装所有[lightnovel.py](https://github.com/ShengqiWang/lightnovel-download/blob/master/lightnovel.py)中所有导入的包。由于包版本变化较大，就不再提供安装命令了，尽量安装最新版即可。


## 使用说明

1. 手动获取基本信息

&ensp; &ensp; 通过浏览器打开要下载的小说页面（以“空之境界”为例），点击“小说目录”：
![](/fig/1.png)


&ensp; &ensp; 进入“小说目录”：
![](/fig/2.png)

&ensp; &ensp; 先记下网址中的书籍类别号和书籍号。比如上图中绿框的书籍类别号为0，书籍号为112。

&ensp; &ensp; 然后决定自己下载的卷号（按网页排布的卷顺序来，而不是根据卷名称，因为有的小说有番外之类的插入在中间，实际顺序不一定等于卷名称），比如这里要下载从上向下数第2个卷，即上图红圈中的“第二章 中”，那么记下卷编号对应2即可。

&ensp; &ensp; 然后点进需要下载的对应章节的插图链接
![](/fig/3.png)

&ensp; &ensp; 然后点进需要下载的对应章节的插图链接
数一数有几张彩图
![](/fig/4.png)
以上图为例是有2张彩图，那么记下2这个数字。该脚本默认第一张彩图是封面，后面的彩图属于彩页部分。黑白图只下载打包，不会插入到正文，理由见开头。



2. 万事具备 开始运行

```
python lightnovel.py --book_cls 书籍类别号 --book_no 书籍号 --volumn_no  卷号 --color_page 彩图数量
```

&ensp; &ensp; 将上面的命令替换成具体的数字即可，比如下载上面的示例小说:
```
python lightnovel.py --book_cls 0 --book_no 112 --volumn_no 2 --color_page 2
```

&ensp; &ensp; 在脚本文件夹下使用命令行运行上述命令，以window11为例：

&ensp; &ensp; 右键 终端打开：
![](/fig/5.png)

&ensp; &ensp; 输入命令开始下载打包：
![](/fig/6.png)

&ensp; &ensp; 下载脚本会自动获取书籍的一些作者标题信息。
&ensp; &ensp; 最后在"out"文件夹下就可以找到EPUB格式的书籍文件了！！！




