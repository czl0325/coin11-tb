# coin11-tb
使用uiautomator2自动化完成2024年淘宝双11的金币任务，淘金币任务，芭芭农场任务，闲鱼任务。

需要安装adb，自行百度教程。
使用教程请看抖音
```
3.53 04/14 X@z.TY bnD:/ 自动化完成淘宝任务教程  https://v.douyin.com/i5xNsWVx/ 复制此链接，打开Dou音搜索，直接观看视频！
```
或者快手
```
https://v.kuaishou.com/nGmUFX 自动化完成淘宝任务教程 该作品在快手被播放过1次，点击链接，打开【快手极速版】直接观看！
```

* 使用uiauto.dev查看ui组件
```
pip3 install uiautodev
# 启动
uiauto.dev
```

adb命令，获取当前打开的app包名和类名
```shell
adb shell dumpsys window | grep mCurrentFocus
adb shell dumpsys window | findstr mCurrentFocus
```

目前淘宝芭芭农场和淘金币任务相对完善，其他的还有问题。
$\color{red}{目前的问题是，uiautomator2将列表上滑一页后，获取的数据还是上一页的，这个问题已反馈作者但未解决。}$

```shell
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png .
adb shell rm /sdcard/screenshot.png
```
```shell
adb shell uiautomator dump /sdcard/window_dump.xml
adb pull /sdcard/window_dump.xml .
adb shell rm /sdcard/window_dump.xml
```