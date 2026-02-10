import time

import uiautomator2 as u2
from uiautomator2 import Direction
from utils import check_chars_exist, other_app, get_current_app, task_loop, select_device, check_verify, start_app, TB_APP

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
screen_width, screen_height = d.window_size()
time.sleep(5)
# https://dl.ncat1.app/


def check_in_task():
    package_name, activity_name = get_current_app(d)
    if package_name != "com.taobao.taobao":
        return False
    if "com.taobao.themis.container.app.TMSActivity" in activity_name:
        if d(className="android.webkit.WebView", text="芭芭农场").exists:
            if d(className="android.widget.TextView", text="肥料明细").exists:
                return True
            else:
                find_fertilizer_btn()
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


# 查找芭芭农场按钮
def find_farm_btn():
    print("开始查找芭芭农场按钮")
    no_found_count = 0
    while True:
        farm_btn = d(className="android.widget.FrameLayout", description="芭芭农场")
        if farm_btn.exists(timeout=5):
            farm_btn.click()
            time.sleep(12)
        temp_btn = d(className="android.widget.Button", textContains="集肥料")
        new_ui = d(resourceId="game-canvas-fuguo", className="android.widget.Image")
        if temp_btn.exists or new_ui.exists:
            break


# 查找集肥料按钮
def find_fertilizer_btn():
    print("开始查找集肥料按钮...")
    while True:
        fertilize_btn = d(className="android.widget.Button", textContains="集肥料")
        if fertilize_btn.click_exists(timeout=2):
            print("点击集肥料按钮")
            time.sleep(12)
            if check_in_task():
                break
        else:
            new_ui = d(resourceId="game-canvas-fuguo", className="android.widget.Image")
            if new_ui.exists:
                print(f"点击靠近的集肥料按钮, {screen_width * 0.7}, {new_ui.bounds()[3] - 50}")
                d.click(screen_width * 0.7, new_ui.bounds()[3] - 50)
                time.sleep(12)
                if check_in_task():
                    break
    print("进入任务页面")


d.watcher.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
d.watcher.when(xpath="//android.app.Dialog//android.widget.Button[contains(text(), '-tps-')]").click()
d.watcher.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
d.watcher.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']//android.widget.ImageView[@content-desc='关闭按钮']").click()
# d.watcher.when(xpath="//android.widget.TextView[@package='com.eg.android.AlipayGphone']").click()
d.watcher.when("O1CN01sORayC1hBVsDQRZoO_!!6000000004239-2-tps-426-128.png_").click()
d.watcher.when("跳过").click()
d.watcher.when("点击刷新").click()
d.watcher.when("刷新").click()
d.watcher.when("点击重试").click()
# d.watcher.when("关闭").click()
d.watcher.start()
find_farm_btn()
find_fertilizer_btn()
finish_count = 0
while True:
    try:
        print("开始查找按钮")
        check_verify(d)
        time.sleep(4)
        in_other_app = False
        sign_btn = d(className="android.widget.Button", text="去签到")
        if sign_btn.exists:
            sign_btn.click()
            time.sleep(2)
        to_btn = d(className="android.widget.Button", textMatches="去完成|去浏览|去领取")
        if to_btn.exists:
            need_click_view = None
            need_click_index = 0
            task_name = None
            for index, view in enumerate(to_btn):
                text_div = view.sibling(className="android.view.View", instance=0).child(className="android.widget.TextView", instance=0)
                if text_div.exists:
                    if check_chars_exist(text_div.get_text(), ["游戏", "一元抢", "开通", "搜索兴趣商品下单", "买精选商品", "1元抢", "下单", "淘宝秒杀", "消消乐", "3元3件", "中国移动", "百度地图"]):
                        if view not in unclick_btn:
                            unclick_btn.append(view)
                        continue
                    task_name = text_div.get_text()
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
                time.sleep(4)
                task_loop(d, back_to_task)
                finish_count = finish_count + 1
            else:
                error_count += 1
                print("未找到可点击按钮", error_count)
                if error_count >= 2:
                    break
    except Exception as e:
        print(e)
        continue
d.watcher.remove()
print(f"共自动化完成{finish_count}个任务")
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
time2 = time.time()
minutes, seconds = divmod(int(time2 - time1), 60)  # 同时计算分钟和秒
print(f"共耗时: {minutes} 分钟 {seconds} 秒")
