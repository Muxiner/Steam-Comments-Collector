# Steam Comments Collector

> 项目源地址：[https://github.com/Chaobs/Steam-Comments-Collector](https://github.com/Chaobs/Steam-Comments-Collector)
> 
> 使用后发现只能爬取简体中文的评论，且仅能爬取 10 个评论
> 
> 在 [https://cloud.tencent.com/developer/article/1085988](https://cloud.tencent.com/developer/article/1085988) 中的评论发现了问题所在，故而做出修改

这个脚本/爬虫用于收集特定的 Steam 游戏商店页面上的 **简体中文** / **English** 评价。  

脚本自带GUI，可以将评论根据好评/差评保存为电子表格文件。


## 安装说明：

1. `clone` 该仓库到本地
2. 安装第三方库：
    ```
      pip install bs4 xlrd​ requests 
    ```
3. 根据您所会的方式，直接运行脚本

## 使用说明：

1. 游戏商店链接在浏览器还有 Steam 客户端都看得到，记得要复制全哦
2. 游戏名称，用于生成的表格名字
3. 评论数量在这里看，需要什么语言的评论，就看这种语言有多少条。评论越多数量越慢，请按照需要设置评论爬取数量
4. 点击“开始获取”收集评论，中间需要时间等待请勿关闭，不要担心会卡死。


## 注意事项：

1. **请勿短时间频繁爬取！！！当出现表格收集到的评论数量过少、评论大量重复出现，或者评论显示不正确时，就是触发了 Steam 的反爬虫机制**。耐心等吧。至于多久会促发反爬虫，又要等多久能恢复，没测试过。
2. 生成的表格最好用 Excel 的去除重复项检查一下
