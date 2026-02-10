import time

import uiautomator2 as u2
from utils import check_chars_exist, other_app, get_current_app, select_device, task_loop, check_verify, start_app, TB_APP

unclick_btn = []
have_clicked = dict()
is_end = False
error_count = 0
in_other_app = False
time1 = time.time()
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, TB_APP, init=True)
ctx = d.watch_context()
ctx.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
ctx.when("O1CN01sORayC1hBVsDQRZoO_!!6000000004239-2-tps-426-128.png_").click()
ctx.when("领取今日奖励").click()
ctx.when("确认").click()
ctx.when("确定").click()
ctx.when("刷新").click()
ctx.when("点击刷新").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[contains(text(), '-tps-')]").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
ctx.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']//android.widget.ImageView[@content-desc='关闭按钮']").click()
# ctx.when(xpath="//android.widget.TextView[@package='com.eg.android.AlipayGphone']").click()
ctx.start()
time.sleep(3)


def check_in_task():
    package_name, activity_name = get_current_app(d)
    if package_name == "com.taobao.taobao" and "com.taobao.themis.container.app.TMSActivity" in activity_name:
        coin_view = d(className="android.webkit.WebView", text="淘金币首页")
        if coin_view.exists:
            earn_btn1 = d(className="android.widget.TextView", text="赚金币抵钱")
            earn_btn2 = d(className="android.widget.TextView", text="今日累计奖励")
            if earn_btn1.exists or earn_btn2.exists:
                return True
            else:
                earn_btn3 = d(className="android.widget.TextView", textContains="赚更多金币")
                if earn_btn3.exists:
                    earn_btn3.click()
                    time.sleep(3)
                    return True
    return False


def back_to_task():
    print("开始返回任务页面")
    while True:
        temp_package, temp_activity = get_current_app(d)
        if temp_package is None or temp_activity is None or "Ext2ContainerActivity" in temp_activity:
            continue
        print(f"{temp_package}--{temp_activity}")
        if TB_APP not in temp_package:
            print(f"回到原始APP,{TB_APP}")
            start_app(d, TB_APP)
            jump_btn = d(resourceId="com.taobao.taobao:id/tv_close", text="跳过")
            if jump_btn.exists:
                jump_btn.click()
                time.sleep(2)
        else:
            if check_in_task():
                print("当前是任务列表画面，不能继续返回")
                break
            else:
                close_btn1 = d.xpath("//android.widget.FrameLayout[@resource-id='com.alipay.multiplatform.phone.xriver_integration:id/frameLayout_rightButton1']/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.FrameLayout[2]")
                if close_btn1.exists:
                    print("点击关闭小程序按钮")
                    close_btn1.click()
                    time.sleep(1)
                    continue
                task_view = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]')
                if task_view.exists:
                    close_btn2 = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]/preceding-sibling::android.view.View[1]')
                    if close_btn2.exists:
                        print("点击关闭限时下单任务按钮")
                        close_btn2.click()
                        time.sleep(1)
                        continue
                print("点击后退")
                d.press("back")
                time.sleep(0.3)


def find_coin_btn():
    coin_btn = d(className="android.widget.FrameLayout", description="领淘金币", clickable=True)
    if coin_btn.exists:
        d.double_click(coin_btn[0].center()[0], coin_btn[0].center()[1])
        time.sleep(5)
    else:
        d(className="android.view.View", description="搜索栏").click()
        d(resourceId="com.taobao.taobao:id/searchEdit").send_keys("淘金币")
        time.sleep(3)
        d(className="android.view.View", descriptionContains="淘金币").click()
        time.sleep(5)


ctx.wait_stable()
close_btn = d(className="android.widget.ImageView", description="关闭按钮")
if close_btn and close_btn.exists:
    close_btn.click()
    time.sleep(3)
find_coin_btn()

# 因2025双十一活动，需要回旧版本后继续任务
earn_btn = d(className="android.widget.Button", textContains="回日常版")
if earn_btn.exists(timeout=4):
    earn_btn.click()
    time.sleep(3)
earn_btn = d(className="android.widget.TextView", textMatches="签到领金币|点击签到")
if earn_btn.exists(timeout=4):
    earn_btn.click()
    time.sleep(5)
earn_btn = d(className="android.widget.TextView", textContains="赚更多金币")
if earn_btn.exists(timeout=4):
    earn_btn.click()
    time.sleep(3)
else:
    raise Exception("没有找到金币任务按钮")
print("点击开始做任务")
finish_count = 0
while True:
    try:
        in_other_app = False
        time.sleep(4)
        check_verify(d)
        earn_btn = d(className="android.widget.TextView", text="赚更多金币")
        if earn_btn.exists and not d(className="android.widget.TextView", text="赚金币抵钱").exists:
            earn_btn.click()
            time.sleep(2)
            continue
        draw_down_btn = d(className="android.widget.Button", text="立即领取")
        if draw_down_btn.exists:
            draw_down_btn.click()
            time.sleep(2)
        print("开始查找按钮。。。")
        get_btn = d(className="android.widget.Button", text="领取奖励")
        if get_btn.exists:
            get_btn.click()
            print("点击领取奖励")
            time.sleep(2)
            # finish_count = finish_count + 1
            # if finish_count % 20 == 0:
            #     d.swipe_ext("up", scale=0.2)
            #     time.sleep(4)
            continue
        de_btn = d(className="android.widget.Button", text="点击得")
        if de_btn.exists:
            de_btn.click()
            print("点击点击得")
            time.sleep(4)
            continue
        to_btn = d(className="android.widget.Button", textMatches="去完成|去逛逛|去浏览|逛一逛|立即领|去领取|去看看|搜一下|玩一把|捐一笔|逛一下")
        if to_btn.exists:
            need_click_view = None
            need_click_index = 0
            task_name = None
            for index, view in enumerate(to_btn):
                text_div = view.sibling(className="android.view.View", instance=0).child(className="android.widget.TextView", instance=0)
                if text_div.exists:
                    task_name = text_div.get_text()
                    if check_chars_exist(task_name):
                        if view not in unclick_btn:
                            unclick_btn.append(view)
                        continue
                    if task_name in have_clicked:
                        if have_clicked[task_name] >= 2:
                            continue
                    need_click_index = index
                    need_click_view = view
                    break
            if need_click_view:
                print("点击按钮", task_name)
                if have_clicked.get(task_name) is None:
                    have_clicked[task_name] = 1
                else:
                    have_clicked[task_name] += 1
                if check_chars_exist(task_name, other_app):
                    in_other_app = True
                need_click_view.click()
                time.sleep(3.5)
                task_loop(d, back_to_task)
            else:
                error_count += 1
                print("未找到可点击按钮", error_count)
                if error_count >= 2:
                    break
    except Exception as e:
        print(e)
        continue
ctx.close()
print(f"共自动化完成{finish_count}个任务")
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
time2 = time.time()
minutes, seconds = divmod(int(time2 - time1), 60)  # 同时计算分钟和秒
print(f"共耗时: {minutes} 分钟 {seconds} 秒")
