# danmu.fm

这是一个用来获取斗鱼 TV 指定主播的弹幕的命令行小工具。最近更新时间为 2017-07-10

> **如果对你有帮助记得点赞哦**

使用参见
http://www.jianshu.com/p/2e0d14978ae9

原理参见
http://www.jianshu.com/p/ef0225b6bb0e

## 如何使用

首先本程序在 Py3 下执行（不要给程序提兼容 Py2 的 PR 或者兼容 Windows 平台，谢谢）. 依赖 requests 以及外部程序 wget 和 mplayer

如果你是 MacOSX 的用户，你只需要

```bash
brew install mplayer
pip3 install danmu.fm
# 查看海量弹幕，并且在当前目录下缓存视频
danmu.fm -q 3 -m 1 -p . -vvvv  http://www.douyu.com/wt55kai
# 查看海量弹幕，并且直接调用 MPlayer 查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
# 查看正常弹幕，并且直接调用 MPlayer 查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
```

如果你是 Ubuntu 用户，你只需要

```bash
pip3 install danmu.fm
# 查看海量弹幕，并且在当前目录下缓存视频
danmu.fm -q 3 -m 1 -p . -vvvv  http://www.douyu.com/wt55kai
# 查看海量弹幕，并且直接调用 MPlayer 查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
# 查看正常弹幕，并且直接调用 MPlayer 查看视频
danmu.fm -q 3 -m 1 -p 0 -vvvv  http://www.douyu.com/wt55kai
```

如果 Ubuntu 环境报错，请立即帮忙提 Issue, 我会尽快解决。

## 感谢

 - 往事如风
 - douban.fm (Python 版本）

## 最近更新时间

 - **Update 20170710 : ** 感谢 [@jjpprrrr](https://github.com/jjpprrrr) 修复的解析问题 , 版本提升为 0.3.5
 - **Update 20160714 : ** 更新 Python 客户端，微小调整。版本提升为 0.3.1
 - **Update 20160611 : ** 更新 Python 客户端，引入 Click 进行命令行构建，重写一半的逻辑。版本提升为 0.3.0
 - **Update 20160609 : ** 更新 Python 客户端，修复由于斗鱼网页版面修改带来的小问题，直接开启海量弹幕模式（请大家不要问我为什么端午节这一天为什么闲着没事更新代码，这个真的和情人节是同一个原因）.
 - **Update 20160220 : ** 更新 Python 客户端，增加直播视频的 Live 获取，以及 Mac 平台下面的 Mplayer 的视频播放。代码均放在 Github 上面。[GitHub - twocucao/danmu.fm: douyutv danmu 斗鱼 TV 弹幕助手**](//link.zhihu.com/?target=https%3A//github.com/twocucao/danmu.fm)
 - **Update 20160214 : ** 更新 Python 和 Ruby 客户端（请大家不要问我为什么情人节这一天为什么闲着没事更新代码）**

## License

MIT


