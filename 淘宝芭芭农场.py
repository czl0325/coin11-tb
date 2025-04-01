import time

import uiautomator2 as u2
from uiautomator2 import Direction
from utils import check_chars_exist, other_app, get_current_app

unclick_btn = []
have_clicked = dict()
is_end = False
error_count = 0
in_other_app = False
time1 = time.time()
d = u2.connect()
d.shell("adb kill-server && adb start-server")
time.sleep(5)
# d.app_stop("com.taobao.taobao")
# d.app_clear('com.taobao.taobao')
# time.sleep(2)
d.app_start("com.taobao.taobao", stop=True, use_monkey=True)
time.sleep(5)
# https://dl.ncat1.app/


def check_in_task():
    package_name, _ = get_current_app(d)
    if d(resourceId="ice-container", className="android.view.View").exists and package_name == "com.taobao.taobao":
        return True
    return False


def operate_task():
    check_count = 3
    while check_count >= 0:
        if not check_in_task():
            break
        print(f"检查次数：{check_count}当前在任务页面，没有执行任务。。。")
        check_count -= 1
        if check_count <= 0:
            return
        time.sleep(2)
    start_time = time.time()
    while True:
        if time.time() - start_time > 18:
            break
        if not in_other_app:
            d.swipe_ext(Direction.FORWARD)
            time.sleep(3)
            d.swipe_ext(Direction.BACKWARD)
            time.sleep(3)
    try_count = 0
    while True:
        if check_in_task():
            print("当前是任务列表画面，不能继续返回")
            break
        else:
            package_name, activity_name = get_current_app(d)
            # if package_name == "com.miui.home":
            #     d.app_start("com.taobao.taobao")
            #     break
            if package_name == "com.taobao.taobao":
                if activity_name == "com.taobao.tao.welcome.Welcome":
                    find_farm_btn()
                    find_fertilizer_btn()
                    break
            d.press("back")
            try_count += 1
            time.sleep(0.2)
            if try_count > 10:
                if package_name != "com.taobao.taobao":
                    d.app_start("com.taobao.taobao", stop=False)
                    time.sleep(10)
                break
    check_error_page()


# 查找芭芭农场按钮
def find_farm_btn():
    print("开始查找芭芭农场按钮")
    no_found_count = 0
    while True:
        farm_btn = d(className="android.widget.FrameLayout", description="芭芭农场")
        if farm_btn.exists(timeout=5):
            farm_btn.click()
            time.sleep(5)
            temp_btn = d(className="android.widget.Button", textContains="集肥料")
            if temp_btn.exists:
                break
        else:
            no_found_count += 1
            time.sleep(3)
            if no_found_count > 3:
                d.app_start("com.taobao.taobao", stop=True, use_monkey=True)
                time.sleep(5)
                find_farm_btn()


# 查找集肥料按钮
def find_fertilizer_btn():
    print("开始查找集肥料按钮...")
    while True:
        fertilize_btn = d(className="android.widget.Button", textContains="集肥料")
        if fertilize_btn.click_exists(timeout=2):
            print("点击集肥料按钮")
            time.sleep(5)
            if d(text="肥料明细").exists:
                print("进入任务页面")
                break


# 任务完成后检查
def check_error_page():
    while True:
        time.sleep(3)
        if d(text="肥料明细").exists:
            break
        package, activity = get_current_app(d)
        if package != "com.taobao.taobao":
            d.app_start("com.taobao.taobao", stop=False)
        else:
            if activity == "com.taobao.tao.welcome.Welcome":
                find_farm_btn()
                find_fertilizer_btn()
            elif activity == "com.taobao.themis.container.app.TMSActivity" and d(className="android.widget.Button", textMatches=r"施肥，肥料\d+，可施肥\d+次").exists:
                try:
                    find_fertilizer_btn()
                except Exception as e:
                    print(e)


d.watcher.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
d.watcher.when(xpath="//android.app.Dialog//android.widget.Button[contains(text(), '-tps-')]").click()
d.watcher.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
d.watcher.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']//android.widget.ImageView[@content-desc='关闭按钮']").click()
# d.watcher.when(xpath="//android.widget.TextView[@package='com.eg.android.AlipayGphone']").click()
d.watcher.when("O1CN01sORayC1hBVsDQRZoO_!!6000000004239-2-tps-426-128.png_").click()
d.watcher.when("点击刷新").click()
d.watcher.start()
find_farm_btn()
find_fertilizer_btn()
finish_count = 0
while True:
    try:
        print("开始查找按钮")
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
                    if check_chars_exist(text_div.get_text(), ["游戏", "一元抢", "快手", "开通", "搜索兴趣商品下单", "买精选商品", "1元抢", "下单", "淘宝秒杀", "消消乐", "3元3件", "中国移动", "百度地图"]):
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
                time.sleep(2)
                search_view = d(className="android.view.View", text="搜索有福利")
                if search_view.exists:
                    d(className="android.widget.EditText", instance=0).send_keys("笔记本电脑")
                    d(className="android.widget.Button", text="搜索").click()
                    time.sleep(2)
                operate_task()
                finish_count = finish_count + 1
                if finish_count % 20 == 0:
                    d.swipe_ext("up", scale=0.2)
                    time.sleep(4)
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
