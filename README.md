# danmu.fm 

这是一个用来获取斗鱼TV指定主播的弹幕的命令行小工具.最近更新时间为 2016-07-14

> **如果对你有帮助记得点赞哦**

使用参见
http://www.jianshu.com/p/2e0d14978ae9

原理参见
http://www.jianshu.com/p/ef0225b6bb0e

## 如何使用

首先本程序在Py3下执行(不要给程序提兼容Py2的PR或者兼容Windows平台,谢谢).依赖requests以及外部程序wget和mplayer

如果你是MacOSX的用户,你只需要

```bash
brew install mplayer
pip3 install danmu.fm
# 查看海量弹幕,并且在当前目录下缓存视频
danmu.fm -q 3 -m 1 -p . -vvvv  http://www.douyu.com/wt55kai
# 查看海量弹幕,并且直接调用MPlayer查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
# 查看正常弹幕,并且直接调用MPlayer查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
```

如果你是Ubuntu 用户,你只需要

```bash
pip3 install danmu.fm
# 查看海量弹幕,并且在当前目录下缓存视频
danmu.fm -q 3 -m 1 -p . -vvvv  http://www.douyu.com/wt55kai
# 查看海量弹幕,并且直接调用MPlayer查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
# 查看正常弹幕,并且直接调用MPlayer查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
```

如果Ubuntu环境报错,请立即帮忙提Issue,我会尽快解决.

## 感谢

 - 往事如风
 - douban.fm (Python版本)

## 最近更新时间

 - **Update 20160714 : ** 更新Python客户端, 微小调整.版本提升为0.3.1
 - **Update 20160611 : ** 更新Python客户端, 引入Click进行命令行构建,重写一半的逻辑.版本提升为0.3.0
 - **Update 20160609 : ** 更新Python客户端, 修复由于斗鱼网页版面修改带来的小问题,直接开启海量弹幕模式(请大家不要问我为什么端午节这一天为什么闲着没事更新代码,这个真的和情人节是同一个原因).
 - **Update 20160220 : ** 更新Python客户端, 增加直播视频的Live获取,以及Mac平台下面的Mplayer的视频播放.代码均放在Github上面. [GitHub - twocucao/danmu.fm: douyutv danmu 斗鱼TV 弹幕助手**](//link.zhihu.com/?target=https%3A//github.com/twocucao/danmu.fm)
 - **Update 20160214 : ** 更新Python和Ruby客户端(请大家不要问我为什么情人节这一天为什么闲着没事更新代码)**

## TO_DO_LIST

 - [Done]重构代码,引入Click作为命令行构建工具
 - [Done]增加异步获取socket消息(改用多线程实现,PS:单线程由于IO问题只能获取8条每秒)
 - [Done]增加缓存视频功能
 - [ToDo]增加PostgreSQL作为消息缓存数据库(用于最终统计)
 - [ToDo]增加统计功能,增加针对弹幕的文本分析功能

## License

MIT


