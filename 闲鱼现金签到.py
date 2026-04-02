import sys
import time
import uiautomator2 as u2

from utils import get_current_app, task_loop, FISH_APP, start_app, video_task, print_error

d = u2.connect()
start_app(d, FISH_APP, init=True)
screen_width, screen_height = d.window_size()
ctx = d.watch_context()
ctx.when("暂不升级").click()
ctx.when("放弃").click()
ctx.when("确定").click()
ctx.start()
have_clicked = dict()


def check_in_task():
    task_view = d.xpath('//android.webkit.WebView[@text="天天红包"]/android.view.View/android.view.View[5]')
    return task_view.exists


def back_to_task():
    print("开始返回任务页面")
    while True:
        temp_package, temp_activity = get_current_app(d)
        if temp_package is None or temp_activity is None or "Ext2ContainerActivity" in temp_activity:
            continue
        print(f"{temp_package}--{temp_activity}")
        if FISH_APP not in temp_package:
            print(f"回到原始APP,{FISH_APP}")
            start_app(d, FISH_APP)
            jump_btn = d(resourceId="com.taobao.taobao:id/tv_close", text="跳过")
            if jump_btn.exists:
                jump_btn.click()
                time.sleep(2)
        else:
            if check_in_task():
                print("当前是任务列表画面，不能继续返回")
                break
            else:
                if "com.taobao.idlefish.maincontainer.activity.MainActivity" in temp_activity:
                    print("进入到闲鱼首页，重新进入任务页。")
                    to_task()
                    continue
                close_btn1 = d.xpath("//android.widget.FrameLayout[@resource-id='com.alipay.multiplatform.phone.xriver_integration:id/frameLayout_rightButton1']/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.FrameLayout[2]")
                if close_btn1.exists:
                    print("点击关闭小程序按钮")
                    close_btn1.click()
                    time.sleep(1)
                    continue
                task_view1 = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]')
                if task_view1.exists:
                    close_btn2 = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]/preceding-sibling::android.view.View[1]')
                    if close_btn2.exists:
                        print("点击关闭限时下单任务按钮")
                        close_btn2.click()
                        time.sleep(1)
                        continue
                print("点击后退")
                d.press("back")
                time.sleep(0.2)


def to_task():
    time.sleep(5)
    while True:
        me_btn = d(className="android.widget.TextView", text="我的")
        if me_btn.exists:
            print("点击我的按钮")
            me_btn.click()
            time.sleep(4)
        if d(className="android.widget.TextView", resourceId="com.taobao.idlefish:id/personal_user_info_nick_name").exists:
            break
    sign_btn = d(className="android.widget.TextView", text="现金签到")
    if sign_btn.exists:
        print("点击现金签到按钮")
        sign_btn.click()
        time.sleep(8)
    else:
        print("没有现金签到任务，退出程序")
        sys.exit(0)
    show_task()


def show_task():
    while True:
        web_view = d.xpath('//android.webkit.WebView[@text="天天红包"]')
        dialog_view = d.xpath('//android.webkit.WebView[@text="天天红包"]/android.view.View/android.view.View[5]')
        if web_view.exists and dialog_view.exists:
            break
        if web_view.exists and not dialog_view.exists:
            more_btn = d(className="android.widget.TextView", text="更多红包")
            if more_btn.exists:
                print("点击更多红包按钮")
                more_btn.click()
                time.sleep(2)


to_task()
ling_btn = d(className="android.widget.TextView", text="领红包")
if ling_btn.exists:
    print("点击领红包")
    ling_btn.click()
    time.sleep(2)
while True:
    try:
        time.sleep(4)
        show_task()
        get_btn = d.xpath('//android.webkit.WebView[@text="天天红包"]/android.view.View/android.view.View[5]/android.view.View/android.widget.TextView[@text="领红包"]')
        if get_btn.exists:
            print("点击领红包")
            get_btn.click()
            time.sleep(1)
            continue
        to_btn = d.xpath('//android.webkit.WebView[@text="天天红包"]/android.view.View/android.view.View[5]/android.view.View/android.widget.TextView[@text="去完成"]')
        if to_btn.exists:
            name_view = d.xpath('(//android.webkit.WebView[@text="天天红包"]/android.view.View/android.view.View[5]/android.view.View/android.widget.TextView[@text="去完成"])[1]/preceding-sibling::android.view.View[1]/android.widget.TextView[1]')
            task_name = None
            if name_view.exists:
                task_name = name_view.text
                print(f"点击任务：{task_name}")
            to_btn.click()
            time.sleep(3)
            if task_name:
                if "视频" in task_name:
                    video_task(d)
                else:
                    if "神奇鱼塘" in task_name or "闲鱼币" in task_name:
                        time.sleep(5)
                        back_to_task()
                    else:
                        task_loop(d, back_to_task, is_fish=True)
        else:
            print("找不到任务了，退出循环")
            break
    except Exception as e:
        print_error()
        continue
close_btn1 = d.xpath('//android.webkit.WebView[@text="天天红包"]/android.view.View/android.view.View[5]/android.widget.TextView')
if close_btn1.exists:
    print("点击关闭弹窗开始开红包")
    close_btn1.click()
    time.sleep(2)
while True:
    try:
        time.sleep(4)
        count_view = d.xpath('//android.widget.TextView[contains(@text, "剩余红包")]/following-sibling::android.widget.TextView[1]')
        if count_view.exists:
            count = int(count_view.text)
            print(f"剩余红包{count}个")
        else:
            break
        coin_view = d.xpath('//android.webkit.WebView[@text="天天红包"]/android.view.View/android.view.View[4]/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View/android.widget.TextView[3]')
        if coin_view.exists:
            print("有现金打款，点击收下")
            coin_view.click()
            time.sleep(3)
        throw_btn = d(className="android.view.View", resourceId="bigOpenBtn")
        if throw_btn.exists:
            throw_btn.click()
            time.sleep(2)
    except Exception as e:
        print_error()
        continue
print("任务完成。。。")
ctx.stop()
