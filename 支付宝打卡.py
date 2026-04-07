import re
import time

import uiautomator2 as u2
from utils import ALIPAY_APP, start_app, get_current_app, easy_ocr, find_button_multiscale

time1 = time.time()
d = u2.connect()
start_app(d, ALIPAY_APP, init=True)
screen_width, screen_height = d.window_size()
d.watcher.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
d.watcher.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
d.watcher.when(xpath='//android.widget.RelativeLayout[@resource-id="com.alipay.android.living.dynamic:id/cubeContainerView"]/android.widget.FrameLayout/android.widget.LinearLayout/android.view.ViewGroup/android.view.ViewGroup/android.widget.FrameLayout/android.widget.LinearLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]').click()
d.watcher.when(xpath='//android.widget.FrameLayout[@content-desc="推荐广告"]/following-sibling::android.widget.LinearLayout[1]/android.widget.ImageView').click()
d.watcher.start()


def is_card_home():
    task_view1 = d(className="android.widget.TextView", text="今日待办")
    task_view2 = d(className="android.widget.TextView", textMatches=r"打卡(记录|进度)")
    if task_view1.exists and task_view2.exists:
        return True
    return False


def back_to_card():
    print("开始退出")
    while True:
        if is_card_home():
            print("当前在任务页面，退出循环。。。")
            break
        cancel_btn1 = d(className="android.widget.Button", resourceId="android:id/button2", textMatches=r"取消.*?")
        if cancel_btn1.exists:
            print("点击取消")
            cancel_btn1.click()
            time.sleep(1)
        cancel_btn2 = d(className="android.widget.Button", resourceId="com.alipay.mobile.antui:id/btn_cancel")
        if cancel_btn2.exists:
            print("点击取消")
            cancel_btn2.click()
            time.sleep(1)
        close_btn1 = d(className="android.widget.FrameLayout", description="关闭")
        if close_btn1.exists:
            print("点击关闭")
            close_btn1.click()
        else:
            print("点击后退")
            d.press("back")
        time.sleep(1)


video_btn = d(className="android.widget.TextView", resourceId="com.alipay.android.tablauncher:id/tab_description", text="视频")
if video_btn.exists:
    print("点击视频按钮。。。")
    d.click(video_btn.center()[0], video_btn.bounds()[1] - 100)
    time.sleep(5)
pt1, _, _ = find_button_multiscale(d.screenshot(format="opencv"), "./img/img_getToday.png")
if pt1:
    d.click(pt1[0], pt1[1] + 500)
    time.sleep(2)
task_btn = d(className="android.widget.FrameLayout", resourceId="com.alipay.android.living.dynamic:id/iconAndCdpContainerFl")
if task_btn.exists:
    print("点击视频任务按钮。。。")
    task_btn.click()
    time.sleep(5)
    card_btn = d(className="android.widget.TextView", textMatches=r"去(打卡|续签)")
    if card_btn.exists:
        print("点击去打卡。。。")
        card_btn.click()
        time.sleep(5)
        while True:
            time.sleep(5)
            print("开始任务循环")
            has_task = False
            sign_btn = d(className="android.widget.TextView", text="去签到")
            if sign_btn.exists:
                has_task = True
                print("点击去签到。。。")
                sign_btn.click()
                time.sleep(3)
                continue
            browse_btn = d(className="android.widget.TextView", text="去浏览")
            if browse_btn.exists:
                has_task = True
                print("点击去浏览。。。")
                browse_btn.click()
                time.sleep(3)
                browse_start_time = time.time()
                while True:
                    browse_end_time = time.time()
                    if browse_end_time - browse_start_time > 35:
                        break
                    d.swipe(200, 1000, 181, 500)
                    time.sleep(3)
                back_to_card()
                continue
            play_btn = d(className="android.widget.TextView", text="去试玩")
            if play_btn.exists:
                has_task = True
                print("点击去试玩。。。")
                play_btn.click()
                time.sleep(35)
                back_to_card()
                continue
            see_btn = d.xpath('//android.widget.TextView[@text="去看看"]')
            if see_btn.exists:
                name_view = d.xpath(f'(//android.widget.TextView[@text="去看看"])[1]/preceding-sibling::android.widget.TextView[2]')
                name_text = ""
                if name_view.exists:
                    name_text = name_view.text
                print(f"任务名：{name_text}")
                (see_btn.all())[0].click()
                has_task = True
                time.sleep(5)
                if bool(re.fullmatch(r"看\d+个指定视频", name_text)):
                    time.sleep(35)
                else:
                    start_time = time.time()
                    last_text = 0
                    time_list = []
                    direction = "UP"
                    while True:
                        try:
                            end_time = time.time()
                            minutes, seconds = divmod(int(end_time - start_time), 60)
                            region_view = d.xpath('//android.widget.RelativeLayout[@resource-id="com.alipay.android.living.dynamic:id/cubeContainerView"]/android.widget.FrameLayout/android.widget.LinearLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.widget.LinearLayout')
                            if region_view.exists:
                                print("找到时间组件，开始识别时间。。。")
                                region_screenshot = region_view.get().screenshot()
                                # region_text = paddle_ocr(region_screenshot)
                                region_text = easy_ocr(region_screenshot)
                                print("识别到文字：", region_text)
                                if "完成" in region_text:
                                    break
                                temp_text = re.findall(r".*?看\d+分钟视频.*?(\d+.*?\d+)", region_text)
                                if len(temp_text) > 0:
                                    region_text = temp_text[0]
                                region_text = region_text.replace("：", ".").replace(":", ".")
                                if round(last_text - float(region_text), 2) <= 0.04 and last_text != 0:
                                    print("倒计时停了，上滑视频。。。")
                                    if direction == "UP":
                                        d.swipe(301, screen_height - 500, 322, 500, 0.3)
                                    else:
                                        d.swipe(301, 500, 322, screen_height - 500, 0.3)
                                last_text = float(region_text)
                                time_list.append(last_text)
                                if len(time_list) > 3:
                                    time_list.pop(0)
                                if len(set(time_list)) == 1:
                                    direction = "DOWN" if direction == "DOWN" else "UP"
                            else:
                                print("没有找到时间组件。。。")
                                package_name, _ = get_current_app(d)
                                if package_name != ALIPAY_APP:
                                    d.app_start(ALIPAY_APP, stop=False)
                        except Exception as e:
                            print(e)
                        # d.swipe_ext(Direction.FORWARD)
                        time.sleep(8)
                back_to_card()
                continue
            if not has_task:
                progress_view = d.xpath('//android.widget.TextView[@text="今日待办"]/following-sibling::android.widget.TextView[1]')
                if progress_view.exists:
                    progress_text = progress_view.text
                    print(f"查看任务进度：{progress_text}")
                    if "/" in progress_text:
                        arr = progress_text.split("/")
                        if len(arr) == 2:
                            if int(arr[0]) < int(arr[1]):
                                d.swipe(200, 1000, 181, 600)
                                time.sleep(5)
                                continue
                break
        d.press("back")
    else:
        print("你没有打卡任务，退出任务。。。")
    time.sleep(5)
    chai_btn1 = d(className="android.widget.TextView", text="拆红包")
    if chai_btn1.exists:
        print("点击拆红包")
        chai_btn1.click()
        time.sleep(5)
        chai_btn2 = d(className="android.widget.TextView", textContains="拆惊喜红包")
        if chai_btn2.exists:
            print("点击拆惊喜红包")
            chai_btn2.click()
            time.sleep(5)
        d.press("back")
        time.sleep(5)
    sign_btn = d(className="android.widget.TextView", text="去签到")
    if sign_btn.exists:
        print("点击去签到")
        sign_btn.click()
        time.sleep(3)
        pt, _, _ = find_button_multiscale(d.screenshot(format="opencv"), "./img/img_getToday.png")
        if pt:
            print("点击领今日红包")
            d.click(pt[0], pt[1])
            time.sleep(5)
            print("点击看视频必得红包")
            d.click(pt[0], pt[1] + 50)
            time.sleep(35)
            d.press("back")
d.watcher.remove()
