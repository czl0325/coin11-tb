import time

import uiautomator2 as u2
from uiautomator2 import Direction
from utils import check_chars_exist, get_current_app, task_loop, ALIPAY_APP, start_app

time1 = time.time()
unclick_btn = []
is_end = False
in_other_app = False
d = u2.connect()
start_app(d, ALIPAY_APP, init=True)
screen_width, screen_height = d.window_size()
have_clicked = {}


def check_in_task():
    package_name, _ = get_current_app(d)
    if package_name != ALIPAY_APP:
        return False
    if d(className="android.widget.TextView", text="做任务集肥料").exists:
        return True
    return False


d.watcher.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
d.watcher.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
d.watcher.start()
while True:
    farm_btn = d(resourceId="com.alipay.android.phone.openplatform:id/app_text", className="android.widget.TextView", text="芭芭农场")
    if farm_btn.exists:
        print("点击芭芭农场按钮，进入芭芭农场首页")
        farm_btn.click()
        time.sleep(5)
    task_btn = d(className="android.widget.Button", text="任务列表")
    if task_btn.exists:
        print("点击任务列表", task_btn.center()[0], task_btn.center()[1])
        task_btn.click()
        time.sleep(5)
    if check_in_task():
        break
finish_count = 0
error_count = 0
while True:
    try:
        time.sleep(3)
        get_btn = d(className="android.widget.Button", text="领取")
        if get_btn.exists:
            get_btn.click()
            time.sleep(2)
        to_btn = d.xpath('//android.widget.Button[@text="去逛逛" or @text="去完成"]')
        if to_btn.exists:
            print("去完成按钮存在")
            need_click_view = None
            need_click_name = ""
            for index, view in enumerate(to_btn.all()):
                name_view = d.xpath(f'(//android.widget.Button[@text="去逛逛" or @text="去完成"])[{index+1}]/parent::android.view.View/preceding-sibling::android.view.View[1]')
                if name_view.exists:
                    name_text = name_view.text
                    print(f"查找到任务：{name_text}")
                    if check_chars_exist(name_text):
                        continue
                    if have_clicked.get(name_text):
                        have_clicked[name_text] += 1
                    else:
                        have_clicked[name_text] = 1
                    if have_clicked.get(name_text) > 2:
                        continue
                    need_click_view = view
                    need_click_name = name_text
                    break
            if need_click_view:
                need_click_view.click()
                print(f"点击按钮:{need_click_name}")
                time.sleep(4)
                task_loop(d, check_in_task, origin_app=ALIPAY_APP)
                finish_count = finish_count + 1
            else:
                error_count += 1
                print("未找到可点击按钮", error_count)
                if error_count >= 2:
                    break
        else:
            print("没有查找到去完成按钮，退出循环")
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
