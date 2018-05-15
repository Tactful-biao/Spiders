## 项目介绍：

### 在这个文件夹下的爬虫程序都统一写在这个README里面, 欢迎与我交流

1. 简单小爬虫
  + baike.py  这是一个爬取糗事百科的简单的爬虫。详情请参考我的博客：[爬取糗事百科/][1]
  + mmjpg.py  是一个爬虫程序爬取 [http://www.mmjpg.com](http://www.mmjpg.com)代码中已经加入了详细的注释.当然如果你还有什么不懂的，欢迎来我的博客留言：[http://bbiao.me](http://bbiao.me)
  + seed.py  是爬取电影天堂所有电影种子的一个网络爬虫。可以参考我的博客：[爬取《电影天堂》所有电影种子][2]
  + mzitu.py是一个爬虫程序，爬取妹子图[http://www.mzitu.com](http://www.mzitu.com)代码中加入了多线程，爬取速度是十分快的
  代码没有添加注释

2. 12306
   ### 该目录下是一个爬取12306的小程序
   - setup.py 这是一个python的构建工具
   - station_name.py 这是一个获取12306全国所有车站的简写信息的脚本
   - station.py 这个脚本里面包含两个列表，一个是车站中文名，另一个是车站的英文简写
   - tickets.py 这是一个真正获取12306票数信息的脚本，脚本中对数据进行了清理

3. 查询
   该目录下都是一些查询的脚本.
   + KY.py 是查询考研的脚本
   + MHK.py 是查询MHK三级和四级成绩的脚本
   + NCRE.py 是查询全国计算机二级(高级Office)的脚本
   + cet_new.py 是查询大学英语四六级的一个脚本。
   + movie.py 是一个资源获取的脚本(各种资源，只需给个关键词就可以获得想要的东西，自己去探索)
     + 用法： python3 movie.py 想要的资源名称
       ![4][4]
     + 另外，我做了一个网页版的查询, 地址在[http://xxooml.xyz/](http://xxooml.xyz/)，提供种子链接，电脑端如果安装了迅雷等下载器，点击Megent Link就可以直接下载，手机端不支持直接下载。欢迎去体验。多多支持，多多打赏。
     效果如下：
     ![5][5]

   脚本中有简单的注释。如果有不了解的地方，欢迎到我的博客上留言。

4. 监票脚本
  ### 该文件夹下的脚本是对12306中的脚本进行了扩展，添加了监控的功能，其实就是加入了一个发邮件的功能。详情可以参考该文件夹下的README

5. Qzone是一个爬取QQ空间的爬虫，爬取了QQ好友的全部说说，留言，以及个人信息等数据，在我的博客中对该爬虫的思路等进行了简单的介绍
，可以参考我的这篇文章[<爬取QQ空间>][3]

 >爬虫QZone通过Phantomjs模拟登录获取Cookies进行操作，爬取了全部好友的个人说说：

 + 好友姓名(name)
 + 设备(source)
 + 具体内容(content)
 + 发表时间(createTime)
 + 转发量(forward)
 + 评论内容(comment)
 + 配图(pics)
 + 点赞数(like)
 + 具体点赞的人(likers, qq号, 性别, 地址, 星座))

 >留言爬取的内容包括

 * 好友姓名(owner)
 * 总留言数(total)
 * 留言人的昵称(name)
 * 留言人的qq(qq)
 * 留言的时间(time)
 * 留言的内容(content)
 * 回复的内容(replyList(包括回复人的昵称和回复的内容))

 >个人档的爬取包括

 + 好友空间名称(spacename)
 + 好友昵称(nickname)
 + 空间标语(desc)
 + 性别(sex)
 + 年龄(age)
 + 生日(birthday)
 + 星座(constellation)
 + 国家(country)
 + 省份(province)
 + 城市(city)
 + 家乡(hometown)
 + 婚姻状态(marriage)
 + 职业(chreer)
 + 详细地址(address)

数据统一存储在mongodb中，分了四个表，分别是black(记录无法访问空间的好友), information(存储个人信息的表), board(存储留言的表), mood(存储说说的表).

另外点赞的人的爬取需要加上时间限制(大于3秒请求不会出现问题)，如果不加的话，会出现系统繁忙等问题。(亲身经历)

该项目我会不断完善的，如果有什么好的建议或者疑问可以在issues中提，我会尽力解决。






[1]: http://bbiao.me/2017/09/01/%E7%88%AC%E5%8F%96%E7%B3%97%E4%BA%8B%E7%99%BE%E7%A7%91/
[2]: http://bbiao.me/2017/09/17/%E7%88%AC%E5%8F%96%E3%80%8A%E7%94%B5%E5%BD%B1%E5%A4%A9%E5%A0%82%E3%80%8B%E6%89%80%E6%9C%89%E7%94%B5%E5%BD%B1%E7%A7%8D%E5%AD%90/
[3]: http://bbiao.me/2017/11/23/%E7%88%AC%E5%8F%96QQ%E7%A9%BA%E9%97%B4/
[4]: http://oxwgzg29g.bkt.clouddn.com/useage.png
[5]: http://oxwgzg29g.bkt.clouddn.com/use2.png
